#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 7 * * ?
new Env('易班-微社区');
tag: yb_weishequ
"""
import re
import json
import random
import threading
import requests
from env import Env
from time import time, sleep
from common import YiBan, OneSay

env = Env()
YB_CONTENT = []
one = OneSay()
GET_ONE = True


def get_token(cookie):
    # 获取csrfToken
    url = 'https://s.yiban.cn/api/security/getToken'
    headers = {
        'Cookie': cookie,
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 's.yiban.cn',
        'User-Agent': env.UserAgent2,
    }
    try:
        resp = requests.post(url=url, headers=headers)
        ret = json.loads(resp.text)
        if ret['status']:
            data = {
                'csrfToken': ret['data']['csrfToken'],
                'PHPSESSID': resp.cookies.get('PHPSESSID')
            }
        else:
            data = None
        return {'code': int(ret['code']), 'msg': ret['message'], 'data': data}
    except Exception as ex:
        return {'code': -1, 'msg': '获取csrfToken失败' + str(ex)}


def get_list_by_board(offset, count):
    url = "https://s.yiban.cn/api/forum/getListByBoard?"
    params = {
        'offset': offset,
        'count': count,
        'boardId': 'EqGilbKmdn62Ka3',
        'orgId': '2006794'  # 杂谈
    }
    headers = {
        'User-Agent': env.UserAgent2
    }
    try:
        resp = requests.get(url, params=params, headers=headers).json()
        return {'code': int(resp['code']), 'msg': resp['message'], 'data': resp['data']}
    except Exception as ex:
        return {'code': -1, 'msg': str(ex)}


# 点赞
def set_love(ls, ck):
    for n in ls:
        post_id = n['id']
        user_id = n['user']['id']
        consume = 0.0
        for i in ck:
            url = "https://s.yiban.cn/api/post/thumb"
            params = {
                'action': 'up',
                'postId': post_id,
                'userId': user_id
            }
            headers = {
                'User-Agent': env.UserAgent2,
                'Cookie': i['cookie']
            }
            try:
                resp = requests.post(url, data=json.dumps(params, indent=2), headers=headers)
                consume += resp.elapsed.total_seconds()
                resp = resp.json()
                print('id:%s msg:社区点赞 %s token:%s' % (i['userId'], resp['message'], i['token']))
            except Exception as ex:
                print('id:%s msg:社区点赞 %s token:%s' % (i['userId'], str(ex), i['token']))
        s = 0.5 if consume > 3.5 else round(3.5 - consume, 3)
        sleep(s)
    print('微社区 %s' % '点赞完成')


# 评论
def set_comment(ls, ck, pl):
    # 评论数量
    num = len(pl) - 1
    for n in ls:
        post_id = n['id']
        user_id = n['user']['id']
        consume = 0.0
        for i in ck:
            url = 'https://s.yiban.cn/api/post/comment'
            params = {
                'postId': post_id,
                'comment': pl[random.randint(0, num)] + str(random.randint(0, 9999)),
                'userId': user_id,
                'csrfToken': i['csrfToken']
            }
            headers = {
                'User-Agent': env.UserAgent2,
                'Cookie': i['cookie']
            }
            try:
                resp = requests.post(url, data=json.dumps(params, indent=2), headers=headers)
                consume += resp.elapsed.total_seconds()
                resp = resp.json()
                print('id:%s msg:社区评论 %s token:%s' % (i['userId'], resp['message'], i['token']))
                if resp['status']:
                    del_comment(resp['data'], i['userId'], i['cookie'], i['token'])
            except Exception as ex:
                print('id:%s msg:社区评论 %s token:%s' % (i['userId'], str(ex), i['token']))
        s = 0.5 if consume > 60 else round(62 - consume, 3)
        sleep(s)
    print('微社区 %s' % '评论完成')


def del_comment(post_id, uid, ck, tk):
    url = 'https://s.yiban.cn/api/post/delComment'
    params = {
        'commentId': post_id,
    }
    headers = {
        'User-Agent': env.UserAgent2,
        'Cookie': ck
    }
    try:
        resp = requests.post(url, data=json.dumps(params, indent=2), headers=headers).json()
        print('id:%s msg:删除评论 %s token:%s' % (uid, resp['message'], tk))
    except Exception as ex:
        print('id:%s msg:社区评论 %s token:%s' % (uid, str(ex), tk))


# 发帖
def set_advanced(ck, count):
    global YB_CONTENT

    while True:
        if len(YB_CONTENT):
            sleep(5)
            break

    # 数量
    for n in range(count):
        consume = 0.0
        for i in ck:
            num = random.randint(0, len(YB_CONTENT) - 1)
            url = 'https://s.yiban.cn/api/post/advanced'
            params = {
                'channel': [
                    {
                        "boardId": "EqGilbKmdn62Ka3",
                        "orgId": 2006794
                    }
                ],  # 杂谈
                'content': "<p>" + YB_CONTENT[num]['content'] + "<p>",
                'hasVLink': 0,
                'isPublic': 1,  # 公开
                'summary': '',
                'thumbType': 1,
                'title': YB_CONTENT[num]['title']
            }
            headers = {
                'User-Agent': env.UserAgent2,
                'Cookie': i['cookie'],
                'Host': 's.yiban.cn'
            }
            try:
                resp = requests.post(url, data=json.dumps(params), headers=headers)
                consume += resp.elapsed.total_seconds()
                resp = resp.json()
                print('id:%s msg:社区发帖 %s token:%s' % (i['userId'], resp['message'], i['token']))
            except Exception as ex:
                print('id:%s msg:社区发帖 %s token:%s' % (i['userId'], str(ex), i['token']))
        s = 0.5 if consume > 60 else round(62 - consume, 3)
        sleep(s)
    print('微社区 %s' % '发帖完成')


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
    list_num = 35
    add_num = 20
    # 获取微社区列表
    result = get_list_by_board(10, list_num)
    if result['code'] != 200:
        print('获取微社区列表失败 %s ' % (result['msg']))
        exit()
    list = result['data']['list']

    # 获取评论发布内容
    result = env.get_env('YB_COMMENT')
    if result['code'] != 1:
        result = {'data': ['打卡打卡打卡打卡']}
    yb_comment = result['data'][0].split('|')

    # result = env.get_env('YB_CONTENT')
    # if result['code'] != 1:
    #     result = {'data': ['坚持坚持再坚持，努力努力再努力！']}
    # yb_content = result['data'][0].split('|')

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
            # 获取评论 csrfToken
            result = get_token(i)
            if result['code'] != 200:
                print('csrfToken获取失败 %s %s' % (token, result['msg']))
                continue
            temp = {
                'userId': check['data']['userId'],
                'token': token,
                'csrfToken': result['data']['csrfToken'],
                'cookie': i + '; PHPSESSID=' + result['data']['PHPSESSID'],
            }
            cookies.append(temp)
        except Exception as ex:
            print('微社区 %s' % ex)
    try:
        # 点赞
        _love = threading.Thread(target=set_love, args=(list, cookies,))
        # 评论
        _comment = threading.Thread(target=set_comment, args=(list, cookies, yb_comment,))
        # 发帖
        _advanced = threading.Thread(target=set_advanced, args=(cookies, add_num,))
        # 一言
        _one = threading.Thread(target=get_one)

        _love.start()
        _comment.start()
        _one.start()
        _advanced.start()

        _love.join()
        _comment.join()
        _advanced.join()
        GET_ONE = False
    except Exception as ex:
        print('微社区 %s' % str(ex))
    print('任务结束 time:%f' % time())
