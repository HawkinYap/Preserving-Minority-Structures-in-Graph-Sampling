import networkx as nx
import random, time, csv, math
import sys, os, re
from collections import Counter


class PrimNode():
    def __init__(self, adjvex, cost):
        self.adjvex = adjvex
        self.lowestcost = cost


class SST():
    def __init__(self, param_settings=None):
        self.L = 3
        pass

    # 最小生成树
    def prim(self, G, adjmat):
        # 寻找最近路径的点
        def minmum(closedge, vertexset):
            minvalue = sys.maxsize
            index = -1
            for i in vertexset:
                if closedge[i].lowestcost < minvalue and closedge[i].lowestcost != 0:
                    minvalue = closedge[i].lowestcost
                    index = i
            return index

        # 构建邻接矩阵
        vertexset = list(G.nodes)
        start_node = random.choice(vertexset)  # 随机起点
        # 定义一个辅助数组用来保存U-V中的最小值和邻接点
        closedge = {i: PrimNode(start_node, adjmat[start_node][i]) for i in vertexset}
        closedge[start_node].lowestcost = 0
        result_edges = []
        # 找寻n-1最小值边
        vertexNum = len(vertexset)
        for e in range(1, vertexNum):
            k = minmum(closedge, vertexset)
            result_edges.append((k, closedge[k].adjvex))
            closedge[k].lowestcost = 0
            for i in vertexset:
                if adjmat[k][i] < closedge[i].lowestcost:
                    closedge[i].adjvex = k
                    closedge[i].lowestcost = adjmat[k][i]
        return result_edges

    def run_samping(self, G, rate):
        size = round(len(G) * rate)
        Gs = nx.Graph()
        vertexset = list(G.nodes)
        edgeset = list(G.edges)
        # 构建邻接矩阵
        adjmat = {source: {target: sys.maxsize for target in vertexset} for source in vertexset}
        for edge in edgeset:
            adjmat[edge[0]][edge[1]] = 1
            adjmat[edge[1]][edge[0]] = 1
        un_enough = True
        treelist = []
        iter_time = self.L
        while un_enough:
            treelist = []
            # 待采样节点备选集
            node_unselect = set()
            t = 1
            while t <= iter_time:
                tree_item = self.prim(G, adjmat)
                treelist.extend(tree_item)
                t += 1
                node_unselect.update(set(_[0] for _ in tree_item))
                node_unselect.update(set(_[1] for _ in tree_item))
            if len(node_unselect) >= size:
                un_enough = False
            else:
                iter_time += 1
        count = Counter(treelist)
        sort_count = sorted(count.items(), key=lambda x: x[1], reverse=True)
        i = 0
        while len(Gs) < size:
            Gs.add_edge(sort_count[i][0][0], sort_count[i][0][1])
            i += 1
        induced_graph = G.subgraph(Gs.nodes())
        return induced_graph
