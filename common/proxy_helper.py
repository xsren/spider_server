#coding:utf8
import requests
import time
import json
FAIL_SLEEP_TIME = 10
host = 'http://127.0.0.1:5003'


def get_proxy(count=1, protocol=None, logger=None):
    while True:
        try:
            if protocol is not None:
                url = '%s/select?count=%s&protocol=%s'%(host,count,protocol)
            else:
                url = '%s/select?count=%s'%(host,count)
            res = requests.get(url)
            return json.loads(res.text)['data']
        except Exception as e:
            if logger:
                logger.error(str(e))
            else:
                print str(e)
            time.sleep(FAIL_SLEEP_TIME)

def delete_proxy(ip, logger=None):
    while True:
        try:
            url = '%s/delete?ip=%s'%(host,ip)
            res = requests.get(url)
            return json.loads(res.text)['data']
        except Exception as e:
            if logger:
                logger.error(str(e))
            else:
                print str(e)
            time.sleep(FAIL_SLEEP_TIME)