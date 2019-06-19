# coding:utf-8
""" 
企业微信外部联系人模块
"""
__author__ = 'BLUE'
__time__ = 'Thu May 16 2019 17:23:11 GMT+0800'
# ------------------------------------------------------------------------
import time
from WechatBiz.core.WechatBase import WechatBase
from WechatBiz.core.WxToken import AccessToken
from WechatBiz.wxconfig import WECHAT_CRM_SECRET
from WechatBiz.core.Exceptions import NeedParamError
from WechatBiz.sdk.WxBizMsg import WxBizMsg


class WxBizCrm(WxBizMsg, WechatBase):
    """ 
        企业微信外部联系人类 
        继承于企业微信消息类，用于解析回调事件消息
    """

    def __init__(self):
        token, expires_at = self.initToken()
        if token and expires_at > time.time():
            super(WxBizCrm, self).__init__(
                access_token=token, access_token_expires_at=expires_at)
        else:
            raise NeedParamError(message=u'access_token不存在或已过期')

    def initToken(self):
        """ 重写获取token方法 """
        access = AccessToken.get_access_token(
            'wx_crm_token', WECHAT_CRM_SECRET)
        return access.get('access_token'), access.get('expires_at')

    # 获取配置了客户联系功能的成员列表
    def GetCrmUsers(self):
        """
            获取配置了客户联系功能的成员列表

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91554
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get('https://qyapi.weixin.qq.com/cgi-bin/crm/get_customer_contacts', data={})

    # 获取外部联系人列表
    def GetExternalList(self, userid):
        """
            获取外部联系人列表

            :param userid: 企业成员的userid
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91555
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get('https://qyapi.weixin.qq.com/cgi-bin/crm/get_external_contact_list', data=dict(userid=userid))

    # 获取外部联系人详情
    def GetExternalInfo(self, external_userid):
        """
            获取外部联系人详情

            :param external_userid: 外部联系人的userid，注意不是企业成员的帐号
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91556
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get('https://qyapi.weixin.qq.com/cgi-bin/crm/get_external_contact', data=dict(external_userid=external_userid))

    # 配置客户联系[联系我]
    def AddContactWay(self, data):
        """
            配置客户联系[联系我]

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91558
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['type', 'scene'], data, u'配置客户联系[联系我]接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/add_contact_way',
            data=data
        )

    # 获取企业已配置的「联系我」方式
    def GetContactWay(self, config_id):
        """
            获取企业已配置的「联系我」方式

            :param config_id: 联系方式的配置id
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91558
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/get_contact_way',
            data=dict(config_id=config_id)
        )

    # 更新企业已配置的「联系我」方式
    def UpdateContactWay(self, data):
        """
            更新企业已配置的「联系我」方式

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91558
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['config_id'], data, u'更新企业已配置的「联系我」方式接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/update_contact_way',
            data=data
        )

    # 删除企业已配置的「联系我」方式
    def DelContactWay(self, config_id):
        """
            删除企业已配置的「联系我」方式

            :param config_id: 联系方式的配置id
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91558
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/del_contact_way',
            data=dict(config_id=config_id)
        )

    # 添加企业群发消息模板
    def AddMsgTemplate(self, data):
        """
            添加企业群发消息模板

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91560
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/add_msg_template',
            data=data
        )

    # 获取企业群发消息发送结果
    def GetGroupMsgResult(self, msgid):
        """
            获取企业群发消息发送结果

            :param msgid: 群发消息的id
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91561
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/get_group_msg_result',
            data=dict(msgid=msgid)
        )

    # 获取员工行为数据
    def GetUserBehavior(self, userid, start_time, end_time):
        """
            获取员工行为数据

            :param userid: userid列表List
            :param start_time: 开始时间戳
            :param end_time: 结束时间戳
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91580
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/get_user_behavior_data',
            data=dict(userid=userid, start_time=start_time, end_time=end_time)
        )

    # 获取离职人员的客户列表
    def GetUnsignGuest(self,page_id=0,page_size=1000):
        """
            获取离职人员的客户列表

            :param page_id: 分页查询，要查询页号，从0开始
            :param page_size: 每次返回的最大记录数，默认为1000，最大值为1000
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91563
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/get_unassigned_customers',
            data=dict(page_id=page_id, page_size=page_size)
        )

    # 离职成员的外部联系人再分配
    def TransferUnsignGuest(self,external_userid,handover_userid,takeover_userid):
        """
            离职成员的外部联系人再分配

            :param external_userid: 外部联系人的userid，注意不是企业成员的帐号
            :param handover_userid: 离职成员的userid
            :param takeover_userid: 接替成员的userid
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/91564
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/crm/transfer_external_contact',
            data=dict(external_userid=external_userid, handover_userid=handover_userid,takeover_userid=takeover_userid)
        )