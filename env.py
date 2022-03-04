#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import requests

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
    AppVersion = '5.0.2'

    # 适配各种平台环境cookie
    @staticmethod
    def check_file():
        if os.path.exists('/ql/config/env.sh'):
            return '/ql/config/env.sh'
        elif os.path.exists('/ql/config/cookie.sh'):
            return '/ql/config/env.sh'

    # 获取指定 环境变量
    def get_env(self, name):
        try:
            if os.path.exists(self.check_file()) is False:
                return {'code': -1, 'msg': '当前环境青龙面板旧版'}
            if name in os.environ:
                cookies = os.environ[name]
                return {'code': 1, 'msg': '获取成功', 'data': cookies.split('&')}
            return {'code': -1, 'msg': '获取变量失败'}
        except Exception as ex:
            return {'code': -2, 'msg': "获取变量失败 " + str(ex)}
