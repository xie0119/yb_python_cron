#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 12 * * ?
new Env('易班-网薪统计');
tag: yb_total_salary
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
            result = yb.total_salary(i)
            print('网薪统计 token:%s date:%s amount: %d' % (token, result['date'], result['amount']))
        except Exception as ex:
            print('网薪统计 %s %s' % (i, ex))
