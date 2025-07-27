from enum import StrEnum, unique, auto
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.core.texts import TextEnum, get_text


@unique
class CallbackData(StrEnum):
    start_yes = auto()
    start_check_subscribe = auto()

    meditation = auto()
    preparation = auto()
    about_project = auto()
    tariffs = auto()
    referral = auto()
    leave_feedback = auto()

    back_to_menu = auto()
    back = auto()


class Keyboards:
    @property
    async def start_yes(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.start_yes_button),
                        callback_data=CallbackData.start_yes)
                ]
            ]
        )

    @property
    async def subscribe(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.channel_subscribe_button),
                        url=await get_text(text_enum=TextEnum.channel_link)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.channel_check_button),
                        callback_data=CallbackData.start_check_subscribe
                    ),

                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.feedback_button),
                        url=await get_text(text_enum=TextEnum.feedback_link)
                    ),
                ]
            ]
        )

    @property
    async def main_menu(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.meditation_button),
                        callback_data=CallbackData.meditation
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.preparation_button),
                        callback_data=CallbackData.preparation
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.about_button),
                        callback_data=CallbackData.about_project
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.tariffs_button),
                        callback_data=CallbackData.tariffs
                    )
                ],

                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.channel_button),
                        url=await get_text(text_enum=TextEnum.channel_link)
                    ),

                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.feedback_button),
                        url=await get_text(text_enum=TextEnum.feedback_link)
                    )
                ],

                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.support_button),
                        url=await get_text(text_enum=TextEnum.feedback_link)
                    ),

                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.referral_button),
                        callback_data=CallbackData.referral
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.leave_feedback_button),
                        callback_data=CallbackData.leave_feedback
                    )
                ]
            ]
        )

    @property
    async def preparation(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.preparation_meditation_text),
                        callback_data=CallbackData.meditation)
                ],
                [await self.back_to_menu_button]
            ]
        )

    @property
    async def about_project(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.about_meditation_text),
                        callback_data=CallbackData.meditation
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=await get_text(text_enum=TextEnum.about_preparation_text),
                        callback_data=CallbackData.preparation
                    )
                ],
                [await self.back_to_menu_button]
            ]
        )

    @property
    async def back_to_menu(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [await self.back_to_menu_button]
            ]
        )

    @property
    async def back_to_menu_button(self):
        return InlineKeyboardButton(
            text=await get_text(text_enum=TextEnum.back_to_menu_button),
            callback_data=CallbackData.back_to_menu
        )


keyboards = Keyboards()
