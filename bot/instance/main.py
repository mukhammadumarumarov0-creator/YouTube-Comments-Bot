from aiogram import Bot, Dispatcher, types
from bot.instance.handlers.user_handlers import user_router
from bot.instance.handlers.conf import BOT

webhook_dp = Dispatcher()
webhook_dp.include_router(user_router)

async def feed_update(token: str, update: dict):
    
    try:
        aiogram_update = types.Update(**update)
        await webhook_dp.feed_update(bot=BOT,update=aiogram_update)
    finally:
        await BOT.session.close()
