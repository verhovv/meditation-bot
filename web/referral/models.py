from django.db import models
from solo.models import SingletonModel


class Settings(SingletonModel):
    days_per_sub = models.IntegerField('Бесплатных дней реферреру за подписку', default=7)
    money_per_sub = models.IntegerField('Денег к выводу реферреру за подписку', default=100)

    def __str__(self):
        return 'Настройки'

    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'
