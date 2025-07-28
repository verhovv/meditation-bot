from django.contrib import admin
from django.contrib.admin import display
from django.utils import timezone

from web.panel.models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'sub', 'has_referrals', 'created_at')
    fields = ('id', 'username', 'first_name', 'last_name', 'send_feedback', 'created_at')
    readonly_fields = ('id', 'username', 'first_name', 'last_name', 'created_at')

    exclude = ('data',)

    @display(description='Дата окончания подписки')
    def sub(self, obj: User):
        user_sub, created = UserSubscription.objects.get_or_create(user=obj)
        return user_sub.leave_date if user_sub.leave_date and user_sub.leave_date > timezone.now() else 'Бесплатная'

    @display(boolean=True, description='Есть рефералы')
    def has_referrals(self, obj: User):
        return bool(obj.referrals.all())

    def has_add_permission(self, request):
        return False


class AttachmentsInline(admin.TabularInline):
    model = Attachments

    exclude = ('file_id',)

    extra = 0


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['datetime', 'pay_user', 'text', 'is_ok']
    readonly_fields = ['is_ok']
    inlines = [AttachmentsInline]


@admin.register(UserReferral)
class UserReferralAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'referral']
    list_filter = ('user', 'referral')
    search_fields = ('referral__username',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['name', 'text']
    readonly_fields = ['name']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TextWithMedia)
class TextWithMediaAdmin(admin.ModelAdmin):
    list_display = ['name', 'text', 'media', 'media_type']
    fields = ['name', 'text', 'media', 'media_type']
    readonly_fields = ['name']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Meditation)
class MeditationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    fields = ['name', 'description', 'file_id']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'sum', 'date', 'status']
    fields = ['user', 'sum', 'date', 'status']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'days', 'cost']
