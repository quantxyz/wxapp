from django.contrib import admin
from .models import AppInfo, SessionInfo


# Register your models here.
class AppInfoAdmin(admin.ModelAdmin):
    # ...
    list_display = ('id', 'title', 'appid', 'login_duration', 'session_duration')


class SessionInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'create_time', 'last_vist_time', 'open_id')

admin.site.register(AppInfo, AppInfoAdmin)
admin.site.register(SessionInfo, SessionInfoAdmin)