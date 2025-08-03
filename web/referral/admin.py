from django.contrib import admin
from web.referral.models import *
from solo.admin import SingletonModelAdmin


@admin.register(Settings)
class SettingsAdmin(SingletonModelAdmin):
    pass
