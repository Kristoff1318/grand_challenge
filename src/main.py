from scipy.stats import norm
from stn import STN
from temporal_constraint import TemporalConstraint
from srea import srea
from drea import drea
from dispatcher import Dispatcher

stn = STN()
stn.add_edge('START', 'START', TemporalConstraint([0.0, 0.0]))
stn.add_edge('START', 'Ast', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Aet', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Bst', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Bet', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'C', TemporalConstraint([0, 20.0]))

stn.add_edge('Ast', 'Aet', TemporalConstraint(norm(loc=6, scale=2), contingent=True))
stn.add_edge('Bst', 'Bet', TemporalConstraint(norm(loc=6, scale=1), contingent=True))
# stn.add_edge('Bst', 'Bet', TemporalConstraint([2.0, 4.0]))
stn.add_edge('Aet', 'Bet', TemporalConstraint([-2.0, 2.0]))
stn.add_edge('Bet', 'C', TemporalConstraint([2.0, 7.0]))

# srea_result = srea(stn, 0, 1, 0.001)
# print('Optimal alpha', srea_result['alpha'])
# print('State results', srea_result['execution_windows'])
# srea_result['stnu'].display()

# stn3 = STN()
# stn3.add_edge('START', 'START', TemporalConstraint([0.0, 0.0]))
# stn3.add_edge('START', 'TaskA_start', TemporalConstraint([0.0, 8.0]))
# stn3.add_edge('START', 'TaskB_start', TemporalConstraint([0.0, 8.0]))
# stn3.add_edge('TaskA_start', 'TaskA_end', TemporalConstraint(norm(loc=6, scale=1), contingent=True))
# stn3.add_edge('TaskB_start', 'TaskB_end', TemporalConstraint(norm(loc=8, scale=1), contingent=True))
# stn3.add_edge('TaskA_end', 'TaskC_start', TemporalConstraint([0.0, 2.0]))
# stn3.add_edge('TaskB_end', 'TaskC_start', TemporalConstraint([0.0, 2.0]))
# stn3.add_edge('TaskC_start', 'TaskC_end', TemporalConstraint(norm(loc=10, scale=1), contingent=True))
# stn3.add_edge('TaskC_end', 'END', TemporalConstraint([0.0, 0.0]))

dispatcher = Dispatcher(sim_time=True)
drea(stn, dispatcher)