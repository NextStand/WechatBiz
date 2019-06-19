# coding:utf-8
""" 
企业微信消通讯录相关模块
"""
__author__ = 'BLUE'
__time__ = 'Wed May 9 2019 9:06:50 GMT+0800'
# ------------------------------------------------------------------------

import time
from WechatBiz.core.WechatBase import WechatBase
from WechatBiz.core.WxToken import AccessToken
from WechatBiz.core.Exceptions import ParseError, NeedParseError, OfficialAPIError, NeedParamError
from WechatBiz.wxconfig import WECHAT_ADDR_SECRET


class AddrBook(WechatBase):
    """ 通讯录管理 """

    def __init__(self):
        token, expires_at = self.initToken()
        if token and expires_at > time.time():
            super(AddrBook, self).__init__(
                access_token=token, access_token_expires_at=expires_at)
        else:
            raise NeedParamError(message=u'access_token不存在或已过期')

    def initToken(self):
        """ 重写获取token方法 """
        access = AccessToken.get_access_token(
            'wx_addr_token', WECHAT_ADDR_SECRET)
        return access.get('access_token'), access.get('expires_at')

    # 创建部门
    def CreateDepartment(self, data):
        """
            创建部门
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90204
            :param data: 部门数据 (dict形式)，见参考文档
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/department/create',
            data=data
        )

    # 更新部门
    def UpdateDepartment(self, data):
        """
            更新部门
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90206
            :param data: 部门数据 (dict形式)，见参考文档
            :return: 携带JSON数据包的异步Future
        """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/department/update',
            data=data
        )

    # 删除部门
    def DeleteDepartment(self, id):
        """
            删除部门
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90207
            :param id1: 部门id。（注：不能删除根部门；不能删除含有子部门、成员的部门）
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/department/delete',
            data=dict(id=id)
        )

    # 获取部门列表
    def ListDepartment(self, id=None):
        """
            获取部门列表
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90208
            :param id: 部门id。
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/department/list',
            data=dict(id=id)
        )

    # 创建成员
    def CreateUser(self, data):
        """
            创建成员
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90195
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['userid', 'name', 'department'], data, u'创建成员接口中，')
        if 'mobile' in data or 'email' in data:
            return self.request.post(
                url='https://qyapi.weixin.qq.com/cgi-bin/user/create',
                data=data
            )
        else:
            raise NeedParamError(u'mobile/email二者不能同时为空')

    # 读取成员
    def GetUser(self, userid):
        """
            读取成员
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90196
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/get',
            data=dict(userid=userid)
        )

    # 更新成员
    def UpdateUser(self, data):
        """
            更新成员
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90197
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['userid'], data, u'更新成员接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/user/update',
            data=data
        )

    # 删除成员
    def DeleteUser(self, userid):
        """
            删除成员
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90198
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/delete',
            data=dict(userid=userid)
        )

    # 批量删除成员
    def BatchdeleteUser(self, data):
        """
            批量删除成员,限制200个
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90199
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['useridlist'], data, u'批量删除成员接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/user/batchdelete',
            data=data
        )

    # 获取部门成员简单信息
    def SimplelistUser(self, department_id, fetch_child=0):
        """
            获取部门成员简单信息
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90200
            :department_id: 部门id
            :fetch_child: 是否递归获取子部门成员
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/simplelist',
            data=dict(department_id=department_id, fetch_child=fetch_child)
        )

    # 获取部门成员详细信息
    def ListUser(self, department_id, fetch_child=0):
        """
            获取部门成员详细信息
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90201
            :department_id: 部门id
            :fetch_child: 是否递归获取子部门成员
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/list',
            data=dict(department_id=department_id, fetch_child=fetch_child)
        )

    # userid转openid
    def Userid2Openid(self, userid):
        """
            userid转openid
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90202
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_openid',
            data=dict(userid=userid)
        )

    # openid转userid
    def Openid2Userid(self, openid):
        """
            openid转userid
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90202
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_userid',
            data=dict(openid=openid)
        )

    # code换取userid后二次验证
    def AuthsuccUser(self, userid):
        """
            code换取userid后二次验证
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90203
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/authsucc',
            data=dict(userid=userid)
        )

    # 邀请成员使用企业微信
    def InviteBatch(self, data):
        """
            邀请成员使用企业微信
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90975
            :return: 携带JSON数据包的异步Future
        """
        if 'user' in data or 'party' in data or 'tag' in data:
            return self.request.post(
                url='https://qyapi.weixin.qq.com/cgi-bin/batch/invite',
                data=data
            )
        else:
            raise NeedParamError(u'user/party/tag二者不能同时为空')

    # 创建标签
    def CreateTag(self, data):
        """
            创建标签

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90209
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['tagname'], data, u'创建标签接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/tag/create',
            data=data
        )

    # 更新标签名称
    def UpdateTag(self, data):
        """
            更新标签名字
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90211
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['tagname', 'tagid'], data, u'更新标签名字接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/tag/update',
            data=data
        )

    # 删除标签
    def DeleteTag(self, tagid):
        """
            删除标签
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90212
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/tag/delete',
            data=dict(tagid=tagid)
        )

    # 增加标签成员
    def AddTagUsers(self, data):
        """
            增加标签成员
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90209
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['tagid'], data, u'增加标签成员中，')
        if 'userlist' in data or 'partylist' in data:
            return self.request.post(
                url='https://qyapi.weixin.qq.com/cgi-bin/tag/addtagusers',
                data=data
            )
        else:
            raise NeedParamError(u'userlist/partylist二者不能同时为空')

    # 获取标签成员
    def GetTagUsers(self, tagid):
        """
            获取标签成员
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90213
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/tag/get',
            data=dict(tagid=tagid)
        )

    # 删除标签成员
    def DelTagUsers(self, data):
        """
            删除标签成员
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90215
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['tagid'], data, u'删除标签成员中，')
        if 'userlist' in data or 'partylist' in data:
            return self.request.post(
                url='https://qyapi.weixin.qq.com/cgi-bin/tag/deltagusers',
                data=data
            )
        else:
            raise NeedParamError(u'userlist/partylist二者不能同时为空')

    # 获取标签列表
    def ListTag(self):
        """
            获取标签列表

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90216
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get('https://qyapi.weixin.qq.com/cgi-bin/tag/list', data={})
