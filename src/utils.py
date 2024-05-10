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
        return str(round(v,2))