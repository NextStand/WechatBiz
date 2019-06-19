# coding:utf-8
""" 
所有功能模块的基类，包含一些工具、请求对象、配置对象
主要放置一些基类
"""
__author__ = 'BLUE'
__time__ = 'Sun Oct 28 2018 21:14:44 GMT+0800'
# ------------------------------------------------------------------------
import time
import string
import random
from .WechatConf import WechatConf
from .WechatRequest import WechatRequest
from WechatBiz.core.WxToken import AccessToken
from WechatBiz.core.Exceptions import NeedParamError
from WechatBiz.wxconfig import WECHAT_CORP_SECRET


class WechatBase(object):
    def __init__(self, token=None, appid=None, appsecret=None, paysignkey=None, access_token=None, access_token_expires_at=None):
        """
        :param token: 微信加密自定义token
        :param appid: 微信公众号appid
        :param appsecret:App Secret
        :param paysignkey: 商户签名密钥 Key, 支付权限专用
        :param access_token: 直接导入的 access_token 值, 该值需要在上一次该类实例化之后手动进行缓存并在此处传入, 如果不传入, 将会在需要时自动重新获取
        :param access_token_expires_at: 直接导入的 access_token 的过期日期，该值需要在上一次该类实例化之后手动进行缓存并在此处传入, 如果不传入, 将会在需要时自动重新获取
        """
        self.__conf = WechatConf(
            token=token,
            appid=appid,
            appsecret=appsecret,
            access_token=access_token,
            access_token_expires_at=access_token_expires_at,
            encrypt_mode='normal')
        self.__request = WechatRequest(conf=self.__conf)

    @property
    def conf(self):
        """ 获取当前 WechatConf 配置实例 """
        return self.__conf

    @conf.setter
    def conf(self, conf):
        """ 设置当前 WechatConf 实例  """
        self.__conf = conf
        self.__request = WechatRequest(conf=self.__conf)

    @property
    def request(self):
        """ 获取当前 WechatRequest 配置实例 """
        return self.__request

    @request.setter
    def request(self, request):
        """ 设置当前 WechatRequest 实例  """
        self.__request = request

    @property
    def access_token(self):
        return self.conf.access_token

    def initToken(self):
        """ 获取access_token接口 """
        access = AccessToken.get_access_token(
            'wx_core_token', WECHAT_CORP_SECRET)
        access_token = access.get('access_token')
        access_token_expires_at = access.get('expires_at')
        if access_token and access_token_expires_at > time.time():
            return access_token, access_token_expires_at
        else:
            raise NeedParamError(message=u'access_token不存在或已过期')

    def ChkNeedParamsError(self, needpara, params, tips=''):
        """ 检测必填参数是否够 """
        paramsSet = set(params.keys())
        needSet = set(needpara)
        commonSet = needSet & paramsSet
        if len(commonSet) != len(needSet):
            # 如果需要参数和实际参数的交集不等于需要参数的长度，说明有比选参数没有传
            diffSet = needSet - commonSet
            tips += u'缺少必填参数%s' % str(list(diffSet)[0])
            raise NeedParamError(tips)

    def NonceStr(self, length=32):
        """ 生成随机32位字符串，用于签名 """
        char = string.ascii_letters+string.digits
        return "".join(random.choice(char) for _ in range(length))

    @classmethod
    def _transcoding(cls, data):
        """编码转换 for str
        :param data: 需要转换的数据
        :return: 转换好的数据
        """
        result = None
        if not data:
            return result
        if isinstance(data, str) and hasattr(data, 'decode'):
            result = data.decode('utf-8')
        else:
            result = data
        return result

    @classmethod
    def _transcoding_list(cls, data):
        """编码转换 for list
        :param data: 需要转换的 list 数据
        :return: 转换好的 list
        """
        if not isinstance(data, list):
            raise ValueError('Parameter data must be list object.')
        result = []
        for item in data:
            if isinstance(item, dict):
                result.append(cls._transcoding_dict(item))
            elif isinstance(item, list):
                result.append(cls._transcoding_list(item))
            elif isinstance(item, str):
                result.append(cls._transcoding(item))
            else:
                result.append(item)
        return result

    @classmethod
    def _transcoding_dict(cls, data):
        """
        编码转换 for dict
        :param data: 需要转换的 dict 数据
        :return: 转换好的 dict
        """
        if not isinstance(data, dict):
            raise ValueError('Parameter data must be dict object.')
        result = {}
        for k, v in data.items():
            k = cls._transcoding(k)
            if isinstance(v, dict):
                v = cls._transcoding_dict(v)
            elif isinstance(v, list):
                v = cls._transcoding_list(v)
            elif isinstance(v, str):
                v = cls._transcoding(v)
            result.update({k: v})
        return result



class WxBizMsgTypeBase(object):
    """ 基本消息类型基类 """

    def __init__(self, message):
        self.MsgId = int(message.pop('MsgId', 0))
        self.ToUserName = message.pop('ToUserName', None)
        self.FromUserName = message.pop('FromUserName', None)
        self.CreateTime = int(message.pop('CreateTime', 0))
        self.AgentID = int(message.pop('AgentID', 0))
        self.__dict__.update(message)


class WxBizCrmEventBase(object):
    """ 外部联系人变更事件消息基类 """

    def __init__(self, message):
        self.ToUserName = message.pop('ToUserName', None)
        self.FromUserName = message.pop('FromUserName', None)
        self.CreateTime = int(message.pop('CreateTime', 0))
        self.ExternalUserID = message.pop('ExternalUserID', None)
        self.UserID = message.pop('UserID', None)
        self.__dict__.update(message)


class WxBizContactUserBase(WxBizMsgTypeBase):
    """ 通讯录成员变更事件基类 """

    def __init__(self, message):
        self.UserID = message.pop('UserID', None)
        self.Name = message.pop('Name', None)
        self.Department = message.pop('Department', None)
        self.IsLeaderInDept = message.pop('IsLeaderInDept', None)
        self.Position = message.pop('Position', None)
        self.Mobile = message.pop('Mobile', None)
        self.Gender = message.pop('Gender', None)
        self.Email = message.pop('Email', None)
        self.Status = message.pop('Status', None)
        self.Avatar = message.pop('Avatar', None)
        self.Alias = message.pop('Alias', None)
        self.Telephone = message.pop('Telephone', None)
        self.Address = message.pop('Address', None)
        self.ExtAttr = message.pop('ExtAttr', None)
        super(WxBizContactUserBase, self).__init__(message)
        self.__dict__.update(message)


class WxBizContactPartyBase(WxBizMsgTypeBase):
    """ 部门变更事件基类 """

    def __init__(self, message):
        self.Id = message.pop('Id', None)
        self.Name = message.pop('Name', None)
        self.ParentId = message.pop('ParentId', None)
        super(WxBizContactPartyBase, self).__init__(message)
        self.__dict__.update(message)


class WxBizPicEventBase(WxBizMsgTypeBase):
    """ 相册相关事件基类 """
    def __init__(self, message):
        self.EventKey = message.pop('EventKey')
        self.SendPicsInfo = message.pop('SendPicsInfo')
        self.Count = self.SendPicsInfo[0].get('Count')
        self.PicList = self.SendPicsInfo[0].get(
            'PicList', [{}])[0].get('item', [])
        super(WxBizPicEventBase, self).__init__(message)
        self.__dict__.update(message)

class WxBizReply(object):
    """ 被动回复消息基类 """

    def __init__(self, message=None, **kwargs):
        if 'FromUserName' not in kwargs and isinstance(message, WxBizMsgTypeBase):
            kwargs['FromUserName'] = message.ToUserName
        if 'ToUserName' not in kwargs and isinstance(message, WxBizMsgTypeBase):
            kwargs['ToUserName'] = message.FromUserName
        if 'CreateTime' not in kwargs:
            kwargs['CreateTime'] = int(time.time())
        self._args = dict()
        for k, v in kwargs.items():
            self._args[k] = v

    def render(self):
        raise NotImplementedError()