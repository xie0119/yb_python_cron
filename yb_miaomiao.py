#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 8 * * ?
new Env('易班-易喵喵');
tag: yb_miaomiao
"""
import json
import random
import re
import threading

import requests
from env import Env
from time import time, sleep
from common import YiBan, OneSay

env = Env()
YB_CONTENT = []
one = OneSay()
GET_ONE = True


def get_mm_list(ck, sz):
    url = "https://mm.yiban.cn/news/index/index3?offset=10&size=" + str(sz)
    headers = {
        'Origin': 'https://mm.yiban.cn',
        'Host': 'mm.yiban.cn',
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': env.UserAgent,
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
            url = "https://mm.yiban.cn/news/comment/add?recommend_type=3"
            params = {
                'id': comment_id,
                'comment': pl[random.randint(0, num)] + str(random.randint(0, 9999)),
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
                consume += resp.elapsed.total_seconds()
                resp = resp.json()
                print('id:%s msg:喵喵评论 %s token:%s ' % (i['userId'], resp['message'], i['token']))
                # 有时候没有id 烦
                if int(resp['code']) == 200 and resp['data'] != '':
                    mm_del_comment(resp['data']['id'], resp['data']['News_id'], i['userId'], i['cookie'], i['token'])
            except Exception as ex:
                print('id:%s msg:喵喵评论 %s token:%s ' % (i['userId'], str(ex), i['token']))
        s = 0.5 if consume > 60 else round(62 - consume, 3)
        sleep(s)
    print('易喵喵 %s' % '评论完成')


def mm_del_comment(cid, nid, uid, ck, tk):
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
        print('id:%s msg:删除评论 %s token:%s' % (uid, resp['message'], tk))
    except Exception as ex:
        print('id:%s msg:社区评论 %s token:%s' % (uid, str(ex), tk))


def mm_add(ck):
    global YB_CONTENT
    while True:
        if len(YB_CONTENT):
            sleep(5)
            break
    for n in range(3):
        consume = 0.0
        for v, k in ck:
            num = random.randint(0, len(YB_CONTENT) - 1)
            url = 'https://mm.yiban.cn/article/index/add'
            data = {
                'content': (None, YB_CONTENT[num]['title']),
            }
            headers = {
                'Origin': 'https://mm.yiban.cn',
                'Host': 'mm.yiban.cn',
                'User-Agent': env.UserAgent,
                'Cookie': v['cookie']
            }
            try:
                resp = requests.post(url, files=data, headers=headers)
                consume += resp.elapsed.total_seconds()
                resp = resp.json()
                print('id:%s msg:易喵喵发贴 %s token:%s' % (v['userId'], resp['message'], v['token']))
                if resp['code'] == 200:
                    ck.pop(k)
            except Exception as ex:
                print('id:%s msg:易喵喵发帖 %s token:%s ' % (v['userId'], str(ex), v['token']))
        if len(ck) == 0:
            break
        s = 0.5 if consume > 60 else round(62 - consume, 3)
        sleep(s)
    print('易喵喵 %s' % '发帖完成')


def get_one():
    global YB_CONTENT
    global GET_ONE
    while GET_ONE:
        ret = one.get_()
        if ret['code']:
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
        print(result['msg'])
        exit(0)

    cookies = []
    # 检查 token, 获取评论 token
    for i in result['data']:
        try:
            token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i)[0]
            check = YiBan.check_token(i)
            if check['code'] != 200:
                print('token失效 %s %s' % (token, check['msg']))
                continue
            temp = {
                'userId': check['data']['userId'],
                'token': token,
                'cookie': i,
            }
            cookies.append(temp)
        except Exception as ex:
            print('状态 %s' % ex)

    # 获取易喵喵列表 5 条评论
    result = get_mm_list(cookies[0]['cookie'], list_num)
    if result['code'] != 200:
        print('获取微社区列表失败 %s ' % (result['msg']))
        exit()
    list = result['data']['list']

    # 获取评论发布内容
    result = env.get_env('YB_COMMENT')
    if result['code'] != 1:
        result = {'data': ['打卡打卡打卡打卡打卡']}
    yb_comment = result['data'][0].split('|')

    # result = env.get_env('YB_CONTENT')
    # if result['code'] != 1:
    #     result = {'data': ['坚持坚持再坚持，努力努力再努力！']}
    # yb_content = result['data'][0].split('|')

    try:
        # 评论
        _comment = threading.Thread(target=mm_comment, args=(list, cookies, yb_comment,))
        # 发帖
        _add = threading.Thread(target=mm_add, args=(cookies,))
        # 一言
        _one = threading.Thread(target=get_one)

        _comment.start()
        _one.start()
        _add.start()

        _comment.join()
        _add.join()
        GET_ONE = False
    except Exception as ex:
        print('易喵喵 %s' % str(ex))
    print('任务结束 time:%f' % time())
