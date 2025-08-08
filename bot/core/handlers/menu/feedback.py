from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, Message
from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

from bot.core.keyboards import CallbackData
from bot.core.texts import get_text, TextEnum
from web.panel.models import Meditation, UserMeditation, User, UserSubscription
from bot.core.keyboards import keyboards
from bot.core.filters import StateFilter

router = Router()


@router.callback_query(F.data == CallbackData.leave_feedback)
async def on_feedback(callback: CallbackQuery, user: User):
    user.state = 'feedback'
    await user.asave()

    text = await get_text(TextEnum.feedback)

    await callback.message.answer(
        text=text,
        reply_markup=await keyboards.back_to_menu
    )


@router.message(StateFilter('feedback'))
async def on_feedback(message: Message):
    @sync_to_async
    def can_send() -> bool:
        with transaction.atomic():
            user = User.objects.select_for_update().get(id=message.from_user.id)
            send = False

            user_group_id = user.data.get('group_id', None)

            if user_group_id is not None and user_group_id == message.media_group_id:
                user.data['message_ids'].append(message.message_id)
            elif user_group_id is None or user_group_id != message.media_group_id:
                user.data['message_ids'] = [message.message_id]
                send = True

            user.data['group_id'] = message.media_group_id
            user.save()

            return send

    if await can_send():
        await message.answer(
            text='Подтвердите отзыв или пришлите другой',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Отправить отзыв', callback_data='f_agree')],
                    [await keyboards.back_to_menu_button]
                ]
            )
        )


@router.callback_query(F.data == 'f_agree')
async def on_feedback_agree(callback: CallbackQuery, user: User, bot: Bot):
    await callback.message.answer(
        text='Ваш отзыв успешно отправлен',
        reply_markup=await keyboards.back_to_menu
    )

    async for u in User.objects.filter(send_feedback=True):
        await bot.send_message(
            chat_id=u.id,
            text=f'Новый отзыв от @{user.username}'
        )

        await bot.forward_messages(
            from_chat_id=callback.from_user.id,
            message_ids=user.data['message_ids'],
            chat_id=u.id
        )
