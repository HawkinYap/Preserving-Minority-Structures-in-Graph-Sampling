from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings
import re, json, os, time
from utils.sampling_program import Run_Sampling_Model
from utils.json_generator import JSON_Generator
from utils.minotype_test import Minotype_Test

@require_GET
def index(request):
    # 初始化：将frontend下的原始图的svg转化为json
    # if settings.INIT_SVG == False:
    #     filelist = list(filter(lambda item: ".svg" in item,
    #                       os.listdir(os.path.join(settings.BASE_DIR, 'frontend/dist/static/GraphData_Origin/'))))
    #     for file in filelist:
    #         generator = JSON_Generator()
    #         source_svg_path = os.path.join(settings.BASE_DIR, 'frontend/dist/static/GraphData_Origin/' + file)
    #         target_json_path = os.path.join(settings.BASE_DIR,
    #                                         'frontend/dist/static/GraphData_Origin/graph_json_file/' + file.replace(".svg",
    #                                                                                                                 ".json"))
    #         generator.convertion(source_svg_path, target_json_path)
    #     settings.INIT_SVG = True
    return render(request, 'index.html')


@require_POST
def run_sampling(request):
    parameters = json.loads(request.body)
    graph_name = parameters['graph_name']
    algorithm_name = parameters['algorithm_name']
    param_settings = parameters['settings']
    
    float_param_settings = {
        'rate': float(param_settings['rate']),
        'alpha': float(param_settings['alpha']),
        'beta': float(param_settings['beta']),
        'loss weight': list(float(_) for _ in re.findall('([0-9]*\.{0,1}[0-9]*)', param_settings['loss weight'])[::2])
    }

    run_switch_model = Run_Sampling_Model(graph_name, algorithm_name, float_param_settings)

    start_time = time.perf_counter()
    Gs = run_switch_model.run()


    Gs_nodes = set(list(_ for _ in Gs.nodes()))
    Gs_edges = set(list(_ for _ in Gs.edges()))
    start_time = time.perf_counter()

    # 重写采样svg
    # 获取svg头信息
    with open(
            os.path.join(settings.BASE_DIR, 'frontend/dist/static/GraphData_Origin/origin_{}.svg'.format(graph_name)),
            'r', encoding='utf-8')as fp:
        svg_text = fp.readline()
        svg_header = ''
        while ('version="1.1"' not in svg_text):
            svg_header += svg_text
            svg_text = fp.readline()
        svg_header += svg_text
    # 获取采样svg_edge和svg_node
    with open(
            os.path.join(settings.BASE_DIR, 'frontend/dist/static/GraphData_Origin/origin_{}.svg'.format(graph_name)),
            'r', encoding='utf-8')as fp:
        svg_text = fp.read()
        edges = re.findall('<path .*\n.*\n.*/>', svg_text)
        nodes = re.findall('<circle .*\n.*\n.*/>', svg_text)
        edges_list = re.findall('class="id_([0-9]*) id_([0-9]*)"', svg_text)
        nodes_list = re.findall('class="id_([0-9]*)"', svg_text)
        edge_svg_text = []
        for edge, source_edge in zip(edges_list, edges):
            if (int(edge[0]), int(edge[1])) in Gs_edges or (int(edge[1]), int(edge[0])) in Gs_edges:
                edge_svg_text.append(source_edge)
        node_svg_text = []
        for node, source_node in zip(nodes_list, nodes):
            if int(node) in Gs_nodes:
                node_svg_text.append(source_node)
    g_edges = '<g id="edges">\n' + "\n".join(edge_svg_text) + '</g>'
    g_nodes = '<g id="nodess">\n' + "\n".join(node_svg_text) + '</g>'
    sampling_svg_content = svg_header + g_edges + g_nodes + '</svg>'

    # 部署环境下写入svg文件
    with open(os.path.join(settings.BASE_DIR, 'frontend/dist/static/sampling_result/new_sampling.svg'), 'w',
              encoding='utf-8')as fp:
        fp.write(sampling_svg_content)

    generator = JSON_Generator()
    source_svg_path = os.path.join(settings.BASE_DIR, 'frontend/dist/static/sampling_result/new_sampling.svg')
    target_json_path = os.path.join(settings.BASE_DIR,
                                    'frontend/dist/static/sampling_result/graph_json_file/new_sampling.json')
    generator.convertion(source_svg_path, target_json_path)

    return HttpResponse(json.dumps({'state': "success"}), content_type='application/json')

@require_POST
def get_minotype(request):
    parameters = json.loads(request.body)
    graph_name = parameters['graph_name']
    minotype_Test = Minotype_Test(graph_name)
    anomaly_total = minotype_Test.run()
    new_rim = []
    new_tie = []
    for rim in anomaly_total['Rim']:
        if type(rim)==int:
            new_rim.append(rim)
        else:
            for node in rim:
                new_rim.append(node)
    for tie in anomaly_total['Tie']:
        if type(tie)==int:
            new_tie.append(tie)
        else:
            for node in tie:
                new_tie.append(node)
    anomaly_total['Rim'] = new_rim
    anomaly_total['Tie'] = new_tie
    with open(os.path.join(settings.BASE_DIR, 'utils/sham.json'), 'r',encoding='utf-8')as fp:
        anomaly_total['sham_rim_list'] = json.load(fp)
    return HttpResponse(json.dumps({'state': "success",'anomaly_total':anomaly_total}), content_type='application/json')
