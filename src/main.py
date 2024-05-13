from scipy.stats import norm, truncnorm
from stn import STN
from temporal_constraint import TemporalConstraint
from srea import srea
from drea import drea
from dispatcher import Dispatcher
import numpy as np

stn = STN()
stn.add_edge('START', 'START', TemporalConstraint([0.0, 0.0]))
stn.add_edge('START', 'Ast', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Aet', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Bst', TemporalConstraint([0.0, 10.0]))
stn.add_edge('START', 'Bet', TemporalConstraint([0.0, 10.0]))

stn.add_edge('Ast', 'Aet', TemporalConstraint(truncnorm(a=(0-6)/2, b=np.inf, loc=6, scale=2), contingent=True))
stn.add_edge('Bst', 'Bet', TemporalConstraint(truncnorm(a=(0-2)/1, b=np.inf, loc=2, scale=1), contingent=True))
stn.add_edge('Aet', 'Bet', TemporalConstraint([-2.0, 2.0]))

# stn.add_edge('Bst', 'Bet', TemporalConstraint([2.0, 4.0]))

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

# pstn = STN()
# pstn.add_edge('START', 'START', TemporalConstraint([0,0]))
# pstn.add_edge('START', 'Ast', TemporalConstraint(norm(loc=15, scale=5), contingent=True))
# pstn.add_edge('START', 'Aet', TemporalConstraint(norm(loc=30, scale=3), contingent=True))
# pstn.add_edge('START', 'Bst', TemporalConstraint(norm(loc=10, scale=2), contingent=True))
# pstn.add_edge('START', 'Bet', TemporalConstraint(norm(loc=60, scale=2), contingent=True))
# pstn.add_edge('Ast', 'END', TemporalConstraint([0,100]))
# pstn.add_edge('Aet', 'END', TemporalConstraint([0,100]))
# pstn.add_edge('Bst', 'END', TemporalConstraint([0,100]))
# pstn.add_edge('Bet', 'END', TemporalConstraint([0,100]))


# stn = STN()
# stn.add_edge('START', 'START', TemporalConstraint([0.0, 0.0]))
# stn.add_edge('START', 'Ast', TemporalConstraint([0.0, 10.0]))
# stn.add_edge('START', 'Aet', TemporalConstraint([0.0, 10.0]))
# stn.add_edge('START', 'Bst', TemporalConstraint([0.0, 10.0]))
# stn.add_edge('START', 'Bet', TemporalConstraint([0.0, 10.0]))

# stn.add_edge('Ast', 'Aet', TemporalConstraint(norm(loc=6, scale=2), contingent=True))
# stn.add_edge('Bst', 'Bet', TemporalConstraint(norm(loc=6, scale=1), contingent=True))
# stn.add_edge('Aet', 'Bet', TemporalConstraint([-2.0, 2.0]))


# stn_complex = STN()

# # Adding tasks and their temporal constraints
# stn_complex.add_edge('START', 'TaskA_start', TemporalConstraint([0.0, 8.0]))
# stn_complex.add_edge('START', 'TaskB_start', TemporalConstraint([0.0, 8.0]))
# stn_complex.add_edge('TaskA_start', 'TaskA_end', TemporalConstraint(norm(loc=6, scale=1), contingent=True))
# stn_complex.add_edge('TaskB_start', 'TaskB_end', TemporalConstraint(norm(loc=8, scale=1), contingent=True))
# stn_complex.add_edge('TaskA_end', 'TaskC_start', TemporalConstraint([0.0, 2.0]))
# stn_complex.add_edge('TaskB_end', 'TaskC_start', TemporalConstraint([0.0, 2.0]))
# stn_complex.add_edge('TaskC_start', 'TaskC_end', TemporalConstraint(norm(loc=10, scale=1), contingent=True))
# stn_complex.add_edge('TaskC_end', 'TaskD_start', TemporalConstraint([0.0, 3.0]))
# stn_complex.add_edge('TaskD_start', 'TaskD_end', TemporalConstraint(norm(loc=14, scale=2), contingent=True))
# stn_complex.add_edge('TaskD_end', 'END', TemporalConstraint([0.0, 0.0]))

# # Additional temporal constraints for robustness
# stn_complex.add_edge('TaskA_start', 'TaskB_start', TemporalConstraint([0.0, 2.0]))
# stn_complex.add_edge('TaskB_start', 'TaskA_start', TemporalConstraint([0.0, 2.0]))
# stn_complex.add_edge('TaskA_end', 'TaskB_end', TemporalConstraint([0.0, 3.0]))
# stn_complex.add_edge('TaskB_end', 'TaskA_end', TemporalConstraint([0.0, 3.0]))
# stn_complex.add_edge('TaskC_start', 'TaskD_start', TemporalConstraint([0.0, 1.0]))
# stn_complex.add_edge('TaskD_start', 'TaskC_start', TemporalConstraint([0.0, 1.0]))
# stn_complex.add_edge('TaskC_end', 'TaskD_end', TemporalConstraint([0.0, 2.0]))
# stn_complex.add_edge('TaskD_end', 'TaskC_end', TemporalConstraint([0.0, 2.0]))

# success = 0
# attempts = 500
# for i in range(attempts):
#     print(i)
#     dispatcher = Dispatcher(sim_time=True, quiet=True)
#     success += drea(stn, dispatcher)
# print('Robustness:', success/attempts * 100)

dispatcher = Dispatcher(sim_time=True)
drea(stn, dispatcher)