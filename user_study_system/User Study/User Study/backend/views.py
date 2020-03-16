from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_GET, require_POST
import json, time, os
from random import shuffle
from re import sub
from django.conf import settings
from backend import models
from datetime import datetime


# Create your views here.
@require_POST
def register(request):
    params = json.loads(request.body)
    try:
        models.User.objects.create(username=params['name'], education=params['education'], age=params['age'],
                                   gender=params['gender'], major=params['major'])
        return HttpResponse("OK")
    except Exception as e:
        print(e)
        return HttpResponse("fail")


# 产生实验图源数据
@require_GET
def getExpeSvgList(request):
    image_1 = os.listdir(os.path.join(settings.BASE_DIR, "frontend/public/static/images/formal_34/"))  # 第一部分
    image_2 = os.listdir(os.path.join(settings.BASE_DIR, "frontend/public/static/images/sampling_graph_6/"))  # 第二部分
    shuffle(image_1)
    shuffle(image_2)
    img_list = image_1 + image_2
    return HttpResponse(json.dumps({'img_list': img_list}), content_type='application/json')


# 根据用户名返回用户图源列表
@require_GET
def getSvgRecordList(request):
    username = request.GET.get('current_user')
    records = models.Record.objects.filter(user=username)
    img_list = list(_.img for _ in records)
    return HttpResponse(json.dumps({'img_list': img_list}), content_type='application/json')


# 根据用户名和图片名获取具体的用户框选svg文件
@require_GET
def getSvgUserImage(request):
    def file_iterator(svgfile, chunk_size=512):
        content = svgfile.content.encode('utf-8')
        content_length = len(content)
        for i in range(0, content_length, chunk_size):
            yield content[i:i + chunk_size]

    username = request.GET.get('current_user')
    img_name = request.GET.get('image_name')
    svg_file = models.SVGFileData.objects.filter(img=img_name, user=username)[0]
    response = StreamingHttpResponse(file_iterator(svg_file))
    response['Content-Type'] = 'application/octet-stream'
    return response


# 保存用户实验记录和框选数据
@require_POST
def saveRecord(request):
    params = json.loads(request.body)
    rectangleInfos = params['rectangleInfos']
    try:
        # user = models.User.objects.get(username=request.COOKIES.get("current_user")) # 这种方法仅适用于127.0.0.1的，不适用于localhost和绝对ip的
        user = models.User.objects.get(username=params['current_user'])
        print(params['img'], 'Ok')
        record = models.Record.objects.create(user=user, img=params['img'], create_time=params['create_time'],
                                              consuming_time=params['consuming_time'])
        for _ in rectangleInfos:
            models.Rectangle.objects.create(timestamp=_['timestamp'], img=_['img'], x1=_['x1'], y1=_['y1'], x2=_['x2'],
                                            y2=_['y2'], record=record, user=user)
            # models.Rectangle.objects.create(img=_['img'], x1=_['x1'], y1=_['y1'], x2=_['x2'],y2=_['y2'])
        return HttpResponse(json.dumps({'state': "success"}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'state': "fail"}), content_type='application/json')


# 保存用户所绘制的svg至服务器数据库
@require_POST
def receiveSvg(request):
    params = json.loads(request.body)
    svg_code = '<?xml version="1.0" encoding="UTF-8"?>\n' + params["svg_code"]
    svg_code = sub(r'style="position:.*>', '>', svg_code)  
    img_name = params["img_name"]
    user = models.User.objects.get(username=params['current_user'])
    record = models.Record.objects.filter(user=user, img=img_name)[0]
    file_name = img_name[:-4] + "_" + str(int(time.time())) + ".svg"
    models.SVGFileData.objects.create(file_name=file_name, img=img_name, content=svg_code,
                                      create_time=record.create_time, user=user, record=record)

    return HttpResponse('ok')


# 以下是热力图部分
@require_GET
def getAllImages(request):
    images = os.listdir(os.path.join(settings.BASE_DIR, "frontend/public/static/images/formal/"))
    return HttpResponse(json.dumps({'img_list': images}), content_type='application/json')


# 保存热力分析图svg至服务器数据库
@require_POST
def saveHeatMap(request):
    # params = json.loads(request.body)
    # svg_code = '<?xml version="1.0" encoding="UTF-8"?>\n' + params["svg_code"]
    # svg_code = sub(r'style="position:.*>', '>', svg_code)  # 去除样式
    # svg_code = sub(r'>.*</svg>')
    # file_name = params["img_name"]
    # # 保存svg文件至服务器本地
    # with open(os.path.join(settings.BASE_DIR, 'user_heatmap/' + file_name), 'w', encoding='utf-8') as fp:
    #     fp.write(svg_code)
    #     print(file_name, 'ok')
    return HttpResponse('ok')


# 根据图片名获取原始svg文件
@require_GET
def getSvgOriImage(request):
    def file_iterator(svgfile, chunk_size=512):
        with open(os.path.join(settings.BASE_DIR, "frontend/public/static/images/formal/" + svgfile), 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    svg_file = request.GET.get('image_name')
    response = StreamingHttpResponse(file_iterator(svg_file))
    response['Content-Type'] = 'application/octet-stream'
    return response


@require_POST
def readRects(request):
    params = json.loads(request.body)
    rect_data = models.Rectangle.objects.filter(img=params['img_name']).values()
    return HttpResponse(json.dumps({'datum': list(rect_data)}), content_type='application/json')


# 获取采样算法评估数据源
@require_GET
def getSourceData(request):
    source_data = os.listdir(os.path.join(settings.BASE_DIR, "frontend/public/static/images/evaluation"))
    return HttpResponse(json.dumps({'source_data': source_data}), content_type='application/json')


# 保存评价记录
@require_POST
def saveEvaluationRecord(request):
    try:
        params = json.loads(request.body)
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        models.AlgorithmEvaluation.objects.create(origin_graph=params['origin_graph'],
                                                  algorithm=params['algorithm'],
                                                  community_cluster=params['community_cluster'],
                                                  graph_similarity=params['graph_similarity'],
                                                  connectivity=params['connectivity'],
                                                  high_degree_nodes=params['high_degree_nodes'],
                                                  margin_nodes=params['margin_nodes'],
                                                  boundary_nodes=params['boundary_nodes'],
                                                  create_time=create_time)
        return HttpResponse(json.dumps({'state': "success"}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'state': "fail"}), content_type='application/json')
