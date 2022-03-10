#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron: 0 0
 * * ?
new Env('易班-易伴参与挑战');
RandomDelay="300"
tag: yb_yiban_pay
"""
import re
import requests
from env import Env

env = Env()


# 将支付金额转换为对应ID
def get_data_id(num):
    # 网薪: id
    return {'10': '3', '50': '5', '100': '6', '300': '10', '500': '7', '800': '9'}[num]


# 支付网薪
def payment(cookie):
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
    try:
        data_id = '3'

        url = "https://f.yiban.cn/iframe/index?act=iapp642231"

        headers = {
            'User-Agent': env.UserAgent3,
            'Cookie': cookie
        }
        session = requests.session()
        session.get(url, headers=headers)

        # 下单地址
        pay_url = "https://daka.yibangou.com/index.php?m=Wap&c=User&a=chongzhi&dataname=1&dataid=" + data_id

        headers = {
            'Host': 'daka.yibangou.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': env.UserAgent3,
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://daka.yibangou.com/index.php?m=Wap&c=Index&a=index&res=29',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        resp = session.get(pay_url, headers=headers).text

        dataid = re.findall(r'name="dataid" value="(.*?)"', resp)[0]
        dataname = re.findall(r'name="dataname" value="(.*?)"', resp)[0]
        danhao = re.findall(r'name="danhao" value="(.*?)"', resp)[0]

        params = {
            'danhao': danhao,
            'dataid': dataid,
            'dataname': dataname
        }
        headers = {
            'Host': 'daka.yibangou.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://daka.yibangou.com',
            'User-Agent': env.UserAgent3,
            'Connection': 'keep-alive',
            'Referer': pay_url,
        }

        # 支付方式 0 = 余额, 1 = 网薪
        type = ['Payyue', 'yibanpay']
        url = 'https://daka.yibangou.com/index.php?m=Wap&c=Ajax&a='
        resp = session.post(url + type[0], data=params, headers=headers).json()
        code = int(resp['code'])
        if code == 200:
            return {'code': code, 'msg': '支付成功'}
        elif code == 1:
            return {'code': code, 'msg': '余额不足'}
        elif code == 2:
            return {'code': code, 'msg': '跳转首页'}
        else:
            return {'code': code, 'msg': '未知状态'}
    except Exception as ex:
        return {'code': -1, 'msg': ex}


# 脚本
if __name__ == '__main__':
    result = env.get_env('YB_COOKIE')
    if result['code'] != 1:
        print(result['msg'])
        exit(0)

    for i in result['data']:
        try:
            token = re.findall(r'yiban_user_token=([a-f\d]{32}|[A-F\d]{32})', i)[0]
            result = payment(i)
            print('易伴支付 token:%s %s %s' % (token, result['code'], result['msg']))
        except Exception as ex:
            print('易伴支付 %s' % ex)

