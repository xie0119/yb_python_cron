#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 6 * * ?
new Env('易班-Cookie更新');
tag: yb_cookie
"""

from common import YiBan, UserServer, Setting, Env, Sqlite

label = 'yb_cookie'
env = Env(label)
st = Setting(label)


if __name__ == '__main__':
    result = env.get_env('YB_COOKIE')
    if result['code'] != 1:
        st.msg_(-999, result['msg'])
        exit(0)

    db = Sqlite()

    user_list = []
    for i in result['data']:
        # 遍历 'YB_COOKIE'
        if i['name'] not in 'YB_COOKIE' or i['status'] != 0:
            continue

        yb = YiBan()

        lit = i['remarks'].split('|')
        if len(lit) != 2:
            st.msg_(-1, '账号密码分割出错 ', data={'value': i['remarks']})
            break
        account = lit[0]
        password = lit[1]
        yiban_token = i['value']
        status = 0
        for count in range(3):
            try:
                result = yb.chrome_login(account, password)
                if result['code'] == 711:
                    st.msg_(result['code'], '第 %d次登录失败 %s' % (count, result['message']), data={'loginCount': count}, phone=account)
                    continue

                if result['code'] != 200:
                    st.msg_(result['code'], '登录失败 %s' % (result['message']), phone=account)
                    status = 2
                    continue
                status = 0
                yiban_token = f'yiban_user_token={result["yiban_user_token"]};'

                temp = {
                    'name': i['name'],
                    'value': yiban_token,
                    'remarks': i['remarks'],
                    'id': i['id'],
                    'status': status
                }
                user_list.append(temp)
                st.msg_(result['code'], result['message'], data=result['data'], phone=account)

                sql = "UPDATE Envs SET value = ? WHERE id = ?"
                val = [yiban_token, i['id']]
                db.update(sql, val)
                break
            except Exception as ex:
                st.msg_(-1, '更新Cookie失败 ', phone=account)


    db.closeDB()

    # 提交用户服务端
    us = UserServer()
    result = us.get_token()
    if result['code'] != 200:
        st.msg_(-999, result['message'])
        exit(0)

    result = us.submit_user_token(user_list)
    st.msg_(result['code'], "[cookie同步]" + result['message'])

    st.msg_(2000, f"[{label}]执行完成。")
    exit(0)

