# coding:utf-8
""" 
企业微信消息相关模块
"""
__author__ = 'BLUE'
__time__ = 'Wed May 13 2019 10:09:50 GMT+0800'
# ------------------------------------------------------------------------
import time
import functools

from WechatBiz.lib.WxBizMsgCrypt import WxBizMsgCrypt
from WechatBiz.core.Exceptions import ParseError, NeedParseError
from WechatBiz.lib.crypto.Exceptions import EncryptAESError
from WechatBiz.lib.Parse import XMLStore
from WechatBiz.core.WechatBase import WechatBase
from WechatBiz.core.WxMsgModel import MESSAGE_TYPES, UnknownMessage
from WechatBiz.core.WxMsgReply import (
    TextReply, ImageReply, VoiceReply, VideoReply, Article, ArticleReply)
from WechatBiz.lib.Utils import generate_nonce, generate_timestamp, to_binary
from WechatBiz.wxconfig import WECHAT_TOKEN, WECHAT_CORP_ID, WECHAT_AES_KEY, WECHAR_AGENT_ID


def hand_for_send(type1):
    def wrapper(func):
        @functools.wraps(func)
        def fun(s, data, *args, **kwargs):
            if len(args) > 0:
                data['safe'] = 1 if args[0] == 1 else 0
            if kwargs.has_key('safe'):
                data['safe'] = 1 if kwargs.get('safe', 0) == 1 else 0
            data['msgtype'] = type1
            data.setdefault('agentid', WECHAR_AGENT_ID)
            return func(s, data)
        return fun
    return wrapper


class WxBizMsg(WechatBase):
    """ 
    消息类
    收到消息解析、发送消息、被动回复消息 
    """

    def __init__(self, **kwargs):
        self.__is_parse = False
        self.__message = None
        self.__wxcpt = WxBizMsgCrypt(
            WECHAT_TOKEN, WECHAT_AES_KEY, WECHAT_CORP_ID)
        if not kwargs.has_key('access_token'):
            token, expires_at = self.initToken()
            kwargs['access_token'] = token
            kwargs['access_token_expires_at'] = expires_at
        super(WxBizMsg, self).__init__(**kwargs)

    def __SendMsg(self, data):
        """ 发送应用消息接口 """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/message/send',
            data=data
        )

    def _check_parse(self):
        """
        检查是否成功解析微信服务器传来的数据
        :raises NeedParseError: 需要解析微信服务器传来的数据
        """
        if not self.__is_parse:
            raise NeedParseError(u'尚未解析微信服务器请求数据异常')

    def _encrypt_reply(self, reply):
        nonce = generate_nonce()
        timestamp = generate_timestamp()
        ret, sEncryptMsg = self.__wxcpt.EncryptMsg(
            to_binary(reply), nonce, timestamp)
        if ret != 0:
            raise EncryptAESError(u'回复消息加密失败')
        return sEncryptMsg

    # 检验消息的真实性，并且获取解密后的明文,收到消息的第一步
    def ParseMsg(self, sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce):
        """ 
        检验消息的真实性，并且获取解密后的明文
        :param sReqData: 密文，对应POST请求的数据
        :param sReqMsgSig: 签名串，对应URL参数的msg_signature
        :param sReqTimeStamp: 时间戳，对应URL参数的timestamp
        :param sReqNonce: 随机串，对应URL参数的nonce
        """
        ret, sMsg = self.__wxcpt.DecryptMsg(
            sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
        if ret != 0:
            raise ParseError(u'解析微信服务器数据异常')
        try:
            xml = XMLStore(xmlstring=sMsg)
        except Exception:
            raise ParseError()
        result = xml.xml2dict
        result['Raw'] = sMsg
        msgType = result.pop('MsgType').lower()
        if msgType == 'event':
            result['MsgType'] = result.pop('ChangeType').lower() if result.has_key(
                'ChangeType') else result.pop('Event').lower()
        else:
            result['MsgType'] = msgType
        message_type = MESSAGE_TYPES.get(result['MsgType'], UnknownMessage)
        self.__message = message_type(result)
        self.__is_parse = True

    # 获取解析后的消息，对应的消息类
    def GetMessage(self):
        self._check_parse()
        return self.__message

    @property
    def message(self):
        return self.GetMessage()

    # 发送应用文本消息
    @hand_for_send('text')
    def SendText(self, data, safe=0):
        """
            发送应用文本消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'text'], data, u'发送应用文本消息中，')
        return self.__SendMsg(data)

    # 发送应用图片消息
    @hand_for_send('image')
    def SendImage(self, data, safe=0):
        """
            发送应用图片消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['image'], data, u'发送应用图片消息中，')
        return self.__SendMsg(data)

    # 发送应用语音消息
    @hand_for_send('voice')
    def SendVoice(self, data, safe=0):
        """
            发送应用语音消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['voice'], data, u'发送应用语音消息中，')
        return self.__SendMsg(data)

    # 发送应用视频消息
    @hand_for_send('video')
    def SendVideo(self, data, safe=0):
        """
            发送应用视频消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['video'], data, u'发送应用视频消息中，')
        return self.__SendMsg(data)

    # 发送应用文件消息
    @hand_for_send('file')
    def SendFile(self, data, safe=0):
        """
            发送应用文件消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['file'], data, u'发送应用文件消息中，')
        return self.__SendMsg(data)

    # 发送应用文本卡片消息
    @hand_for_send('textcard')
    def SendTextCard(self, data, safe=0):
        """
            发送应用文本卡片消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['textcard'], data, u'发送应用文本卡片消息中，')
        return self.__SendMsg(data)

    # 发送应用图文消息
    @hand_for_send('news')
    def SendNews(self, data, safe=0):
        """
            发送应用图文消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['news'], data, u'发送应用图文消息中，')
        return self.__SendMsg(data)

    # 发送应用markdown消息
    @hand_for_send('markdown')
    def SendMarkdown(self, data, safe=0):
        """
            发送应用markdown消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['markdown'], data, u'发送应用markdown消息中，')
        return self.__SendMsg(data)

    # 发送小程序通知消息
    @hand_for_send('miniprogram_notice')
    def SendMiniNotice(self, data, safe=0):
        """
            发送小程序通知消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['miniprogram_notice'], data, u'发送应用小程序通知消息中，')
        return self.__SendMsg(data)

    # 发送应用任务卡片消息
    @hand_for_send('taskcard')
    def SendTaskCard(self, data, safe=0):
        """
            发送应用任务卡片消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90236
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['taskcard'], data, u'发送应用任务卡片消息中，')
        return self.__SendMsg(data)

    # 回复空消息
    def ReplyNone(self):
        """
        被动回复空消息

        :return: 符合微信服务器要求的加密 XML 响应数据
        """
        self._check_parse()
        return self._encrypt_reply('success')

    # 回复文本消息
    def ReplyText(self, content):
        """
        被动回复文本消息

        :param content: 回复文本
        :return: 符合微信服务器要求的加密 XML 响应数据
        """
        self._check_parse()
        content = self._transcoding(content)
        response = TextReply(message=self.__message, content=content).render()
        return self._encrypt_reply(response)

    # 回复图片消息
    def ReplyImage(self, media_id):
        """
        被动回复图片消息

        :param media_id: 图片的 MediaID
        :return: 符合微信服务器要求的加密 XML 响应数据
        """
        self._check_parse()
        response = ImageReply(message=self.__message,
                              media_id=media_id).render()
        return self._encrypt_reply(response)

    # 回复语音消息
    def ReplyVoice(self, media_id):
        """
        被动回复语音消息

        :param media_id: 语音的 MediaID
        :return: 符合微信服务器要求的加密 XML 响应数据
        """
        self._check_parse()
        response = VoiceReply(message=self.__message,
                              media_id=media_id).render()
        return self._encrypt_reply(response)

    # 回复视频消息
    def ReplyVideo(self, media_id, title=None, description=None):
        """
        被动回复视频消息

        :param media_id: 视频的 MediaID
        :param title: 视频消息的标题
        :param description: 视频消息的描述
        :return: 符合微信服务器要求的加密 XML 响应数据
        """
        self._check_parse()
        title = self._transcoding(title)
        description = self._transcoding(description)
        response = VideoReply(message=self.__message, media_id=media_id,
                              title=title, description=description).render()
        return self._encrypt_reply(response)

    # 回复图文消息
    def ReplyNews(self, articles):
        """
        被动回复图文消息

        :param articles: list 对象, 每个元素为一个 dict 对象, key 包含 `title`, `description`, `picurl`, `url`
        :return: 符合微信服务器要求的加密 XML 响应数据
        """
        self._check_parse()
        for article in articles:
            if article.get('title'):
                article['title'] = self._transcoding(article['title'])
            if article.get('description'):
                article['description'] = self._transcoding(
                    article['description'])
            if article.get('picurl'):
                article['picurl'] = self._transcoding(article['picurl'])
            if article.get('url'):
                article['url'] = self._transcoding(article['url'])

        news = ArticleReply(message=self.__message)
        for article in articles:
            article = Article(**article)
            news.add_article(article)
        response = news.render()
        return self._encrypt_reply(response)


class WxBizConver(WechatBase):
    """ 会话消息类 """

    def __init__(self):
        token, expires_at = self.initToken()
        super(WxBizConversation, self).__init__(
            access_token=token, access_token_expires_at=expires_at)

    def __SendAppchat(self, data):
        """ 企业内消息推送接口 """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/appchat/send',
            data=data
        )

    def __SendLinkedCropMsg(self, data):
        """ 互联消息推送接口 """
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/linkedcorp/message/send',
            data=data
        )

    # 创建群聊会话
    def CreateAppchat(self, data):
        """
            创建群聊会话

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90245
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['userlist'], data, u'创建群聊会话接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/appchat/create',
            data=data
        )

    # 修改群聊会话
    def UpdateAppchat(self, data):
        """
            修改群聊会话

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90246
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(['chatid'], data, u'修改群聊会话接口中，')
        return self.request.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/appchat/update',
            data=data
        )

    # 获取群聊会话
    def GetAppchat(self, chatid):
        """
            获取群聊会话

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90247
            :return: 携带JSON数据包的异步Future
        """
        return self.request.get(
            'https://qyapi.weixin.qq.com/cgi-bin/appchat/get',
            data=dict(chatid=chatid)
        )

    # 发送文本会话消息
    def SendText(self, chatid, content, safe=0):
        """
            发送文本会话消息

            :param chatid: 会话id
            :param content: 消息内容
            :param safe: 表示是否是保密消息，0表示否，1表示是，默认0
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/%E6%96%87%E6%9C%AC%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "text",
            "text": {"content": content},
            "safe": safe
        }
        return self.__SendAppchat(data)

    # 发送图片会话消息
    def SendImage(self, chatid, media_id, safe=0):
        """
            发送图片会话消息

            :param chatid: 会话id
            :param media_id: 图片媒体文件id，可以调用上传临时素材接口获取
            :param safe: 表示是否是保密消息，0表示否，1表示是，默认0
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/%E5%9B%BE%E7%89%87%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "image",
            "image": {
                "media_id": media_id
            },
            "safe": safe
        }
        return self.__SendAppchat(data)

    # 发送语音会话消息
    def SendVoice(self, chatid, media_id, safe=0):
        """
            发送语音会话消息

            :param chatid: 会话id
            :param media_id: 图片媒体文件id，可以调用上传临时素材接口获取
            :param safe: 表示是否是保密消息，0表示否，1表示是，默认0
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/%E8%AF%AD%E9%9F%B3%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "voice",
            "voice": {
                "media_id": media_id
            }
        }
        return self.__SendAppchat(data)

    # 发送视频会话消息
    def SendVideo(self, chatid, media_id, title='', description='', safe=0):
        """
            发送视频会话消息

            :param chatid: 会话id
            :param media_id: 图片媒体文件id，可以调用上传临时素材接口获取
            :param title: 视频消息的标题，不超过128个字节，超过会自动截断
            :param description: 视频消息的描述，不超过512个字节，超过会自动截断
            :param safe: 表示是否是保密消息，0表示否，1表示是，默认0
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/%E8%A7%86%E9%A2%91%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "video",
            "video": {
                "media_id": media_id,
                "description": description
            },
            "safe": safe
        }
        return self.__SendAppchat(data)

    # 发送文件会话消息
    def SendFile(self, chatid, media_id, safe=0):
        """
            发送文件会话消息

            :param chatid: 会话id
            :param media_id: 图片媒体文件id，可以调用上传临时素材接口获取
            :param safe: 表示是否是保密消息，0表示否，1表示是，默认0
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/%E6%96%87%E4%BB%B6%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "file",
            "file": {
                "media_id": media_id
            },
            "safe": safe
        }
        return self.__SendAppchat(data)

    # 发送文本卡片会话消息
    def SendTextCard(self, chatid, title, description, url, btntxt=u'详情', safe=0):
        """
            发送文本卡片会话消息

            :param chatid: 会话id
            :param media_id: 图片媒体文件id，可以调用上传临时素材接口获取
            :param title: 标题，不超过128个字节，超过会自动截断
            :param description: 描述，不超过512个字节，超过会自动截断
            :param url: 点击后跳转的链接
            :param safe: 表示是否是保密消息，0表示否，1表示是，默认0
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/%E6%96%87%E6%9C%AC%E5%8D%A1%E7%89%87%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "textcard",
            "textcard": {
                "title": title,
                "description": description,
                "btntxt": btntxt
            },
            "safe": safe
        }
        return self.__SendAppchat(data)

    # 发送图文会话消息
    def SendNews(self, chatid, articles, safe=0):
        """
            发送图文会话消息

            :param chatid: 会话id
            :param articles: 图文消息list，一个图文消息支持1到8条图文
            :param safe: 表示是否是保密消息，0表示否，1表示是，默认0
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/%E5%9B%BE%E6%96%87%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "news",
            "news": {
                "articles": articles
            },
            "safe": safe
        }
        return self.__SendAppchat(data)

    # 发送图文会话消息(mpnews)
    def SendMapNews(self, chatid, articles, safe=0):
        """
            发送图文会话消息

            :param chatid: 会话id
            :param articles: 图文消息list，一个图文消息支持1到8条图文
            :param safe: 表示是否是保密消息，0表示否，1表示是，默认0
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/%E5%9B%BE%E6%96%87%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "mpnews",
            "mpnews": {
                "articles": articles
            },
            "safe": safe
        }
        return self.__SendAppchat(data)

    # 发送markdown会话消息(mpnews)
    def SendMarkdown(self, chatid, content):
        """
            发送markdown会话消息

            :param chatid: 会话id
            :param content: markdown内容，最长不超过2048个字节，必须是utf8编码
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90248/markdown%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        data = {
            "chatid": chatid,
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        return self.__SendAppchat(data)

    # 发送互联企业文本消息
    def SendLinkText(self, data):
        """
            发送互联企业文本消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E6%96%87%E6%9C%AC%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'text'], data, u'发送互联企业文本消息接口中，')
        data['msgtype'] = 'text'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业图片消息
    def SendLinkImage(self, data):
        """
            发送互联企业图片消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E5%9B%BE%E7%89%87%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'image'], data, u'发送互联企业图片消息接口中，')
        data['msgtype'] = 'image'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业语音消息
    def SendLinkVoice(self, data):
        """
            发送互联企业语音消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E8%AF%AD%E9%9F%B3%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'voice'], data, u'发送互联企业语音消息接口中，')
        data['msgtype'] = 'voice'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业视频消息
    def SendLinkVideo(self, data):
        """
            发送互联企业视频消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E8%A7%86%E9%A2%91%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'video'], data, u'发送互联企业视频消息接口中，')
        data['msgtype'] = 'video'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业文件消息
    def SendLinkFile(self, data):
        """
            发送互联企业视频消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E6%96%87%E4%BB%B6%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'file'], data, u'发送互联企业文件消息接口中，')
        data['msgtype'] = 'file'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业文本卡片消息
    def SendLinkTextCard(self, data):
        """
            发送互联企业文本卡片消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E6%96%87%E6%9C%AC%E5%8D%A1%E7%89%87%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'textcard'], data, u'发送互联企业文本卡片消息接口中，')
        data['msgtype'] = 'textcard'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业图文消息
    def SendLinkNews(self, data):
        """
            发送互联企业图文消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E5%9B%BE%E6%96%87%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'news'], data, u'发送互联企业图文消息接口中，')
        data['msgtype'] = 'news'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业图文消息(mpnews)
    def SendLinkMpNews(self, data):
        """
            发送互联企业图文消息(mpnews)

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E5%9B%BE%E6%96%87%E6%B6%88%E6%81%AF%EF%BC%88mpnews%EF%BC%89
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'mpnews'], data, u'发送互联企业图文消息(mpnews)接口中，')
        data['msgtype'] = 'mpnews'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业markdown消息
    def SendLinkMarkdown(self, data):
        """
            发送互联企业markdown消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/markdown%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'markdown'], data, u'发送互联企业markdown消息中，')
        data['msgtype'] = 'markdown'
        return self.__SendLinkedCropMsg(data)

    # 发送互联企业小程序通知消息
    def SendLinkMiniNotice(self, data):
        """
            发送互联企业markdown消息

            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90249/%E5%B0%8F%E7%A8%8B%E5%BA%8F%E9%80%9A%E7%9F%A5%E6%B6%88%E6%81%AF
            :return: 携带JSON数据包的异步Future
        """
        self.ChkNeedParamsError(
            ['agentid', 'miniprogram_notice'], data, u'发送互联企业小程序通知消息中，')
        data['msgtype'] = 'miniprogram_notice'
        return self.__SendLinkedCropMsg(data)
