from typing import Tuple
import random

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