# User Study System

## Install
+ install the dependencies of the frontend
```
$ cd frontend
$ npm install
```
+ install the packages of the backend and 进行后台数据库文件映射
```
$ pip install -r requirements.txt

$ python manage.py makemigrations
$ python manage.py migrate
```


## Usage

+ Compiles and run the frontend of System
```
$ npm run serve
```

+ Run the backend of System
```
$ python manage.py runserver 0.0.0.0:8000
```

之后便可通过访问 http://127.0.0.1:8080 进入系统