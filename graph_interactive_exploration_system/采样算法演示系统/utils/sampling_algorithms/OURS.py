import networkx as nx
import math, random
import numpy as np


class OURS():
    def __init__(self, param_settings):
        self.alpha = param_settings['alpha']
        self.beta = param_settings['beta']
        self.loss_weight_percentages = np.array(param_settings['loss weight']) / sum(param_settings['loss weight'])

    # 新算法获取tie和rim
    def new_Extract_Tie_and_Rim(self, G, anomaly_total, node_degree_dict):
        anomaly_total['rim'] = []
        anomaly_total['tie'] = []
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
            if (len(a_one_nodes) == 0 and len(b_one_nodes) != 0) or (len(a_one_nodes) != 0 and len(b_one_nodes) == 0):
                anomaly_total['rim'].append(chain_item)
            else:
                anomaly_total['tie'].append(chain_item)

        parachute = list(sorted(parachute, key=lambda item: node_degree_dict[item], reverse=True))
        anomaly_total['rim'].extend(parachute)

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
        anomaly_total['pivot'] = [_ for _ in nodes_5 if _ in triangle_list]

        # nodes_20 = list(sorted(nodes, key=lambda item: node_degree_dict[item], reverse=True))[
        #            :math.ceil(len(nodes) * 0.20)]
        # for node in nodes_20:
        #     if (node not in seen) or (node not in triangle_list):
        #         DFS(node)
        # anomaly_total['star'] = [_ for _ in nodes_20 if _ not in triangle_list]

        degree_threshold = sum(list(node_degree_dict.values())) / len(nodes)
        nodes_star = set(filter(lambda item: node_degree_dict[item] >= degree_threshold, nodes))
        for node in nodes_star:
            if (node not in seen) or (node not in triangle_list):
                DFS(node)
        anomaly_total['star'] = [_ for _ in nodes_star if _ not in triangle_list]

    # 稀有结构领域采样
    def addMinorityStructure(self, G, Gs, rate, anomaly_total, total_anomaly):
        def neighborSampler(G, beta, rate, node, s=0):
            rate = rate / beta
            if s == 0:
                nodelist = list(G.neighbors(node))
                samplesize = math.floor(len(nodelist) * rate)
                samplenodelist = random.sample(nodelist, samplesize)
                return samplenodelist
            if s == 1:
                nodelist = []
                for n in node:
                    nodelist = nodelist + list(G.neighbors(n))
                coneighbor = list(set(nodelist) - set(node))
                samplesize = math.floor(len(coneighbor) * rate)
                samplenodelist = random.sample(nodelist, samplesize)
                return samplenodelist

        # truncation
        for minoname, minokeynode in anomaly_total.items():
            truncation = math.ceil(len(minokeynode) * rate * self.alpha)
            anomaly_total[minoname] = minokeynode[:truncation]

        # add in Gs
        for minoname, minokeynode in anomaly_total.items():
            for node in minokeynode:
                if type(node) == int:
                    total_anomaly.append(node)
                    Gs.add_node(node)
                    sampleneighborlist = neighborSampler(G, self.beta, rate, node)
                else:
                    total_anomaly = total_anomaly + list(node)
                    Gs.add_nodes_from(node)
                    sampleneighborlist = neighborSampler(G, self.beta, rate, node, s=1)
                Gs.add_nodes_from(sampleneighborlist)
        return (total_anomaly, anomaly_total)

    # 随机删除节点
    def RandomGiveUp(self, Gs, size, total_anomaly):
        # print('giveup')
        Gsnodes = list(Gs.nodes())
        while len(Gs) > size:
            choice = random.choice(Gsnodes)
            if choice not in total_anomaly:
                Gs.remove_node(choice)
                Gsnodes.remove(choice)

    # 随机增加节点
    def RandomSample(self, G, Gs, size):
        # print('samplemore')
        Gedges = list(G.edges())
        while len(Gs) < size:
            choice = random.choice(Gedges)
            Gs.add_edge(choice[0], choice[1])

    # 主结构采样
    def SampleOtherNode(self, G, Gs, size, source_node_degree_dict, source_neighbors_records):
        G_nodes = set(G.nodes)
        Gs_nodes_set = set(Gs.nodes)
        # 备选节点集
        unselect_node_list = G_nodes - Gs_nodes_set

        # 当前采样图中的度
        current_degrees = {_[0]: _[1] for _ in list(G.subgraph(Gs_nodes_set).degree())}

        # 采样图与原始图中度差值
        sub_degrees = {key: source_node_degree_dict[key] - value for key, value in current_degrees.items()}

        # 平方和临时变量，避免后续的二次运算
        temp_arr_value = ((np.array(list(sub_degrees.values()))) ** 2).sum()

        # 获取连通子图数目
        sub_graph = G.subgraph(Gs_nodes_set)
        temp_graph = nx.Graph()
        temp_graph.add_nodes_from(sub_graph.nodes)
        temp_graph.add_edges_from(sub_graph.edges)
        # 原始图中的连通子图个数
        source_connected_components = len(sorted(nx.connected_components(G)))
        # 当前图的连通子图,使用networkx内置库
        temp_connected_components = len(sorted(nx.connected_components(temp_graph)))
        temp_CC = 1
        # 当前图的JI_sum
        temp_JI_sum = np.sum(
            list(current_degrees[_] / source_node_degree_dict[_] if source_node_degree_dict[_] != 0 else 0 for _ in
                 Gs_nodes_set))
        # 现在的新的,均衡计算三个loss
        while len(Gs) < size:
            # 最小loss记录列表
            min__loss = {
                'rmse': {
                    'value': temp_arr_value,
                    'node': None,
                    'new_edges': []
                },
                'CC': {
                    'value': temp_CC,
                    'node': None,
                    'new_edges': []
                },
                'JI': {
                    'value': temp_JI_sum,
                    'node': None,
                    'new_edges': []
                }
            }
            # 最大loss记录列表
            max__loss = {
                'rmse': temp_arr_value,
                'CC': temp_CC,
                'JI': temp_JI_sum
            }
            record_list = {}
            for iter_node in unselect_node_list:
                # 获取iter_node在Gs中的邻居节点
                new_edges = list(Gs_nodes_set & source_neighbors_records[iter_node])
                # 计算pow值
                new_rmse = temp_arr_value + (source_node_degree_dict[iter_node] - len(new_edges)) ** 2

                new_JI_sum = 0 if self.loss_weight_percentages[2] == 0 else temp_JI_sum + len(new_edges) / len(
                    source_neighbors_records[iter_node]) if len(
                    source_neighbors_records[iter_node]) != 0 else 0

                for other_node in new_edges:
                    new_rmse += - 2 * sub_degrees[other_node] + 1
                    new_JI_sum += 0 if self.loss_weight_percentages[2] == 0 else 1 / source_node_degree_dict[
                        other_node] if source_node_degree_dict[
                                           other_node] != 0 else 0
                # 化为与loss weight成正比以便计算总的loss
                new_CC = 0 if self.loss_weight_percentages[
                                  1] == 0 else temp_connected_components / source_connected_components if len(
                    new_edges) != 0 else (temp_connected_components + 1) / source_connected_components
                # 比较，如更小则更新min__loss记录
                if self.loss_weight_percentages[0] != 0:
                    if new_rmse <= min__loss['rmse']['value']:
                        min__loss['rmse']['value'] = new_rmse
                        min__loss['rmse']['node'] = iter_node
                        min__loss['rmse']['new_edges'] = new_edges
                    if new_rmse >= max__loss['rmse']:
                        max__loss['rmse'] = new_rmse
                if self.loss_weight_percentages[1] != 0:
                    if new_CC <= min__loss['CC']['value']:
                        min__loss['CC']['value'] = new_CC
                        min__loss['CC']['node'] = iter_node
                        min__loss['CC']['new_edges'] = new_edges
                    if new_CC >= max__loss['CC']:
                        max__loss['CC'] = new_CC
                if self.loss_weight_percentages[2] != 0:
                    if new_JI_sum <= min__loss['JI']['value']:
                        min__loss['JI']['value'] = new_JI_sum
                        min__loss['JI']['node'] = iter_node
                        min__loss['JI']['new_edges'] = new_edges
                    if new_JI_sum >= max__loss['JI']:
                        max__loss['JI'] = new_JI_sum

                # 一些记录
                record_list[iter_node] = {
                    'new_edges': new_edges,
                    'rmse': new_rmse,
                    'CC': new_CC,
                    'JI': new_JI_sum
                }

            # 获取待选节点，并进行处理
            select_node = None
            if self.loss_weight_percentages[0] == 0 and self.loss_weight_percentages[1] == 0:
                select_node = min__loss['JI']['node']
            elif self.loss_weight_percentages[0] == 0 and self.loss_weight_percentages[2] == 0:
                select_node = min__loss['CC']['node']
            elif self.loss_weight_percentages[1] == 0 and self.loss_weight_percentages[2] == 0:
                select_node = min__loss['rmse']['node']
            else:
                min_loss = 1
                for key, value in record_list.items():
                    rmse_detal = max__loss['rmse'] - min__loss['rmse']['value']
                    CC_detal = max__loss['CC'] - min__loss['CC']['value']
                    JI_detal = max__loss['JI'] - min__loss['JI']['value']
                    try:
                        loss_rmse_value = 0 if self.loss_weight_percentages[0] == 0 else (value['rmse'] -
                                                                                          min__loss['rmse'][
                                                                                              'value']) / rmse_detal
                        loss_CC_value = 0 if self.loss_weight_percentages[1] == 0 else (value['CC'] -
                                                                                        min__loss['CC'][
                                                                                            0]) / CC_detal
                        loss_JI_value = 0 if self.loss_weight_percentages[2] == 0 else (value['JI'] -
                                                                                        min__loss['JI'][
                                                                                            0]) / JI_detal
                        loss_weight = loss_rmse_value * self.loss_weight_percentages[0] + loss_CC_value * \
                                      self.loss_weight_percentages[1] + loss_JI_value * self.loss_weight_percentages[2]
                        if loss_weight <= min_loss:
                            min_loss = loss_weight
                            select_node = key
                    except Exception as e:
                        continue
            if select_node == None:
                select_node = unselect_node_list.pop()
            # 更新度差值
            sub_degrees[select_node] = source_node_degree_dict[select_node] - len(record_list[select_node]['new_edges'])
            for other_node in record_list[select_node]['new_edges']:
                sub_degrees[other_node] -= 1
            # 新增node
            Gs.add_node(select_node)
            Gs_nodes_set.add(select_node)
            temp_arr_value = record_list[select_node]['rmse']
            temp_connected_components = temp_connected_components if len(
                record_list[select_node]['new_edges']) != 0 else temp_connected_components + 1
            temp_JI_sum = record_list[select_node]['JI']
            temp_CC = record_list[select_node]['CC']
            # 从备选集中删除
            try:
                unselect_node_list.remove(select_node)
            except Exception as e:
                pass

    def run_samping(self, G, rate):
        Gs = nx.Graph()
        total_anomaly = []
        # 原始图中各节点度记录
        node_degree_dict = {item[0]: item[1] for item in G.degree()}
        # 原始图中节点邻居记录
        source_neighbors_records = {_: set(G.neighbors(_)) for _ in G.nodes}
        isBalance = True
        if isBalance:
            anomaly_total = {}
            # 稀有结构采样
            self.new_Extract_Star_and_Pivot(G, anomaly_total, node_degree_dict, source_neighbors_records)
            self.new_Extract_Tie_and_Rim(G, anomaly_total, node_degree_dict)
            # 邻域采样
            total_anomaly, anomaly_total = self.addMinorityStructure(G, Gs, rate, anomaly_total, total_anomaly)
        # else:
        #     partitions = nx.metis.partition(G, 2)
        #     for partition in partitions[1]:
        #         Gt = nx.Graph()
        #         Gt.add_nodes_from(partition)
        #         Gp = G.subgraph(Gt.nodes())
        #
        #         # basic variable
        #         node_degree = [[n, d] for n, d in Gp.degree()]
        #
        #         anomaly_total = {}
        #         Extract_Global_High_Neighbor(Gp, heigh_neighbour, anomaly_total, node_degree)
        #         Extract_Star(Gp, threshold, anomaly_total, node_degree)
        #         Extract_Star_new(G, threshold, anomaly_total, node_degree)
        #         Articulation_Points_and_Bridge(Gp, anomaly_total)
        #         MetisRank(Gp, anomaly_total)
        #         anomaly, anomaly_total = addMinorityStructure(Gp, Gs, rate, anomaly_total, total_anomaly)
        #         total_anomaly = list(set(total_anomaly + anomaly))
        size = round(len(G) * rate)
        if len(Gs) > size:
            self.RandomGiveUp(Gs, size, total_anomaly)
        if len(Gs) < size:
            self.SampleOtherNode(G, Gs, size, node_degree_dict, source_neighbors_records)
        Gs = G.subgraph(Gs.nodes())
        return Gs
