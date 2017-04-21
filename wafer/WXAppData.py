#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import uuid
import datetime
from .WXBizDataCrypt import WXBizDataCrypt
import base64
from requests.exceptions import RequestException


class WXAppData:
    def __init__(self, appId, secret):
        self.appId = appId
        self.secret = secret

    def get_session(self, code, encrypt_data='', iv=''):
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code'\
              % (self.appId, self.secret, code)
        try:
            response = requests.get(url)
            r = response.json()
            if r['openid'] and len(r['openid']) > 8 and r['session_key'] and len(r['session_key'])>2 \
                    and r['expires_in'] and r['expires_in'] > 0:
                u_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(time.time()))
                skey = uuid.uuid3(uuid.NAMESPACE_DNS, str(time.time()))
                create_time = datetime.datetime.now()
                last_vist_time = datetime.datetime.now()
                openid = r['openid']
                session_key = r['session_key']
                user_info = ''
                if encrypt_data and iv and len(encrypt_data) > 50 and len(iv)> 5:
                    pc = WXBizDataCrypt(self.appId, session_key)
                    user_info = pc.decrypt(encrypt_data, iv)
                return {
                    'ok': 'success',
                    'session': {
                        'uuid': u_uuid,
                        'skey': skey,
                        'create_time': create_time,
                        'last_vist_time': last_vist_time,
                        'openid': openid,
                        'session_key': session_key,
                        'user_info': user_info,
                        'expires_in': r['expires_in']
                    }
                }
            elif r['errcode'] and r['errmsg']:
                return {
                    'ok': 'fail',
                    'msg': r['errmsg']
                }
            else:
                return {
                    'ok': 'fail',
                    'msg': '微信返回值错误'
                }
        except RequestException:
            return {
                'ok': 'fail',
                'msg': '网络错误'
            }



