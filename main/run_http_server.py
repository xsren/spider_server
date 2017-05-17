#coding:utf8

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET
import time
import sys
from Queue import Queue
import atexit
import json

sys.path.append('../common')
import DbManager
import utils
import settings
import common

class CrawlerServer(Resource):

    def __init__(self):
        write_queues = {}
        task_queues = {}
        count_queue = Queue(maxsize = settings.count_queue_size)

        mc = settings.getMCInstance(isTxMongo=False)
        self.logger = utils.initLogger('%s/run_data_server_main.log'%settings.logs_dir_home)
        self.db = DbManager.DbManager(self.logger, mc, write_queues, task_queues, count_queue)

        # 开一个线程定时清理
        reactor.callInThread(self.sched_cleanup)

        self.logger.info("__init__ finish")

    def render_GET(self, request):
        return 'started ......'

    def render_POST(self, request):
        try:
            data = request.args["data"][0]
            rj = json.loads(data)
        except Exception, e:
            self.logger.error(str(e))
            return "post data error"

        if rj == 'echo':
            return
        
        if rj['type'] == common.REQUEST_MESSAGE:
            dbName = rj["dbName"]
            collName = rj["collName"]
            action = rj["action"]
            data = rj["data"]
            self.handle_request(dbName, collName, action, data, request)
            if action == common.GET_TASK:
                return NOT_DONE_YET

        elif rj['type'] == common.ECHO_MESSAGE:
            pass
        else:
            info = "not support message:%s"%rj['type']
            self.logger.warning(info)
            return info

    def handle_request(self, dbName, collName, action, data, request):
        db = self.db
        if action == common.PUT_TASK:
            db._common_put_task_to_db(dbName, collName, data)
        elif action == common.GET_TASK:
            d = db._common_get_task_from_db(dbName, collName, data['count'])
            d.addCallback(self.handle_success,request)
            d.addErrback(self.handle_failure,request)
        elif action == common.PUT_DATA:
            db._common_put_data_to_db(dbName, collName, data)
        elif action == common.CHANGE_TASK_STATUS:
            db._common_change_task_status(dbName, collName, data)

    def handle_success(self, res, request):
        res = {
            '_type':common.RESPONSE_MESSAGE,
            'status':common.OK,
            # 'fromAddr':'server',
            # 'toAddr':self.name,
            'data':res,
        }
        _res = json.dumps(res)

        # print _res
        request.write(_res)
        request.finish()

    def handle_failure(self, err, request):
        res = {
            '_type':common.RESPONSE_MESSAGE,
            'status':common.FAIL,
            # 'fromAddr':'server',
            # 'toAddr':self.name,
            'data':[],
        }
        _res = json.dumps(res)
        self.logger.error(err)
        request.write(_res)
        request.finish()

    # 定时清理
    def sched_cleanup(self):
        while True:
            time.sleep(10)
            self.cleanup()

    def cleanup(self):
        self.db.cleanup_handle_queue()

if __name__ == '__main__':

    root = Resource()
    root.putChild("crawler", CrawlerServer())
    factory = Site(root)
    reactor.listenTCP(2234, factory)
    reactor.run()

    # 退出时做清理工作
    atexit.register(factory.cleanup)
    atexit.register(factory.archive)