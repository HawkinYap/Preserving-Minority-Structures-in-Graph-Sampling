import networkx as nx
import random, re, csv, os, time


class SSP:
    def __init__(self, param_settings=None):
        self.L = 2500
        pass

    def run_samping(self, G, rate):
        size = round(len(G) * rate)
        Gs = nx.Graph()
        Gnode = list(G.nodes())
        path_dict = dict()
        edges_set = set()

        for _ in range(self.L):
            vs = random.choice(Gnode)
            vs_neighbors = set(G.neighbors(vs))
            other_nodes = list(set(Gnode) - vs_neighbors)
            vd = random.choice(other_nodes)
            while 1:
                try:
                    dis = nx.dijkstra_path(G, source=vs, target=vd)
                    break
                except:
                    vd = random.choice(other_nodes)
            iter_length = len(dis)
            for index in range(iter_length - 1):
                edge = (min(dis[index], dis[index + 1]), max(dis[index], dis[index + 1]))
                if edge not in edges_set:
                    path_dict[edge] = 1
                    edges_set.add(edge)
                else:
                    path_dict[edge] += 1
        sort_count = sorted(path_dict.items(), key=lambda x: x[1], reverse=True)
        i = 0
        while len(Gs) < size:
            Gs.add_edge(sort_count[i][0][0], sort_count[i][0][1])
            i += 1

        return Gs
