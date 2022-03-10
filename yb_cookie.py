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

            yiban_token = i['value']
            status = 0
            for ct in range(3):

                result = yb.chrome_login(account, password)

                if result['code'] == 711:
                    print('Cookie: 第 %d次登录失败 %s %s' % (ct, account, result['message']))
                    continue

                if result['code'] != 200:
                    print('Cookie: 登录失败 %s %s' % (account, result['message']))
                    status = 2
                    continue
                yiban_token = f'yiban_user_token={result["yiban_user_token"]};'
                result = api.update_envs(i['id'], i['name'], yiban_token, i['remarks'])
                break

            temp = {
                'name': i['name'],
                'value': yiban_token,
                'remarks': i['remarks'],
                'id': i['id'],
                'status': status
            }
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
