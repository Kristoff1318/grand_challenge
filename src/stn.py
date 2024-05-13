import networkx as nx
from utils import display_stn
import numpy as np
from temporal_constraint import TemporalConstraint
from scipy.stats import truncnorm
import copy

class STN:
    def __init__(self):
        self.stn = nx.DiGraph()
    
    def add_edge(self, e1, e2, tc : TemporalConstraint):
        self.stn.add_edge(e1, e2, tc=tc)
    
    def display(self):
        display_stn(self.stn)

    def set_bounded(self):
        """
        Returns true if all edges have a set-bounded constraint
        """
        for u, v, tc in self.stn.edges(data='tc'):
            if not tc.constraint or not isinstance(tc.constraint, list):
                print(tc, tc.constraint.constraint)
                return False
        return True
    
    def contingent_map(self):
        """
        Returns dictionary mapping each contingent event to its incoming contingent edge (there should only be one). 
        """
        contingent_events = {}
        for event in self.stn.nodes:
            in_edges = self.stn.in_edges(event)
            for edge in in_edges:
                if self.stn.edges[edge]['tc'].contingent:
                    contingent_events[event] = edge
        return contingent_events
    
    def _distance_graph(self):
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
    
    def enabled(self, event, schedule, predecessors=None):
        contingent_map = self.contingent_map()
        if event in contingent_map:
            return contingent_map[event][0] in schedule
        
        for p in predecessors[event]:
            if p not in schedule:
                return False
        return event not in schedule

    def dispatchable_form(self):
        """
        Converts distance graph to dispatchable form by exposing implicit constraints.
        """
        distance_graph = self._distance_graph()
        g = nx.DiGraph()
        apsp = nx.floyd_warshall(distance_graph)
        for s in apsp:
            for t in apsp:
                if s != t:
                    g.add_edge(s,t,weight=apsp[s][t])
        return g

    def consistent(self):
        distance_graph = self._distance_graph()
        apsp = nx.floyd_warshall_numpy(distance_graph)
        return all(np.diag(apsp) >= 0)
    
    def find_predecessors(self, event):
        dispatchable_form = self.dispatchable_form()
        predecessors = {'START'}
        for neighbor in dispatchable_form.neighbors(event):
            if dispatchable_form[event][neighbor]['weight'] < 0:
                predecessors.add(neighbor) 
        return predecessors
    
    def execution_update(self, time, schedule, contingent_dispatch_arrivals):
        new_stn = copy.deepcopy(self)
        
        contingent_mapping = self.contingent_map()
        for event in self.stn.nodes:
            if event == 'START':
                continue
            elif event not in schedule: # events must be scheduled after current time, but before makespan limit
                tc = new_stn.stn['START'][event]['tc']
                new_stn.stn['START'][event]['tc'] = TemporalConstraint([time, tc.constraint[1]])
            else: 
                exec_time = schedule[event]
                new_stn.stn['START'][event]['tc'] = TemporalConstraint([exec_time, exec_time])

                for neighbor in self.stn.neighbors(event):
                    if neighbor in schedule:
                        new_stn.stn.remove_edge(event, neighbor)
                    else:
                        tc = new_stn.stn[event][neighbor]['tc']
                        if not tc.contingent: # neighbor event cannot precede an executed one
                            new_stn.stn[event][neighbor]['tc'] = TemporalConstraint([max(0, tc.constraint[0]), tc.constraint[1]])
                
                # truncate distributions based on current time
                for con in contingent_dispatch_arrivals:
                    start, end = contingent_dispatch_arrivals[con]
                    if con in schedule:
                        continue
                    duration = time - start
                    edge = contingent_mapping[con]
                    mean, std = new_stn.stn.edges[edge]['tc'].constraint.mean(), new_stn.stn.edges[edge]['tc'].constraint.std()
                    a = (duration - mean) / std
                    new_stn.stn.edges[edge]['tc'] = TemporalConstraint(truncnorm(a=a, b=np.inf, loc=mean, scale=std), contingent=True) 
        
        return new_stn

    def find_invalid_constraint(self, schedule):
        distance_graph = self.distance_graph()
        for u, v, bound in distance_graph.edges(data="weight"):
            if schedule[v] - schedule[u] > bound:
                return u, v