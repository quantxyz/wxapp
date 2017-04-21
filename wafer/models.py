#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import models


# Create your models here.
class AppInfo(models.Model):
    title = models.CharField(max_length=30, verbose_name='小程序名字')
    appid = models.CharField(max_length=200, verbose_name='微信小程序appid')
    secret = models.CharField(max_length=300, verbose_name='微信小程序appsecret')
    login_duration = models.SmallIntegerField(verbose_name='登录过期时间(天)', default=30)
    session_duration = models.PositiveIntegerField(verbose_name='会话过期时间(秒)', default=2592000)

    def __unicode__(self):
        return self.title


class SessionInfo(models.Model):
    uuid = models.CharField(max_length=100, verbose_name='会话 uuid')
    skey = models.CharField(max_length=100, verbose_name='会话 Skey')
    # 判断会话对应的 open_id 和 session_key 是否超过`login_duration` 配置的天数
    create_time = models.DateTimeField(verbose_name='会话创建时间')
    # 判断会话是否超过 `session_duration` 配置的秒数
    last_vist_time = models.DateTimeField(verbose_name='最近访问时间')
    open_id = models.CharField(max_length=100, verbose_name='openid')
    session_key = models.CharField(max_length=100, verbose_name='session_key')
    user_info = models.CharField(max_length=2048, verbose_name='已解密的用户数据', null=True)

    def __unicode__(self):
        return self.open_id



