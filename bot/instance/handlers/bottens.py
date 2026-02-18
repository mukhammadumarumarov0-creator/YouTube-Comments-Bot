from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton,CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def send_comment_to_telegram(bot: Bot, chat_id: int, comment: dict, video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}&lc={comment['comment_id']}"
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="YouTube’da ko‘rish", url=url)
    )
    text = f"{comment['author_name']}:\n{comment['text']}"
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

async def register_button(message: Message, text: str):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📃 Ro'yhatdan o'tish")]],
        resize_keyboard=True
    )
    await message.answer(text=text, reply_markup=keyboard, parse_mode='HTML')

async def face_btn(message: Message, text: str):
  keyboard = ReplyKeyboardMarkup(
        keyboard=[
           [KeyboardButton(text="Video➕"),KeyboardButton(text="✳️ My Videos")]
            ],
        resize_keyboard=True
    )
  await message.answer(text=text, reply_markup=keyboard, parse_mode='HTML')

async def face_btn_callback(callback: CallbackQuery, text: str):
  keyboard = ReplyKeyboardMarkup(
        keyboard=[
           [KeyboardButton(text="Video➕"),KeyboardButton(text="✳️ My Videos")]
            ],
        resize_keyboard=True
    )
  await callback.message.answer(text=text, reply_markup=keyboard, parse_mode='HTML')

async def phone_button(message: Message, text: str):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📲 Raqam jo'natish", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer(text=text, reply_markup=keyboard, parse_mode='HTML')

async def back_to_menu(message: Message, text: str):
  keyboard = ReplyKeyboardMarkup(
        keyboard=[
           [KeyboardButton(text="⬅️ Orqaga")]
            ],
        resize_keyboard=True
    )
  await message.answer(text=text, reply_markup=keyboard, parse_mode='HTML')
