import networkx as nx
from utils import display_stn
from temporal_constraint import TemporalConstraint

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