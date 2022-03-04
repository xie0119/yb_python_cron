#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 0/1 * * ?
new Env('易班-Cookie校验');
"""

import re
import json
import requests
from env import Env

UserAgent = Env.UserAgent2


# 检测cookie是否正确
def login(cookie):
    url = 'https://www.yiban.cn/ajax/my/getLogin'
    headers = {
        'Cookie': cookie,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Connection': 'keep-alive',
        'Referer': 'https://www.yiban.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'www.yiban.cn',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        resp = requests.get(url=url, verify=False, headers=headers, timeout=60).text
        resp = json.loads(resp)
        return {'code': int(resp['code']), 'msg': resp['message'], 'data': resp['data'] if (resp['data']) else None}
    except Exception:
        return {'code': -1, 'msg': '签到失败'}


if __name__ == '__main__':
    result = Env().get_env('YB_COOKIE')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)
    for i in result['data']:
        result = login(i)
        if result['code'] != 200:
            pattern = re.search(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i, re.M | re.I)
            print('Cookie失效 %d %s %s' % (result['code'], result['msg'], pattern.group() if pattern else None))
        else:
            print('验证成功 id:%d nick:%s token:%s' % (result['data']['user']['id'], result['data']['user']['nick'], result['data']['user']['token']))
