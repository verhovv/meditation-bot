from web.panel.models import User, UserSubscription
from django.utils import timezone
from datetime import timedelta


async def add_sub_days(user: User, plus_days: int):
    user_sub, created = await UserSubscription.objects.aget_or_create(user=user)
    plus_time = timedelta(days=plus_days)
    if not user_sub.leave_date or user_sub.leave_date <= timezone.now():
        user_sub.leave_date = timezone.now() + plus_time
    else:
        user_sub.leave_date += plus_time
    await user_sub.asave()
