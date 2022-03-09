#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 10 6 * * ?
new Env('易班-每日登录');
tag: yb_every_login
"""
import re
from env import Env
from common import YiBan

env = Env()

if __name__ == '__main__':
    yb = YiBan()
    result = env.get_env('YB_COOKIE')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)

    for i in result['data']:
        try:
            token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i)[0]
            result = yb.mobile_auto_login(i)
            print('每日登录 token:%s %s %s' % (token, result['code'], result['msg']))
        except Exception as ex:
            print('每日登录 %s %s' % (i, ex))
