from datetime import timedelta

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from django.utils import timezone

from bot.core.keyboards import CallbackData
from bot.core.texts import get_text, TextEnum
from bot.core.yookassa import YooKassaAsyncClient
from web.panel.models import User, Subscription, UserSubscription, Payment, UserReferral
from bot.core.keyboards import keyboards

router = Router()


@router.callback_query(F.data == 'back_sub')
@router.callback_query(F.data == CallbackData.tariffs)
async def on_tariffs(callback: CallbackQuery, user: User):
    user_sub, created = await UserSubscription.objects.aget_or_create(user=user)

    if user_sub.leave_date and user_sub.leave_date > timezone.now():
        text = f'Подписка действительна до {timezone.localtime(user_sub.leave_date).strftime('%d.%m.%Y %H:%M')}\n\n'
    else:
        text = ''

    text += 'Подписки:\n'
    keyboard = list()

    i = 0
    async for sub in Subscription.objects.order_by('id'):
        if not i % 5:
            keyboard.append(list())

        text += f'{i + 1}) {sub.name}; Срок подписки: {sub.days} дней; Стоимость: {sub.cost}₽\n'
        keyboard[-1].append(InlineKeyboardButton(text=str(i + 1), callback_data=f'sub_v_{sub.id}'))

        i = i % 5 + 1

    keyboard.append(
        [
            InlineKeyboardButton(
                text=await get_text(TextEnum.back_to_menu_button),
                callback_data=CallbackData.back_to_menu
            )
        ]
    )

    await callback.message.answer(text=text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))


@router.callback_query(F.data.startswith('sub_v'))
async def on_view_sub(callback: CallbackQuery):
    *_, sub_id = callback.data.split('_')
    sub = await Subscription.objects.aget(id=int(sub_id))

    await callback.message.answer(
        text=f'<b>{sub.name}</b>\n<b>Срок подписки:</b> {sub.days} дней\n<b>Стоимость подписки:</b> {sub.cost}₽',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Купить подписку', callback_data=f'sub_b_{sub.id}')],
                [InlineKeyboardButton(text=await get_text(TextEnum.back_button), callback_data=f'back_sub')]
            ]
        ),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data.startswith('sub_b_'))
async def on_view_sub(callback: CallbackQuery):
    *_, sub_id = callback.data.split('_')
    sub_id = int(sub_id)
    sub = await Subscription.objects.aget(id=int(sub_id))

    try:
        async with YooKassaAsyncClient() as client:
            payment = await client.create_payment(
                amount=sub.cost,
                description=sub.name
            )
            print(payment)
            payment_url = payment['confirmation']['confirmation_url']
            payment_id = payment['id']
    except Exception as E:
        print(E)
        await callback.message.answer(
            text='Ошибка! Нет связи с банком. Попробуйте позднее.',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=await get_text(TextEnum.back_button), callback_data=f'back_sub')]],
            )
        )
        return

    await callback.message.answer(
        text=f'Ссылка для оплаты: {payment_url}',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Я оплатила', callback_data=f'sub_bought_{payment_id}_{sub.id}')],
                [InlineKeyboardButton(text=await get_text(TextEnum.back_button), callback_data=f'back_sub')]
            ]
        ),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data.startswith('sub_bought'))
async def on_view_sub(callback: CallbackQuery, user: User, bot: Bot):
    *_, payment_id, sub_id = callback.data.split('_')
    sub_id = int(sub_id)

    try:
        async with YooKassaAsyncClient() as client:
            payment = await client.get_payment_status(payment_id=payment_id)
    except Exception as E:
        print(E)
        await callback.answer(text='Ошибка! Нет связи с банком. Попробуйте позднее', show_alert=True)
        return

    payed = payment['status'] == 'succeeded'

    if not payed:
        await callback.answer(text='Оплата еще не прошла', show_alert=True)
        return

    sub = await Subscription.objects.aget(id=int(sub_id))
    user_sub, created = await UserSubscription.objects.aget_or_create(user=user)
    await add_sub_days(user=user, plus_days=sub.days)

    await Payment.objects.acreate(
        user=user,
        date=timezone.now(),
        sum=sub.cost
    )

    await callback.message.answer(
        text=f'<b>Вы успешно купили подписку!</b>\n\nПодписка действительна до {timezone.localtime(user_sub.leave_date).strftime('%d.%m.%Y %H:%M')}',
        reply_markup=await keyboards.back_to_menu,
        parse_mode=ParseMode.HTML
    )

    referrer = await sync_to_async(lambda: user.referrers.first().user)()

    await add_sub_days(user=referrer, plus_days=7)

    await bot.send_message(
        text=f'Ваш реферал оплатил подписку. Вам начислено 7 дней',
        chat_id=referrer.id,
        reply_markup=await keyboards.back_to_menu
    )


async def add_sub_days(user: User, plus_days: int):
    user_sub, created = await UserSubscription.objects.aget_or_create(user=user)
    plus_time = timedelta(days=plus_days)
    if not user_sub.leave_date or user_sub.leave_date <= timezone.now():
        user_sub.leave_date = timezone.now() + plus_time
    else:
        user_sub.leave_date += plus_time
    await user_sub.asave()
