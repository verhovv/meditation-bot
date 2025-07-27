from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from web.panel.models import User


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(message, CallbackQuery):
            message = message.message

        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class StateFilter(BaseFilter):
    def __init__(self, state: str):
        self.state = state

    async def __call__(self, telegram_entity: Message, user: User) -> bool:
        return user.state == self.state
