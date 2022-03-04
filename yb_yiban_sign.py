#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron: 0 20 6-7 * * ?
new Env('易班-易伴打卡');
RandomDelay="300"
"""

import json
import base64
import re

import requests
from env import Env
from common import Captcha

UserAgent = Env.UserAgent
AppVersion = Env.AppVersion

try:
    ct = Captcha()
except Exception as ex:
    print('请检查打码平台账号')
    exit(0)


# 打卡
def set_sign(cookie):
    """
    打卡
    :return:
    """
    try:
        url = "https://f.yiban.cn/iframe/index?act=iapp642231"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6305002e)',
            'Cookie': cookie
        }
        session = requests.session()
        session.get(url, headers=headers)

        # 验证码获取链接
        captcha_url = "https://daka.yibangou.com/index.php?m=Wap&c=Index&a=yanzhengma&res=62"
        headers = {
            'Host': 'daka.yibangou.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': UserAgent,
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        # 跑 3 次防止验证码识别错误次数过多
        for count in range(3):
            images = session.get(captcha_url, headers=headers)

            base64_image = base64.encodebytes(images.content).decode('UTF-8').replace("\n",
                                                                                      "")  # data:image/png;base64,
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
            }
            params = {'yzm': capt['data']}
            resp = session.post("https://daka.yibangou.com/index.php?m=Wap&c=Ajax&a=daka", data=params,
                                headers=headers).text
            result = json.loads(resp)

            if result['code'] == 1:
                ct.report_error(capt['id'])
                print('状态 token:%s %s %s' % (
                    re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', cookie)[0], result['code'], '验证码错误'))
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
    except Exception as ex:
        return {'code': -1, 'msg': ex}


# 脚本开始
if __name__ == '__main__':
    result = Env().get_env('YB_COOKIE')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)
    for i in result['data']:
        try:
            token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i)[0]
            result = set_sign(i)
            print('状态 token:%s %s %s' % (token, result['code'], result['msg']))
        except Exception as ex:
            print('状态 %s' % ex)
