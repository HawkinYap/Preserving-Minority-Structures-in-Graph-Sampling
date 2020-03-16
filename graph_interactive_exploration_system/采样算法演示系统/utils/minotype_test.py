import math
import networkx as nx
import csv, os
from django.conf import settings



class Minotype_Test():
    def __init__(self, graph):
        self.G = self.read_graph(graph)
        self.run()

    def run(self):
        # 原始图中各节点度记录
        node_degree_dict = {item[0]: item[1] for item in self.G.degree()}
        # 原始图中节点邻居记录
        source_neighbors_records = {_: set(self.G.neighbors(_)) for _ in self.G.nodes}
        anomaly_total = {}
        # 稀有结构采样
        self.new_Extract_Star_and_Pivot(self.G, anomaly_total, node_degree_dict, source_neighbors_records)
        self.new_Extract_Tie_and_Rim(self.G, anomaly_total, node_degree_dict)
        return anomaly_total

    def read_graph(self, file_name):
        with open(os.path.join(settings.BASE_DIR, 'frontend/dist/static/GraphDataSet/{}_node.csv'.format(file_name)),
                  'r')as fp:
            reader = csv.reader(fp)
            next(reader)
            nodes = list(int(_[0]) for _ in reader)
        with open(os.path.join(settings.BASE_DIR, 'frontend/dist/static/GraphDataSet/{}_edge.csv'.format(file_name)),
                  'r')as fp:
            reader = csv.reader(fp)
            next(reader)
            edges = list([int(_[0]), int(_[1])] for _ in reader)
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        return G

    # 新算法获取tie和rim

    def new_Extract_Tie_and_Rim(self, G, anomaly_total, node_degree_dict):
        anomaly_total['Rim'] = []
        anomaly_total['Tie'] = []
        # 割点
        cut_points = set(nx.articulation_points(G))
        # print("割点集", cut_points)
        # 原始图中度为1的节点集合
        one_degree_nodes_set = set(filter(lambda item: node_degree_dict[item] == 1, node_degree_dict.keys()))
        Gs = G.subgraph(cut_points)
        # 割点在采样图中度记录
        cut_points_degree_dict = {_[0]: _[1] for _ in Gs.degree()}
        # 割点在诱导子图中邻居节点记录
        neighbors_records = {_: list(Gs.neighbors(_)) for _ in cut_points}
        # 割点在原始图中邻居节点记录
        source_neighbors_record = {_: set(G.neighbors(_)) for _ in cut_points}
        # 从度小于等于1的割点开始（作为链的端点）
        iter_nodes = list(filter(lambda item: cut_points_degree_dict[item] <= 1, cut_points))
        chains = []
        seen = set()
        parachute = set()
        # 循环遍历所有割点
        while len(cut_points - seen) > 0:
            for node in iter_nodes:
                if node not in seen:
                    temp_chain = [node]
                    seen.add(node)
                    current = node
                    while 1:
                        if len(source_neighbors_record[current] & one_degree_nodes_set) > 0:
                            parachute.add(current)
                        neighbors = neighbors_records[current]
                        # 当前割点没有同为割点的邻居，时退出循环
                        if len(neighbors) == 0 or len(set(neighbors) - seen) >= 2:
                            break
                        else:
                            # 取出未遍历的割点作为新的当前割点
                            # other = neighbors[0] if len(neighbors) == 1 or neighbors[0] not in seen else neighbors[1]
                            other = neighbors[0]
                            for _ in neighbors:
                                if _ not in seen:
                                    other = _
                                    break
                            if other not in seen:
                                temp_chain.append(other)
                                seen.add(other)
                                current = other
                            else:
                                break
                    if len(temp_chain) > 1:
                        chains.append(temp_chain)
            other_cut_point = cut_points - seen
            cut_points_degree_dict = {_[0]: _[1] for _ in G.subgraph(other_cut_point).degree()}
            iter_nodes = set(filter(lambda item: cut_points_degree_dict[item] <= 1, other_cut_point))
            if len(iter_nodes) == 0:
                for cut_point in other_cut_point:
                    if len(source_neighbors_record[cut_point] & one_degree_nodes_set) > 0:
                        parachute.add(cut_point)
                break

        for chain_item in chains:
            # 分别获取chain两端节点的度为一的邻居节点集合
            a_one_nodes = source_neighbors_record[chain_item[0]] & one_degree_nodes_set
            b_one_nodes = source_neighbors_record[chain_item[-1]] & one_degree_nodes_set
            # 判断邻居节点中度等于1的节点是否有且只出现在一端，是则加入rim，否则加入tie
            if (len(a_one_nodes) == 0 and len(b_one_nodes) != 0) or (
                    len(a_one_nodes) != 0 and len(b_one_nodes) == 0):
                anomaly_total['Rim'].append(chain_item)
            else:
                anomaly_total['Tie'].append(chain_item)

        parachute = list(sorted(parachute, key=lambda item: node_degree_dict[item], reverse=True))
        anomaly_total['Rim'].extend(parachute)

    # 新算法获取star和pivot

    def new_Extract_Star_and_Pivot(self, G, anomaly_total, node_degree_dict, source_neighbors_record):
        nodes = set(G.nodes)
        seen = set()
        triangle_list = set()

        def DFS(current_node, father_node=None, grandfather_node=None):
            seen.add(current_node)
            for other_node in source_neighbors_record[current_node]:
                if other_node == grandfather_node:
                    triangle_list.add(current_node)
                    triangle_list.add(father_node)
                    triangle_list.add(grandfather_node)
                elif other_node == father_node:
                    continue
                elif father_node != None and (other_node in source_neighbors_record[father_node]):
                    triangle_list.add(current_node)
                    triangle_list.add(father_node)
                    triangle_list.add(other_node)
                elif father_node != None and (other_node not in source_neighbors_record[father_node]):
                    continue
                else:
                    if other_node not in seen:
                        DFS(other_node, current_node, father_node)
                    else:
                        DFS(other_node, current_node)

        nodes_5 = list(sorted(nodes, key=lambda item: node_degree_dict[item], reverse=True))[
                  :math.ceil(len(nodes) * 0.05)]
        for node in nodes_5:
            if (node not in seen) or (node not in triangle_list):
                DFS(node)
        anomaly_total['Pivot'] = [_ for _ in nodes_5 if _ in triangle_list]

        degree_threshold = sum(list(node_degree_dict.values())) / len(nodes)
        nodes_star = set(filter(lambda item: node_degree_dict[item] >= degree_threshold, nodes))
        for node in nodes_star:
            if (node not in seen) or (node not in triangle_list):
                DFS(node)
        anomaly_total['Star'] = [_ for _ in nodes_star if _ not in triangle_list]
