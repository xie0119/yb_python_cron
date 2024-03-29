#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sqlite3
import time
import requests
import base64
import json
# docker exec -it qinglong bash -c "apk add python3 zlib-dev gcc jpeg-dev python3-dev musl-dev freetype-dev"
# docker exec -it qinglong bash -c "pip install pycryptodome"
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from hashlib import md5, sha1

requests.packages.urllib3.disable_warnings()


class Env:
    # iPhone 13 Pro
    UserAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                'Mobile/15E148 yiban_iOS/5.0.8 '
    # Chrome浏览器
    UserAgent2 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/96.0.4664.110 Safari/537.36 '

    # 微信浏览器
    UserAgent3 = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 ' \
                 'Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6305002e) '

    # APP版本
    AppVersion = '5.0.11'

    def __init__(self, label=None):
        # 0 = sqlite数据库获取, 1 = 外部获取
        self.mode = 1
        self.label = label

    # 适配各种平台环境cookie
    @staticmethod
    def check_env_file():
        if os.path.exists('/ql/config/env.sh'):
            return '/ql/config/env.sh'
        elif os.path.exists('/ql/config/cookie.sh'):
            return '/ql/config/env.sh'
        elif os.path.exists('/ql/data/config/env.sh'):
            return '/ql/data/config/env.sh'
        return False

    # 检查sqlite
    @staticmethod
    def check_sqlite_file():
        if os.path.exists('/ql/db/database.sqlite'):
            return '/ql/db/database.sqlite'
        elif os.path.exists('/ql/data/db/database.sqlite'):
            return '/ql/data/db/database.sqlite'
        return False

    # 获取指定 环境变量
    def get_env(self, name):
        if self.mode == 1 and name == 'YB_COOKIE':
            return self.get_server()
        else:
            return self.get_sqlite(name)

    def get_sqlite(self, name):
        try:
            if self.check_sqlite_file() is False:
                return {'code': -1, 'msg': '数据库不存在'}
            # 查询数据
            db = Sqlite()
            sql = "SELECT * FROM Envs WHERE name = ? AND status = 0"
            r1 = db.queryDict(sql, [name])
            db.closeDB()
            return {'code': 1, 'msg': '获取成功', 'data': r1}
        except Exception as ex:
            return {'code': -2, 'msg': '获取失败' + str(ex)}

    def get_server(self):
        try:
            us = UserServer()
            result = us.get_token()
            if result['code'] != 200:
                return {'code': result['code'], 'msg': result['message']}
            # 查询数据
            r1 = us.get_user_list(self.label)
            # 更新任务状态
            us.set_task_status(self.label, 0)
            if r1['code'] != 200:
                return {'code': r1['code'], 'msg': r1['message']}
            return {'code': 1, 'msg': r1['message'], 'data': r1['data']}
        except Exception as ex:
            return {'code': -2, 'msg': '获取失败' + str(ex)}

    # 结束设置
    def set_stop_status(self):
        try:
            us = UserServer()
            result = us.get_token()
            if result['code'] != 200:
                return {'code': result['code'], 'msg': result['message']}
            # 查询数据
            r1 = us.set_task_status(self.label, 1)
            if r1['code'] != 200:
                return {'code': r1['code'], 'msg': r1['message']}
            return {'code': 1, 'msg': r1['message'], 'data': r1['data']}
        except Exception as ex:
            return {'code': -2, 'msg': '获取失败' + str(ex)}


env = Env()


class Setting:
    label = None

    def __init__(self, label=None):
        self.label = label

    def msg_(self, code, msg, data=None, phone=None, label=None):
        print({'code': code, 'message': msg, 'data': data, 'label': label if label else self.label, 'phone': phone, 'time': time.time()})
        if code == -999 or code == 2000:
            Env(self.label).set_stop_status()



class YiBan:
    # v5.0.2版本Rsa公钥
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
    @staticmethod
    def encrypt_password(password, public_key):
        cipher = PKCS1_v1_5.new(RSA.importKey(public_key))
        cipher_text = base64.b64encode(cipher.encrypt(bytes(password, encoding="utf8")))
        return cipher_text.decode("utf-8")

    # 移动端登录
    def mobile_login(self, account, password):
        """
        登录
        :return:
        """
        params = {
            'mobile': account,
            'password': self.encrypt_password(password, self.public_key),
            'ct': '2',
            'identify': f'8693{account}',
            'app': '1',
            'apn': 'wifi',
            'v': env.AppVersion,
        }
        # 请求头
        headers = {
            'Origin': 'https://m.yiban.cn',
            'AppVersion': env.AppVersion,
            'User-Agent': env.UserAgent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # 新的登录接口
        resp = requests.post("https://mobile.yiban.cn/api/v4/passport/login", params=params, headers=headers)
        response = resp.json()
        response['https_waf_cookie'] = resp.cookies.get('https_waf_cookie')
        return response

    # PC 端登录
    def chrome_login(self, account, password):
        session = requests.session()
        headers = {
            'Accept': 'application/json,text/javascript,*/*;q=0.01',
            'Accept-Encoding': 'gzip,deflate,br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Host': 'www.yiban.cn',
            'Origin': 'https://www.yiban.cn',
            'Referer': 'https://www.yiban.cn/login?go=https%3A%2F%2Fwww.yiban.cn%2F',
            'sec-ch-ua': '"Chromium";v="92","NotA;Brand";v="99","GoogleChrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': env.UserAgent2,
        }
        html = session.get("https://www.yiban.cn/login?go=https%3A%2F%2Fwww.yiban.cn%2F", headers=headers).text
        keysTime = re.findall(r"data-keys-time='(.*?)'", html)[0]
        keys = re.findall(r"data-keys='(.*?[^%&',;=?$\x22]+)'", html)[0]

        data = {
            'account': account,  # 填写账号
            'password': self.encrypt_password(password, keys),  # 密码Rsa加密
            'captcha': '',
            'keysTime': keysTime,
        }
        url = "https://www.yiban.cn/login/doLoginAjax"
        resp = session.post(url, data=data)
        response = resp.json()
        response['yiban_user_token'] = resp.cookies.get('yiban_user_token')
        return response

    # 自动登录
    @staticmethod
    def mobile_auto_login(ck):
        url = 'https://m.yiban.cn/api/v4/passport/autologin'
        headers = {
            'loginToken': re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', ck)[0],
            'Host': 'm.yiban.cn',
            'AppVersion': env.AppVersion,
            'User-Agent': env.UserAgent,
        }
        try:
            resp = requests.get(url=url, headers=headers).json()
            if resp['response'] != 100:
                return {'code': resp['response'], 'msg': resp['message'], 'data': None}
            return {'code': resp['response'], 'msg': resp['message'], 'data': resp['data']}
        except Exception as ex:
            return {'code': -1, 'msg': '登录失败' + str(ex), 'data': None}

    # 检测cookie/Token是否正确
    @staticmethod
    def check_token(cookie):
        url = 'https://s.yiban.cn/api/my/getInfo'
        headers = {
            'Cookie': cookie,
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 's.yiban.cn',
            'User-Agent': env.UserAgent2,
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        try:
            resp = requests.get(url=url, headers=headers).json()
            if resp['status']:
                return {'code': int(resp['code']), 'msg': resp['message'], 'data': resp['data']}
            return {'code': int(resp['code']), 'msg': resp['message']}
        except Exception as ex:
            return {'code': -1, 'msg': '检查失败' + str(ex)}

    # 获取网薪
    @staticmethod
    def get_salary(ck, pg=1):
        url = f'https://m.yiban.cn/api/v4/web-salary/logs?page={pg}'
        headers = {
            'loginToken': re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', ck)[0],
            'Host': 'm.yiban.cn',
            'User-Agent': env.UserAgent,
            'AppVersion': env.AppVersion,
        }
        try:
            resp = requests.get(url=url, headers=headers).json()
            if resp['response'] != 100:
                return {'code': resp['response'], 'msg': resp['message'], 'data': []}
            return {'code': resp['response'], 'msg': resp['message'], 'data': resp['data']}
        except Exception as ex:
            return {'code': -1, 'msg': '检查失败' + str(ex)}


# 图鉴 - 验证码识别 (http://www.ttshitu.com/)
class Captcha:
    ct_user = None
    ct_pass = None

    def __init__(self):
        try:
            result = env.get_env('CAPTCHA')
            if result['code'] == 1:
                ct = result['data'][0]['value'].split('|')
                self.ct_user = ct[0]
                self.ct_pass = ct[1]
            else:
                Setting('Captcha').msg_(result['code'], result['msg'])
        except Exception as ex:
            Setting('Captcha').msg_(-1, 'Captcha 初始化失败 ' + str(ex))

    # base64 验证码识别
    def base64_api(self, images):
        if self.ct_user is None:
            return {'code': -1, 'msg': '打码平台账号获取失败'}
        data = {"username": self.ct_user, "password": self.ct_pass, "typeid": '1', "image": images}
        ret = requests.post("http://api.ttshitu.com/predict", json=data).json()
        if ret['success']:
            return {'code': 1, 'msg': ret["message"], 'data': ret["data"]["result"], 'id': ret["data"]["id"]}
        else:
            return {'code': -1, 'msg': ret["message"]}

    # 报错提交
    def report_error(self, id):
        if self.ct_user is None:
            return {'code': -1, 'msg': '打码平台账号获取失败'}
        data = {"id": id}
        ret = requests.post("http://api.ttshitu.com/reporterror.json", json=data).json()
        if ret['success']:
            return {'code': 1, 'msg': ret["message"], 'data': ret["data"]}
        else:
            return {'code': -1, 'msg': ret["message"]}


# 青龙面板开放APi
class OpenApi:
    token, domain, client, secret = [None, None, None, None]

    # 初始化
    def __init__(self):
        try:
            result = env.get_env('DOMAIN')
            if result['code'] != 1:
                Setting('OpenApi').msg_(result['code'], result['msg'])
            else:
                self.domain = result['data'][0]
            result = env.get_env('APPLICATION')
            if result['code'] != 1:
                Setting('OpenApi').msg_(result['code'], result['msg'])
            else:
                self.client, self.secret = result['data'][0].split('|', 1)
        except Exception as ex:
            Setting('OpenApi').msg_(-1, 'OpenApi 环境变量获取失败 ' + str(ex))

    # 获取面板token
    def get_token(self):
        try:
            if self.domain is None or self.client is None or self.secret is None:
                return {'code': -1, 'message': 'OpenApi 环境变量[DOMAIN]或[CLIENT]获取失败'}
            url = self.domain + "/open/auth/token?client_id=" + self.client + "&client_secret=" + self.secret
            resp = requests.get(url).json()
            if resp['code'] == 200:
                self.token = resp['data']['token']
            return resp
        except Exception as ex:
            return {'code': -1, 'message': 'OpenApi 获取token出错' + str(ex)}

    # 获取所有环境变量
    def get_envs(self):
        if self.token is None:
            return {'code': -1, 'message': 'OpenApi token不存在 '}
        url = self.domain + "/open/envs"
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            resp = requests.get(url, headers=headers).json()
            return resp
        except Exception as ex:
            return {'code': -1, 'message': 'OpenApi 获取envs出错' + str(ex)}

    # 更新指定ID环境变量
    def update_envs(self, id, name, value, remarks):
        if self.token is None:
            return {'code': -1, 'message': 'OpenApi token不存在 '}
        url = self.domain + "/open/envs"
        params = {
            'id': id,
            'name': name,
            'value': value,
            'remarks': remarks,
        }
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }
        try:
            resp = requests.put(url, headers=headers, data=json.dumps(params)).json()
            return resp
        except Exception as ex:
            return {'code': -1, 'message': 'OpenApi 获取envs出错' + str(ex)}


# 一言 APi
class OneSay:

    def get_(self):
        url = "https://v1.hitokoto.cn/?c=k&c=i&c=d&min_length=10"
        try:
            resp = requests.get(url).json()
            if 'id' not in resp:
                return {'code': -1, 'message': 'OneSay 获取句子出错'}

            if self.check_filter(resp['hitokoto']) is True:
                return {'code': -1, 'message': 'OneSay 句子包含敏感词'}

            data = {
                'title': f"[分享]{resp['hitokoto']}",
                'content': f"{resp['hitokoto']}————{resp['from']}"
            }
            return {'code': 1, 'message': 'OneSay 获取成功', 'data': data}
        except Exception as ex:
            return {'code': -1, 'message': 'OneSay 获取envs出错' + str(ex)}

    @staticmethod
    def check_filter(text):
        keywords = ["暴力", "色情", "其他关键字"]
        for v in keywords:
            if v.strip() in text:
                return True
        return False


# 时间转换
class Now:
    @staticmethod
    def to_time(date, pattern="%Y-%m-%d %H:%M:%S"):
        # 先转换为时间数组
        timeArray = time.strptime(date, pattern)
        # 转换为时间戳
        return int(time.mktime(timeArray))

    @staticmethod
    def to_date(t, pattern="%Y-%m-%d %H:%M:%S"):
        # 先转换为时间数组
        timeArray = time.localtime(t)
        # 转换为日期文本
        return time.strftime(pattern, timeArray)


# 对接控制台
class UserServer:
    token, private_key, domain, account, password = [None, None, None, None, None]
    headers = {}

    # 初始化
    def __init__(self):
        try:
            result = env.get_env('USER_SERVER')
            if result['code'] != 1:
                Setting('UserServer').msg_(result['code'], result['msg'])
            else:
                self.domain, self.account, self.password = result['data'][0]['value'].split('|')
        except Exception as ex:
            Setting('UserServer').msg_(-1, '环境变量获取失败 ' + str(ex))

    def get_token(self):
        try:
            if self.domain is None or self.account is None or self.password is None:
                return {'code': -1, 'message': 'UserServer 环境变量[USER_SERVER]获取失败'}
            url = self.domain + "/api/auth/getToken"
            params = {
                'user': self.account,
                'pasw': sha1(self.password.encode("utf-8")).hexdigest()
            }
            resp = requests.post(url, data=params).json()
            if resp['code'] != 200:
                return resp
            data = resp['data']['token'].encode("utf-8")
            self.token = sha1(md5(data).hexdigest().encode("utf-8")).hexdigest()
            self.private_key = resp['data']['private_key']
            self.headers = {
                'Token': self.token,
                'User': self.account,
                'Content-Type': 'application/json'
            }
            return resp
        except Exception as ex:
            return {'code': -1, 'message': 'UserServer 获取token出错'}

    def get_user_list(self, tips):
        try:
            if self.domain is None or self.account is None or self.password is None:
                return {'code': -1, 'message': 'UserServer 环境变量[USER_SERVER]获取失败'}
            url = self.domain + "/api/Cron/get_user_list"
            params = {
                'tips': tips,
            }
            resp = requests.post(url, data=json.dumps(params), headers=self.headers).json()
            return resp
        except Exception as ex:
            return {'code': -1, 'message': '[get_user_list] 用户列表失败'}

    def send_message(self, qq, content):
        try:
            if self.domain is None or self.account is None or self.password is None:
                return {'code': -1, 'message': 'UserServer 环境变量[USER_SERVER]获取失败'}
            url = self.domain + "/api/Cron/sendMessage"
            params = {
                'qq': qq,
                'content': content
            }
            resp = requests.post(url, data=params, headers=self.headers).json()
            return resp
        except Exception as ex:
            return {'code': -1, 'message': 'UserServer 获取token出错' + str(ex)}

    def submit_user_token(self, data):
        try:
            if self.domain is None or self.account is None or self.password is None:
                return {'code': -1, 'message': 'UserServer 环境变量[USER_SERVER]获取失败'}
            url = self.domain + "/api/Cron/update_user_token"
            resp = requests.post(url, data=json.dumps({'data': data}), headers=self.headers).json()
            return resp
        except Exception as ex:
            return {'code': -1, 'message': 'UserServer 更新账号token出错' + str(ex)}

    def set_task_status(self, label, status):
        try:
            if self.domain is None or self.account is None or self.password is None:
                return {'code': -1, 'message': 'UserServer 环境变量[USER_SERVER]获取失败'}
            url = self.domain + "/api/Cron/set_task_status"
            resp = requests.post(url, data=json.dumps({'label': label, 'status': status}), headers=self.headers).json()
            return resp
        except Exception as ex:
            return {'code': -1, 'message': 'UserServer 设置任务状态出错' + str(ex)}


class Sqlite:
    def __init__(self, path=env.check_sqlite_file()):
        try:
            self.connect = sqlite3.connect(path)
            self.cursor = self.connect.cursor()
        except Exception as e:
            Setting('Sqlite').msg_(-1, '连接数据库失败' + str(e))

    def query(self, sql: str) -> list:
        """查询"""
        try:
            queryResult = self.cursor.execute(sql).fetchall()
            return queryResult
        except Exception as e:
            return []
        finally:
            self.connect.commit()

    def queryDict(self, sql: str, ob) -> list:
        """调用该函数返回结果为字典形式"""
        try:
            self.cursor.row_factory = self.dictFactory
            queryResult = self.cursor.execute(sql, ob).fetchall()
            return queryResult
        except Exception as e:
            return []
        finally:
            self.connect.commit()

    def insert(self, sql: str, ob) -> bool:
        """插入数据"""
        try:
            self.cursor.execute(sql, ob)
            return True
        except Exception as e:
            return False
        finally:
            self.connect.commit()

    def update(self, sql: str, ob) -> bool:
        try:
            self.cursor.execute(sql, ob)
            return True
        except Exception as e:
            return False
        finally:
            self.connect.commit()

    def delete(self, sql: str, ob) -> bool:
        try:
            self.cursor.execute(sql, ob)
            return True
        except Exception as e:
            return False
        finally:
            self.connect.commit()

    def closeDB(self) -> bool:
        try:
            self.cursor.close()
            self.connect.close()
            return True
        except Exception as e:
            return False

    @staticmethod
    def dictFactory(cursor, row):
        """将sql查询结果整理成字典形式"""
        d = {}
        for index, col in enumerate(cursor.description):
            d[col[0]] = row[index]
        return d
