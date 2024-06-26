from srea import srea
from stn import STN
from dispatcher import Dispatcher
from utils import trunc

def live(event, exec_windows, time):
    return time+0.001 >= trunc(exec_windows[event][0],1) and time-0.001 <= trunc(exec_windows[event][1],1)

def check_schedule_consistency(schedule, stn):
    for u, v, tc in stn.stn.edges(data='tc'):
        if not tc.contingent:
            if (schedule[v] - schedule[u] < tc.constraint[0]-.001) or (schedule[v] - schedule[u] > tc.constraint[1]+.001):
                print(f'Invalid: ({u}, {schedule[u]}) and ({v}, {schedule[v]}) violate {tc.constraint}.')
                return False
    print('Valid!')
    return True

def drea(pstn : STN, dispatcher : Dispatcher):
    srea_out = srea(pstn)
    guide_stn : STN = srea_out['stnu']
    execution_windows = srea_out['execution_windows']
    alpha = srea_out['alpha']
    nodes = set( guide_stn.stn.nodes )

    schedule = {'START' : 0.0}
    contingent_dispatch_arrivals = {}
    req_enabled = set()

    predecessors = {event : guide_stn.find_predecessors(event) for event in nodes}
    predecessors['START'] = set()

    contingent_map = guide_stn.contingent_map()
    required_events = nodes - set(contingent_map.keys()) - set('START')
    run_srea = False

    k = 0
    mAR = 2
    mSC = -1
    dispatcher.start()
    while len(schedule) < guide_stn.stn.number_of_nodes():
        t = trunc(dispatcher.time(),1)
        print(f"{'TIME:':<40}{t}\n")
        print(f"{'CAPTURED P MASS:':<40}{1-alpha}\n")
        print(f"{'DISPATCHED:':<40}{schedule}\n")
        print(f"{'SREA RESULT (EXEC WINDOWS):':<40}{execution_windows}\n")
        print(f"{'(HIDDEN) ARRIVALS:':<40}{contingent_dispatch_arrivals}\n")
        print("===========")
        # print(t, schedule, execution_windows, contingent_dispatch_arrivals, )
        # print()
            
        for con in contingent_dispatch_arrivals:
            end = contingent_dispatch_arrivals[con][1]
            if t < trunc(end,1):
                run_srea = True
                k += 1
            elif t == trunc(end,1):
                schedule[con] = t
                dispatcher.receive(con)
                run_srea = True
                k += 1
        
        for req in required_events:
            if guide_stn.enabled(req, schedule, predecessors):
                req_enabled.add(req)
        
        if run_srea:# and (1 - alpha) ** k <= mAR:
            updated_stn = pstn.execution_update(t, schedule, contingent_dispatch_arrivals)
            updated_srea = srea(updated_stn)
            if updated_srea['stnu'] is None:
                print("No LP solution, controllability not guaranteed")
            else:
                #if abs( updated_srea['alpha'] - alpha ) >= mSC:
                guide_stn, execution_windows, alpha = updated_srea['stnu'], updated_srea['execution_windows'], updated_srea['alpha']
                k = 0
            contingent_map = guide_stn.contingent_map()
        
        for req in required_events:
            if live(req, execution_windows, t) and (req in req_enabled):
                schedule[req] = t
                dispatcher.dispatch(req)
                req_enabled.remove(req)
        
        for con in contingent_map:
            if guide_stn.enabled(con, schedule) and con not in contingent_dispatch_arrivals:
                if con == 'Aet':
                    contingent_dispatch_arrivals[con] = (t, t + 3.88 )
                else:
                    contingent_dispatch_arrivals[con] = (t, t + pstn.stn.edges[contingent_map[con]]['tc'].sample() )
        
        run_srea = False

        dispatcher.sleep(0.10000001)
    
    if len(schedule) == guide_stn.stn.number_of_nodes():
        print("~~~~~~Dispatching complete~~~~~~")
        return check_schedule_consistency(schedule, pstn)
        # print(schedule)
    else:
        print("Execution terminating early, STN inconsistent")
        return False

            
                
