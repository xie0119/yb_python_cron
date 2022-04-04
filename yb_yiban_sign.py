#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron: 0 20 6-7 * * ?
new Env('易班-易伴打卡');
tag: yb_yiban_sign
"""
import base64
import requests
from common import Captcha, Setting, Env

ct = Captcha()
label = 'yb_yiban_sign'
env = Env(label)
st = Setting(label)
client_id = "7af698a43be206c0"


# 打卡
def set_sign(cookie, account):
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
        # 登录
        r1 = session.get(url, headers=headers)

        if client_id in r1.text:
            oauth_header = {
                'Host': 'oauth.yiban.cn',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': env.UserAgent,
                'Referer': 'https://oauth.yiban.cn/code/html?client_id=' + client_id + '&redirect_uri=http://f.yiban.cn/iapp642231',
            }

            oauth_param = {
                "client_id": "7af698a43be206c0",
                "redirect_uri": "http://f.yiban.cn/iapp642231",
                "state": "",
                "scope": "1,2,3,4,",
                "display": "html"
            }

            oauth_url = 'https://oauth.yiban.cn/code/usersure'
            r2 = session.post(oauth_url, data=oauth_param, headers=oauth_header)
            session.get(r2.json()['reUrl'], headers=headers)
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

                st.msg_(resp['code'], '验证码错误', phone=account)
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
        st.msg_(-999, '易伴打卡: ' + result['msg'])
        exit(0)

    lst = result['data']
    for count in range(2):
        for k, i in enumerate(lst):
            lit = i['remarks'].split('|')
            if len(lit) != 2:
                st.msg_(-1, '账号密码分割出错 ', data={'value': i['remarks']})
                break
            account = lit[0]
            try:
                result = set_sign(i['value'], account)
                st.msg_(result['code'], result['msg'], phone=account)
                if result['code'] != -1:
                    lst.pop(k)
            except Exception as ex:
                st.msg_(-1, '打卡 %s' % ex, phone=account)

    st.msg_(2000, f"[{label}]执行完成。")
    exit(0)
