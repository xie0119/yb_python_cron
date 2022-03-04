#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 8 * * ?
new Env('易班-每日签到');
RandomDelay="300"
"""

import re
import json
import requests
from env import Env

UserAgent = Env.UserAgent2


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
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        resp = requests.post(url=url, data=param, verify=False, headers=headers, timeout=60).text
        resp = json.loads(resp)
        return {'code': int(resp['code']), 'msg': resp['message']}
    except Exception:
        return {'code': -1, 'msg': '签到失败'}


if __name__ == '__main__':
    result = Env().get_env('YB_COOKIE')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)
    for i in result['data']:
        try:
            token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i)[0]
            result = set_sign(i)
            print('状态 token:%s %s %s' % (token, result['code'], result['msg']))
        except Exception as ex:
            print('状态 %s' % ex)
