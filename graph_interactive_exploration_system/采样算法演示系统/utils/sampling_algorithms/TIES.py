import random


class TIES():
    def __init__(self, param_settings=None):
        pass

    def run_samping(self, G, rate):
        size = round(len(G) * rate)
        edges_list = list(G.edges())
        Vs_list = set()
        while (len(Vs_list)) < size:
            edges_sample = random.choice(edges_list)
            Vs_list.add(edges_sample[0])
            Vs_list.add(edges_sample[1])
        Gs = G.subgraph(Vs_list)
        return Gs
