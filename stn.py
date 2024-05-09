import networkx as nx
from utils import display_stn
import numpy as np
import scipy.stats
from scipy.optimize import linprog
import random
from typing import Tuple
from dispatcher import Dispatcher

class TemporalConstraint:
    """
    Can specify one of requirement constraint (req), contingent constraint (con), or both.
    Requirement must be an STC of form [float, float]. Used for static scheduling.
    Contingent constraint is a scipy.stats distribution supporting sampling via RV.rvs()
    """
    def __init__(self, constraint, contingent : bool = False): 
        self.constraint = constraint
        self.contingent = contingent

        if not self.contingent:
            if not isinstance(constraint, tuple) or len(constraint) != 2 or not isinstance(constraint[0], float) or not isinstance(constraint[1], float):
                raise Exception(f'Requirement constraint is not a float tuple of length 2')
    
    @property
    def set_bounded(self):
        return isinstance(self.constraint, Tuple)
    
    def sample(self):
        if not self.contingent:
            raise Exception("Cannot sample from requirement constraint")
        if self.set_bounded:
            return random.uniform(self.constraint[0], self.constraint[1])
        else:
            return self.constraint.rvs()

    def __getitem__(self, index):
        if not self.set_bounded:
            raise Exception(f'Cannot get bounds for probabilistic constraint')
        if index == 0:
            return self.constraint[0]
        elif index == 1:
            return self.constraint[1]
        else:
            raise IndexError("Valid indices are 0 or 1")

class STN:
    def __init__(self):
        self.stn = nx.DiGraph()
        self.edges = {}
    
    def add_edge(self, e1, e2, tc : TemporalConstraint):
        self.edges[(e1, e2)] = tc
        self.stn.add_edge(e1, e2, tc=tc)
    
    def display(self):
        display_stn(self.stn)
    
    @property
    def num_contingent(self):
        num_contingent = 0
        for u, v, tc in self.stn.edges(data='tc'):
            num_contingent += tc.contingent
        return num_contingent

    def set_bounded(self):
        """
        Returns true if all edges have a set-bounded constraint
        """
        for u, v, tc in self.stn.edges(data='tc'):
            if not tc.constraint:
                return False
        return True
    
    def distance_graph(self):
        """
        Converts STN to a distance graph.
        """
        if not self.set_bounded():
            raise Exception("Cannot find distance graph when probabilistic constraints are present")
        
        dg = nx.DiGraph()
        for e in self.stn.edges:
            e_from = e[0]
            e_to = e[1]
            lowerb = self.stn[e_from][e_to]['tc'][0]
            upperb = self.stn[e_from][e_to]['tc'][1]
            dg.add_edge(e_from, e_to, weight=upperb)
            dg.add_edge(e_to, e_from, weight=-lowerb)
        return dg

    def dispatchable_form(self, dg):
        """
        Converts distance graph to dispatchable form by exposing implicit constraints.
        """
        g = nx.DiGraph()
        apsp = nx.floyd_warshall(dg)
        for s in apsp:
            for t in apsp:
                if s != t:
                    g.add_edge(s,t,weight=apsp[s][t])
        return g

    def _propagate(self, event, dispatch_time, stn, exec_windows):
        for neighbor in stn.neighbors(event):
            up = min(exec_windows[neighbor][1], dispatch_time + stn[event][neighbor]['weight'])
            lp = max(exec_windows[neighbor][0], dispatch_time - stn[neighbor][event]['weight'])
            exec_windows[neighbor] = [lp, up]
    
    def _enabled(self, event, schedule, predecessors):
        for p in predecessors[event]:
            if p not in schedule:
                return False
        return True
    
    def find_invalid_constraint(self, schedule):
        distance_graph = self.distance_graph()
        for u, v, bound in distance_graph.edges(data="weight"):
            if schedule[v] - schedule[u] > bound:
                return u, v
            
    def srea(self, a):
        nodes = list(self.stn.nodes)

        # Contingent reduction
        for u,v,tc in self.stn.edges(data='tc'):
            if tc.contingent:
                ub = tc.constraint.ppf(1 - a/2)
                lb = -tc.constraint.ppf(a/2)
                self.stn[u][v]['tc'] = TemporalConstraint((lb, ub), contingent=True)
        
        # LP setup
        state_dim = 2 * (len(nodes) + len(nodes))
        A_ub = np.empty((1,state_dim))
        b_ub = np.empty((1,1))
        A_eq = np.empty((1,state_dim))
        b_eq = np.empty((1,1))

        coefs = np.zeros((1, state_dim))
        coefs[2 * len(nodes):] = 1

        # Inequalities
        # timepoint upper bound ≥ lower bound
        for i in range(len(nodes)):
            c = np.zeros((1,state_dim))
            c[0, 2*i] = -1
            c[0, 2*i+1] = 1
            A_ub = np.vstack([A_ub, c])
            b_ub = np.vstack([b_ub, [0]])
        
        # all deltas ≥ 0
        for i in range(self.num_contingent):
            c = np.zeros((1,state_dim))
            c[0, 2*len(nodes) + 2*i] = -1
            A_ub = np.vstack([A_ub, c])
            b_ub = np.vstack([b_ub, [0]])

        # original constraints respected
        distance_graph = self.distance_graph()
        dispatchable_stn = self.dispatchable_form(distance_graph)

        for i in range(len(nodes)):
            for j in range(len(nodes)):

                if i != j and ( not self.stn.has_edge(nodes[i], nodes[j]) or not self.stn[nodes[i]][nodes[j]]['tc'].contingent ):
                    c = np.zeros((1,state_dim))
                    ub = dispatchable_stn[nodes[i]][nodes[j]]['weight']
                    
                    c[0, 2*i] = 1
                    c[0, 2*j+1] = -1
                    A_ub = np.vstack([A_ub, c])
                    b_ub = np.vstack([b_ub, [ub]])

                    # c = np.zeros((1,state_dim))
                    # lb = dispatchable_stn[nodes[j]][nodes[i]]
                    # c[0, 2*j] = 1
                    # c[0, 2*i+1] = -1
                    # A_ub = np.vstack([A_ub, c])
                    # b_ub = np.vstack([b_ub, [lb]])
                
                if self.stn.has_edge(nodes[i], nodes[j]) and self.stn.edges[nodes[i], nodes[j]]['tc'].contingent:
                    c = np.zeros((1,state_dim))
                    constraint = self.stn[nodes[i]][nodes[j]]['tc']
                    lb, ub = constraint.constraint

                    c[0, 2*j] = 1
                    c[0, 2*i] = -1
                    c[0, 2*len(nodes) + 2*i] = -1
                    A_eq = np.vstack([A_eq, c])
                    b_eq = np.vstack([b_eq, [ub]])

                    c = np.zeros((1,state_dim))
                    c[0, 2*j+1] = 1
                    c[0, 2*i+1] = -1
                    c[0, 2*len(nodes) + 2*j] = 1
                    A_eq = np.vstack([A_eq, c])
                    b_eq = np.vstack([b_eq, [-lb]])
        
        print(coefs, A_ub, b_ub, A_eq, b_eq)
        print( linprog(coefs, A_ub, b_ub, A_eq, b_eq) )

def main():
    stn = STN()
    # stn.add_edge('A', 'B', TemporalConstraint((0.0, 10.0)))
    # stn.add_edge('A', 'C', TemporalConstraint((0.0, 10.0)))
    # stn.add_edge('B', 'D', TemporalConstraint(scipy.stats.norm(loc=2, scale=5), contingent=True))
    # stn.add_edge('C', 'D', TemporalConstraint((2.0, 5.0)))

    stn.add_edge('Ast', 'Aet', TemporalConstraint(scipy.stats.norm(loc=6, scale=2), contingent=True))
    stn.add_edge('Bst', 'Bet', TemporalConstraint(scipy.stats.norm(loc=2, scale=1), contingent=True))
    stn.add_edge('Aet', 'Bet', TemporalConstraint((-2.0, 2.0)))

    # dispatcher = Dispatcher(sim_time=True)
    # stn.display()
    stn.srea(0.506)
    # dispatch_recording = stn.online_dispatch(dispatcher, ignore_contingent=False)
    # invalid_constraint = stn.find_invalid_constraint(dispatch_recording)
    # if invalid_constraint:
    #     print(f'NOT VALID: {invalid_constraint[0]} at {dispatch_recording[invalid_constraint[0]]} and {invalid_constraint[1]} at {dispatch_recording[invalid_constraint[1]]} violates constraint.')

if __name__ == '__main__':
    main()