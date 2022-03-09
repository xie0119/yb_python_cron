#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 8 * * ?
new Env('易班-每日签到');
RandomDelay="300"
"""

import re
import requests
from env import Env

env = Env()


def set_sign(cookie):
    url = 'https://www.yiban.cn/ajax/checkin/answer'
    param = {
        "optionid[]": 22571,
        "input": "",
    }
    headers = {
        'Cookie': cookie,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Connection': 'keep-alive',
        'Referer': 'https://www.yiban.cn/user/info/index',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'www.yiban.cn',
        'User-Agent': env.UserAgent2,
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        resp = requests.post(url=url, data=param, verify=False, headers=headers, timeout=60).json()
        return {'code': int(resp['code']), 'msg': resp['message']}
    except Exception as ex:
        return {'code': -1, 'msg': '签到失败' + str(ex)}


if __name__ == '__main__':
    result = env.get_env('YB_COOKIE')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)
    for i in result['data']:
        try:
            token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i)[0]
            result = set_sign(i)
            print('每日签到 token:%s %s %s' % (token, result['code'], result['msg']))
        except Exception as ex:
            print('每日签到 %s' % ex)
