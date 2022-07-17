#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 8 * * ?
new Env('易班-易喵喵');
tag: yb_miaomiao
"""
import json
import random
import threading
import requests
from time import sleep
from common import YiBan, OneSay, Setting, Env

YB_CONTENT = []
one = OneSay()
GET_ONE = True
comment_interval = 70  # 评论间隔
advanced_interval = 70  # 发布间隔

label = 'yb_miaomiao'
env = Env(label)
st = Setting(label)


def get_mm_list(ck, sz):
    url = "https://mm.yiban.cn/news/index/index3?offset=6&size=" + str(sz)
    headers = {
        'Origin': 'https://mm.yiban.cn',
        'Host': 'mm.yiban.cn',
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': env.UserAgent2,
        'Cookie': ck
    }
    try:
        resp = requests.get(url=url, headers=headers).json()
        return {'code': int(resp['code']), 'msg': resp['message'], 'data': resp['data']}
    except Exception as ex:
        return {'code': -1, 'msg': '易喵喵文章列表获取失败' + str(ex)}


def mm_comment(ls, ck, pl):
    # 评论数量
    num = len(pl) - 1
    for n in ls:
        comment_id = n['id']
        consume = 0.0
        for i in ck:
            comment = pl[random.randint(0, num)] + str(random.randint(0, 9999))
            url = "https://mm.yiban.cn/news/comment/add?recommend_type=3"
            params = {
                'id': comment_id,
                'comment': comment,
            }
            headers = {
                'Origin': 'https://mm.yiban.cn',
                'Host': 'mm.yiban.cn',
                'Content-Type': 'application/json;charset=UTF-8',
                'User-Agent': env.UserAgent,
                'Cookie': i['cookie']
            }
            try:
                resp = requests.post(url=url, data=json.dumps(params), headers=headers)
                consume += resp.elapsed.total_seconds() if resp.elapsed.total_seconds() > 0 else 0
                resp = resp.json()
                st.msg_(resp['code'], '[评论] %s' % resp['message'], data={'comment': comment, 'type': 'comment'}, phone=i['account'])
                # 有时候没有id
                if int(resp['code']) == 200 and resp['data'] != '':
                    mm_del_comment(resp['data']['id'], resp['data']['News_id'], i['cookie'], i['account'])
            except Exception as ex:
                st.msg_(-1, '[评论] %s ' % str(ex), data={'comment': comment, 'type': 'comment'}, phone=i['account'])
        s = 1 if consume > comment_interval else round(comment_interval - consume, 3)
        sleep(s)


def mm_del_comment(cid, nid, ck, users):
    url = 'https://mm.yiban.cn/news/comment/del'
    params = {
        'id': cid,
        'newsid': nid
    }
    headers = {
        'Origin': 'https://mm.yiban.cn',
        'Host': 'mm.yiban.cn',
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': env.UserAgent,
        'Cookie': ck
    }
    try:
        resp = requests.post(url, data=json.dumps(params, indent=2), headers=headers).json()
        st.msg_(resp['code'], '[删除评论] %s' % resp['message'], phone=users)
    except Exception as ex:
        st.msg_(-1, '[删除评论] %s' % str(ex), phone=users)


def mm_add(ck):
    ck = ck.copy()
    global GET_ONE
    global YB_CONTENT
    while True:
        if len(YB_CONTENT):
            sleep(5)
            break
    for n in range(3):
        consume = 0.0
        for k, v in enumerate(ck):
            num = random.randint(0, len(YB_CONTENT) - 1)
            content = YB_CONTENT[num]['title'] + '[' + str(random.randint(10, 99)) + ']'
            url = 'https://mm.yiban.cn/article/index/add'
            data = {
                'content': (None, content),
            }
            headers = {
                'Origin': 'https://mm.yiban.cn',
                'Host': 'mm.yiban.cn',
                'User-Agent': env.UserAgent,
                'Cookie': v['cookie']
            }
            try:
                resp = requests.post(url, files=data, headers=headers)
                consume += resp.elapsed.total_seconds() if resp.elapsed.total_seconds() > 0 else 0
                resp = resp.json()
                st.msg_(resp['code'], '[发贴] %s' % resp['message'], data={'content': content, 'type': 'add'}, phone=v['account'])
                if resp['code'] == 200:
                    ck.pop(k)
            except Exception as ex:
                st.msg_(-1, '[发贴] %s' % str(ex), data={'content': content, 'type': 'add'}, phone=v['account'])

        if len(ck) == 0:
            break
        s = 1 if consume > advanced_interval else round(advanced_interval - consume, 3)
        sleep(s)
    GET_ONE = False


def get_one():
    global YB_CONTENT
    global GET_ONE
    while GET_ONE:
        ret = one.get_()
        if ret['code'] == 1:
            YB_CONTENT.append({
                'title': ret['data']['title'],
                'content': ret['data']['content'],
            })
        sleep(2)


# 脚本
if __name__ == '__main__':
    list_num = 10
    # 获取用户Cookie
    result = env.get_env('YB_COOKIE')
    if result['code'] != 1:
        st.msg_(-999, result['msg'])
        exit(0)

    cookies = []
    # 检查 token, 获取评论 token
    for i in result['data']:

        lit = i['remarks'].split('|')
        if len(lit) != 2:
            st.msg_(-1, '账号密码分割出错 ', data={'value': i['remarks']})
            break
        account = lit[0]

        for count in range(3):
            try:
                check = YiBan.check_token(i['value'])
                if check['code'] != 200:
                    st.msg_(check['code'], 'token失效 %s' % (check['msg']), phone=account)
                    continue
                temp = {
                    'userId': check['data']['userId'],
                    'cookie': i['value'] + i['value'].replace('yiban_user_token', 'loginToken'),,
                    'account': account
                }
                cookies.append(temp)
                break
            except Exception as ex:
                st.msg_(-1, 'token验证失败 %s' % ex, phone=account)

    if len(cookies) < 1:
        st.msg_(-999, '可用cookie为空。')
        exit(0)

    # 获取易喵喵列表 list_num 条评论
    lst = []
    for count in range(3):
        result = get_mm_list(cookies[0]['cookie'], list_num)
        if result['code'] != 200:
            st.msg_(result['code'], '获取易喵喵列表失败 %s ' % (result['msg']), phone=cookies[0]['account'])
            continue
        lst = result['data']['list']
        break

    if len(lst) == 0:
        st.msg_(-1, '易喵喵评论列表为空')

    # 获取评论发布内容
    result = env.get_env('YB_COMMENT')
    if result['code'] != 1:
        result = {'data': ['打卡打卡打卡打卡打卡']}
    yb_comment = result['data'][0]['value'].split('|')

    # result = env.get_env('YB_CONTENT')
    # if result['code'] != 1:
    #     result = {'data': ['坚持坚持再坚持，努力努力再努力！']}
    # yb_content = result['data'][0].split('|')

    try:
        # 评论
        _comment = threading.Thread(target=mm_comment, args=(lst, cookies, yb_comment,))
        # 发帖
        _add = threading.Thread(target=mm_add, args=(cookies,))
        # 一言
        _one = threading.Thread(target=get_one)

        _comment.start()
        _one.start()
        _add.start()

        _comment.join()
        _add.join()
    except Exception as ex:
        st.msg_(-1, '易喵喵 %s' % str(ex))

    st.msg_(2000, f"[{label}]执行完成。")
    exit(0)
