#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron: 0 0 16 * * ?
new Env('易班-易伴参与挑战');
RandomDelay="300"
"""

import json
import re
import requests
from env import Env
from common import YbLogin

UserAgent = Env.UserAgent
AppVersion = Env.AppVersion
yb = YbLogin()


# 将支付金额转换为对应ID
def get_data_id(num):
    # 网薪: id
    return {'10': '3', '50': '5', '100': '6', '300': '10', '500': '7', '800': '9'}[num]


# 支付网薪
def payment(access_token, http_waf_cookie, data_id):
    """
    支付网薪

    data_id:
    3  = 10网薪（送20网薪体验金）；
    5  = 50网薪（送20网薪体验金）；
    6  = 100网薪（送20网薪体验金）；
    10 = 300网薪（送20网薪体验金）；
    7  = 500网薪（送20网薪体验金）；
    9  = 800网薪（送20网薪体验金）；
    :return:
    """

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'AppVersion': AppVersion,
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'loginToken': access_token,
        'User-Agent': UserAgent,
        'Cookie': 'client=iOS; loginToken=' + access_token + '; yibanM_user_token=' + access_token + '; http_waf_cookie=' + http_waf_cookie
    }

    session = requests.session()
    # 先登录
    session.get("http://f.yiban.cn/iapp642231", headers=headers)
    # session.get("https://f.yiban.cn/iapp/index?act=iapp642231", headers=headers)

    cookies = 'SERVERID=' + session.cookies.get('SERVERID') + '; client=iOS; PHPSESSID=' + session.cookies.get(
        'PHPSESSID')

    # 下单地址
    pay_url = "https://daka.yibangou.com/index.php?m=Wap&c=User&a=chongzhi&dataname=1&dataid=" + data_id

    headers = {
        'Host': 'daka.yibangou.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': cookies,
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Referer': 'https://daka.yibangou.com/index.php?m=Wap&c=Index&a=index&res=29',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    resp = requests.get(pay_url, headers=headers).text

    dataid = re.findall(r'name="dataid" value="(.*?)"', resp)[0]
    dataname = re.findall(r'name="dataname" value="(.*?)"', resp)[0]
    danhao = re.findall(r'name="danhao" value="(.*?)"', resp)[0]

    params = {
        "danhao": danhao,
        "dataid": dataid,
        "dataname": dataname
    }
    headers = {
        'Host': 'daka.yibangou.com',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://daka.yibangou.com',
        'User-Agent': UserAgent,
        'Connection': 'keep-alive',
        'Referer': pay_url,
        'Cookie': cookies,
    }
    # print(cookies)
    resp = requests.post("https://daka.yibangou.com/index.php?m=Wap&c=Ajax&a=yibanpay", data=params,
                         headers=headers).text
    result = json.loads(resp)
    code = int(result['code'])
    if code == 200:
        return {'code': code, 'msg': '支付成功'}
    elif code == 1:
        return {'code': code, 'msg': '余额不足'}
    elif code == 2:
        return {'code': code, 'msg': '跳转首页'}
    else:
        return {'code': code, 'msg': '未知状态'}


# 脚本
if __name__ == '__main__':
    result = Env().get_env('YB_ACCOUNT')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)

    for i in result['data']:
        # 空格分割账号密码
        account, password, money = i.split('|', 2)

        # 登录账号
        result = yb.login(account, password)
        if result['response'] != 100:
            print('状态 %s %s %s' % (account, result['response'], result['message']))
            continue

        result = payment(result['data']['access_token'], result['http_waf_cookie'], get_data_id(money))
        print('状态 %s %s %s' % (account, result['code'], result['msg']))
