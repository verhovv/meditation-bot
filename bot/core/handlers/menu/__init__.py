from aiogram import Router
from .texts_with_media import router as text_with_media_router
from .meditations import router as meditations_router
from .subscriptions import router as subscription_router
from .referral import router as referral_router
from .feedback import router as feedback_router

router = Router()
router.include_routers(
    text_with_media_router,
    meditations_router,
    subscription_router,
    referral_router,
    feedback_router
)
