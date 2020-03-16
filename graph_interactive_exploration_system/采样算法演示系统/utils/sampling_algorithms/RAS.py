import networkx as nx
import random


class RAS():
    def __init__(self, param_settings=None):
        self.T = 100
        pass

    def run_samping(self, G, rate):
        size = round(len(G) * rate)
        Gs = nx.Graph()
        nodes = list(G.nodes())
        select_nodes = [random.choice(nodes)]
        select_nodes = select_nodes + random.sample(nodes, self.T)
        for i in select_nodes:
            if len(Gs) < size:
                Gs.add_node(i)
                if len(Gs) < size:
                    i_neighbor = list(G.neighbors(i))
                    Gs.add_nodes_from(i_neighbor)
                else:
                    break
            else:
                break
        if len(Gs) > size:
            Gsnodes = list(Gs.nodes())
            Gs.remove_nodes_from(Gsnodes[size:])
        Gs_induce = G.subgraph(Gs.nodes())
        return Gs_induce
