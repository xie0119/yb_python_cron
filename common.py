#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import base64
import requests
# docker exec -it QL bash -c "apk add python3 zlib-dev gcc jpeg-dev python3-dev musl-dev freetype-dev"
# docker exec -it QL bash -c "pip install pycryptodome"
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from env import Env

UserAgent = Env.UserAgent
AppVersion = Env.AppVersion


class YbLogin:
    # 请求头
    headers = {
        "Origin": "https://m.yiban.cn",
        'AppVersion': AppVersion,
        "User-Agent": UserAgent
    }

    # 密码加密
    public_key = '''-----BEGIN PUBLIC KEY-----
        MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA6aTDM8BhCS8O0wlx2KzA
        Ajffez4G4A/QSnn1ZDuvLRbKBHm0vVBtBhD03QUnnHXvqigsOOwr4onUeNljegIC
        XC9h5exLFidQVB58MBjItMA81YVlZKBY9zth1neHeRTWlFTCx+WasvbS0HuYpF8+
        KPl7LJPjtI4XAAOLBntQGnPwCX2Ff/LgwqkZbOrHHkN444iLmViCXxNUDUMUR9bP
        A9/I5kwfyZ/mM5m8+IPhSXZ0f2uw1WLov1P4aeKkaaKCf5eL3n7/2vgq7kw2qSmR
        AGBZzW45PsjOEvygXFOy2n7AXL9nHogDiMdbe4aY2VT70sl0ccc4uvVOvVBMinOp
        d2rEpX0/8YE0dRXxukrM7i+r6lWy1lSKbP+0tQxQHNa/Cjg5W3uU+W9YmNUFc1w/
        7QT4SZrnRBEo++Xf9D3YNaOCFZXhy63IpY4eTQCJFQcXdnRbTXEdC3CtWNd7SV/h
        mfJYekb3GEV+10xLOvpe/+tCTeCDpFDJP6UuzLXBBADL2oV3D56hYlOlscjBokNU
        AYYlWgfwA91NjDsWW9mwapm/eLs4FNyH0JcMFTWH9dnl8B7PCUra/Lg/IVv6HkFE
        uCL7hVXGMbw2BZuCIC2VG1ZQ6QD64X8g5zL+HDsusQDbEJV2ZtojalTIjpxMksbR
        ZRsH+P3+NNOZOEwUdjJUAx8CAwEAAQ==
        -----END PUBLIC KEY-----'''

    # 密码加密
    def encrypt_password(self, pwd):
        cipher = PKCS1_v1_5.new(RSA.importKey(self.public_key))
        cipher_text = base64.b64encode(cipher.encrypt(bytes(pwd, encoding="utf8")))
        return cipher_text.decode("utf-8")

    # 登录
    def login(self, account, password):
        """
        登录
        :return:
        """
        params = {
            "mobile": account,
            "password": self.encrypt_password(password),
            "ct": "1",
            "identify": "1",
        }

        # 新的登录接口
        resp = requests.post("https://mobile.yiban.cn/api/v4/passport/login", params=params, headers=self.headers)
        response = json.loads(resp.text)
        response['http_waf_cookie'] = resp.headers["Set-Cookie"]
        return response


# 图鉴 - 验证码识别 (http://www.ttshitu.com/)
class Captcha:

    def __init__(self):
        result = Env().get_env('CAPTCHA')['data'][0]
        self.ct_user, self.ct_pass = result.split('|', 1)

    # base64 验证码识别
    def base64_api(self, images):
        data = {"username": self.ct_user, "password": self.ct_pass, "typeid": '1', "image": images}
        ret = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        if ret['success']:
            return {'code': 1, 'msg': ret["message"], 'data': ret["data"]["result"], 'id': ret["data"]["id"]}
        else:
            return {'code': -1, 'msg': ret["message"]}

    # 报错提交
    @staticmethod
    def report_error(id):
        data = {"id": id}
        ret = json.loads(requests.post("http://api.ttshitu.com/reporterror.json", json=data).text)
        if ret['success']:
            return {'code': 1, 'msg': ret["message"], 'data': ret["data"]}
        else:
            return {'code': -1, 'msg': ret["message"]}
