#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 12 * * ?
new Env('易班-网薪统计');
tag: yb_total_salary
"""
import re
import time

from env import Env
from common import YiBan, Now

env = Env()
yb = YiBan()


# 网薪统计 ck = cookie, t = 统计时间, page = 前 page * 100 条数据 由于没有查询 不建议查询超过3天前的数据
def total_salary(ck, t=time.time(), page=5):
    # 时间格式化
    d = Now.to_date(t, '%Y-%m-%d 00:00:00')
    # 再转时间戳
    start_time = Now.to_time(d)

    d = Now.to_date(t, '%Y-%m-%d 23:59:59')
    stop_time = Now.to_time(d)

    score = 0
    p = 1
    temp = []
    while p <= page:

        result = yb.get_salary(ck, p)
        if result['code'] != 100:
            return {'code': 1, 'msg': '第 ' + str(p) + '页获取失败', 'data': temp, 'amount': score,
                    'date': Now.to_date(t, '%Y-%m-%d'), }

        lens = len(result['data'])
        for n in result['data']:
            create_time = Now.to_time(n['createTime'])
            if stop_time > create_time > start_time:
                score += n['amount'] if n['amount'] > 0 else 0
                temp.append(n)
            if start_time > create_time:
                p = page
                break
            if start_time < create_time and page == p:
                page += 1
        if lens < 30:
            p = page + 1
        else:
            p += 1
    return {'code': 1, 'msg': '操作成功', 'data': temp, 'amount': score, 'date': Now.to_date(t, '%Y-%m-%d'), }


if __name__ == '__main__':

    result = env.get_env('YB_COOKIE')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)

    for i in result['data']:
        try:
            token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i)[0]
            result = total_salary(i)
            print('网薪统计 token:%s date:%s amount: %d' % (token, result['date'], result['amount']))
        except Exception as ex:
            print('网薪统计 %s %s' % (i, ex))
