from aiogram import Router
from aiogram.enums import ChatType
from bot.core.filters import ChatTypeFilter

from .start import router as start_router
from .menu import router as menu_router
from .get_id import router as get_id_router

router = Router()
router.message.filter(ChatTypeFilter(ChatType.PRIVATE))
router.callback_query.filter(ChatTypeFilter(ChatType.PRIVATE))

router.include_routers(
    start_router,
    menu_router,
    get_id_router
)
