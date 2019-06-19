# coding:utf-8
__author__ = 'BLUE'
__time__ = 'Sun Oct 28 2018 21:45:21 GMT+0800'

import json
import six
import urllib
import requests
import tornado.httpclient

from tornado import gen
from WechatBiz.core.Exceptions import OfficialAPIError
from WechatBiz.lib.Utils import encodeMulFormdata


class WechatRequest(object):
    """ 
    WechatRequest 请求类

    对微信服务器的请求响应处理进行封装
    """

    def __init__(self, conf=None):
        """
        :param conf: WechatConf 配置类实例
        """
        self.__conf = conf

    @tornado.gen.coroutine
    def request(self, method, url, access_token=None, **kwargs):
        """
            向微信服务器发送请求

            :param method: 请求方法
            :param url: 请求地址
            :param access_token: access token 值, 如果初始化时传入 conf 会自动获取, 如果没有传入则请提供此值
            :param kwargs: 附加数据
            :return: 微信服务器响应的 JSON 数据 ,异步Future
        """
        access_token = self.__conf.access_token if self.__conf.access_token is not None else access_token
        """ if isinstance(kwargs.get('data', ''), dict):
            body = json.dumps(kwargs.get("data"), ensure_ascii=False)
            if isinstance(body, six.text_type):
                body = body.encode('utf-8')
            kwargs['data'] = body """
        http = tornado.httpclient.AsyncHTTPClient()
        httprequest = None
        if method == 'GET':
            params = kwargs.get('data')
            pstr = urllib.urlencode(params)
            url = '%s?access_token=%s&%s' % (
                url, access_token, pstr) if access_token else '%s?%s' % (url, pstr)
            httprequest = tornado.httpclient.HTTPRequest(
                url=url,
                method=method
            )
        else:
            url1 = '%s?access_token=%s' % (url, access_token) if url.find(
                'access_token') < 0 else url
            httprequest = tornado.httpclient.HTTPRequest(
                url=url1,
                method=method,
                body=json.dumps(kwargs.get('data'), ensure_ascii=False)
            )
        response = yield http.fetch(httprequest)
        if kwargs.get('_all', 0) == 1:
            raise tornado.gen.Return(response)
        else:
            response_json = json.loads(response.body)
            headimgurl = response_json.get('headimgurl')
            if headimgurl:
                response_json['headimgurl'] = headimgurl.replace('\\', '')
            self._check_official_error(response_json)
            raise tornado.gen.Return(response_json)

    def syncrequest(self, method, url, access_token=None, **kwargs):
        """
            向微信服务器发送同步请求

            :param method: 请求方法
            :param url: 请求地址
            :param access_token: access token 值, 如果初始化时传入 conf 会自动获取, 如果没有传入则请提供此值
            :param kwargs: 附加数据
            :return: 微信服务器响应的 JSON 数据
        """
        access_token = self.__conf.access_token if self.__conf.access_token is not None else access_token
        if "params" not in kwargs:
            kwargs["params"] = {
                "access_token": access_token
            }
        else:
            kwargs["params"]["access_token"] = access_token
        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            if isinstance(body, six.text_type):
                body = body.encode('utf8')
            kwargs["data"] = body
        r = requests.request(
            method=method,
            url=url,
            **kwargs
        )
        r.raise_for_status()
        try:
            response_json = r.json()
        except ValueError:  # 非 JSON 数据
            return r
        headimgurl = response_json.get('headimgurl')
        if headimgurl:
            response_json['headimgurl'] = headimgurl.replace('\\', '')
        self._check_official_error(response_json)
        return response_json

    @tornado.gen.coroutine
    def uploadMedia(self, url, **kwargs):
        """
            向微信服务器上传文件

            :param url: 请求地址
            :param kwargs: 附加数据
            :return: 微信服务器响应的 JSON 数据 ,异步Future
        """
        files = kwargs.get('data').get('files')
        content_type, body = encodeMulFormdata(files)
        access_token = self.__conf.access_token
        headers = {"Content-Type": content_type,
                   'content-length': str(len(body))}
        url = '%s?access_token=%s&type=%s' % (
            url, access_token, kwargs.get('data').get('type', 'image'))
        request = tornado.httpclient.HTTPRequest(url=url,
                                                 method="POST", headers=headers, body=body)
        response = yield tornado.httpclient.AsyncHTTPClient().fetch(request)
        response_json = json.loads(response.body)
        self._check_official_error(response_json)
        raise tornado.gen.Return(response_json)

    def get(self, url, access_token=None, **kwargs):
        """
        使用 GET 方法向微信服务器发出请求
        :param url: 请求地址
        :param access_token: access token 值, 如果初始化时传入 conf 会自动获取, 如果没有传入则请提供此值
        :param kwargs: 附加数据
        :return: 微信服务器响应的 JSON 数据
        """
        data = kwargs.get('data', {})
        if data.pop('_mode', 'async') == 'async':
            return self.request(
                method="GET",
                url=url,
                access_token=access_token,
                **kwargs
            )
        else:
            return self.syncrequest(
                method="GET",
                url=url,
                access_token=access_token,
                **kwargs
            )

    def post(self, url, access_token=None, **kwargs):
        """
        使用 POST 方法向微信服务器发出请求
        :param url: 请求地址
        :param access_token: access token 值, 如果初始化时传入 conf 会自动获取, 如果没有传入则请提供此值
        :param kwargs: 附加数据
        :return: 微信服务器响应的 JSON 数据
        """
        data = kwargs.get('data', {})
        if data.pop('_mode', 'async') == 'async':
            return self.request(
                method="POST",
                url=url,
                access_token=access_token,
                **kwargs
            )
        else:
            return self.syncrequest(
                method="POST",
                url=url,
                access_token=access_token,
                **kwargs
            )

    def getRes(self, url, access_token=None, **kwargs):
        kwargs['_all'] = 1
        return self.get(url, access_token, **kwargs)

    def postRes(self, url, access_token=None, **kwargs):
        kwargs['_all'] = 1
        return self.post(url, access_token, **kwargs)

    def _check_official_error(self, json_data):
        """
        检测微信公众平台返回值中是否包含错误的返回码
        :raises OfficialAPIError: 如果返回码提示有错误，抛出异常
        """
        if 'errcode' in json_data and json_data.get('errcode') != 0:
            raise OfficialAPIError(errcode=json_data.get(
                'errcode'), errmsg=json_data.get('errmsg', ''))
