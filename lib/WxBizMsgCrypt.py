# coding:utf-8
""" 对企业微信发送给企业后台的消息加解密示例代码.
@copyright: Copyright (c) 1998-2014 Tencent Inc.
"""
# ------------------------------------------------------------------------
from .crypto.WxBizCryptBase import WxBizCryptBase


class WxBizMsgCrypt(WxBizCryptBase):
    def __init__(self, sToken, sEncodingAESKey, sReceiveId):
        super(WxBizMsgCrypt, self).__init__(
            sToken, sEncodingAESKey, sReceiveId)

    def VerifyURL(self, sMsgSignature, sTimeStamp, sNonce, sEchoStr):
        """
        验证URL

        :param sMsgSignature: 签名串，对应URL参数的msg_signature
        :param sTimeStamp: 时间戳，对应URL参数的timestamp
        :param sNonce: 随机串，对应URL参数的nonce
        :param sEchoStr: 随机串，对应URL参数的echostr
        :param sEchoStr: 随机串，对应URL参数的echostr
        :return: (状态码,解密之后的echostr)，状态码为0表示成功
        """
        return self._VerifyURL(sMsgSignature, sTimeStamp, sNonce, sEchoStr)

    def EncryptMsg(self, sReplyMsg, sNonce, timestamp=None):
        """
        将企业回复用户的消息加密打包

        :param sReplyMsg: 企业号待回复用户的消息，xml格式的字符串
        :param sTimeStamp: 时间戳，可以自己生成，也可以用URL参数的timestamp,如为None则自动用当前时间
        :param sNonce: 随机串，可以自己生成，也可以用URL参数的nonce
        :return: (状态码,加密后的可以直接回复用户的密文，包括msg_signature, timestamp, nonce, encrypt的xml格式的字符串,)
        状态码为0表示成功
        """
        return self._EncryptMsg(sReplyMsg, sNonce, timestamp)

    def DecryptMsg(self, sPostData, sMsgSignature, sTimeStamp, sNonce):
        """
        检验消息的真实性,验证安全签名，并且获取解密后的明文

        :param sPostData: 密文，对应POST请求的数据
        :param sMsgSignature: 签名串，对应URL参数的msg_signature
        :param sTimeStamp: 时间戳，对应URL参数的timestamp
        :param sNonce: 随机串，对应URL参数的nonce
        :return: (状态码, 解密后的原文xml),状态码为0表示成功
        """
        return self._DecryptMsg(sPostData, sMsgSignature, sTimeStamp, sNonce)