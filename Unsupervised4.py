import graphviz

# Function to generate computational graph for expression
def make_computational_graph(expr, name='p'):
    graph = graphviz.Digraph()
    count = [0]

    def add_node(label):
        node_id = f"n{count[0]}"
        graph.node(node_id, label)
        count[0] += 1
        return node_id

    def build_graph(expr):
        if isinstance(expr, sp.Symbol):
            return add_node(str(expr))
        elif isinstance(expr, sp.Number):
            return add_node(str(expr))
        elif isinstance(expr, sp.Pow):
            base = build_graph(expr.args[0])
            exp = build_graph(expr.args[1])
            node = add_node("^")
            graph.edge(base, node)
            graph.edge(exp, node)
            return node
        elif isinstance(expr, sp.Mul):
            node = add_node("*")
            for arg in expr.args:
                child = build_graph(arg)
                graph.edge(child, node)
            return node
        elif isinstance(expr, sp.Add):
            node = add_node("+")
            for arg in expr.args:
                child = build_graph(arg)
                graph.edge(child, node)
            return node
        elif isinstance(expr, sp.Max):
            node = add_node("max")
            for arg in expr.args:
                child = build_graph(arg)
                graph.edge(child, node)
            return node
        elif isinstance(expr, sp.exp):
            arg = build_graph(expr.args[0])
            node = add_node("exp")
            graph.edge(arg, node)
            return node
        else:
            # Fallback for other types
            node = add_node(str(expr.func))
            for arg in expr.args:
                child = build_graph(arg)
                graph.edge(child, node)
            return node

    output_node = build_graph(expr)
    graph.node('output', name)
    graph.edge(output_node, 'output')
    return graph

# Create computational graphs
graph1 = make_computational_graph(p1, name='p1')
graph2 = make_computational_graph(p2, name='p2')

# Render as SVG for display
graph1_svg = graph1.pipe(format='svg')
graph2_svg = graph2.pipe(format='svg')

(graph1_svg, graph2_svg)

