from django.db import models

# Create your models here.
# 用户类
class User(models.Model):
    username = models.CharField(primary_key=True, max_length=50)
    gender = models.CharField(max_length= 10)
    age = models.IntegerField()
    education = models.CharField(max_length=20)
    major = models.CharField(max_length=100)

# 实验记录类
class Record(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, default='')
    img = models.CharField(max_length=50)
    create_time = models.CharField(max_length=50)
    consuming_time = models.IntegerField()

# 框选数据类
class Rectangle(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=50)
    img = models.CharField(max_length=50)
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
    user = models.ForeignKey('User', on_delete=models.CASCADE, default='')
    record = models.ForeignKey('Record', on_delete=models.CASCADE, default='')

# 实验结果类
class SVGFileData(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, default='')
    file_name = models.CharField(max_length=50)
    img = models.CharField(max_length=50)
    content = models.TextField()
    create_time = models.CharField(max_length=50)
    record = models.ForeignKey('Record', on_delete=models.CASCADE, default='')

# 算法评估记录
class AlgorithmEvaluation(models.Model):
    id = models.AutoField(primary_key=True)
    origin_graph = models.CharField(max_length=50)  # 原始图
    algorithm = models.CharField(max_length=50)  # 采样算法名称
    # 评价指标 * 6
    community_cluster = models.IntegerField()
    graph_similarity = models.IntegerField()
    connectivity = models.IntegerField()
    high_degree_nodes = models.IntegerField()
    margin_nodes = models.IntegerField()
    boundary_nodes = models.IntegerField()
    create_time = models.CharField(max_length=50)  # 创建时间