from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile

from bot.core.keyboards import CallbackData, keyboards
from bot.core.texts import TextWithMediaEnum
from web.panel.models import TextWithMedia

router = Router()


async def send_text_with_media(bot: Bot, chat_id: int, text: TextWithMedia, reply_markup=None):
    if not text.media_type:
        await bot.send_message(chat_id=chat_id, text=text.text, reply_markup=reply_markup)

    if text.media_type == 'photo':
        msg = await bot.send_photo(
            chat_id=chat_id,
            photo=FSInputFile(path=text.media.path) if not text.file_id else text.file_id,
            caption=text.text,
            reply_markup=reply_markup
        )

        if not text.file_id:
            text.file_id = msg.photo[-1].file_id
            await text.asave()

    if text.media_type == 'video':
        msg = await bot.send_video(
            chat_id=chat_id,
            video=FSInputFile(path=text.media.path) if not text.file_id else text.file_id,
            caption=text.text,
            reply_markup=reply_markup
        )

        text.file_id = msg.video.file_id
        await text.asave()


@router.callback_query(F.data == CallbackData.preparation)
async def send_preparation_text(callback: CallbackQuery, bot: Bot):
    await send_text_with_media(
        bot=bot,
        chat_id=callback.from_user.id,
        text=await TextWithMedia.objects.aget(name=TextWithMediaEnum.preparation),
        reply_markup=await keyboards.preparation
    )


@router.callback_query(F.data == CallbackData.about_project)
async def send_preparation_text(callback: CallbackQuery, bot: Bot):
    await send_text_with_media(
        bot=bot,
        chat_id=callback.from_user.id,
        text=await TextWithMedia.objects.aget(name=TextWithMediaEnum.about),
        reply_markup=await keyboards.about_project
    )
