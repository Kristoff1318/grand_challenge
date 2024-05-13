import networkx as nx

g = nx.DiGraph()
g.add_edge('a', 'b', weight=5)
g.add_edge('a', 'c')
g.add_edge('d', 'a')

print(
    g.in_edges('a')
)



"""
inconsistent run:
5.67 {'START': 0.0, 'Ast': 0.0, 'Bst': 4.86, 'Aet': 5.18} {'Aet': (0.01, 5.185607832702389), 'Bet': (4.87999999999994, 6.2472841225062465)}
"""