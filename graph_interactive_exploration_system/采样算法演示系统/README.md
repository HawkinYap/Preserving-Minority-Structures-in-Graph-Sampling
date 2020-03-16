# 图采样算法演示系统

本系统用于对图采样算法进行可视化展示，系统默认提供了一些可选的数据集和采样算法，同时可检测并高亮出图中的一些稀有结构。

## Install
+ 系统前端安装命令
```
$ cd frontend
$ npm install
```
+ 系统后台安装命令
```
$ pip install -r requirements.txt
```

## Usage

+ Compiles and minifies for production of frontend
```
$ npm run build
```

+ Run the project
```
$ python manage.py runserver 0.0.0.0:8000
```

之后便可通过访问 http://127.0.0.1:8000 进入系统