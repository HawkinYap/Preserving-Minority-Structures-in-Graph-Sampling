import random, math
import networkx as nx
from collections import defaultdict
import community


class DPL():
    def __init__(self, param_settings=None):
        pass

    def sampleNodes(self, node, n_sample_nodes, G):
        result_nodes = set()
        if n_sample_nodes <= len(node):
            node = node[:n_sample_nodes]
        for _ in node:
            pt = 1 / G.degree(_)
            if random.random() > pt:
                result_nodes.add(_)
        return result_nodes

    def sampleEdges(self, edge, n_sample_edges, G):
        if len(edge) == 0:
            return []
        edges = []
        if n_sample_edges <= len(edge):
            edge = edge[:n_sample_edges]
        for _ in edge:
            pt = 1 / (G.degree(_[0]) + G.degree(_[1]))
            if random.random() > pt:
                edges.append(_)
        return edges

    def nearestPair(self, G, Gs, S, alpha):
        dis = {}
        S_copy = {}
        index = 1
        for i, s in S.items():
            S_copy[index] = s
            index += 1

        for i, s1 in S_copy.items():
            for j, s2 in S_copy.items():
                if j <= i:
                    continue
                else:
                    dis[(i, j)] = 0
                    a = G.degree(s1)
                    b = G.degree(s2)
                    try:
                        dis[(i, j)] += len(nx.dijkstra_path(G, source=a, target=b)) - 1
                    except:
                        dis[(i, j)] += 5000
        key_min = min(dis.keys(), key=(lambda k: dis[k]))
        P = set(S_copy[key_min[0]]) | set(S_copy[key_min[1]])
        P_nodes = P & set(Gs.nodes())

        induce = G.subgraph(P_nodes)
        edge = list(induce.edges())
        induce2 = Gs.subgraph(P_nodes)
        edge2 = list(induce2.edges())

        edge_eee = list(set(edge) - set(edge2))

        n_sample_edges = round(len(P_nodes) ** alpha) - len(edge2)
        edges = self.sampleEdges(edge_eee, n_sample_edges, G)
        Gs.add_edges_from(edges)

        S_copy.pop(key_min[0])
        S_copy.pop(key_min[1])
        S_copy[(key_min[0], key_min[1])] = list(P)
        return (S_copy)

    def run_samping(self, G, rate):
        Gs = nx.Graph()
        # 获取社区划分
        partition = community.best_partition(G)
        S = defaultdict(list)
        for node, com_id in partition.items():
            S[com_id].append(node)

        # sample from the original communities
        alpha_mean = 0
        # 遍历社区结构index:index_node_list
        for index, index_node_list in S.items():
            induce = G.subgraph(index_node_list)
            edge = list(induce.edges())
            alpha = math.log(len(edge), len(index_node_list))
            alpha_mean += alpha
            n_sample_nodes = round(len(index_node_list) * rate)
            n_sample_edges = round(n_sample_nodes ** alpha)
            nodes = self.sampleNodes(index_node_list, n_sample_nodes, G)
            edges = self.sampleEdges(list(G.subgraph(nodes).edges()), n_sample_edges, G)
            Gs.add_nodes_from(nodes)
            Gs.add_edges_from(edges)
        alpha_mean /= len(S)
        # sample edges between sampled communities
        while len(S) > 1:
            S = self.nearestPair(G, Gs, S, alpha_mean)

        return Gs
