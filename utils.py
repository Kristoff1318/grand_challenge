from IPython.display import display, SVG
import tempfile
import subprocess
import os
import numpy as np

def display_stn(g):
    # display(SVG(graph_to_svg(g, writer_fn=write_stn_to_dot)))
    graph_to_svg(g, writer_fn=write_stn_to_dot)

def graph_to_svg(g, writer_fn):
    with tempfile.NamedTemporaryFile(mode='w', suffix=".dot", delete=False) as f:
        name = f.name
        writer_fn(g, f)
    # Call dot on the name
    svg_file = "{}.svg".format(name)
    result = subprocess.call(["dot", "-Tsvg", name, "-o", svg_file])
    with open(svg_file, "r") as f:
        svg = f.read()

    with open("stn.svg", "w") as f:
        f.write(svg)

    os.remove(name)
    os.remove(svg_file)

    # return svg

def write_stn_to_dot(g, f):
    #dpi=90
    f.write("digraph G {\n  rankdir=LR;\ndpi=70\n")
    # Nodes
    for v in g.nodes():
        f.write("  \"{}\" [shape=circle, width=0.6, fixedsize=true];\n".format(v))
    # Simple temporal constraints
    for (u, v) in g.edges():
        stc = g[u][v]['tc'].constraint
        f.write("  \"{}\" -> \"{}\" [label=\"{}\"];".format(u, v, format_stc(stc)))
    f.write("}")

def format_stc(stc):
    return "[{}, {}]".format(format_num(stc[0]), format_num(stc[1]))

def format_num(v):
    if v == np.inf:
        return "∞"
    elif v == -np.inf:
        return "-∞"
    else:
        return str(v)
    

#    def schedule_offline(self, start_event):
#         """
#         Computes a fixed schedule offline that satisfies all of the
#         temporal constraints in the STN.
#         """
#         distance_graph = self.distance_graph()
#         dispatchable_stn = self.dispatchable_form(distance_graph)

#         schedule = []
#         unscheduled = list(self.stn.nodes)
#         exec_windows = {event : [-np.inf, np.inf] for event in self.stn.nodes}

#         schedule.append( (start_event, 0.0) )
#         unscheduled.remove(start_event)
#         self._propagate(start_event, 0.0, dispatchable_stn, exec_windows)
        
#         while(unscheduled):
#             event = unscheduled.pop()
#             dispatch_time = exec_windows[event][0]
#             schedule.append( (event, dispatch_time) )
#             self._propagate(event, dispatch_time, dispatchable_stn, exec_windows)

#         return schedule

# def online_dispatch(self, dispatcher, ignore_contingent):
#         distance_graph = self.distance_graph()
#         dispatchable_stn = self.dispatchable_form(distance_graph)

#         schedule = {}
#         predecessors = {event : set() for event in self.stn.nodes}
#         exec_windows = {event : [-np.inf, np.inf] for event in self.stn.nodes}

#         for event in self.stn.nodes:
#             for neighbor in dispatchable_stn.neighbors(event):
#                 if dispatchable_stn[event][neighbor]['weight'] <= 0:
#                     predecessors[event].add(neighbor)            
        
#         contingent_queue = {}

#         dispatcher.start()
#         while len(schedule) < self.stn.number_of_nodes():
#             dispatchable_events = list( filter( lambda x : 
#                                             x not in schedule and 
#                                             x not in contingent_queue and
#                                             self._enabled(x, schedule, predecessors),
#                                             self.stn.nodes
#                                         ) )
#             executable_t = None
#             if dispatchable_events:
#                 executable_ev = min( dispatchable_events, key = lambda x : exec_windows[x][0] )
#                 executable_t = exec_windows[executable_ev][0]

#             if contingent_queue:
#                 contingent_ev = min( contingent_queue, key = lambda x : contingent_queue[x] )
#                 contingent_t = contingent_queue[contingent_ev]

#             if contingent_queue and (len(dispatchable_events) == 0 or contingent_t < executable_t): # contingent is next
#                 dispatcher.sleep( contingent_t - dispatcher.time() )
                
#                 dispatch_time = dispatcher.time()
#                 dispatcher.print_time_message("Received {} {}".format(event, ""), dispatch_time)
#                 schedule[contingent_ev] = dispatch_time
#                 self._propagate(contingent_ev, schedule[contingent_ev], dispatchable_stn, exec_windows)
#             elif dispatchable_events: # required is next
#                 if dispatcher.time() > exec_windows[executable_ev][1]:
#                     raise Exception(f'Event {executable_ev} could not be scheduled: exec window [{executable_t}, {exec_windows[executable_ev][1]}] missed at current time {dispatcher.time()}')
#                 dispatcher.sleep( max(0, executable_t - dispatcher.time()) )
#                 dispatch_time = dispatcher.dispatch(executable_ev)
#                 schedule[executable_ev] = dispatch_time
#                 self._propagate(executable_ev, dispatch_time, dispatchable_stn, exec_windows)

#                 if not ignore_contingent:
#                     for successor in self.stn.successors(executable_ev):
#                         constraint = self.stn[executable_ev][successor]['tc']
#                         if constraint.contingent:
#                             successor_dispatch_time = schedule[executable_ev] + constraint.sample()
#                             contingent_queue[successor] = successor_dispatch_time
#         dispatcher.done()
#         return schedule