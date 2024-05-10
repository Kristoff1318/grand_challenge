import numpy as np
import copy
from scipy.optimize import linprog
from temporal_constraint import TemporalConstraint
from stn import STN

def optimize_timepoints(template_stn : STN, a):
    stn = copy.deepcopy(template_stn)

    nodes = list(stn.stn.nodes)
    contingent_dict = {}
    contingent_id = 0

    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if stn.stn.has_edge(nodes[i], nodes[j]) and stn.stn[nodes[i]][nodes[j]]['tc'].contingent:
                contingent_dict[ (nodes[i], nodes[j]) ] = contingent_id
                contingent_id += 1

    # Contingent reduction
    for u,v,tc in stn.stn.edges(data='tc'):
        if tc.contingent:
            ub = tc.constraint.ppf(1-a/2)
            lb = -tc.constraint.ppf(a/2)
            stn.stn[u][v]['tc'] = TemporalConstraint((lb, ub), contingent=True)
    
    # LP setup
    state_dim = 2 * (len(nodes) + contingent_id)
    A_ub = np.empty((0,state_dim))
    b_ub = np.empty((0,1))
    A_eq = np.empty((0,state_dim))
    b_eq = np.empty((0,1))

    coefs = np.zeros((1, state_dim))            

    for i in range(len(nodes)):
        # timepoint upper bound ≥ lower bound
        c_upper_lower = np.zeros((1,state_dim))
        c_upper_lower[0, 2*i] = -1
        c_upper_lower[0, 2*i+1] = 1
        A_ub = np.vstack([A_ub, c_upper_lower])
        b_ub = np.vstack([b_ub, [0]])

        for j in range(len(nodes)):
            # Requirement
            if stn.stn.has_edge(nodes[i], nodes[j]):
                if not stn.stn[nodes[i]][nodes[j]]['tc'].contingent:
                    lb, ub = stn.stn[nodes[i]][nodes[j]]['tc']

                    c_orig_ub = np.zeros((1,state_dim))
                    c_orig_ub[0, 2*j] = 1
                    c_orig_ub[0, 2*i+1] = -1

                    c_orig_lb = np.zeros((1,state_dim))
                    c_orig_lb[0, 2*i] = 1
                    c_orig_lb[0, 2*j+1] = -1

                    A_ub = np.vstack([A_ub, c_orig_ub, c_orig_lb])
                    b_ub = np.vstack([b_ub, [ub], [-lb]])

                    # print('Requirement', nodes[i], nodes[j], 'UB', ub)

                # Contingent
                else:
                    delta_id = contingent_dict[(nodes[i], nodes[j])]
                    coefs[0, 2*len(nodes) + 2*delta_id] = -1
                    coefs[0, 2*len(nodes) + 2*delta_id + 1] = -1

                    # deltas ≥ 0
                    c_positive_delta = np.zeros((1,state_dim))
                    c_positive_delta[0, 2*len(nodes) + 2*delta_id] = -1
                    
                    c_positive_delta_rev = np.zeros((1,state_dim))
                    c_positive_delta_rev[0, 2*len(nodes) + 2*delta_id+1] = -1

                    A_ub = np.vstack([A_ub, c_positive_delta, c_positive_delta_rev])
                    b_ub = np.vstack([b_ub, [0], [0]])

                    # enforce timepoint diffs to upper bound
                    lb, ub = stn.stn[nodes[i]][nodes[j]]['tc'].constraint

                    c_contingent_ub = np.zeros((1,state_dim))
                    c_contingent_ub[0, 2*j] = 1
                    c_contingent_ub[0, 2*i] = -1
                    c_contingent_ub[0, 2*len(nodes) + 2*delta_id] = -1

                    # enforce timepoint diffs to lower bound
                    c_contingent_lb = np.zeros((1,state_dim))
                    c_contingent_lb[0, 2*j+1] = 1
                    c_contingent_lb[0, 2*i+1] = -1
                    c_contingent_lb[0, 2*len(nodes) + 2*delta_id+1] = 1

                    A_eq = np.vstack([A_eq, c_contingent_ub, c_contingent_lb])
                    b_eq = np.vstack([b_eq, [ub], [-lb]])

                    # print('Contingent', nodes[i], nodes[j], 'UB', ub, 'LB', -lb)
    
    bounds = 2 * [(0,0)]
    bounds += 2 * (len(nodes)-1) * [(0,10)]
    bounds += 2 * contingent_id * [(0, None)]

    return linprog(coefs, A_ub, b_ub, A_eq, b_eq, bounds=bounds)

def srea(stn, am, ap, r):
    if ap - am <= r:
        return {'alpha' : ap, 'linprog' : optimize_timepoints(stn, ap) }
    
    an = (am + ap) / 2

    if optimize_timepoints(stn, an).status == 2:
        return srea(stn, an, ap, r)
    
    return srea(stn, am, an, r)