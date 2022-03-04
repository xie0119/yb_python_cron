#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron: 0 20 6-7 * * ?
new Env('易班-易伴打卡');
RandomDelay="300"
"""

import json
import base64
import requests
from env import Env
from common import YbLogin
from common import Captcha

UserAgent = Env.UserAgent
AppVersion = Env.AppVersion
yb = YbLogin()
ct = Captcha()


# 打卡
def set_sign(account, access_token, http_waf_cookie):
    """
    打卡
    :return:
    """
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'AppVersion': AppVersion,
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'User-Agent': UserAgent,
        'loginToken': access_token,
        'Cookie': 'client=iOS; loginToken=' + access_token + '; yibanM_user_token=' + access_token + '; http_waf_cookie=' + http_waf_cookie
    }

    session = requests.session()
    # 先登录
    session.get("http://f.yiban.cn/iapp642231", headers=headers)
    # session.get("https://f.yiban.cn/iapp/index?act=iapp642231", headers=headers)

    cookies = 'SERVERID=' + session.cookies.get('SERVERID') + '; client=iOS; PHPSESSID=' + session.cookies.get(
        'PHPSESSID')

    # 验证码获取链接
    captcha_url = "https://daka.yibangou.com/index.php?m=Wap&c=Index&a=yanzhengma&res=62"
    headers = {
        'Host': 'daka.yibangou.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookies,
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    # 跑 3 次防止验证码识别错误次数过多
    for count in range(3):
        images = requests.get(captcha_url, headers=headers)

        base64_image = base64.encodebytes(images.content).decode('UTF-8').replace("\n", "")  # data:image/png;base64,
        capt = ct.base64_api(base64_image)

        if capt['code'] != 1:
            return {'code': -1, 'msg': capt['msg']}

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
            'Cookie': cookies,
        }
        params = {'yzm': capt['data']}
        resp = requests.post("https://daka.yibangou.com/index.php?m=Wap&c=Ajax&a=daka", data=params,
                             headers=headers).text
        result = json.loads(resp)

        if result['code'] == 1:
            ct.report_error(capt['id'])
            print('状态 %s %s %s' % (account, result['code'], '验证码错误'))
        elif result['code'] == 2:
            return {'code': result['code'], 'msg': '操作失败'}
        elif result['code'] == 4:
            return {'code': result['code'], 'msg': '已打卡'}
        elif result['code'] == 5:
            return {'code': result['code'], 'msg': '打卡成功'}
        elif result['code'] == 6:
            return {'code': result['code'], 'msg': '挑战成功'}
        else:
            return {'code': result['code'], 'msg': '未知状态码'}
    return {'code': -1, 'msg': '验证码错误次数过多'}


# 脚本开始
if __name__ == '__main__':
    result = Env().get_env('YB_ACCOUNT')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)
    for i in result['data']:
        account, password, money = i.split('|', 2)

        # 登录账号
        result = yb.login(account, password)
        if result['response'] != 100:
            print('状态 %s %s %s' % (account, result['response'], result['message']))
            continue

        result = set_sign(account, result['data']['access_token'], result['http_waf_cookie'])
        print('状态 %s %s %s' % (account, result['code'], result['msg']))
