#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 6 * * ?
new Env('易班-Cookie更新');
tag: yb_cookie
"""
from common import OpenApi, YiBan, UserServer

if __name__ == '__main__':
    api = OpenApi()
    us = UserServer()
    result = api.get_token()
    if result['code'] != 200:
        print(result['message'])
        exit(0)
    result = api.get_envs()
    if result['code'] != 200:
        print(result['message'])
        exit(0)

    user_list = []
    for i in result['data']:
        # 遍历 'YB_COOKIE'
        if i['name'] not in 'YB_COOKIE' or i['status'] == 1:
            continue

        yb = YiBan()
        try:
            lit = i['remarks'].split('|')
            account = lit[0]
            password = lit[1]
            result = yb.chrome_login(account, password)

            temp = {
                'name': i['name'],
                'remarks': i['remarks'],
                'id': i['id'],
            }

            if result['code'] != 200:
                temp['value'] = i['value']
                temp['status'] = 2
                user_list.append(temp)
                print('Cookie: 登录失败 %s %s' % (account, result['message']))
                continue
            yiban_token = f'yiban_user_token={result["yiban_user_token"]};'
            result = api.update_envs(i['id'], i['name'], yiban_token, i['remarks'])
            temp['value'] = yiban_token
            temp['status'] = 0
            user_list.append(temp)
            print('Cookie: 更新成功 user: %s token: %s' % (account, yiban_token))
        except Exception as ex:
            print('Cookie: 更新失败 ' + i['remarks'] + str(ex))

    # 提交用户服务端
    result = us.get_token()
    if result['code'] != 1:
        print(result['msg'])
        exit(0)

    result = us.submit_user_token(user_list)
    print('UserServer:', result['msg'])
    print('Cookie: 更新完成。')
