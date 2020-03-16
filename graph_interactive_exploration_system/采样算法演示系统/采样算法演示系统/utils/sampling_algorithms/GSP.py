import networkx as nx
import random


class GSP():
    def __init__(self, param_settings=None):
        pass

    def R2(self, G_edges, A, B):
        if A and B:
            Ne = 0
            for u in A:
                for v in B:
                    if (u, v) in G_edges or (v, u) in G_edges:
                        Ne += 1
            R_AB = Ne / (len(A) * len(B))
        else:
            R_AB = 0
        return R_AB

    def R1(self, G_edges, A):
        if A:
            Ne = 0
            copy_A = list(A)
            for i in range(len(copy_A) - 1):
                for j in range(i + 1, len(copy_A)):
                    if (copy_A[i], copy_A[j]) in G_edges or (copy_A[j], copy_A[i]) in G_edges:
                        Ne += 1
            if len(copy_A) - 1 != 0:
                R_A = 2 * Ne / (len(copy_A) * (len(copy_A) - 1))
            else:
                R_A = 0
        else:
            R_A = 0
        return R_A

    def edgeWeightComputing(self, G):
        neighbors_record = {node: set(G.neighbors(node)) for node in G.nodes}
        G_edges = set(G.edges)
        G_weight = dict()
        for u, v in G_edges:
            u_neighbor = neighbors_record[u]
            v_neighbor = neighbors_record[v]
            Vuv = u_neighbor & v_neighbor
            Vu = u_neighbor - Vuv
            Vv = v_neighbor - Vuv
            cycle_ratio = len(Vuv) / (len(Vu) + len(Vv) + len(Vuv))
            EWe = self.R2(G_edges, Vu, Vuv) + self.R2(G_edges, Vu, Vv) + self.R2(G_edges, Vuv, Vv) + self.R1(G_edges,
                                                                                                             Vuv) + cycle_ratio
            G[u][v]['Ewe'] = EWe
            G_weight[(u, v)] = EWe

    def GraphSampling(self, Gi, Gs_node, vs, size, p=0.5):
        if len(Gs_node) < size:
            Gs_node.add(vs)
            VGi = {}
            for vi in Gi.nodes():
                distance = len(nx.dijkstra_path(Gi, source=vi, target=vs)) - 1
                if distance == 0:
                    continue
                if distance in VGi.keys():
                    VGi[distance].append(vi)
                else:
                    VGi[distance] = [vi]
            for v in VGi.values():
                for i in v:
                    if len(Gs_node) < size:
                        pf = random.random()
                        if pf < p:
                            Gs_node.add(i)
                    else:
                        break

    def filterEdges(self, G, eta, rate):
        G_copy = G.copy()
        Gs_node = set()
        size = round(len(G) * rate)
        for u, v, d in G.edges(data='Ewe'):
            if d < eta:
                G_copy.remove_edge(u, v)
        for c in nx.connected_components(G_copy):
            Gi = G_copy.subgraph(c)

            # 新的一整套流程：找diameter同时进行后续采样操作，因old中后续采样还需要重新找一遍路径，耗时
            # 这一套新的在找diameter时同时可以记录路径，不需要后续重新找path
            # 下面这种借助nx.shortest_path_length()找path比原来快一点，也可大大减少后续采样的开销
            path = nx.shortest_path_length(Gi)
            max_value = 0
            diameter = []
            end_point_path_record = {}
            for one_path in path:
                length = list(one_path[1].values())[-1]
                if length >= max_value:
                    max_value = length
                    end_point_path_record[one_path[0]] = one_path[1]
                    diameter = [one_path[0], list(one_path[1].keys())[-1]]

            # 以下操作基本不耗时间，在0.1s内，而原来的self.GraphSampling()巨耗时，不可估量
            startpoint = random.choice(diameter)
            end_point_path = end_point_path_record[startpoint]
            diameter_dict = {}
            for key, value in end_point_path.items():
                if value not in diameter_dict.keys():
                    diameter_dict[value] = [key]
                else:
                    diameter_dict[value].append(key)
            for _ in range(1, max_value):
                nodes = random.sample(diameter_dict[_], round(rate * len(diameter_dict[_])))
                sub_size = size - len(Gs_node)
                if sub_size <= 0:
                    break
                if len(nodes) > sub_size:
                    Gs_node.update(set(nodes[:sub_size]))
                else:
                    Gs_node.update(set(nodes))
            if len(Gs_node) >= size:
                break
        Gs = G.subgraph(Gs_node)

        return Gs

    def getInfo(self, G, Gs):
        G_set = set(G.nodes())
        Gs_set = set(Gs.nodes())
        for node in G_set:
            if node in Gs_set:
                G.node[node]['class'] = 2
            else:
                G.node[node]['class'] = 1

    def run_samping(self, G, rate):
        # Graph Partition Process
        self.edgeWeightComputing(G)
        eta = 0.65
        Gs = self.filterEdges(G, eta, rate)
        return Gs
