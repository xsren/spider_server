# spider_server
这是一个分布式爬虫服务器，将爬虫常用的操作在server端封装，爬虫客户端使用socket调研server端封装的接口。
后端数据库用的是mongodb。

### 一、接口解释

可以参考 test_spider_client.py 

##### 1、get_task 获取任务
```
def get_task(self, dbName, collName, count=1):
```

##### 2、insert_data 存储抓取结果
```
def insert_data(self, dbName, collName, data):
```

##### 3、put_task 存储新增任务
```
def put_task(self, dbName, collName, data):
```

##### 4、change_task_status 更改任务状态
```
def change_task_status(self, dbName, collName, data):
任务状态
NOT_CRAWL = 0
CRAWLING = 1
CRAWL_SUCCESS = 2
CRAWL_FAIL= 3
INVALID_TASK = 4
```
### 二、使用示例

crawler中是qq音乐的爬虫

##### 1、启动server
```
python run_server.py
```

##### 2、启动spider
```
# 初始化歌单任务
python run_crawler.py -s qq -t init_playlist_tasks 
# 抓取歌单列表
python run_crawler.py -s qq -t crawl_playlist_index 
# 抓取歌单详情
python run_crawler.py -s qq -t crawl_playlist 
```





