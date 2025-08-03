from time import timezone

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.filters.command import CommandStart, CommandObject
from asgiref.sync import sync_to_async

from bot.core.texts import TextEnum, get_text
from bot.core.keyboards import keyboards, CallbackData

from web.panel.models import User, UserReferral, UserSubscription, Settings
from bot.core.utils import add_sub_days
from django.utils import timezone

router = Router()


async def get_menu_text(user: User) -> str:
    text = await get_text(text_enum=TextEnum.main_menu)

    text = text.replace('ИМЯ', user.first_name)
    text = text.replace('TELEGRAM_ID', f'<a href="tg://user?id={user.id}">{user.id}</a>')

    user_sub, created = await UserSubscription.objects.aget_or_create(user=user)
    payed_sub = user_sub.leave_date and user_sub.leave_date > timezone.now()

    sub_text = (f'{"Ваша подписка не активна" if not payed_sub else "Ваша подписка активна!\n"}'
                f'{f"Дата окончания подписки: <b>{timezone.localtime(user_sub.leave_date).strftime('%d.%m.%Y %H:%M')}</b>" if payed_sub else ""}')

    text = text.replace('О ПОДПИСКЕ', sub_text)

    return text


@router.callback_query(F.data == CallbackData.back_to_menu)
@router.message(CommandStart())
async def start(message: Message, bot: Bot, user: User, user_created: bool, command: CommandObject = None):
    user.state = None
    await user.asave()

    settings = await sync_to_async(Settings.get_solo)()
    if user_created and settings.give_free_sub:
        await add_sub_days(user=user, plus_days=settings.free_sub_days)
        await message.answer(text=f'Тебе доступна бесплатная подписка на {settings.free_sub_days} дней')

    if command:
        ref_id = command.args

        try:
            referrer = await User.objects.aget(id=int(ref_id))
            if not await sync_to_async(lambda: len(user.referrers.all()))() \
                    and referrer.id != user.id:
                _ = await UserReferral.objects.aget_or_create(user=referrer, referral=user)
        except Exception as E:
            print(E)

    if isinstance(message, CallbackQuery):
        message = message.message
    else:
        try:
            await message.delete()
        except:
            pass

    if not await check_channel_subscribe(bot=bot, user_id=message.from_user.id):
        await message.answer(
            text=await get_text(text_enum=TextEnum.start),
            reply_markup=await keyboards.start_yes
        )
        return

    await message.answer(
        text=await get_menu_text(user=user),
        reply_markup=await keyboards.main_menu,
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == CallbackData.start_yes)
async def start_yes_callback(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        text=await get_text(text_enum=TextEnum.channel),
        reply_markup=await keyboards.subscribe
    )


async def check_channel_subscribe(bot: Bot, user_id: int) -> bool:
    channel_id = int(await get_text(text_enum=TextEnum.channel_id))

    chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    return chat_member.status not in [ChatMemberStatus.KICKED, ChatMemberStatus.LEFT]


@router.callback_query(F.data == CallbackData.start_check_subscribe)
async def start_check_subscribe_callback(callback: CallbackQuery, bot: Bot, user: User):
    if not await check_channel_subscribe(bot=bot, user_id=callback.from_user.id):
        await callback.answer(
            text=await get_text(text_enum=TextEnum.channel_check_canceled),
            show_alert=True
        )
        return

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        text=await get_menu_text(user=user),
        reply_markup=await keyboards.main_menu,
        parse_mode=ParseMode.HTML
    )
