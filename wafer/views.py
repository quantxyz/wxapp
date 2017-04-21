#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AppInfo, SessionInfo
from WXAppData import WXAppData
import logging
import json
import datetime
logger = logging.getLogger(__name__)


# utils
def check_session_for_login(params):
    ss = SessionInfo.objects.filter(open_id=params['openid'])
    if ss.exists():
        s = ss.first()
        if s and s.create_time:
            return True
        else:
            return False
    else:
        s = SessionInfo(uuid=params['uuid'], skey=params['skey'],
                        create_time=params['create_time'],
                        last_vist_time=params['last_vist_time'],
                        open_id=params['openid'],
                        session_key=params['session_key'],
                        user_info=params['user_info'])
        s.save()
        return True


def check_session_for_auth(params):
    ss = SessionInfo.objects.filter(uuid=params['uuid'], skey=params['skey'])
    if ss.exists():
        s = ss.first()
        now_time = datetime.datetime.now()
        create_time = s.create_time
        last_vist_time = s.last_vist_time
        if int((now_time - create_time).days) > params['login_duration']:
            return False
        elif int((now_time - last_vist_time).total_seconds()) > params['session_duration']:
            return False
        else:
            s.last_vist_time = now_time
            s.save()
            return s.user_info
    else:
        return False


def change_session(params):
    if check_session_for_login(params):
        ss = SessionInfo.objects.filter(open_id=params['openid'])
        if ss.exists():
            s = ss.first()
            if not s.uuid:
                s.uuid = params['uuid']
                s.session_key = params['session_key']
                s.create_time = params['create_time']
                s.last_vist_time = params['last_vist_time']
                s.skey = params['skey']
                s.user_info = params['user_info']
                s.save()
                return s.uuid
            else:
                s.session_key = params['session_key']
                s.create_time = params['create_time']
                s.last_vist_time = params['last_vist_time']
                s.skey = params['skey']
                s.user_info = params['user_info']
                s.save()
                return s.uuid
        else:
            s = SessionInfo(uuid=params['uuid'], skey=params['skey'],
                            create_time=params['create_time'],
                            last_vist_time=params['last_vist_time'],
                            open_id=params['openid'],
                            session_key=params['session_key'],
                            user_info=params['user_info'])
            s.save()
            return True
    else:
        return False


# Create your views here.
def index(request):
    return JsonResponse({'msg': 'welcome'})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        app_id = int(data.get('app_id', 1))
        encrypt_data = data.get('encrypt_data', '').strip()
        code = data.get('code', '').strip()
        iv = data.get('iv', '').strip()
        if app_id and app_id > 0 and code and len(code) > 6:
            apps = AppInfo.objects.filter(pk=app_id)
            if apps.exists():
                app_info = apps.first()
                wxapp_data = WXAppData(appId=app_info.appid, secret=app_info.secret)
                result = wxapp_data.get_session(code=code, encrypt_data=encrypt_data, iv=iv)
                if result['ok'] == 'fail':
                    return JsonResponse(result)
                else:
                    s = result['session']
                    result_s = change_session(params=s)
                    if result_s is False:
                        return JsonResponse({'ok': 'fail', 'msg': '更新session出错'})
                    elif result_s is True:
                        return JsonResponse({'ok': 'success', 'msg': '新增session成功',
                                             'data': {
                                                 'uuid': s['uuid'],
                                                 'skey': s['skey'],
                                                 'user_info': s['user_info'],
                                                 'duration': s['expires_in']
                                             }})
                    else:
                        return JsonResponse({'ok': 'success', 'msg': '更新session成功',
                                             'data': {
                                                 'uuid': result_s,
                                                 'skey': s['skey'],
                                                 'user_info': s['user_info'],
                                                 'duration': s['expires_in']
                                             }})
            else:
                return JsonResponse({'ok': 'fail', 'msg': '获取app相关参数出错'})
        else:
            return JsonResponse({'ok': 'fail', 'msg': '参数错误'})
    else:
        return JsonResponse({'ok': 'fail', 'msg': 'not post method'})


@csrf_exempt
def auth(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        app_id = int(data['app_id'])
        uuid = data['uuid'].strip()
        skey = data['skey'].strip()
        if app_id and app_id > 0 and uuid and len(uuid) > 5 \
                and skey and len(skey) > 6:
            apps = AppInfo.objects.filter(pk=app_id)
            if apps.exists():
                # 1 means default '旅游小程序'
                app_info = apps.first()
                login_duration = app_info.login_duration
                session_duration = app_info.session_duration
                params = {'uuid': uuid, 'skey': skey,
                          'login_duration': login_duration, 'session_duration': session_duration}
                s_result = check_session_for_auth(params)
                if s_result is False:
                    return JsonResponse({'ok': 'fail', 'msg': '验证失败'})
                else:
                    return JsonResponse({'ok': 'success', 'msg': '验证成功',
                                         'data': {
                                             'user_info': s_result
                                         }})

            else:
                return JsonResponse({'ok': 'fail', 'msg': '获取app相关参数出错'})
        else:
            return JsonResponse({'ok': 'fail', 'msg': '请求参数错误'})
    else:
        return JsonResponse({'ok': 'fail', 'msg': 'not post method'})

