#coding:utf8
import random


'''
common
'''
openUrlTimeout = 3
noHttpProxySleepTime = 60

http_sleep_time = 0#random.uniform(0.5,1)

u0_no_task_sleep_time = 60*60*24
u1_no_task_sleep_time = 60
u2_no_task_sleep_time = 0.5
no_task_sleep_time = 60
'''
server
'''
server_ip = "127.0.0.1"
server_port = 2234

'''
log
'''
# logs_dir
logs_dir_home = '/mnt/spider/logs'
tmp_dir_home = './tmp'

'''
email
'''

tcp_login_key = 'my_tcp_login_key'

'''
mongo
'''
count_db_name = "test"
count_coll_name = "count"
#mongodb
mongo_host = "127.0.0.1"
mongo_port = 27017

mongo_user = ""
mongo_passwd = ""

auth_db = 'test'


def getMCInstance(isAuth=False, isTxMongo=False):
    if isTxMongo:
        from txmongo import MongoConnection as MongoClient
    else:
        from pymongo import MongoClient
    if isAuth:
        mongourl = 'mongodb://%s:%s@%s:%s/%s'%(mongo_user,mongo_passwd,mongo_host,mongo_port,auth_db)
    else:
        mongourl = 'mongodb://%s:%s/%s'%(mongo_host,mongo_port,auth_db)
    return MongoClient(mongourl, connect=False)

get_tasks_num_one_time = 1
return_tasks_one_time = 30

# queue size
write_queue_size = 0
html_queue_size = 0
task_queue_size = 0
count_queue_size = 0

proxy_one_time_limit=3
