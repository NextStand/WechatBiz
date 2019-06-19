# coding:utf-8
__author__ = 'BLUE'
__time__ = 'Sun Oct 28 2018 21:54:41 GMT+0800'

import io
import six
import time
import random


def to_text(value, encoding='utf-8'):
    """
    将 value 转为 unicode，默认编码 utf-8
    :param value: 待转换的值
    :param encoding: 编码
    """
    if not value:
        return ''
    if isinstance(value, six.text_type):
        return value
    if isinstance(value, six.binary_type):
        return value.decode(encoding)
    return six.text_type(value)


def to_binary(value, encoding='utf-8'):
    """
    将 values 转为 bytes，默认编码 utf-8
    :param value: 待转换的值
    :param encoding: 编码
    """
    if not value:
        return b''
    if isinstance(value, six.binary_type):
        return value
    if isinstance(value, six.text_type):
        return value.encode(encoding)

    if six.PY3:
        return six.binary_type(str(value), encoding)  # For Python 3
    return six.binary_type(value)


def disable_urllib3_warning():
    pass


def generate_timestamp():
    """
    生成时间戳
    :return: timestamp string
    """
    return int(time.time())


def generate_nonce():
    """
    生成随机数
    :return: nonce string
    """
    return random.randrange(1000000000, 2000000000)


def convert_ext_to_mime(extension):
    """
        将扩展名转换为 MIME 格式
        
        :return: mime string
    """
    table = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'bmp': 'image/bmp',
        'amr': 'voice/amr',
        'mp4': 'video/mp4',
        'txt':'application/octet-stream'
    }

    if extension in table:
        return table[extension]
    else:
        return 'application/octet-stream'
    raise ValueError("Invalid extension in MIME table")


def is_allowed_extension(extension, type='upload_media'):
    """检查扩展名是否是可以上传到服务器
    :return: True if ok
    """
    table = ('jpg', 'jpeg','png','bmp','txt','amr', 'mp4')

    if extension in table:
        return True
    return False


def encodeMulFormdata(files):
    """ 
        构造附件请求体描述 

        :param files: [(文件描述名, 文件数据流)]
        :return:(content_type,body)
    """
    boundary = '------BLUE--BLUE--BLUE------_$'
    crlf = '\r\n'
    l = []
    for (filename, value) in files:
        filename = filename.encode("utf8")
        l.append('--' + boundary)
        l.append(
            'Content-Disposition: form-data; name="media"; filename="%s"' % (
                filename
            )
        )
        l.append('Content-Type: %s' %
                 convert_ext_to_mime(filename.split('.')[-1].lower()))
        l.append('')
        l.append(value)
    l.append('--' + boundary + '--')
    l.append('')

    body = crlf.join(l)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body
