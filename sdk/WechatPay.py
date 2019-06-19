# coding:utf-8
""" 
微信支付模块
该模块比较独立

__time__ = 'Wed Oct 31 2018 15:09:12 GMT+0800'
"""
__author__ = 'BLUE'
__time__ = 'Wed May 22 2019 10:42:07 GMT+0800'
# ------------------------------------------------------------------------
import hashlib
import random
import string
import time
import urllib2
import json
import tornado.httpclient
from tornado import gen
from WechatBiz.core.Exceptions import WechatPayError
from WechatBiz.wxconfig import WECHAT_APP_ID, WECHAT_PAY_MCHID, WECHAT_PAY_SECRET
from WechatBiz.core.WechatBase import WechatBase

try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree


class WechatPay(WechatBase):
    """ 微信支付封装 """

    def __init__(self, wx_app_id=WECHAT_APP_ID, wx_mch_id=WECHAT_PAY_MCHID, wx_mch_key=WECHAT_PAY_SECRET, wx_notify_url=None):
        """
        :param wx_app_id: 微信公众号appid
        :param wx_mch_id: 微信商户号id
        :param wx_mch_key:微信支付密钥
        :param wx_notify_url: 接受微信付款消息通知地址(程序中需要有该接口)
        """
        self.WX_APP_ID = wx_app_id
        self.WX_MCH_ID = wx_mch_id
        self.WX_MCH_KEY = wx_mch_key
        self.WX_NOTIFY_URL = wx_notify_url

    @staticmethod
    def to_utf8(raw):
        return raw.encode("utf-8") if isinstance(raw, unicode) else raw

    # xml字符转对象
    @staticmethod
    def to_dict(content):
        """ xml字符转对象，没有使用Parse中的方法，为了让模块更独立 """
        raw = {}
        root = ETree.fromstring(content)
        for child in root:
            raw[child.tag] = child.text
        return raw

    # 生成0~9的随机字符序列
    @staticmethod
    def random_num(length):
        """ 生成0~9的随机字符序列 """
        digit_list = list(string.digits)
        random.shuffle(digit_list)
        return ''.join(digit_list[:length])

    # 生成签名
    def sign(self, raw):
        """
            生成签名

            参考微信签名生成算法
            详情参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=4_3
            :param raw: 参数字典
            :return: 返回的签名
        """
        raw = [(k, str(raw[k]) if isinstance(raw[k], (int, float)) else raw[k])
               for k in sorted(raw.keys())]
        s = "&".join("=".join(kv) for kv in raw if kv[1])
        s += "&key={0}".format(self.WX_MCH_KEY)
        return hashlib.md5(self.to_utf8(s)).hexdigest().upper()

    # 验证签名是否正确,用于收到消息时候
    def check_sign(self, raw):
        """
            验证签名是否正确,sign不参与签名

            :param raw: 参数字典
            :return: 验证结果True or False
        """
        sign = raw.pop('sign')
        return sign == self.sign(raw)

    # 字典转换成xml
    def dict2xml(self, raw):
        """ 
            字典转换成xml 

            :param raw:参数字典
            :return: xml字符串
        """
        s = ""
        for k, v in raw.iteritems():
            s += '<{0}>{1}</{0}>'.format(k, self.to_utf8(v))
        return "<xml>{0}</xml>".format(s)

    # 向服务发起POST请求
    @gen.coroutine
    def fetch(self, url, data):
        """ 
            向服务发起POST请求 

            :param url: 请求地址
            :param data:参数字典
            :return:响应微信服务器的字典对象 异步Future
        """
        http = tornado.httpclient.AsyncHTTPClient()
        httprequest = tornado.httpclient.HTTPRequest(
            url=url,
            method='POST',
            body=self.dict2xml(data)
        )
        response = yield http.fetch(httprequest)
        try:
            raw = self.to_dict(response.body)
        except ETree.ParseError:
            raise tornado.gen.Return(response.body)
        else:
            if raw.get('return_code') == 'FAIL':
                raise WechatPayError(raw.get('return_msg'))
            err_msg = raw.get("err_code_des")
            if err_msg:
                raise WechatPayError(err_msg)
            raise tornado.gen.Return(raw)

    # 向服务器发起带SSL证书的请求
    @gen.coroutine
    def fetch_with_ssl(self, url, data, api_client_cert_path, api_client_key_path):
        """ 
            向服务器发起带SSL证书的请求 

            :param url: 请求地址
            :param data: 参数字典
            :api_client_cert_path: 客户端证书证书部分文件路径
            :api_client_key_path: 客户端证书密钥部分文件路径
            :return:响应微信服务器的字典对象 异步Future
        """
        http = tornado.httpclient.AsyncHTTPClient()
        httprequest = tornado.httpclient.HTTPRequest(
            url=url,
            method='POST',
            body=self.dict2xml(data),
            client_key=api_client_key_path,
            client_cert=api_client_cert_path
        )
        response = yield http.fetch(httprequest)
        try:
            raw = self.to_dict(response.body)
        except ETree.ParseError:
            raise tornado.gen.Return(response.body)
        else:
            if raw.get('return_code') == 'FAIL':
                raise WechatPayError(raw.get('return_msg'))
            err_msg = raw.get("err_code_des")
            if err_msg:
                raise WechatPayError(err_msg)
            raise tornado.gen.Return(raw)

    # 回复数据微信服务器xml数据格式
    def reply(self, msg, ok=True):
        """ 
            回复数据微信服务器xml数据格式 

            :param msg: 自定义内容
            :param ok: 成功消息为True，失败消息为False
            :retrun: xml字符串
        """
        code = "SUCCESS" if ok else "FAIL"
        return self.dict2xml(dict(return_code=code, return_msg=msg))

    # 统一下单
    def unifiedOrder(self, **data):
        """
            统一下单

            详细参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
            :param data: out_trade_no, body, total_fee, trade_type
                out_trade_no: 商户订单号
                body: 商品描述
                total_fee: 标价金额, 整数, 单位 分
                trade_type: 交易类型,JSAPI、NATIVE（含有二维码链接，自行生成二维码）、APP
                spbill_create_ip:客户端ip 
            :return: 统一下单生成结果 异步Future
        """
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        self.ChkNeedParamsError(['out_trade_no', 'body', 'total_fee',
                                 'trade_type', 'spbill_create_ip'], data, u'微信支付统一下单接口中，')
        # 关联参数
        data.setdefault('appid', self.WX_APP_ID)
        data.setdefault('mch_id', self.WX_MCH_ID)
        data.setdefault('nonce_str', self.NonceStr())
        if self.WX_NOTIFY_URL:
            data.setdefault('notify_url', self.WX_NOTIFY_URL)
        data.setdefault('sign', self.sign(data))
        return self.fetch(url, data)

    # 生成给JavaScript调用的数据,微信内H5调用凭据
    def jsPayApi(self, **kwargs):
        """
            生成给JavaScript调用的数据,微信内H5调用凭据

            详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=7_7&index=6
            :param kwargs: openid, body, total_fee,prepay_id
                openid: 用户openid
                body: 商品名称
                total_fee: 标价金额, 整数, 单位 分
                prepay_id:预支付交易会话标识
                out_trade_no: 商户订单号, 若未传入则自动生成
            :return: 携带微信JS接口支付所需的信息的dict
        """
        self.ChkNeedParamsError(['prepay_id'], kwargs,
                                u'生成给JavaScript调用的数据接口中，')
        kwargs.setdefault('trade_type', 'JSAPI')
        if 'out_trade_no' not in kwargs:
            kwargs.setdefault("out_trade_no", self.NonceStr())
        package = "prepay_id={0}".format(kwargs["prepay_id"])
        timestamp = str(int(time.time()))
        nonce_str = self.NonceStr()
        raw = dict(appId=self.WX_APP_ID, timeStamp=timestamp,
                   nonceStr=nonce_str, package=package, signType='MD5')
        sign = self.sign(raw)
        return dict(package=package, appId=self.WX_APP_ID, timeStamp=timestamp, nonceStr=nonce_str, paySign=sign, signType='MD5')

    # 订单查询
    def orderQuery(self, **data):
        """
            订单查询

            详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_2
            :param data: out_trade_no, transaction_id至少填一个
                out_trade_no: 商户订单号
                transaction_id: 微信订单号
            :return: 携带订单查询结果的Future
        """
        url = "https://api.mch.weixin.qq.com/pay/orderquery"
        if 'out_trade_no' not in data and 'transaction_id' not in data:
            raise WechatPayError(u"订单查询接口中，out_trade_no、transaction_id至少填一个")
        data.setdefault("appid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.NonceStr())
        data.setdefault("sign", self.sign(data))
        return self.fetch(url, data)

    # 关闭订单
    def closeOrser(self, out_trade_no):
        """
            关闭订单

            详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_3
            :param out_trade_no: 商户订单号
            :return: 携带申请关闭订单结果的Future
        """
        url = "https://api.mch.weixin.qq.com/pay/closeorder"
        data = {
            'out_trade_no': out_trade_no,
            'appid': self.WX_APP_ID,
            'mch_id': self.WX_MCH_ID,
            'nonce_str': self.NonceStr(),
        }
        data['sign'] = self.sign(data)
        return self.fetch(url, data)

    # 申请退款
    def refund(self, api_cert_path, api_key_path, **data):
        """
            申请退款

            详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_4
            :param api_cert_path: 微信支付商户证书路径，此证书(apiclient_cert.pem)需要先到微信支付商户平台获取，下载后保存至服务器
            :param api_key_path: 微信支付商户证书路径，此证书(apiclient_key.pem)需要先到微信支付商户平台获取，下载后保存至服务器
            :param data: out_trade_no、transaction_id至少填一个, out_refund_no, total_fee, refund_fee
                out_trade_no: 商户订单号
                transaction_id: 微信订单号
                out_refund_no: 商户退款单号（若未传入则自动生成）
                total_fee: 订单金额
                refund_fee: 退款金额
            :return: 携带退款申请返回结果的Future
        """
        url = "https://api.mch.weixin.qq.com/secapi/pay/refund"

        if "out_trade_no" not in data and "transaction_id" not in data:
            raise WechatPayError(u"退款申请接口中，out_trade_no、transaction_id至少填一个")
        self.ChkNeedParamsError(
            ['total_fee', 'refund_fee', 'out_refund_no'], data, u'退款申请接口中，')
        data.setdefault("appid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("op_user_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.NonceStr())
        data.setdefault("sign", self.sign(data))
        if self.WX_NOTIFY_URL:
            data.setdefault('notify_url', self.WX_NOTIFY_URL)
        return self.fetch_with_ssl(url, data, api_cert_path, api_key_path)

    # 查询退款
    def refundQuery(self, **data):
        """
            查询退款

            提交退款申请后，通过调用该接口查询退款状态。退款有一定延时，
            用零钱支付的退款20分钟内到账，银行卡支付的退款3个工作日后重新查询退款状态。
            详细参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_5
            :param data: out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个
                out_refund_no: 商户退款单号
                out_trade_no: 商户订单号
                transaction_id: 微信订单号
                refund_id: 微信退款单号
            :return: 携带退款查询结果的异步Future
        """
        url = "https://api.mch.weixin.qq.com/pay/refundquery"

        if "out_refund_no" not in data and "out_trade_no" not in data and "transaction_id" not in data and "refund_id" not in data:
            raise WechatPayError(
                u"退款查询接口中，out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个")

        data.setdefault("appid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.NonceStr())
        data.setdefault("sign", self.sign(data))
        return self.fetch(url, data)

    # 下载对账单
    def downloadBill(self, bill_date, bill_type=None):
        """
            下载对账单

            详细参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_6
            :param bill_date: 对账单日期
            :param bill_type: 账单类型(ALL-当日所有订单信息，[默认]SUCCESS-当日成功支付的订单, REFUND-当日退款订单)
            :return: 数据流形式账单 异步Future
        """
        url = "https://api.mch.weixin.qq.com/pay/downloadbill"
        data = {
            'bill_date': bill_date,
            'bill_type': bill_type if bill_type else 'SUCCESS',
            'appid': self.WX_APP_ID,
            'mch_id': self.WX_MCH_ID,
            'nonce_str': self.NonceStr()
        }
        data['sign'] = self.sign(data)
        return self.fetch(url, data)

    # 发给用户微信红包
    def sendRedPack(self, api_cert_path, api_key_path, **data):
        """
            发给用户微信红包

            详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/tools/cash_coupon.php?chapter=13_4&index=3
            :param api_cert_path: 微信支付商户证书路径，此证书(apiclient_cert.pem)需要先到微信支付商户平台获取，下载后保存至服务器
            :param api_key_path: 微信支付商户证书路径，此证书(apiclient_key.pem)需要先到微信支付商户平台获取，下载后保存至服务器
            :param data: send_name, re_openid, total_amount, wishing, client_ip, act_name, remark
                send_name: 商户名称
                re_openid: 用户openid
                total_amount: 付款金额
                wishing: 红包祝福语
                client_ip: 调用接口的机器Ip地址, 注：此地址为服务器地址
                act_name: 活动名称 
                remark: 备注 
            :return: 红包发放结果 异步Future
        """
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack"
        self.ChkNeedParamsError(['send_name', 're_openid', 'total_amount',
                                 'wishing', 'client_ip', 'act_name', 'raise'], data, u'向用户发送红包接口中，')
        data.setdefault("wxappid", self.WX_APP_ID)
        data.setdefault('mch_id', self.WX_MCH_ID)
        data.setdefault('nonce_str', self.NonceStr())
        data.setdefault('mch_billno', u'{0}{1}{2}'.format(self.WX_MCH_ID, time.strftime(
            '%Y%m%d', time.localtime(time.time())), self.random_num(10)))
        data.setdefault('total_num', 1)
        data.setdefault('scene_id', 'PRODUCT_4')
        data.setdefault('sign', self.sign(data))
        return self.fetch_with_ssl(url, data, api_cert_path, api_key_path)

    # 企业对个人付款
    def enterprisePayment(self, api_cert_path, api_key_path, **data):
        """
            使用企业对个人付款功能

            详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/tools/mch_pay.php?chapter=14_2
            :param api_cert_path: 微信支付商户证书路径，此证书(apiclient_cert.pem)需要先到微信支付商户平台获取，下载后保存至服务器
            :param api_key_path: 微信支付商户证书路径，此证书(apiclient_key.pem)需要先到微信支付商户平台获取，下载后保存至服务器
            :param data: openid, check_name, re_user_name, amount, desc, spbill_create_ip,partner_trade_no
                openid: 用户openid
                check_name: 是否校验用户姓名
                re_user_name: 如果 check_name 为True，则填写，否则不带此参数
                amount: 金额: 企业付款金额，单位为分
                desc: 企业付款描述信息
                spbill_create_ip: 调用接口的机器Ip地址, 注：该IP可传用户端或者服务端的IP,
                partner_trade_no:商户订单号,如果不传自动生成
            :return: 企业转账结果 异步Future
        """
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers"
        self.ChkNeedParamsError(
            ['openid', 'check_name', 'amount', 'desc', 'spbill_create_ip'], data, u'企业付款申请接口中，')
        data.setdefault("mch_appid", self.WX_APP_ID)
        data.setdefault("mchid", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.NonceStr())
        data.setdefault("partner_trade_no", u'{0}{1}{2}'.format(
            self.WX_MCH_ID, time.strftime(
                '%Y%m%d', time.localtime(time.time())), self.random_num(10)
        ))
        data['check_name'] = 'FORCE_CHECK' if data['check_name'] else 'NO_CHECK'
        data.setdefault("sign", self.sign(data))
        return self.fetch_with_ssl(url, data, api_cert_path, api_key_path)

    # 提交刷卡支付
    def swiping_card_payment(self, **data):
        """
            提交刷卡支付

            详细参考 https://pay.weixin.qq.com/wiki/doc/api/micropay.php?chapter=9_10&index=1
            :param data: body, out_trade_no, total_fee, auth_code, (可选参数 device_info, detail, goods_tag, limit_pay)
                body: 商品描述
                *out_trade_no: 商户订单号
                total_fee: 标价金额, 整数, 单位 分
                auth_code: 微信支付二维码扫描结果
                *device_info: 终端设备号(商户自定义，如门店编号)
                spbill_create_ip 用户ip地址
            :return: 统一下单生成结果 异步Future
        """
        url = "https://api.mch.weixin.qq.com/pay/micropay"
        if "out_trade_no" not in data:
            data.setdefault("out_trade_no", self.NonceStr())
        self.ChkNeedParamsError(
            ['body', 'total_fee', 'spbill_create_ip'], data, u'刷卡支付接口中，')
        data.setdefault("appid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.NonceStr())
        data.setdefault("spbill_create_ip", data.get('spbill_create_ip'))
        data.setdefault("sign", self.sign(data))
        return self.fetch(url, data)
