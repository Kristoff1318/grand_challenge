from scipy.stats import norm
from stn import STN
from temporal_constraint import TemporalConstraint
from srea import srea

stn = STN()
stn.add_edge('START', 'START', TemporalConstraint([0.0, 0.0]))
stn.add_edge('START', 'Ast', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Aet', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Bst', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Bet', TemporalConstraint([0.0, 10.0]))

stn.add_edge('Ast', 'Aet', TemporalConstraint(norm(loc=6, scale=2), contingent=True))
stn.add_edge('Bst', 'Bet', TemporalConstraint(norm(loc=2, scale=1), contingent=True))
stn.add_edge('Aet', 'Bet', TemporalConstraint([-2.0, 2.0]))

srea_result = srea(stn, 0, 1, 0.001)
print('Optimal alpha', srea_result['alpha'])
print('State results', srea_result['linprog_state'])
srea_result['stnu'].display()