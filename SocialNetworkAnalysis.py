import networkx as nx


class SocialNetworkAnalysis(object):
    
    
    def __init__(self):
        self.G = nx.Graph()

    def append_row_to_graph(self, row):
        self.G.add_node(row['domain'], start=row['label'], current=row['label'])
        self.G.add_node(row['domain_ip'], start=row['label'], current=row['label'])
        self.G.add_node(row['as_subnet'], start=0.5, current=0.5)
        self.G.add_node(row['as_number'], start=0.5, current=0.5)
        self.G.add_node(row['as_name'], start=0.5, current=0.5)
        self.G.add_node(row['ns_base_domain'], start=0.5, current=0.5)
        self.G.add_node(row['ns_as_subnet'], start=0.5, current=0.5)
        self.G.add_node(row['ns_as_number'], start=0.5, current=0.5)
        self.G.add_node(row['ns_as_name'], start=0.5, current=0.5)
        
        self.G.add_edge(row['domain'], row['domain_ip'])
        self.G.add_edge(row['domain_ip'], row['as_subnet'])
        self.G.add_edge(row['as_subnet'], row['as_number'])
        self.G.add_edge(row['as_number'], row['as_name'])
        
        self.G.add_edge(row['domain'], row['ns_base_domain'])
        self.G.add_edge(row['ns_base_domain'], row['ns_as_subnet'])
        self.G.add_edge(row['ns_as_subnet'], row['ns_as_number'])
        self.G.add_edge(row['ns_as_number'], row['ns_as_name'])
        
        if None in self.G:
            self.G.remove_node(None)
    
    
    def stable_graph(self):
        for _ in range(10):
            self.__graph_iteration(self.G)


    def __graph_iteration(self, G):
        H = self.G.copy()
        for node in H.nodes():
            self.__update_node(G, node)


    def __update_node(self, G, node):
        if G.degree(node) > 0:
            neighbors_current_score = 0
            for neighbor in G.neighbors(node):
                neighbors_current_score += G.nodes[neighbor]['current']
            neighbors_current_avg = neighbors_current_score / G.degree(node)
            G.nodes[node]['current'] = 0.5 * G.nodes[node]['current'] + 0.5 * neighbors_current_avg

