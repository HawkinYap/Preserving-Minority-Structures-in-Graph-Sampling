import random
import networkx as nx


class BF():
    def __init__(self, param_settings=None):
        pass

    def run_samping(self, G, rate):
        size = round(len(G) * rate)
        list_nodes = list(G.nodes())
        list_edges = list(G.edges())

        nr_nodes = len(list_nodes)
        upper_bound_nr_nodes_to_sample = size
        index_of_first_random_node = random.randint(0, nr_nodes - 1)

        sampled_graph = []
        sampled_graph_edges = []
        sampled_graph.append(list_nodes[index_of_first_random_node])

        index = 0

        while (len(sampled_graph) < upper_bound_nr_nodes_to_sample):
            for edge in list_edges:
                tmpsource = edge[0]
                tmptarget = edge[1]

                if (tmpsource == list_nodes[index_of_first_random_node]) and not (tmptarget in sampled_graph):
                    sampled_graph.append(tmptarget)
                    sampled_graph_edges.append([tmpsource, tmptarget])
                if len(sampled_graph) >= upper_bound_nr_nodes_to_sample:
                    break

                elif (tmptarget == list_nodes[index_of_first_random_node]) and not (tmpsource in sampled_graph):
                    sampled_graph.append(tmpsource)
                    sampled_graph_edges.append([tmpsource, tmptarget])
                if len(sampled_graph) >= upper_bound_nr_nodes_to_sample:
                    break

            index = index + 1
            index_of_first_random_node = list_nodes.index(sampled_graph[index])

        Gs = nx.Graph()
        Gs.add_edges_from(sampled_graph_edges)
        return Gs
