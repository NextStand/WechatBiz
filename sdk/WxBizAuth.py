# coding:utf-8
""" 
企业微信身份验证模块
"""
__author__ = 'BLUE'
__time__ = 'Thu May 16 2019 14:13:17 GMT+0800'
# ------------------------------------------------------------------------
from WechatBiz.core.WechatBase import WechatBase


class WxBizAuth(WechatBase):
    """ 企业微信身份验证 """
    def __init__(self):
        token, expires_at = self.initToken()
        super(WxBizAuth, self).__init__(
            access_token=token, access_token_expires_at=expires_at)

    def GetUserInfo(self, code):
        """ 
            获取用户基本信息 

            :param code: 前端授权码
            :详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91023
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo',
            data=dict(code=code)
        )
