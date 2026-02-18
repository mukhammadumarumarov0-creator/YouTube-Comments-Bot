from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message,CallbackQuery
from asgiref.sync import sync_to_async

from bot.models import Video, User
from .utils import (extract_video_id, is_registered, normalize_phone, validate_full_name, create_user,
      PHONE_ERROR, FULLNAME_ERROR,all_my_videos,all_my_videos_update)
from .service import save_new_comments
from .bottens import register_button, phone_button, face_btn,face_btn_callback,back_to_menu
from .messages import ( ask_name_message, ask_phone_message,video_title_prompt,
video_keywords_prompt,comment_length_prompt,video_url_prompt,video_group,message_for_my_videos)
from .conf import BOT
import re

user_router = Router()

class RegisterProcess(StatesGroup):
    full_name = State()
    phone = State()

class AddVideo(StatesGroup):
    waiting_for_video_title = State()
    waiting_for_video_keywords = State()
    waiting_for_video_length = State()
    waiting_for_video_url = State()
    waiting_for_group = State()

    

@user_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user = await is_registered(message.from_user.id)
    if user:
        intro_message_registered = (
        f"<b>👋 Assalomu Alaykum, {message.from_user.first_name}!</b>\n\n"
        "🎯 Siz bot yordamida:\n"
        "• 📹 Sevimli videolaringiz uchun commentlarni kuzatishingiz mumkin\n"
        "• 💬 Foydalanuvchi izohlarini real vaqtida olishingiz mumkin\n"
        "• ⚡ Barcha videolar va commentlarni boshqarishingiz mumkin\n\n"
        "📝 Yangi video qo‘shish uchun pastdagi tugmani bosing:")
        await face_btn(message=message, text=intro_message_registered)
        return
    else:
       intro_message = (
        "<b>👋 Assalomu Alaykum!</b>\n"
        "Bizning <b>YouTube Comment Tracker Botimiz</b>ga xush kelibsiz!\n\n"
        "🎯 Botimiz yordamida siz:\n"
        "• 📺 Sevimli videolaringiz uchun commentlarni kuzatishingiz mumkin\n"
        "• 💬 Foydalanuvchi izohlarini real vaqtida ko‘rishingiz mumkin\n"
        "• ⚡ Botimiz orqali barcha videolar va commentlarni boshqarishingiz mumkin\n\n"
        "📝 Boshlash uchun, iltimos, botimizdan ro‘yxatdan o‘ting va videolar qo‘shing!")
       await register_button(message, intro_message)


# ================= REGISTER =================
@user_router.message(F.text == "📃 Ro'yhatdan o'tish")
async def start_register(message: Message, state: FSMContext):
    if not await is_registered(message.from_user.id):
        await state.set_state(RegisterProcess.full_name)
        await message.answer(ask_name_message, parse_mode="HTML")


@user_router.message(RegisterProcess.full_name)
async def fullname_register(message: Message, state: FSMContext):
    if not message.text or not await validate_full_name(message.text):
        await message.answer(FULLNAME_ERROR, parse_mode="HTML")
        return

    await state.update_data(full_name=message.text)
    await state.set_state(RegisterProcess.phone)
    await phone_button(message, ask_phone_message)


@user_router.message(RegisterProcess.phone)
async def phone_register(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    if not phone:
        await message.answer(PHONE_ERROR)
        return

    normalized = await normalize_phone(phone)
    if not normalized:
        await message.answer(PHONE_ERROR)
        return
    
    username = message.from_user.username
    if not username:
        username = f"tg_{message.from_user.id}"

    data = await state.get_data()
    user = await create_user(
        full_name=data["full_name"],
        phone=normalized,
        telegram_id=message.from_user.id,
        username=username
    )

    await state.clear()

    done_message = (
    f"🎉 Tabriklaymiz, <b>{message.from_user.first_name}</b>!\n\n"
    "<b>✅ Ro‘yxatdan muvaffaqiyatli o‘tdingiz!</b>\n\n"
    "🎯 Endi siz botimizning barcha imkoniyatlaridan to‘liq foydalanishingiz mumkin:\n"
    "• 📹 Videolar qo‘shish va kuzatish\n"
    "• 💬 Commentlarni real vaqtida ko‘rish\n"
    "• ⚡ Barcha videolar va commentlarni boshqarish\n\n")

    await face_btn(message=message, text=done_message)






@user_router.message(F.text == "Video➕")
async def video_plus_handler(message: Message, state: FSMContext):
    await back_to_menu(message=message,text=video_title_prompt)
    await state.set_state(AddVideo.waiting_for_video_title)


@user_router.message(F.text == "⬅️ Orqaga")
async def video_plus_handler(message: Message, state: FSMContext):
    await state.clear()
    await face_btn(message=message,text="🏠 <b>Bosh sahifaga qaytingiz</b>")


@user_router.message(AddVideo.waiting_for_video_title)
async def video_title_handler(message: Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer("❌ Sarlavha bo‘sh bo‘lishi mumkin emas!")
        return

    await state.update_data(title=title)
    await message.answer(text=video_keywords_prompt,parse_mode="HTML")
    await state.set_state(AddVideo.waiting_for_video_keywords)


@user_router.message(AddVideo.waiting_for_video_keywords)
async def video_keywords_handler(message: Message, state: FSMContext):
    keywords = message.text.strip()
    await state.update_data(keywords=keywords)
    await message.answer(text=comment_length_prompt,parse_mode="HTML")
    await state.set_state(AddVideo.waiting_for_video_length)


@user_router.message(AddVideo.waiting_for_video_length)
async def video_length_handler(message: Message, state: FSMContext):
    pattern = r'^[1-9]\d*$'
    length = message.text.strip()
    if not re.match(pattern,length):
        await message.answer("❌ Iltimos, musbat butun son kiriting!")
        return              
    await state.update_data(length=int(length))
    await message.answer(text=video_group,parse_mode="HTML")
    await state.set_state(AddVideo.waiting_for_group)



@user_router.message(AddVideo.waiting_for_group)
async def group_id_handler(message: Message, state: FSMContext):
    user_input = message.text.strip()

    sent_message_error = ("❌ Bu groupga xabar yubora olmayapman.\n"
    "Iltimos, avval meni groupga qo‘shing va keyin linkni qayta yuboring.")

    if user_input.startswith("https://t.me/"):
        username_or_link = user_input.split("/")[-1]
    else:
        username_or_link = user_input

    if not username_or_link.startswith("@"):
        username_or_link = f"@{username_or_link}"

    try:
        chat = await BOT.get_chat(username_or_link)
        chat_id = chat.id

        try:
            await BOT.send_message(chat_id,"✅ Men endi ushbu groupda faolman va kommentlarni qabul qilaman.")
        except Exception:
            

            await message.answer(text=sent_message_error)
            return

        await state.update_data(comment_group_id=chat_id)

        await message.answer(text=f"✅ Group/Channel muvaffaqiyatli tasdiqlandi! (ID: {chat_id})\n\n"
        "🌐 <b>Endi 📺 YouTube video URL ni kiriting:</b>\n\n"
        "Masalan:\n""<i>https://www.youtube.com/watch?v=7hghdagy</i>\n\n"
        "❗ Iltimos, faqat to‘g‘ri YouTube video havolasini yuboring.",parse_mode="HTML")

        await state.set_state(AddVideo.waiting_for_video_url)

    except Exception as e:
        await message.answer(text=sent_message_error,parse_mode="HTML")


@user_router.message(AddVideo.waiting_for_video_url)
async def video_url_handler(message: Message, state: FSMContext):
    url = message.text.strip()
    video_id = extract_video_id(url)
    if not video_id:
        invalid_url_error = "❌ <b>📺 URL noto‘g‘ri!</b>\nIltimos, to‘g‘ri YouTube video URL kiriting."
        await message.answer(text=invalid_url_error,parse_mode='HTML')
        return

    data = await state.get_data()
    title = data.get("title")
    keywords = data.get("keywords")
    length = data.get("length")
    chat_id = data.get("comment_group_id")

    user = await is_registered(message.from_user.id)
    if not user:
        await message.answer("❌ Siz ro‘yxatdan o‘tmagansiz!")
        await state.clear()
        return

    existing_video = await sync_to_async(lambda: Video.objects.filter(user=user, youtube_id=video_id).first())()
    if existing_video:
        await state.clear()
        await face_btn(message=message, text="<b>Siz bu videoni allaqachon qo‘shgansiz ❗</b>\n")
        return

    video = await sync_to_async(Video.objects.create)(
        user=user,
        youtube_id=video_id,
        url=url,
        title=title,
        keywords=keywords,
        length=length,
        chat_id=chat_id
    )
    await state.clear()
    await face_btn(message=message, text="Video muvaffaqiyatli qo‘shildi ✅")
    await save_new_comments(video=video,bot=BOT)





@user_router.message(F.text == "✳️ My Videos")
async def video_plus_handler(message: Message, state: FSMContext):
    await back_to_menu(message=message,text=message_for_my_videos)
    await all_my_videos(telegram_id=message.from_user.id,message=message)


@user_router.callback_query(F.data.startswith("status_"))
async def status_handler(callback: CallbackQuery):
    await callback.answer()
    video_id = int(callback.data.split("_")[-1])

    video = await sync_to_async(Video.objects.filter(id=video_id).first)()

    if not video:
        await face_btn_callback(callback=callback,text="Video not found ❌")
        return

    video.is_active = not video.is_active
    await sync_to_async(video.save)()

    await all_my_videos_update(callback=callback,telegram_id=callback.from_user.id)
    await callback.answer("Status updated ✅")


@user_router.callback_query(F.data.startswith("delete_"))
async def status_handler(callback: CallbackQuery):
    await callback.answer()
    video_id = int(callback.data.split("_")[-1])

    video = await sync_to_async(Video.objects.filter(id=video_id).first)()

    if not video:
        await face_btn_callback(callback=callback,text="Video not found ❌")
        return

    await sync_to_async(video.delete)()

    await all_my_videos_update(callback=callback,telegram_id=callback.from_user.id)
    await callback.answer("Deleted Successfully ✅")



    