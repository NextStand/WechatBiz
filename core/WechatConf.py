# coding:utf-8
""" 
微信参数配置类 
该类将会存储所有和微信开发相关的配置信息, 同时也会维护配置信息的有效性.
"""
__author__ = 'BLUE'
__time__ = 'Sun Oct 28 2018 21:27:18 GMT+0800'
# ------------------------------------------------------------------------
import time
from .Exceptions import NeedParamError, ParamTimeout


class WechatConf(object):

    def __init__(self, **kwargs):
        """ 
        :param kwargs: 配置信息字典, 可用字典 key 值及对应解释如下: 
            'token': 微信 Token
            'appid': App ID
            'appsecret': App Secret
            'encrypt_mode': 加解密模式 ('normal': 明文模式, 'compatible': 兼容模式, 'safe': 安全模式(默认))
            'access_token': 直接导入的 access token 值, 该值需要在上一次该类实例化之后手动进行缓存并在此处传入, 如果不
                                       传入, 将会在需要时自动重新获取 (传入 access_token_getfunc 和 access_token_setfunc 函数
                                       后将会自动忽略此处的传入值)
            'access_token_expires_at': 直接导入的 access token 的过期日期, 该值需要在上一次该类实例化之后手动进行缓存
                                                  并在此处传入, 如果不传入, 将会在需要时自动重新获取 (传入 access_token_getfunc
                                                  和 access_token_setfunc 函数后将会自动忽略此处的传入值)
            
        """

        """ if kwargs.get('checkssl') is not True:
            disable_urllib3_warning()  # 可解决 InsecurePlatformWarning 警告 """

        self.__token = kwargs.get("token")
        self.__appid = kwargs.get('appid')
        self.__appsecret = kwargs.get('appsecret')
        self.__encrypt_mode = kwargs.get('encrypt_mode', 'safe')
        self.__access_token = kwargs.get('access_token')
        self.__access_token_expires_at = kwargs.get('access_token_expires_at')

    @property
    def token(self):
        """ 获取当前token """
        self._check_token()
        return self.__token

    @token.setter
    def token(self, token):
        """ 设置当前 Token """
        self.__token = token

    @property
    def appid(self):
        """ 获取当前 App ID """
        return self.__appid

    @property
    def appsecret(self):
        """ 获取当前 App Secret """
        return self.__appsecret

    def set_appid_appsecret(self, appid, appsecret):
        """ 设置当前 App ID 及 App Secret"""
        self.__appid = appid
        self.__appsecret = appsecret

    @property
    def encoding_aes_key(self):
        """ 获取当前 EncodingAESKey """
        return self.__encoding_aes_key

    @encoding_aes_key.setter
    def encoding_aes_key(self, encoding_aes_key):
        """ 设置当前 EncodingAESKey """
        self.__encoding_aes_key = encoding_aes_key

    @property
    def encrypt_mode(self):
        """ 获取当前加密模式 """
        return self.__encrypt_mode

    @encrypt_mode.setter
    def encrypt_mode(self, encrypt_mode):
        """ 设置当前加密模式 """
        self.__encrypt_mode = encrypt_mode

    @property
    def access_token(self):
        """ 获取当前 access token 值, 本方法不会自行维护 access token 有效性 """
        if self.__access_token:
            now = int(time.time())
            if self.__access_token_expires_at > now:
                return self.__access_token
            else:
                raise ParamTimeout('Access_token timeout')

    def _check_token(self):
        """
        检查 Token 是否存在

        :raises NeedParamError: Token 参数没有在初始化的时候提供
        """
        if not self.__token:
            raise NeedParamError(
                'Please provide Token parameter in the construction of class.')


