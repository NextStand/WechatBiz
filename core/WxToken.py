# coding:utf-8
import redis
import config
import urllib2
import json
import time
from WechatBiz.wxconfig import WECHAT_CORP_ID

class AccessToken(object):
    """access_token辅助类"""
    __redis = redis.StrictRedis(**config.redis_options)
    __ret = None

    @classmethod
    def update_access_token(cls, tokename, secret):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (
            WECHAT_CORP_ID, secret)
        request = urllib2.Request(url)
        res = urllib2.urlopen(request).read()
        dict_data = json.loads(res)
        errcode = dict_data.get('errcode')
        if str(errcode) != '0':
            raise Exception(dict_data.get('errmsg'))
        else:
            access_token = dict_data["access_token"]
            expires_in = dict_data["expires_in"]
            create_time = time.time()
            ret = dict(access_token=access_token,
                       expires_in=expires_in, create_time=create_time)
            cls.__ret = json.dumps(ret)
            cls.__redis.setex(tokename, expires_in, json.dumps(ret))

    @classmethod
    def get_access_token(cls, tokename, secret):
        cls.__ret = cls.__redis.get(tokename)
        if not cls.__ret:
            # 向微信服务器请求access_token
            cls.update_access_token(tokename, secret)
        ret = cls.__ret
        ret = json.loads(ret)
        access_token = ret.get('access_token')
        create_time = ret.get('create_time')
        expires_in = ret.get('expires_in')
        return dict(access_token=access_token,
                    expires_at=create_time+expires_in)
