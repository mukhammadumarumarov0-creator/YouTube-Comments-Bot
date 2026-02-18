from aiogram import Bot
from decouple import config

BOT = Bot(token=config("BOT_TOKEN"))


