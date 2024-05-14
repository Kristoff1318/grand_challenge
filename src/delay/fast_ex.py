from stnu import NamedStnu
from fast_dc import DcTester, FastDc

def fast_ex(stnu):
    u_x = [edge.fro for edge in stnu.controllable_edges]
    u_c = [edge.fro for edge in stnu.uncontrollable_edges]
    r = {'Z': 0.0}

    fast_dc = FastDc()
    num_nodes, new_edges = fast_dc.generate_graph(stnu)
    _, ds, gx, d_matrix = fast_dc.allmax(num_nodes, new_edges)
    
    def ins(node):
        return [edge for edge in gx.controllable_edges if edge.to == node] + \
                [edge for edge in gx.uncontrollable_edges if edge.to == node]
    
    def outs(node):
        return [edge for edge in gx.controllable_edges if edge.to == node] + \
                [edge for edge in gx.uncontrollable_edges if edge.to == node]

    now = 0
    
    while not u_x and not u_c:
        rd = 
        new_exec_c = [x in new_exec if x.contingent]
        if not new_exec_c:
            for x in new_exec:
                # source/sinkDijkstra
                u_x.remove(x)
                r[x] = now_prime
                # remove x from network
        elif len(new_exec_c) == len(exec_c):
            for c in new_exec:
                # source/sinkDijkstra
                u_c.remove(x)
                r[x] = now_prime
                # remove x from network
        else:
            for x in exec_c:
                if x not in new_exec_c:
                    # source/sinkDijkstra
                u_x.remove(x)
                r[x] = now_prime
                # remove x from network
            for c in new_exec_c:
                # source/sinkDijkstra
                u_c.remove(x)
                r[x] = now_prime
                # remove x from network
        now = now_prime



            

stnu_text = """
    3 \n
    A E 50 55 \n
    B C 0 5 \n
    D E 0 5 \n
    2 \n
    A B 15 25 \n
    C D 15 30 \n
    """

network = NamedStnu()
network.read_from_text(stnu_text)
fast_ex(network)