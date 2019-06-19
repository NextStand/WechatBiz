# coding:utf-8
""" 
微信包所需的配置信息
"""
__author__ = 'BLUE'
__time__ = 'Wed May 15 2019 17:55:23 GMT+0800'
# ------------------------------------------------------------------------
import os
WECHAT_TOKEN = "BLUE"
WECHAT_APP_ID = ""  # 微信公众号id，微信支付时必有
WECHAR_AGENT_ID = "1000002" # 自建应用id
WECHAT_PAYAGENT_ID = "3010046"  # 企业支付应用id
WECHAT_CORP_ID = "wx29ceb07f63b25f34"   # 企业ID
WECHAT_CORP_SECRET = "cKytHTd3QQwTA4dBKRkfAJtS8qEK2e9EHShM4jXPQUs" # 全局密钥
WECHAT_ADDR_SECRET = "gJCVclRNYDDf5pprnOjzTbpZN2RGYDahbBJZbcSqxiI" # 通讯录密钥
WECHAT_CRM_SECRET = "gJCVclRNYDDf5pprnOjzTbpZN2RGYDahbBJZbcSqxiI" # 客户联系密钥
WECHAT_AES_KEY='NmjjvF3xqdUhtuJBkLcTIFwhaFFP8JFlJNoFPipzELj'    # 对称加密key
WECHAT_PAY_SECRET = 'c28868c9f12711e8bab15254005c9e8b'  # 微信支付密钥
WECHAT_PAY_MCHID = '1519091801' # 微信商户号id

# 微信支付数字证书
current_path = os.path.abspath(__file__)
WECHAT_PAY_CERT_PATH = os.path.abspath(os.path.dirname(
    current_path) + "%(sep)sWechat%(sep)scert%(sep)sapiclient_cert.pem" % dict(sep=os.path.sep))
WECHAT_PAY_KEY_PATH = os.path.abspath(os.path.dirname(
    current_path) + "%(sep)sWechat%(sep)scert%(sep)sapiclient_key.pem" % dict(sep=os.path.sep))
