import numpy as np
from copy import deepcopy
from scipy.optimize import linprog
from temporal_constraint import TemporalConstraint
from stn import STN

def optimize_timepoints(template_stn : STN, a):
    stn = deepcopy(template_stn)

    nodes = list(stn.stn.nodes)
    contingent_edge_map = {}
    contingent_id = 0

    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if stn.stn.has_edge(nodes[i], nodes[j]) and stn.stn[nodes[i]][nodes[j]]['tc'].contingent:
                contingent_edge_map[ (nodes[i], nodes[j]) ] = contingent_id
                contingent_id += 1

    # Contingent reduction
    for u,v,tc in stn.stn.edges(data='tc'):
        if tc.contingent:
            ub = tc.constraint.ppf(1-a/2)
            lb = -tc.constraint.ppf(a/2)
            stn.stn[u][v]['tc'] = TemporalConstraint([lb, ub], contingent=True)
    
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
                    delta_id = contingent_edge_map[(nodes[i], nodes[j])]
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
    
    # bounds = [[t, None]] * 2*len(nodes)
    # bounds += [[0, None]] * 2 * contingent_id

    opt = linprog(coefs, A_ub, b_ub, A_eq, b_eq)

    #~~~~~~~~~~~~~~~~
    # Convert to STNU
    # prefer not to do this in same function, but avoids reconstructing STNU
    #~~~~~~~~~~~~~~~~
    
    if opt.status == 0: 
        convert_to_stnu(stn, opt, contingent_edge_map)

    return {
        'status' : opt.status,
        # 'linprog_state' : opt.x if opt.status == 0 else None,
        'stnu' : stn if opt.status == 0 else None, 
        'execution_windows' : extract_execution_windows(stn) if opt.status == 0 else None
    }

def convert_to_stnu(stn, opt, contingent_edge_map):
    nodes = stn.stn.nodes
    for i, node in enumerate(nodes):
        if stn.stn.has_edge('START', node):
            stn.stn['START'][node]['tc'] = TemporalConstraint([opt.x[2*i+1], opt.x[2*i]])
        else:
            stn.stn.add_edge('START', node, tc=TemporalConstraint([opt.x[2*i+1], opt.x[2*i]]))
    for ce in contingent_edge_map:
        stn.stn[ce[0]][ce[1]]['tc'].constraint[0] = -stn.stn[ce[0]][ce[1]]['tc'].constraint[0] - opt.x[2*len(nodes) + 2*contingent_edge_map[ce]+1]
        stn.stn[ce[0]][ce[1]]['tc'].constraint[1] += opt.x[2*len(nodes) + 2*contingent_edge_map[ce]]    

def extract_execution_windows(stn):
    execution_windows = {}
    nodes = stn.stn.nodes
    for node in nodes:
        execution_windows[node] = [stn.stn['START'][node]['tc'][0], stn.stn['START'][node]['tc'][1]]
    return execution_windows

def srea(stn, am=0, ap=1, r=0.001):
    if ap - am <= r:
        return {
            'alpha' : ap,
            'execution_windows' : optimize_timepoints(stn, ap)['execution_windows'],
            'stnu' : optimize_timepoints(stn, ap)['stnu']
        }
    
    an = (am + ap) / 2

    if optimize_timepoints(stn, an)['status'] == 2: # infeasible
        return srea(stn, an, ap, r)
    
    return srea(stn, am, an, r)