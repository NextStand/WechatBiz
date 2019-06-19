# coding:utf-8
""" 
微信回复消息库
"""
__author__ = 'BLUE'
__time__ = 'Wed May 22 2019 11:27:10 GMT+0800'
# ------------------------------------------------------------------------
from .WechatBase import WxBizReply


class TextReply(WxBizReply):
    """
    回复文字消息
    """
    TEMPLATE = u"""
    <xml>
    <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
    <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
    <CreateTime>{CreateTime}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
    </xml>
    """

    def __init__(self, message, content):
        """
        :param message: WxBizMsgTypeBase 对象
        :param content: 文字回复内容
        """
        super(TextReply, self).__init__(message=message, content=content)

    def render(self):
        return TextReply.TEMPLATE.format(**self._args)


class ImageReply(WxBizReply):
    """
    回复图片消息
    """
    TEMPLATE = u"""
    <xml>
    <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
    <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
    <CreateTime>{CreateTime}</CreateTime>
    <MsgType><![CDATA[image]]></MsgType>
    <Image>
    <MediaId><![CDATA[{media_id}]]></MediaId>
    </Image>
    </xml>
    """

    def __init__(self, message, media_id):
        """
        :param message: WechatMessage 对象
        :param media_id: 图片的 MediaID
        """
        super(ImageReply, self).__init__(message=message, media_id=media_id)

    def render(self):
        return ImageReply.TEMPLATE.format(**self._args)


class VoiceReply(WxBizReply):
    """
    回复语音消息
    """
    TEMPLATE = u"""
    <xml>
    <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
    <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
    <CreateTime>{CreateTime}</CreateTime>
    <MsgType><![CDATA[voice]]></MsgType>
    <Voice>
    <MediaId><![CDATA[{media_id}]]></MediaId>
    </Voice>
    </xml>
    """

    def __init__(self, message, media_id):
        """
        :param message: WechatMessage 对象
        :param media_id: 语音的 MediaID
        """
        super(VoiceReply, self).__init__(message=message, media_id=media_id)

    def render(self):
        return VoiceReply.TEMPLATE.format(**self._args)


class VideoReply(WxBizReply):
    """
    回复视频消息
    """
    TEMPLATE = u"""
    <xml>
    <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
    <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
    <CreateTime>{CreateTime}</CreateTime>
    <MsgType><![CDATA[video]]></MsgType>
    <Video>
    <MediaId><![CDATA[{media_id}]]></MediaId>
    <Title><![CDATA[{title}]]></Title>
    <Description><![CDATA[{description}]]></Description>
    </Video>
    </xml>
    """

    def __init__(self, message, media_id, title=None, description=None):
        """
        :param message: WechatMessage对象
        :param media_id: 视频的 MediaID
        :param title: 视频消息的标题
        :param description: 视频消息的描述
        """
        title = title or ''
        description = description or ''
        super(VideoReply, self).__init__(message=message,
                                         media_id=media_id, title=title, description=description)

    def render(self):
        return VideoReply.TEMPLATE.format(**self._args)


class Article(object):
    def __init__(self, title=None, description=None, picurl=None, url=None):
        self.title = title or ''
        self.description = description or ''
        self.picurl = picurl or ''
        self.url = url or ''


class ArticleReply(WxBizReply):
    """
    回复图文消息
    """
    TEMPLATE = u"""
    <xml>
    <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
    <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
    <CreateTime>{CreateTime}</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>{count}</ArticleCount>
    <Articles>{items}</Articles>
    </xml>
    """

    ITEM_TEMPLATE = u"""
    <item>
    <Title><![CDATA[{title}]]></Title>
    <Description><![CDATA[{description}]]></Description>
    <PicUrl><![CDATA[{picurl}]]></PicUrl>
    <Url><![CDATA[{url}]]></Url>
    </item>
    """

    def __init__(self, message, **kwargs):
        super(ArticleReply, self).__init__(message, **kwargs)
        self._articles = []

    def add_article(self, article):
        if len(self._articles) >= 10:
            raise AttributeError(
                "Can't add more than 10 articles in an ArticleReply")
        else:
            self._articles.append(article)

    def render(self):
        items = []
        for article in self._articles:
            items.append(ArticleReply.ITEM_TEMPLATE.format(
                title=article.title,
                description=article.description,
                picurl=article.picurl,
                url=article.url,
            ))
        self._args["items"] = ''.join(items)
        self._args["count"] = len(items)
        return ArticleReply.TEMPLATE.format(**self._args)
