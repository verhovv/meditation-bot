from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from django.utils import timezone

from bot.core.keyboards import CallbackData
from bot.core.texts import get_text, TextEnum
from web.panel.models import Meditation, UserMeditation, User, UserSubscription, UserReferral

router = Router()


@router.callback_query(F.data == CallbackData.referral)
async def on_referral(callback: CallbackQuery, bot: Bot, user: User):
    text = await get_text(text_enum=TextEnum.referral)
    text = text.replace(
        'ССЫЛКА',
        f'<code copyable>https://t.me/{(await bot.get_me()).username}?start={callback.from_user.id}</code>'
    )

    referral_count = await sync_to_async(lambda: len(user.referrals.all()))()

    text = text.replace(
        'КОЛ-ВО РЕФЕРАЛОВ',
        str(referral_count)
    )

    await callback.message.answer(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=await get_text(TextEnum.back_to_menu_button),
                        callback_data=CallbackData.back_to_menu
                    )
                ],
            ]
        ),
        parse_mode=ParseMode.HTML
    )
