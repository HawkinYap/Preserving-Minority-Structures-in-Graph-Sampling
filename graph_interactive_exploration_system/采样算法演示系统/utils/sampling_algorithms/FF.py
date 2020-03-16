import random
import networkx as nx


class FF():
    def __init__(self, param_settings=None):
        pass

    def run_samping(self, G, rate):
        size = round(len(G) * rate)
        list_nodes = list(G.nodes())
        dictt = set()
        random_node = random.choice(list_nodes)
        q = set()  # q = set contains the distinct values
        q.add(random_node)
        Gs = nx.Graph()
        while (len(Gs.nodes()) < size):
            if (len(q) > 0):
                initial_node = q.pop()
                if (initial_node not in dictt):
                    dictt.add(initial_node)
                    neighbours = list(G.neighbors(initial_node))
                    np = random.randint(1, len(neighbours))
                    for x in neighbours[:np]:
                        if (len(Gs.nodes()) < size):
                            Gs.add_edge(initial_node, x)
                            q.add(x)
                        else:
                            break
                else:
                    continue
            else:
                random_node = random.sample(set(list_nodes) and dictt, 1)[0]
                q.add(random_node)
        q.clear()
        return Gs
