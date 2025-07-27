from django.db import models


class User(models.Model):
    id = models.BigIntegerField('Идентификатор Телеграм', primary_key=True, blank=False)

    username = models.CharField('Юзернейм', max_length=64, null=True, blank=True)
    first_name = models.CharField('Имя', null=True, blank=True)
    last_name = models.CharField('Фамилия', null=True, blank=True)

    send_feedback = models.BooleanField('Отправлять отзывы этому пользователю', default=False)

    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True, blank=True)

    data = models.JSONField(default=dict, blank=True)
    state = models.CharField(null=True, blank=True)

    def __str__(self):
        return f'id{self.id} | @{self.username or "-"} {self.first_name or "-"} {self.last_name or "-"}'

    class Meta:
        verbose_name = 'Телеграм пользователь'
        verbose_name_plural = 'Телеграм пользователи'


class UserReferral(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals', verbose_name='Пригласивший')
    referral = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrers', verbose_name='Приглашенный')

    class Meta:
        verbose_name = 'Реферал'
        verbose_name_plural = 'Рефералы'

    def __str__(self):
        return f'{self.user} - {self.referral}'


class Attachments(models.Model):
    types = {
        'photo': 'Фото',
        'video': 'Видео',
        'document': 'Документ'
    }

    type = models.CharField('Тип вложения', choices=types)
    file = models.FileField('Файл', upload_to='web/media/mailing')
    file_id = models.TextField(null=True)
    mailing = models.ForeignKey('Mailing', on_delete=models.SET_NULL, null=True, related_name='attachments')

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'


class Mailing(models.Model):
    text = models.TextField('Текст', blank=True, null=True)
    datetime = models.DateTimeField('Дата/Время')
    pay_user = models.BooleanField('Платным пользователям', default=False)
    is_ok = models.BooleanField('Статус отправки', default=False)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Text(models.Model):
    name = models.CharField('Название текста', primary_key=True)
    text = models.TextField('Текст', default='Текст')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Текст'
        verbose_name_plural = 'Тексты'


class TextWithMedia(models.Model):
    media_types = {
        'photo': 'Фото',
        'video': 'Видео'
    }

    name = models.CharField('Название текста', primary_key=True)
    text = models.TextField('Текст', default='Текст')
    media = models.FileField('Медиа', upload_to='web/media/TextsWithMedia', null=True, blank=True)
    media_type = models.CharField('Тип медиа', choices=media_types, null=True, blank=True)
    file_id = models.CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            if self.pk:
                old_photo = TextWithMedia.objects.get(pk=self.pk).media
                if old_photo != self.media:
                    self.file_id = None
        except:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Текст с медиа'
        verbose_name_plural = 'Тексты с медиа'


class Meditation(models.Model):
    name = models.CharField('Название')
    description = models.TextField('Описание')

    file_id = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Медитация'
        verbose_name_plural = 'Медитации'


class UserMeditation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='meditations')
    meditation = models.ForeignKey(Meditation, on_delete=models.CASCADE, null=True, related_name='users')
    has_listened = models.BooleanField(default=False)


class Subscription(models.Model):
    name = models.CharField('Название')
    days = models.IntegerField('Количество подписки в днях')
    cost = models.IntegerField('Цена в рублях')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    sum = models.IntegerField('Сумма')
    status = models.BooleanField(default=True)
    date = models.DateTimeField('Дата')

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    leave_date = models.DateTimeField(null=True)
