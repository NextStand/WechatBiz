# coding:utf-8
""" 
企业微信开发包
    |- WechatPay     微信支付
    |- AddrBook      通讯录管理
    |- WxBizAgent    应用管理
    |- WxBizAuth     身份验证
    |- WxBizJsSdk    JS-SDK服务
    |- WxBizCrm      外部关系
    |- WxBizMedia    素材管理
    |- WxBizMsg      收到消息解析、发送消息、被动回复消息 
    |- WxBizConver   会话消息
"""
__author__ = 'BLUE'
__time__ = 'Wed May 22 2019 11:59:11 GMT+0800'
# ------------------------------------------------------------------------
from .sdk.WechatPay import WechatPay
from .sdk.WxBizAddrBook import AddrBook
from .sdk.WxBizAgent import WxBizAgent
from .sdk.WxBizAuth import WxBizAuth
from .sdk.WxBizClient import WxBizJsSdk
from .sdk.WxBizCrm import WxBizCrm
from .sdk.WxBizMedia import WxBizMedia
from .sdk.WxBizMsg import WxBizMsg, WxBizConver
