from stn import STN
from temporal_constraint import TemporalConstraint
import random
from copy import deepcopy

def pstn_to_stnu(pstn: STN, total_risk):
    stnu = deepcopy(pstn)
    partial_risk = total_risk/pstn.num_contingent
    for u,v,tc in pstn.stn.edges(data='tc'):
        if tc.contingent:
            ub = tc.constraint.ppf(1-partial_risk/2)
            lb = tc.constraint.ppf(partial_risk/2)
            stnu.stn[u][v]['tc'] = TemporalConstraint([lb, ub], contingent=True)
    return stnu


# def gamma_bar(max_delay=10, inf_prob=0.05):
#     """Variable delay function
    
#        Return an interval [a, b], bounds the amount of time
#        that may pass between assignment and observation."""
#     if random.uniform(0, 1) <= inf_prob:
#         return 'inf'
#     return sorted(random.uniform(0, max_delay), random.uniform(0, max_delay))


# def observation_projection(stn: STN):
#     """Mapping from contingent events to fixed observation
#        delays"""
#     proj = {}
#     for u, v, tc in stn.edges(data='tc'):
#         if tc.contingent:
#             gb_lb, gb_ub = gamma_bar(tc.contingent)
#             proj[v] = random.uniform(gb_lb, gb_ub)


# def variable_to_fixed(s: STN):
#     """Converts a variable-delay controllability problem
#        to a fixed-delay controllability problem
       
#        s: must be an stn with BOUNDED contingent edges"""
#     new_s = deepcopy(s)
#     new_gamma = {}
#     for u, v, tc in new_s.stn.edges(data='tc'):
#         if tc.contingent:
#             a, b = new_s.edges[u, v]
#             gb_ub, gb_lb = gamma_bar()
#             if gb_ub == 'inf' or gb_ub == gb_lb:
#                 new_gamma[v] = b
#             elif b - a <= gb_ub - gb_lb:
#                 new_gamma[v] = 'inf'
#             else:
#                 new_s.stn.edges[u][v]['tc'] = TemporalConstraint(
#                     [a + gb_ub, b + gb_lb], contingent=True)
#                 new_gamma[v] = 0
#                 for w, x, tc_ in new_s.stn.edges(data='tc'):
#                     if w == v:
#                         if not tc_.contingent:
#                             c, d = new_s.edges[w, x]
#                             new_s.stin.edges[w][x]['tc'] = TemporalConstraint(
#                                 c + gb_ub, d + gb_lb)
#     return new_s, new_gamma

# variable_stn = STN()
# variable_stn.add_edge('X', 'E', TemporalConstraint((1, 2), contingent=True))
# variable_stn.add_edge('E', 'Z', TemporalConstraint((3, 4), contingent=True))
# variable_stn.display()
# fixed_stn, fixed_gamma = variable_to_fixed(variable_stn)
# fixed_stn.display()


#####

# AllMax projection:
# STN where all contingent links in the STNU take on
# their maximum value

def all_max_proj(stnu: STN):
    all_max = deepcopy(stnu)
    for u,v,tc in stnu.stn.edges(data='tc'):
        if tc.contingent:
            max_val = max(stnu.edges[u, v])
            all_max.stn[u][v]['tc'] = TemporalConstraint([max_val, max_val])
    return all_max



def fast_ex_update(t, new_exec, all_max_graph, dist_matrix):
    pass


def fast_ex():
    pass