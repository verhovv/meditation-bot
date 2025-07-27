from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.caption == '/get_id')
async def get_id(message: Message):
    await message.reply(text=message.audio.file_id)
