#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron: 0 20 6-7 * * ?
new Env('易班-易伴打卡');
RandomDelay="300"
"""
import re
import base64
import requests
from env import Env
from common import Captcha

env = Env()
ct = Captcha()


# 打卡
def set_sign(cookie):
    """
    打卡
    :return:
    """
    try:
        url = "https://f.yiban.cn/iframe/index?act=iapp642231"
        headers = {
            'User-Agent': env.UserAgent,
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
            'User-Agent': env.UserAgent,
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        # 跑 3 次防止验证码识别错误次数过多
        for count in range(3):
            images = session.get(captcha_url, headers=headers)
            # data:image/png;base64,
            base64_image = base64.encodebytes(images.content).decode('UTF-8').replace("\n", "")
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
                'User-Agent': env.UserAgent,
                'Connection': 'keep-alive',
            }
            params = {'yzm': capt['data']}
            url = 'https://daka.yibangou.com/index.php?m=Wap&c=Ajax&a=daka'
            resp = session.post(url, data=params, headers=headers).json()
            if resp['code'] == 1:
                ct.report_error(capt['id'])
                yb_token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', cookie)[0]
                print('易伴打卡 token:%s %s %s' % (yb_token, resp['code'], '验证码错误'))
            elif resp['code'] == 2:
                return {'code': resp['code'], 'msg': '操作失败'}
            elif resp['code'] == 4:
                return {'code': resp['code'], 'msg': '已打卡'}
            elif resp['code'] == 5:
                return {'code': resp['code'], 'msg': '打卡成功'}
            elif resp['code'] == 6:
                return {'code': resp['code'], 'msg': '挑战成功'}
            else:
                return {'code': resp['code'], 'msg': '未知状态码'}
        return {'code': -1, 'msg': '验证码错误次数过多'}
    except Exception as ex:
        return {'code': -1, 'msg': str(ex)}


# 脚本开始
if __name__ == '__main__':
    if ct.ct_user is None or ct.ct_pass is None:
        exit(0)
    result = env.get_env('YB_COOKIE')
    if result['code'] != 1:
        print('易伴打卡: ' + result['msg'])
        exit(0)

    for i in result['data']:
        try:
            token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i)[0]
            result = set_sign(i)
            print('易伴打卡 token:%s %s %s' % (token, result['code'], result['msg']))
        except Exception as ex:
            print('易伴打卡 %s' % ex)
