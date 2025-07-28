from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from django.utils import timezone

from bot.core.keyboards import CallbackData
from bot.core.texts import get_text, TextEnum
from web.panel.models import Meditation, UserMeditation, User, UserSubscription

router = Router()


@router.callback_query(F.data == CallbackData.back)
@router.callback_query(F.data == CallbackData.meditation)
async def on_meditation(callback: CallbackQuery, user: User):
    user_sub, created = await UserSubscription.objects.aget_or_create(user=user)
    has_sub = user_sub.leave_date and user_sub.leave_date > timezone.now()

    text = '🎧 Выбери медитацию, чтобы начать:\n\n' + \
           'Каждая практика — как мягкое прикосновение. Глубокое. Настоящее. Только для тебя.\n'

    i = 0
    j = 0
    keyboard = []
    async for meditation in Meditation.objects.order_by('id'):
        m, _ = await UserMeditation.objects.aget_or_create(user=user, meditation=meditation)

        if not m.has_listened and j == 3 and not has_sub:
            break

        if not i % 5:
            keyboard.append(list())

        text += f'{i + 1}. {meditation}{'✓' if m.has_listened else ''}\n'
        keyboard[-1].append(
            InlineKeyboardButton(
                text=f'{i + 1}{'✓' if m.has_listened else ''}',
                callback_data=f'm_l_{await sync_to_async(lambda: m.meditation_id)()}'
            )
        )

        if not m.has_listened:
            break

        i += 1

    m_len = await sync_to_async(lambda: len(Meditation.objects.all()))()
    text += f'<b>\nТы прослушала {i} из {m_len} медитаций</b>'

    if not has_sub and i > 2:
        text += '\n\nЧтобы слушать больше медитаций нужно оформить подписку'

    keyboard.append(
        [
            InlineKeyboardButton(
                text=await get_text(text_enum=TextEnum.back_to_menu_button),
                callback_data=CallbackData.back_to_menu
            )
        ]
    )

    await callback.message.answer(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        ),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data.startswith('m_l'))
async def on_listen(callback: CallbackQuery, user: User):
    await callback.answer()

    *_, m_id = callback.data.split('_')
    m_id = int(m_id)

    meditation = await Meditation.objects.aget(id=m_id)

    msg = await callback.message.answer_document(
        document=meditation.file_id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=await get_text(TextEnum.listened_button),
                        callback_data=f'm_a_{m_id}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.back_button),
                        callback_data=CallbackData.back
                    )
                ]
            ]
        ),
        caption=meditation.description + f'\n\n{await get_text(TextEnum.listened_text)}',
        protect_content=True
    )

    if not meditation.file_id:
        meditation.file_id = msg.audio.file_id
        await meditation.asave()


@router.callback_query(F.data.startswith('m_a'))
async def on_listen(callback: CallbackQuery, user: User):
    *_, m_id = callback.data.split('_')
    m_id = int(m_id)

    user_meditation = await UserMeditation.objects.aget(meditation__id=m_id, user=user)
    user_meditation.has_listened = True

    await user_meditation.asave()
    await on_meditation(callback, user)
