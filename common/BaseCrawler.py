#coding:utf8

#系统库
import pdb
import sys, copy, time, json
import requests
import base64
import traceback

#本地库
sys.path.append('../../common')
sys.path.append('../../main')
import settings
import utils
import common
import proxy_helper
import account_helper
#requests.adapters.DEFAULT_RETRIES = 1#重试一次

class BaseCrawler:
    """BaseCrawler 爬虫基类"""
    def __init__(self, threadID, logger, ttype, siteName, siteHost, proxy_type, sock, seeds, limit=settings.proxy_one_time_limit, timeout=settings.openUrlTimeout, reset_session_flag=True):
        self.threadID = threadID
        self.logger = logger
        self.ttype = ttype
        self.siteName = siteName
        self.siteHost = siteHost
        self.proxy_type = proxy_type
        self.sock = sock
        self.seeds = seeds
        self.session = requests.Session()
        self.timeout = timeout
        self.last_timestamp = int(time.time())
        self.last_crawl_count = 0
        self.total_crawl_count = 0
        self.ip = None
        self.port = None
        self.limit = limit
        self.reset_session_flag = reset_session_flag
        self.proxy_count = 0

    def run(self):
        self.init_session()
        try:
            if hasattr(self, self.ttype):
                getattr(self, self.ttype)()
            else:
                self.logger.error('no such task type:%s'%self.ttype)
        except:
            self.logger.error(traceback.format_exc())
            utils.send_email(traceback.format_exc())

        self.sock.finish()

    #新加入自动重试功能
    def openUrl(self, url, method='get', headers={}, data = {}, isImg=False, timeout=settings.openUrlTimeout, encoding=None, headersHost=None, retries=10):
        try_times = 0
        while try_times < retries:
            if self.last_crawl_count >= self.limit and self.reset_session_flag:#当一个账号使用超过限制以后会换账号
                self.init_session()
            response = self._openUrl(url, method=method, headers=headers, data = data, isImg=isImg, timeout=timeout, encoding=encoding, headersHost=headersHost)
            return response
            # if response == None or response == "":
            #     self.init_session()
            #     try_times += 1
            #     continue
            # else:
            #     self.last_crawl_count += 1
            #     return response

    #自定义url opener函数
    def _openUrl(self, url, method='get', headers={}, data = {}, isImg=False, timeout=settings.openUrlTimeout, encoding=None, headersHost=None):
        _headers = copy.copy(headers)
        if headersHost is not None:
            _headers['Host'] = headersHost
        else:
            try:
                _headers['Host'] = url.split('//')[1].split('/')[0]
            except Exception, e:
                self.logger.error(str(e)+' : '+url)

        # url = 'https://www.youtube.com/user/NBA'
        t0 = time.time()
        self.logger.debug("begin to crawl url :%s"%url)
        if self.timeout > timeout:#取大的超时时间
            timeout = self.timeout
        try:
            if method == 'get':
                res = self.session.get(url, headers=_headers, params=data, timeout=timeout)
            else: 
                res = self.session.post(url, headers=_headers, params=data, timeout=timeout)

            self.logger.debug('status:%d, encoding:%s'%(res.status_code,res.encoding))
            # pdb.set_trace()

            if res.status_code != 200:#http status
                self.logger.error('status:%d, encoding:%s, url:%s'%(res.status_code,res.encoding,url))
                if res.status_code == 403 and (self.proxy_type == "socks" or self.proxy_type == "http"):
                    proxy_helper.delete_proxy(ip=self.ip)
                # if res.status_code == 503:
                #     sys.exit(-1)
                #     time.sleep(60)
                # self.logger.error(res.text)
                return None
            if encoding is not None:#编码
                res.encoding = encoding
            else:
                if res.encoding.lower() in ['gbk', 'gb2312', 'windows-1252']:
                    res.encoding = 'gb18030'
                elif res.encoding.lower() in ['iso-8859-1', 'iso8859-1']:
                    res.encoding = 'utf8'

            if isImg:
                response = res.content
            else:
                response = res.text
            time.sleep(settings.http_sleep_time)    
        except Exception,e:
            self.logger.error('download html failed, url: '+url+' , error: '+str(e))
            if (self.proxy_type == "socks" or self.proxy_type == "http"):
                proxy_helper.delete_proxy(ip=self.ip)
            # if self.proxy_type == "http":
            #     data = [{'ip':self.ip, 'port':self.port, 'site':self.siteName, 'type':self.proxy_type}]
            #     collName = "%s_proxy"%self.siteName
            #     self.sock.write_to_socket(self.dbName,collName,common.CHANGE_PROXY_STATUS,data)
            return None
        #gzip
        # response = utils.decodeGzip(response)
        #decode to unicode
        response = utils.decodeToUnicode(response, isImg)
        t_diff = time.time() - t0
        self.logger.debug("finish to crawl url :%s, use time:%s"%(url,t_diff))
        return response

    def reset_account(self):
        return True
        # account = account_helper.get_account(self.siteName)[0]
        # self.logger.debug(account)
        # self.uname = account['uname']
        # cookies = json.loads(account['cookie'])
        cookies_str = 'fs_uid=www.fullstory.com`1JRNY`5206304379371520:5649050225344512; visitor_hash=bc2251daf066b65710c4b0a3ca990101; _ga=GA1.2.829066366.1492070100; ajs_group_id=null; ajs_user_id=%226337525%22; ajs_anonymous_id=%220ca70d439f399fed31d6ab13a4f3045f%22; amplitude_idangel.co=eyJkZXZpY2VJZCI6ImM2ZGIwZWZlLWIwZGUtNGIzOC05ZjdkLTllOGU0M2M2ZDYwY1IiLCJ1c2VySWQiOiI2MzM3NTI1Iiwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNDkzMzQ0MzY0NDcxLCJsYXN0RXZlbnRUaW1lIjoxNDkzMzQ0OTUxODM5LCJldmVudElkIjo5LCJpZGVudGlmeUlkIjoxMTksInNlcXVlbmNlTnVtYmVyIjoxMjh9; mp_6a8c8224f4f542ff59bd0e2312892d36_mixpanel=%7B%22distinct_id%22%3A%20%226332045%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24username%22%3A%20%22xs-ren%22%2C%22angel%22%3A%20false%2C%22candidate%22%3A%20false%2C%22roles%22%3A%20%5B%5D%2C%22quality_ceiling%22%3A%20%223%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpap%22%3A%20%5B%5D%2C%22__alias%22%3A%20%226337525%22%7D; mp_mixpanel__c=0; _angellist=dd21fc4203e9f3a734b03390274d79bb'
        cookies = {}
        for s in cookies_str.split(';'):
            k = s.split('=')[0]
            v = s.split('=')[0]
            cookies[k] = v
        
        for k,v in cookies.iteritems():
            self.session.cookies.set(k,v)

        return True

    def init_session(self):
        while True:
            self.logger.info('begin to reset session')
            self.last_crawl_count = 0
            self.session = requests.Session()
            #建立session, get http proxy 
            if self.proxy_type == "socks" or self.proxy_type == "http" or self.proxy_type == "all":   
                self.reset_proxy()
            res = self.reset_account()
            if res:
                self.logger.info('reset session success')
                return

    def reset_proxy(self):
        while True:
            self.logger.info('begin to reset_proxy')
            if self.proxy_type == "http":
                proxies = proxy_helper.get_proxy(count=1,protocol=0)
            elif self.proxy_type == "socks":
                proxies = proxy_helper.get_proxy(count=1,protocol=1)
            else:
                proxies = proxy_helper.get_proxy(count=1,protocol=None)
            
            if len(proxies) == 0:
                self.logger.warning('no proxy .....')
                time.sleep(60*10)
                continue
            proxy = proxies[0]
            self.logger.debug(proxy)
            self.ip = proxy['ip']
            self.port = proxy['port']
            if proxy['protocol'] == 0:
                proxies = {'http':'http://%s:%s/'%(self.ip,self.port),
                        'https':'http://%s:%s/'%(self.ip,self.port)
                }
            else:
                user = base64.b64encode(json.dumps( (self.ip,) ))
                password = 'null'
                proxies =  {'http': 'socks5://{0}:{1}@{2}:{3}'.format(user, password, self.ip, self.port),
                        'https': 'socks5://{0}:{1}@{2}:{3}'.format(user, password, self.ip, self.port),
                }
            self.session.proxies = proxies
            self.logger.info('reset_proxy success')
            self.proxy_count += 1
            print 'self.proxy_count:%s...........'%self.proxy_count
            return


    def get_value_from_xpath(self,node,xpath,default=None):
        nodes = node.xpath(xpath)
        if len(nodes):
            return nodes[0]
        else:
            return default
