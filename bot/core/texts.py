from enum import StrEnum, unique
from web.panel.models import Text, TextWithMedia


@unique
class TextEnum(StrEnum):
    start = 'Приветственное сообщение'
    start_yes_button = 'Кнопка согласия на приветственном сообщении'

    channel = 'Подпишитесь на канал сообщение'
    channel_subscribe_button = 'Кнопка подписаться'
    channel_check_button = 'Кнопка проверить подписку'
    channel_check_canceled = 'Если не подписан текст'
    channel_link = 'Ссылка на канал'
    channel_id = 'ID канала'

    main_menu = 'Главное меню сообщение'
    meditation_button = 'Кнопка Медитация'
    preparation_button = 'Кнопка Подготовка'
    about_button = 'Кнопка О проекте точка GG'
    tariffs_button = 'Кнопка Тарифы'
    channel_button = 'Кнопка Канал'
    feedback_button = 'Кнопка Обратная связь'
    feedback_link = 'Ссылка на группу с обратной связью'
    support_button = 'Кнопка Поддержка'
    support_link = 'Ссылка на группу поддержки'
    referral_button = 'Кнопка Рефералка'
    leave_feedback_button = 'Кнопка Оставить отзыв'

    referral = 'Рефералка текст'

    back_to_menu_button = 'Кнопка Назад в меню'
    back_button = 'Кнопка Назад'

    preparation_meditation_text = 'Кнопка Подготовка -> Медитация'
    about_meditation_text = 'Кнопка О проекте -> Медитация'
    about_preparation_text = 'Кнопка О проекте -> Подготовка'

    listened_text = 'текст после описания медитации',
    listened_button = 'кнопка Я прослушала'


default_texts = {
    TextEnum.start: 'Приветственное сообщение, информация о возможностях бота.\n\nВопрос: Ты готова?',
    TextEnum.start_yes_button: 'Да',
    TextEnum.channel: 'Чтобы пользоваться ботом, вам необходимо подписаться на наш канал!',
    TextEnum.channel_subscribe_button: 'Подписаться',
    TextEnum.channel_check_button: 'Проверить подписку',
    TextEnum.channel_check_canceled: 'Проверьте подписку и попробуйте еще раз',
    TextEnum.main_menu: 'Привет, милая ИМЯ!\n\nО ПОДИПИСКЕ\n\nВаш id: TELEGRAM_ID',
    TextEnum.meditation_button: '🎧Медитация',
    TextEnum.preparation_button: '🌙Подготовка',
    TextEnum.about_button: 'ℹО проекте "точка GG"',
    TextEnum.tariffs_button: '💳Тарифы',
    TextEnum.support_button: '👩🏻‍💻Поддержка',
    TextEnum.channel_button: '💬Канал',
    TextEnum.channel_link: '',
    TextEnum.channel_id: '',
    TextEnum.feedback_button: '🤝Обратная связь',
    TextEnum.feedback_link: '',
    TextEnum.referral: 'ССЫЛКА',
    TextEnum.referral_button: 'Рефералка',
    TextEnum.leave_feedback_button: 'Оставить отзыв',
    TextEnum.back_to_menu_button: 'Назад в меню',
    TextEnum.back_button: 'Назад',
    TextEnum.preparation_meditation_text: 'Я готова',
    TextEnum.about_meditation_text: 'Перейти к медитациям',
    TextEnum.about_preparation_text: 'Подготовка',
    TextEnum.listened_text: 'Текстовое сообщение',
    TextEnum.listened_button: 'Я прослушала'
}


@unique
class TextWithMediaEnum(StrEnum):
    preparation = 'Подготовка',
    about = 'О проекте'


default_texts_with_media = {
    TextWithMediaEnum.preparation: 'Подготовка текст',
    TextWithMediaEnum.about: 'О проекте текст'
}


async def setup_texts() -> None:
    for t in default_texts:
        text, created = await Text.objects.aget_or_create(name=t)

        if created:
            text.text = default_texts[t]
            await text.asave()

    for t in default_texts_with_media:
        text, created = await TextWithMedia.objects.aget_or_create(name=t)

        if created:
            text.text = default_texts_with_media[t]
            await text.asave()


async def get_text(text_enum: TextEnum) -> str:
    text = await Text.objects.aget(name=text_enum)
    return text.text
