import csv, os
from django.conf import settings
import networkx as nx
from utils.sampling_algorithms.BF import BF
from utils.sampling_algorithms.DPL import DPL
from utils.sampling_algorithms.FF import FF
from utils.sampling_algorithms.GSP import GSP
from utils.sampling_algorithms.OURS import OURS
from utils.sampling_algorithms.RAS import RAS
from utils.sampling_algorithms.RMSC import RMSC
from utils.sampling_algorithms.SSP import SSP
from utils.sampling_algorithms.SST import SST
from utils.sampling_algorithms.TIES import TIES


class Run_Sampling_Model():
    def __init__(self, graph_name, algorithm_name, param_settings):
        self.G = self.read_graph(graph_name)
        self.Algorithm_Model = self.read_algorithm(algorithm_name, param_settings)
        self.rate = param_settings['rate']

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

    def read_algorithm(self, algorithm_name, param_settings):
        if algorithm_name == 'BF':
            return BF(param_settings)
        if algorithm_name == 'DPL':
            return DPL(param_settings)
        if algorithm_name == 'FF':
            return FF(param_settings)
        if algorithm_name == 'GSP':
            return GSP(param_settings)
        if algorithm_name == 'MCGS':
            return OURS(param_settings)
        if algorithm_name == 'RAS':
            return RAS(param_settings)
        if algorithm_name == 'RMSC':
            return RMSC(param_settings)
        if algorithm_name == 'SSP':
            return SSP(param_settings)
        if algorithm_name == 'SST':
            return SST(param_settings)
        if algorithm_name == 'TIES':
            return TIES(param_settings)

    def run(self):
        Gs = self.Algorithm_Model.run_samping(self.G, self.rate)
        return Gs