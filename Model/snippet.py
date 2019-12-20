def predict(self, X):
    H = self._G.copy()
    X.apply(self._append_row_to_graph, args=(H,), axis=1)
    self._stable_graph(H, iterations=5)

def _stable_graph(self, graph, iterations=10):
    for _ in range(iterations):
        self._graph_iteration(graph)

def _graph_iteration(self, graph):
    for node in graph.nodes():
        self._update_node(graph, node)

def _update_node(self, graph, node):
    if graph.degree(node) > 0:
        neighbors_current_score = 0
        for neighbor in graph.neighbors(node):
            neighbors_current_score += graph.nodes[neighbor]['current']
        neighbors_current_avg = \
            neighbors_current_score / graph.degree(node)
        graph.nodes[node]['current'] = \
            0.5 * graph.nodes[node]['current'] + 0.5 * neighbors_current_avg


def train(self, X, y=None):
    super().train(X, y)
    X.apply(self._append_row_to_graph, args=(self._G,), axis=1)

def _append_row_to_graph(self, row, G):
    # Add nodes
    G.add_node(row['domain'], start=row['label'], current=row['label'])
    G.add_node(row['domain_ip'], start=row['label'], current=row['label'])
    G.add_node(row['as_subnet'], start=0.5, current=0.5)
    G.add_node(row['as_number'], start=0.5, current=0.5)
    G.add_node(row['as_name'], start=0.5, current=0.5)
    G.add_node(row['ns_base_domain'], start=0.5, current=0.5)
    G.add_node(row['ns_as_subnet'], start=0.5, current=0.5)
    G.add_node(row['ns_as_number'], start=0.5, current=0.5)
    G.add_node(row['ns_as_name'], start=0.5, current=0.5)
    # Add domain-IP edges
    G.add_edge(row['domain'], row['domain_ip'])
    G.add_edge(row['domain_ip'], row['as_subnet'])
    G.add_edge(row['as_subnet'], row['as_number'])
    G.add_edge(row['as_number'], row['as_name'])
    # Add nameserver edges
    G.add_edge(row['domain'], row['ns_base_domain'])
    G.add_edge(row['ns_base_domain'], row['ns_as_subnet'])
    G.add_edge(row['ns_as_subnet'], row['ns_as_number'])
    G.add_edge(row['ns_as_number'], row['ns_as_name'])


