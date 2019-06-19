# coding:utf-8
""" 
微信消息模板
"""
__author__ = 'BLUE'
__time__ = 'Wed May 22 2019 11:14:55 GMT+0800'
# ------------------------------------------------------------------------
from .Exceptions import ParseError
from .WechatBase import WxBizMsgTypeBase, WxBizCrmEventBase, WxBizContactUserBase, WxBizContactPartyBase, WxBizPicEventBase

MESSAGE_TYPES = {}


def handle_for_type(type):
    def register(f):
        MESSAGE_TYPES[type] = f
        return f
    return register


@handle_for_type('text')
class TextMessage(WxBizMsgTypeBase):
    """ 文本消息 """

    def __init__(self, message):
        self.Content = message.pop('Content', '')
        super(TextMessage, self).__init__(message)


@handle_for_type('image')
class ImageMessage(WxBizMsgTypeBase):
    """ 图片消息 """

    def __init__(self, message):
        try:
            self.PicUrl = message.pop('PicUrl')
            self.MediaId = message.pop('MediaId')
        except KeyError:
            raise ParseError()
        super(ImageMessage, self).__init__(message)


@handle_for_type('voice')
class VoiceMessage(WxBizMsgTypeBase):
    """ 语音消息 """

    def __init__(self, message):
        try:
            self.MediaId = message.pop('MediaId')
        except KeyError:
            raise ParseError()
        super(VoiceMessage, self).__init__(message)


@handle_for_type('video')
class VideoMessage(WxBizMsgTypeBase):
    """ 视频消息 """

    def __init__(self, message):
        try:
            self.MediaId = message.pop('MediaId')
            self.ThumbMediaId = message.pop('ThumbMediaId')
        except KeyError:
            raise ParseError()
        super(VideoMessage, self).__init__(message)


@handle_for_type('location')
class LocationMessage(WxBizMsgTypeBase):
    """ 位置消息 """

    def __init__(self, message):
        try:
            Location_X = message.pop('Location_X')
            Location_Y = message.pop('Location_Y')
            self.location = (float(Location_X), float(Location_Y))
            self.Scale = int(message.pop('Scale'))
            self.Label = message.pop('Label')
        except KeyError:
            raise ParseError()
        super(LocationMessage, self).__init__(message)


@handle_for_type('link')
class LinkMessage(WxBizMsgTypeBase):
    """ 链接消息 """

    def __init__(self, message):
        try:
            self.Title = message.pop('Title')
            self.Description = message.pop('Description')
            self.PicUrl = message.pop('PicUrl')
        except KeyError:
            raise ParseError()
        super(LinkMessage, self).__init__(message)


@handle_for_type('subscribe')
class SubscribeEvent(WxBizMsgTypeBase):
    """ 关注事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
        except KeyError:
            raise ParseError(u'关注事件消息解析失败')
        super(SubscribeEvent, self).__init__(message)


@handle_for_type('unsubscribe')
class UnSubscribeEvent(WxBizMsgTypeBase):
    """ 取消关注事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
        except KeyError:
            raise ParseError(u'取消关注事件消息解析失败')
        super(UnSubscribeEvent, self).__init__(message)


@handle_for_type('location')
class LocationEvent(WxBizMsgTypeBase):
    """ 上报地理位置事件 """

    def __init__(self, message):
        try:
            self.Location_Y = float(message.pop('Location_Y'))
            self.Location_X = float(message.pop('Location_X'))
            self.Label = message.pop('Label')
            self.Scale = int(message.pop('Scale'))
        except KeyError:
            raise ParseError(u'上报地理位置事件消息解析失败')
        super(LocationEvent, self).__init__(message)


@handle_for_type('batch_job_result')
class BatchJobEvent(WxBizMsgTypeBase):
    """ 异步任务完成推送事件 """

    def __init__(self, message):
        try:
            self.JobId = message.pop('JobId')
            self.JobType = message.pop('JobType')
            self.ErrCode = message.pop('ErrCode')
            self.ErrMsg = message.pop('ErrMsg')
        except KeyError:
            raise ParseError(u'异步任务完成推送事件消息解析失败')
        super(BatchJobEvent, self).__init__(message)


@handle_for_type('create_user')
class CreateUserEvent(WxBizContactUserBase):
    """ 新增成员事件 """

    def __init__(self, message):
        try:
            super(CreateUserEvent, self).__init__(message)
        except KeyError:
            raise ParseError(u'新增成员事件消息解析失败')


@handle_for_type('update_user')
class UpdateUserEvent(WxBizContactUserBase):
    """ 更新成员事件 """

    def __init__(self, message):
        try:
            self.NewUserID = message.pop('NewUserID')
        except KeyError:
            raise ParseError(u'更新成员事件消息解析失败')
        super(UpdateUserEvent, self).__init__(message)


@handle_for_type('delete_user')
class DeleteUserEvent(WxBizMsgTypeBase):
    """ 删除成员事件 """

    def __init__(self, message):
        try:
            self.UserID = message.pop('UserID', None)
        except KeyError:
            raise ParseError(u'删除成员事件消息解析失败')
        super(DeleteUserEvent, self).__init__(message)


@handle_for_type('create_party')
class CreatePartyEvent(WxBizContactPartyBase):
    """ 新增部门事件 """

    def __init__(self, message):
        try:
            self.Order = message.pop('Order')
        except KeyError:
            raise ParseError(u'新增部门事件消息解析失败')
        super(CreatePartyEvent, self).__init__(message)


@handle_for_type('update_party')
class UpdatePartyEvent(WxBizContactPartyBase):
    """ 更新部门事件 """

    def __init__(self, message):
        try:
            super(UpdatePartyEvent, self).__init__(message)
        except KeyError:
            raise ParseError(u'更新部门事件消息解析失败')


@handle_for_type('delete_party')
class DeletePartyEvent(WxBizMsgTypeBase):
    """ 删除部门事件 """

    def __init__(self, message):
        try:
            self.Id = message.pop('Id')
        except KeyError:
            raise ParseError(u'删除部门事件消息解析失败')
        super(DeletePartyEvent, self).__init__(message)


@handle_for_type('update_tag')
class UpdateTagEvent(WxBizMsgTypeBase):
    """ 标签成员变更事件 """

    def __init__(self, message):
        try:
            self.TagId = message.pop('TagId')
            self.AddUserItems = message.pop('AddUserItems')
            self.DelUserItems = message.pop('DelUserItems')
            self.AddPartyItems = message.pop('AddPartyItems')
            self.DelPartyItems = message.pop('DelPartyItems')
        except KeyError:
            raise ParseError(u'标签成员变更事件消息解析失败')
        super(UpdateTagEvent, self).__init__(message)


@handle_for_type('click')
class ClickEvent(WxBizMsgTypeBase):
    """ 点击菜单拉取消息事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
        except KeyError:
            raise ParseError(u'点击菜单拉取消息事件消息解析失败')
        super(ClickEvent, self).__init__(message)


@handle_for_type('view')
class ViewEvent(WxBizMsgTypeBase):
    """ 点击菜单跳转链接事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
        except KeyError:
            raise ParseError(u'点击菜单跳转链接事件消息解析失败')
        super(ViewEvent, self).__init__(message)


@handle_for_type('scancode_push')
class ScancodePushEvent(WxBizMsgTypeBase):
    """ 点击菜单扫码推事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
            self.ScanCodeInfo = message.pop('ScanCodeInfo')
            self.ScanType = self.ScanCodeInfo[0].get('ScanType')
            self.ScanResult = self.ScanCodeInfo[0].get('ScanResult')
        except KeyError:
            raise ParseError(u'扫码推事件消息解析失败')
        super(ScancodePushEvent, self).__init__(message)


@handle_for_type('scancode_waitmsg')
class ScancodeWaitEvent(WxBizMsgTypeBase):
    """ 点击菜单扫码推事件且弹出“消息接收中”提示框事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
            self.ScanCodeInfo = message.pop('ScanCodeInfo')
            self.ScanType = self.ScanCodeInfo[0].get('ScanType')
            self.ScanResult = self.ScanCodeInfo[0].get('ScanResult')
        except KeyError:
            raise ParseError(u'扫码推事件且弹出“消息接收中”提示框事件消息解析失败')
        super(ScancodeWaitEvent, self).__init__(message)


@handle_for_type('pic_sysphoto')
class PicSysPhotoEvent(WxBizPicEventBase):
    """ 点击菜单弹出系统拍照发图事件 """

    def __init__(self, message):
        try:
            super(PicSysPhotoEvent, self).__init__(message)
        except KeyError:
            raise ParseError(u'弹出系统拍照发图事件消息解析失败')


@handle_for_type('pic_photo_or_album')
class PicPhotoOrAlbumEvent(WxBizPicEventBase):
    """ 点击菜单弹出拍照或者相册发图事件 """

    def __init__(self, message):
        print(123)
        try:
            super(PicPhotoOrAlbumEvent, self).__init__(message)
        except KeyError:
            raise ParseError(u'弹出拍照或者相册发图事件消息解析失败')


@handle_for_type('pic_weixin')
class PicWeixinEvent(WxBizPicEventBase):
    """ 点击菜单弹出微信相册发图器事件 """

    def __init__(self, message):
        print('*'*30)
        try:
            super(PicWeixinEvent, self).__init__(message)
        except KeyError:
            raise ParseError(u'弹出拍照或者相册发图事件消息解析失败')


@handle_for_type('location_select')
class LocalSelectEvent(WxBizMsgTypeBase):
    """ 点击菜单弹出地理位置选择器事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
            self.SendLocationInfo = message.pop('SendLocationInfo')
            self.Location_X = self.SendLocationInfo[0].get('Location_X')
            self.Location_Y = self.SendLocationInfo[0].get('Location_Y')
            self.Scale = self.SendLocationInfo[0].get('Scale')
            self.Label = self.SendLocationInfo[0].get('Label')
            self.Poiname = self.SendLocationInfo[0].get('Poiname')
        except KeyError:
            raise ParseError(u'弹出地理位置选择器事件消息解析失败')
        super(LocalSelectEvent, self).__init__(message)


@handle_for_type('open_approval_change')
class ProvalChangeEvent(WxBizMsgTypeBase):
    """ 审核状态通知事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
            self.ApprovalInfo = message.pop('ApprovalInfo')
        except KeyError:
            raise ParseError(u'审核状态通知事件消息解析失败')
        super(ProvalChangeEvent, self).__init__(message)


@handle_for_type('taskcard_click')
class TaskCardEvent(WxBizMsgTypeBase):
    """ 任务卡片事件 """

    def __init__(self, message):
        try:
            self.EventKey = message.pop('EventKey')
            self.TaskId = message.pop('TaskId')
        except KeyError:
            raise ParseError(u'任务卡片事件消息解析失败')
        super(TaskCardEvent, self).__init__(message)


@handle_for_type('add_external_contact')
class AddExternalEvent(WxBizCrmEventBase):
    """ 添加外部联系人事件 """

    def __init__(self, message):
        try:
            self.State = message.pop('State')
        except KeyError:
            raise ParseError(u'添加外部联系人事件消息解析失败')
        super(AddExternalEvent, self).__init__(message)


@handle_for_type('del_external_contact')
class DelExternalEvent(WxBizCrmEventBase):
    """ 删除外部联系人事件 """

    def __init__(self, message):
        super(DelExternalEvent, self).__init__(message)


class UnknownMessage(WxBizMsgTypeBase):
    def __init__(self, message):
        self.MsgType = 'unknown'
        super(UnknownMessage, self).__init__(message)
