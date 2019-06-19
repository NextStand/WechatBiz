# coding:utf-8
"""
企业微信客户端服务模块
    |- 小程序服务模块
    |- JS-SDK服务模块
    |- 移动端SDK服务模块
"""
__author__ = 'BLUE'
__time__ = 'Fri May 17 2019 15:28:25 GMT+0800'
# ------------------------------------------------------------------------
import redis
import hashlib
import urllib2
import config
import json
import time
from WechatBiz.core.WechatBase import WechatBase
from WechatBiz.wxconfig import WECHAT_CORP_ID

class WxBizJsSdk(WechatBase):
    """ JS-SDK服务 """
    __redis = redis.StrictRedis(**config.redis_options)

    def __init__(self):
        self.__ret = None
        token, expires_at = self.initToken()
        super(WxBizJsSdk, self).__init__(
            access_token=token, access_token_expires_at=expires_at)

    def __UpdateTicket(self, ticketname):
        url = "https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token=%s" % self.conf.access_token
        if ticketname == 'app_jsapi_ticket':
            url = "https://qyapi.weixin.qq.com/cgi-bin/ticket/get?access_token=%s&type=agent_config" % self.conf.access_token
        request = urllib2.Request(url)
        res = urllib2.urlopen(request).read()
        dict_data = json.loads(res)
        errcode = dict_data.get('errcode')
        if str(errcode) != '0':
            raise Exception(dict_data.get('errmsg'))
        else:
            ticket = dict_data["ticket"]
            expires_in = dict_data["expires_in"]
            create_time = time.time()
            ret = dict(js_ticket=ticket,
                       expires_in=expires_in, create_time=create_time)
            self.__ret = json.dumps(ret)
            self.__redis.setex(ticketname, expires_in, json.dumps(ret))

    def __GetTicket(self, ticket):
        self.__ret = self.__redis.get(ticket)
        if not self.__ret:
            # 向微信服务器请求access_token
            self.__UpdateTicket(ticket)
        ret = self.__ret
        ret = json.loads(ret)
        js_ticket = ret.get('js_ticket')
        create_time = ret.get('create_time')
        expires_in = ret.get('expires_in')
        return dict(js_ticket=js_ticket,
                    expires_at=create_time+expires_in)

    # 获取企业的jsapi_ticket
    def GetCropJsTicket(self):
        """ 
            获取企业的jsapi_ticket 

            :return: dict(js_ticket,expires_at)
        """
        return self.__GetTicket('crop_jsapi_ticket')

    # 获取应用的jsapi_ticket
    def GetAppJsTicket(self):
        """ 
            获取应用的jsapi_ticket 

           :return: dict(js_ticket,expires_at)
        """
        return self.__GetTicket('app_jsapi_ticket')

    # 使用 jsapi_ticket 对 url 进行签名
    def GetJsApiSign(self, timestamp, noncestr, url, ticket):
        """
            使用 jsapi_ticket 对 url 进行签名

            :param timestamp: 时间戳
            :param noncestr: 随机数
            :param url: 要签名的 url，不包含 # 及其后面部分
            :param ticket: jsapi_ticket 值 
            :return: 返回sha1签名的hexdigest值
        """
        data = {
            'jsapi_ticket': ticket,
            'noncestr': noncestr,
            'timestamp': timestamp,
            'url': url,
        }
        keys = list(data)
        keys.sort()
        data_str = '&'.join(['%s=%s' % (key, data[key]) for key in keys])
        signature = hashlib.sha1(data_str.encode('utf-8')).hexdigest()
        return signature

    # 获取前端注入权限验证配置的一些参数
    def GetCropConfig(self, url):
        """
            获取前端注入权限验证配置的一些参数，是GetJsApiSign的增强

            :param url: 要签名的 url，不包含 # 及其后面部分
            :return: dict(appId、timestamp、nonceStr、signature)
        """
        ret1 = self.GetCropJsTicket()
        timestamp = str(int(time.time()))
        nonce_str = self.NonceStr()
        jsticket = ret1.get('js_ticket')
        signature = self.GetJsApiSign(timestamp, nonce_str, url, jsticket)
        return dict(
            appId=WECHAT_CORP_ID,
            timestamp=timestamp,
            nonceStr=nonce_str,
            signature=signature
        )

    # 获取前端注入应用权限验证配置的一些参数
    def GetAgentConfig(self, url):
        """
            获取前端注入应用权限验证配置的一些参数，是GetJsApiSign的增强

            :param url: 要签名的 url，不包含 # 及其后面部分
            :return: dict(corpid、timestamp、nonceStr、signature)
        """
        ret1 = self.GetAppJsTicket()
        timestamp = str(int(time.time()))
        nonce_str = self.NonceStr()
        jsticket = ret1.get('js_ticket')
        print(jsticket)
        signature = self.GetJsApiSign(timestamp, nonce_str, url, jsticket)
        return dict(
            corpid=WECHAT_CORP_ID,
            timestamp=timestamp,
            nonceStr=nonce_str,
            signature=signature
        )
