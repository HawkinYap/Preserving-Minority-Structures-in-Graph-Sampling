import networkx as nx
import random


class RMSC():
    def __init__(self, param_settings=None):
        pass

    def run_samping(self, G, rate):
        pc = 0.6
        Gs = nx.Graph()
        L = set(random.sample(list(G.nodes), 5))
        size = round(len(G) * rate)
        Gs.add_nodes_from(L)
        flag = 0
        while len(Gs) < size:
            nei = []
            for node in L:
                i_neibor = G.neighbors(node)
                for j in i_neibor:
                    pt = random.random()
                    if pt < pc:
                        nei.append(j)
                        if len(Gs) < size:
                            Gs.add_node(j)
                            Gs.add_edge(node, j)
                        else:
                            flag = 1
                            break
                if flag == 1:
                    break
            if flag == 1:
                break
            L.update(nei)
        return Gs
