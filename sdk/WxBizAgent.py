# coding:utf-8
""" 
企业微信应用管理模块
"""
__author__ = 'BLUE'
__time__ = 'Tue May 21 2019 10:43:40 GMT+0800'
# ------------------------------------------------------------------------
from WechatBiz.core.WechatBase import WechatBase
from WechatBiz.wxconfig import WECHAR_AGENT_ID


class WxBizAgent(WechatBase):
    """ 企业微信应用管理 """
    def __init__(self):
        token, expires_at = self.initToken()
        super(WxBizAgent, self).__init__(
            access_token=token, access_token_expires_at=expires_at)

    # 获取指定的应用详情
    def GetAgentInfo(self, agentid):
        """ 
            获取指定的应用详情 

            :param agentid: 应用id
            :详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90227
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/agent/get',
            data=dict(agentid=agentid)
        )

    # 获取access_token对应的应用列表
    def GetAgentList(self):
        """ 
            获取access_token对应的应用列表 

            :详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90227
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/agent/list',
            data={}
        )

    # 设置应用基础信息
    def SetAgentInfo(self, data):
        """
            设置应用基础信息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90228
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['agentid'], data, u'设置应用基础信息接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/agent/set',
            data=data
        )

    # 创建自定义菜单
    def CreateMenu(self, data):
        """
            创建自定义菜单

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90231
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/menu/create?access_token=%s&agentid=%s' % (
                self.access_token, WECHAR_AGENT_ID),
            data=data
        )

    # 获取菜单
    def GetMenu(self):
        """ 
            获取菜单 

            :详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90232
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/menu/get',
            data=dict(access_token=self.access_token, agentid=WECHAR_AGENT_ID)
        )

    # 删除菜单
    def DeleteMenu(self):
        """ 
            获取菜单 

            :详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90232
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/menu/delete',
            data=dict(access_token=self.access_token, agentid=WECHAR_AGENT_ID)
        )
