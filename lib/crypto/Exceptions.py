# coding:utf-8
__author__ = 'BLUE'
__time__ = 'Sun Oct 28 2018 22:34:48 GMT+0800'

from WechatBiz.core.Exceptions import WechatSDKException


class ierror:
    WXBizMsgCrypt_OK = 0
    WXBizMsgCrypt_ValidateSignature_Error = -40001
    WXBizMsgCrypt_ParseXml_Error = -40002
    WXBizMsgCrypt_ComputeSignature_Error = -40003
    WXBizMsgCrypt_IllegalAesKey = -40004
    WXBizMsgCrypt_ValidateCorpid_Error = -40005
    WXBizMsgCrypt_EncryptAES_Error = -40006
    WXBizMsgCrypt_DecryptAES_Error = -40007
    WXBizMsgCrypt_IllegalBuffer = -40008
    WXBizMsgCrypt_EncodeBase64_Error = -40009
    WXBizMsgCrypt_DecodeBase64_Error = -40010
    WXBizMsgCrypt_GenReturnXml_Error = -40011


class CryptoException(WechatSDKException):
    """加密解密异常基类"""
    pass


class CryptoComputeSignatureError(CryptoException):
    """签名计算错误"""
    pass


class EncryptAESError(CryptoException):
    """AES加密错误"""
    pass


class DecryptAESError(CryptoException):
    """AES解密错误"""
    pass


class IllegalBuffer(CryptoException):
    """不合法的缓冲区"""
    pass


class ValidateAppIDError(CryptoException):
    """验证AppID错误"""
    pass


class ValidateSignatureError(CryptoException):
    """验证签名错误"""
    pass


class ValidateAESKeyError(CryptoException):
    """验证AES Key错误"""
    pass
