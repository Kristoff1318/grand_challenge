from stn import TemporalNetwork
from scipy.optimize import linprog
from dispatcher import Dispatcher

class TemporalNetwork:
    def __init__(self, events, constraints):
        self.events = events
        self.constraints = constraints
        self.validate()
    
    def is_executable(self, event):
        """
        Returns True if given event is executable (all incoming edges are not contingent).
        """
        if event not in self.events:
            raise Exception(f'{event} not in pSTN events: {self.events}')
        
        for c in self.constraints:
            if c.e2 == self.event and c.is_contingent:
                return False
        return True
    
    def validate(self):
        for c in self.constraints:
            if c.e1 not in self.events:
                raise Exception(f'{c.e1} not in pSTN events: {self.events}')
            if c.e2 not in self.events:
                raise Exception(f'{c.e2} not in pSTN events: {self.events}')
    
    def is_STN(self):
        """
        Returns true if all constraints are requirement constraints (STN).
        """
        for c in self.constraints:
            if c.is_contingent:
                return False
        return True
    
    def is_STNU(self):
        """
        Returns true if all constraints are set bounded constraints (STN or STNU).
        """
        for c in self.constraints:
            if c.is_contingent:
                return False
        return True
    
    def map_to_stn(self):
        if not self.is_STN():
            raise Exception("contingent constraint in graph, reduce all to requirements first")
        
        stn = TemporalNetwork()
        for c in self.constraints:
            stn.add_edge(c.e1, c.e2, [c.temporal[0], c.temporal[1]])
        return stn
    
class Constraint:
    def __init__(self, e1, e2, temporal, contingent, set_bounded):
        self.event_1 = e1
        self.event_2 = e2
        self.temporal = temporal
        self.contingent = contingent
        self.set_bounded = set_bounded

def main():
    # STN MODELING
    # stn = STN()
    # stn.add_edge('A', 'E', [0, 10])
    # stn.add_edge('B', 'D', [1, 1])
    # stn.add_edge('A', 'C', [0, 10])
    # stn.add_edge('C', 'D', [2, 2])
    # stn.add_edge('A', 'D', [2, 2])
    # stn.add_edge('Q', 'H', [2, 89])
    # stn.add_edge('A', 'E', [0, 10])
    # stn.add_edge('F', 'H', [1, 1])
    # stn.add_edge('A', 'Q', [0, 10])
    # stn.add_edge('Q', 'Y', [2, 2])
    # stn.add_edge('A', 'D', [2, 2])
    # stn.add_edge('A', 'P', [2, 2])
    # stn.add_edge('E', 'H', [22, 89])
    # stn.display()

    stn = TemporalNetwork()
    stn.add_edge('A', 'B', [0, 10])
    stn.add_edge('B', 'D', [1, 1])
    stn.add_edge('A', 'C', [0, 10])
    stn.add_edge('C', 'D', [2, 2])
    stn.display()

    dispatcher = Dispatcher(sim_time=True)
    stn.online_dispatch(dispatcher)

if __name__ == '__main__':
    main()