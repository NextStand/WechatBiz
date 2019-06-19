# coding:utf-8
"""
企业微信素材管理模块
"""
__author__ = 'BLUE'
__time__ = 'Tue May 21 2019 10:43:40 GMT+0800'
# ------------------------------------------------------------------------
from WechatBiz.core.WechatBase import WechatBase
from WechatBiz.lib.Utils import is_allowed_extension


def hand_check_file(media_file):
    extension = media_file.filename.split('.')[-1].lower()
    if not is_allowed_extension(extension):
        raise ValueError(u'上传文件类型不允许.')
    files = [(media_file.filename, media_file.body)]
    return files


class WxBizMedia(WechatBase):
    def __init__(self):
        self.__tempUrl = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload'
        token, expires_at = self.initToken()
        super(WxBizMedia, self).__init__(
            access_token=token, access_token_expires_at=expires_at)

    # 上传临时图片
    def UploadTempImage(self, media_file):
        """
            上传临时图片

            :param media_file: 要上传的文件，一个 File object
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90253
            :return: 携带JSON数据包的异步Future
        """
        files = hand_check_file(media_file)
        return self.request.uploadMedia(url=self.__tempUrl, data=dict(type='image', files=files))

    # 上传临时语音
    def UploadTempVoice(self, media_file):
        """
            上传临时语音

            :param media_file: 要上传的文件，一个 File object
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90253
            :return: 携带JSON数据包的异步Future
        """
        files = hand_check_file(media_file)
        return self.request.uploadMedia(url=self.__tempUrl, data=dict(type='voice', files=files))

    # 上传临时视频
    def UploadTempVideo(self, media_file):
        """
            上传临时视频

            :param media_file: 要上传的文件，一个 File object
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90253
            :return: 携带JSON数据包的异步Future
        """
        files = hand_check_file(media_file)
        return self.request.uploadMedia(url=self.__tempUrl, data=dict(type='video', files=files))

    # 上传临时文件
    def UploadTempFile(self, media_file):
        """
            上传临时视频

            :param media_file: 要上传的文件，一个 File object
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90253
            :return: 携带JSON数据包的异步Future
        """
        files = hand_check_file(media_file)
        return self.request.uploadMedia(url=self.__tempUrl, data=dict(type='file', files=files))

    # 上传永久图片
    def UploadEverImage(self, media_file):
        """
            上传永久图片

            :param media_file: 要上传的文件，一个 File object
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90256
            :return: 携带JSON数据包的异步Future
        """
        files = hand_check_file(media_file)
        return self.request.uploadMedia(
            url='https://qyapi.weixin.qq.com/cgi-bin/media/uploadimg',
            data=dict(files=files)
        )

    # 获取临时素材(得到的是整个响应对象，自己解析)
    def GetTempMedia(self, media_id):
        """
            获取临时素材(得到的是整个响应对象，自己解析)
            如果要返回前端，则取相应体res.body,并设置响应类型("Content-Type", "image/jpg")

            :param media_id: 媒体文件id
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90254
            :return: 携带JSON数据包的异步Future
        """
        return self.request.getRes(
            'https://qyapi.weixin.qq.com/cgi-bin/media/get', data=dict(
                media_id=media_id
            ))

    # 获取高清语音素材(得到的是整个响应对象，自己解析)
    def GetSuperMedia(self, media_id):
        """
            获取高清语音素材(得到的是整个响应对象，自己解析)

            :param media_file: 通过JSSDK的uploadVoice接口上传的语音文件id
            详情请参考 https://work.weixin.qq.com/api/doc#90000/90135/90255
            :return: 携带JSON数据包的异步Future
        """
        return self.request.getRes(
            'https://qyapi.weixin.qq.com/cgi-bin/media/get/jssdk', data=dict(
                media_id=media_id
            ))

    
