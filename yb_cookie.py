#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 6 * * ?
new Env('易班-Cookie更新');
"""
from common import OpenApi, YiBan

if __name__ == '__main__':
    api = OpenApi()
    result = api.get_token()
    if result['code'] != 200:
        print(result['massage'])
        exit(0)
    result = api.get_envs()
    if result['code'] != 200:
        print(result['massage'])
        exit(0)

    for i in result['data']:
        # 遍历 'YB_COOKIE'
        if i['name'] not in 'YB_COOKIE':
            continue

        yb = YiBan()
        try:
            lit = i['remarks'].split('|')
            account = lit[0]
            password = lit[1]
            result = yb.chrome_login(account, password)
            if result['code'] != 200:
                print('Cookie: 登录失败 %s %s' % (account, result['message']))
                continue
            yiban_token = f'yiban_user_token={result["yiban_user_token"]};'
            result = api.update_envs(i['id'], i['name'], yiban_token, i['remarks'])
            print('Cookie: 更新成功 user: %s token: %s' % (account, yiban_token))
        except Exception as ex:
            print('Cookie: 更新失败 ' + i['remarks'] + str(ex))
