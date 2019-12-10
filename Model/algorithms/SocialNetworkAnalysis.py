import networkx as nx

class SocialNetworkAnalysis(object):
    
    
    def __init__(self):
        self.G = nx.Graph()
        self.H = None

    def copy_graph(self):
        self.H = self.G.copy()

    # def append_row_to_graph(self, row, cascade_updates=False):
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

        # if cascade_updates:
        #     self.__update_node(row['domain'])
        #     self.__update_node(row['domain_ip'])
        #     self.__update_node(row['as_subnet'])
        #     self.__update_node(row['as_number'])
        #     self.__update_node(row['as_name'])
        #     self.__update_node(row['ns_base_domain'])
        #     self.__update_node(row['ns_as_subnet'])
        #     self.__update_node(row['ns_as_number'])
        #     self.__update_node(row['ns_as_name'])
    
    def predict(self, row):
        H = self.G.copy()
        
        H.add_node(row['domain'], start=0.5, current=0.5)
        H.add_node(row['domain_ip'], start=0.5, current=0.5)
        H.add_node(row['as_subnet'], start=0.5, current=0.5)
        H.add_node(row['as_number'], start=0.5, current=0.5)
        H.add_node(row['as_name'], start=0.5, current=0.5)
        H.add_node(row['ns_base_domain'], start=0.5, current=0.5)
        H.add_node(row['ns_as_subnet'], start=0.5, current=0.5)
        H.add_node(row['ns_as_number'], start=0.5, current=0.5)
        H.add_node(row['ns_as_name'], start=0.5, current=0.5)

        H.add_edge(row['domain'], row['domain_ip'])
        H.add_edge(row['domain_ip'], row['as_subnet'])
        H.add_edge(row['as_subnet'], row['as_number'])
        H.add_edge(row['as_number'], row['as_name'])
        H.add_edge(row['domain'], row['ns_base_domain'])
        H.add_edge(row['ns_base_domain'], row['ns_as_subnet'])
        H.add_edge(row['ns_as_subnet'], row['ns_as_number'])
        H.add_edge(row['ns_as_number'], row['ns_as_name'])

        E = nx.ego_graph(H, row['domain'], radius=5, center=True)
        
        if None in E:
            E.remove_node(None)
        
        # print (f'ego graph E\nnodes: {E.nodes()}\nedges: {E.edges()}')
        self.stable_graph(E, iterations=5)
        return E.nodes()[row['domain']]['current']


    def stable_graph(self, graph, iterations=10):
        for _ in range(iterations):
            self.__graph_iteration(graph)


    def __graph_iteration(self, graph):
        # H = self.G.copy()
        for node in graph.nodes():
            self.__update_node(graph, node)


    def __update_node(self, graph, node):
        try:
            if graph.degree(node) > 0:
                neighbors_current_score = 0
                for neighbor in graph.neighbors(node):
                    neighbors_current_score += graph.nodes[neighbor]['current']
                neighbors_current_avg = neighbors_current_score / graph.degree(node)
                graph.nodes[node]['current'] = 0.5 * graph.nodes[node]['current'] + 0.5 * neighbors_current_avg
        except:
            print('-----------------------------')
            print(f'exception in __update_node\nnode: {node}\ntype(node): {type(node)}\ngraph nodes {graph.nodes()}]\ngraph edges: {graph.edges()}')
            print('-----------------------------')


