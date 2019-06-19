# WechatBiz
> 作者：BLUE

> 日期：2019-06-19

> 描述：企业微信SDK，客户端依赖tornado，客户端使用AsyncHTTPClient，token存储依赖Redis，Python2.7

## 1. 配置
wxconfig.py中对一些参数进行配置

```
WECHAT_TOKEN = ""
WECHAT_APP_ID = ""  # 微信公众号id，微信支付时必有
WECHAR_AGENT_ID = "" # 自建应用id
WECHAT_PAYAGENT_ID = ""  # 企业支付应用id
WECHAT_CORP_ID = ""   # 企业ID
WECHAT_CORP_SECRET = "" # 全局密钥
WECHAT_ADDR_SECRET = "" # 通讯录密钥
WECHAT_CRM_SECRET = "" # 客户联系密钥
WECHAT_AES_KEY=""    # 对称加密key
WECHAT_PAY_SECRET = ""  # 微信支付密钥
WECHAT_PAY_MCHID = "" # 微信商户号id

# 微信支付数字证书
current_path = os.path.abspath(__file__)
WECHAT_PAY_CERT_PATH = os.path.abspath(os.path.dirname(
    current_path) + "%(sep)sWechat%(sep)scert%(sep)sapiclient_cert.pem" % dict(sep=os.path.sep))
WECHAT_PAY_KEY_PATH = os.path.abspath(os.path.dirname(
    current_path) + "%(sep)sWechat%(sep)scert%(sep)sapiclient_key.pem" % dict(sep=os.path.sep))
```

## 2. 开始使用
所有的模块出口都在WxBizSDK中

```
    |- WechatPay     微信支付
    |- AddrBook      通讯录管理
    |- WxBizAgent    应用管理
    |- WxBizAuth     身份验证
    |- WxBizJsSdk    JS-SDK服务
    |- WxBizCrm      外部关系
    |- WxBizMedia    素材管理
    |- WxBizMsg      收到消息解析、发送消息、被动回复消息 
    |- WxBizConver   会话消息
```
比如使用通讯录管理模块中的读取成员信息

```
# 导入通讯录管理模块
from WechatBiz.WxBizSDK import AddrBook
# 实例化
ad = AddrBook()
# 调用实例方法
ret = yield ad.GetUser('JS-14')
```
上面的ret就得到了成员的个人信息，其他所有方法的使用都和这个类似
1. 导入模块
2. 实例化
3. 使用实例方法


---
END
