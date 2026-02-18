import re
from asgiref.sync import sync_to_async
from bot.models import User,Video
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,Message,CallbackQuery


def extract_video_id(url: str) -> str | None:
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    else:
        return None


def get_user_sync(telegram_id: int) -> User | None:
    return User.objects.filter(telegram_id=telegram_id).first()


async def is_registered(telegram_id: int) -> User | None:
    return await sync_to_async(get_user_sync)(telegram_id)



async def create_user(full_name: str, phone: str, telegram_id: int,username : str) -> User:
    return await sync_to_async(User.objects.create)(
        full_name=full_name, phone=phone, telegram_id=telegram_id,username=username
    )


FULLNAME_ERROR = (
    "❌ Ism va familiyani to‘g‘ri kiriting.\n"
    "Masalan: Muhammad Umarov"
)


PHONE_ERROR = (
    "❌ Telefon raqam noto‘g‘ri.\n"
    "Namuna: +998901234567\n"
    "Yoki 📞 tugmani bosing"
)


async def validate_full_name(full_name: str) -> bool:
    FULL_NAME_REGEX = (
        r"^[A-Za-zА-Яа-яЎўҚқҒғҲҳЁё]+(?:['’][A-Za-zА-Яа-яЎўҚқҒғҲҳЁё]+)?"
        r"\s"
        r"[A-Za-zА-Яа-яЎўҚқҒғҲҳЁё]+(?:['’][A-Za-zА-Яа-яЎўҚқҒғҲҳЁё]+)?$"
    )

    return bool(re.fullmatch(FULL_NAME_REGEX, full_name.strip()))



async def normalize_phone(phone: str) -> str | None:
    """
    Normalize: +998901234567 formatiga keltirish
    """
    PHONE_REGEX = r"^\+998(90|91|93|94|95|97|98|99|33|88)\d{7}$"
    digits = re.sub(r"\D", "", phone)

    if digits.startswith("998") and len(digits) == 12:
        digits = "+" + digits
    elif digits.startswith("9") and len(digits) == 9:
        digits = "+998" + digits
    else:
        return None

    return digits if re.fullmatch(PHONE_REGEX, digits) else None



async def check_lenght(length:str):
    if not length.isdigit() and int(length) > 0:
        return int(length)
    


async def get_all_users():
    return await sync_to_async(list)(
        User.objects.filter(
            is_staff=False,
            telegram_id__isnull=False
        ).values_list('telegram_id', flat=True)
    )


@sync_to_async
def get_user_by_telegram_id(telegram_id: int) -> User | None:
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None


@sync_to_async
def get_all_user_ids() -> list[int]:
    return list(
        User.objects
        .exclude(telegram_id__isnull=True)
        .values_list("telegram_id", flat=True)
    )


async def is_user_video(telegram_id: int, video_url: str) -> bool:

    user = await is_registered(telegram_id)  
    if not user:
        return False

    exists = await sync_to_async(Video.objects.filter(user=user, url=video_url).first)()
    return exists


async def all_my_videos(telegram_id, message: Message):
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    if not user:
        await message.answer("No videos found ❌")
        return

    videos = await sync_to_async(list)(Video.objects.filter(user=user))

    if not videos:
        await message.answer("🎥 Sizda hozircha hech qanday video yo‘q.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for video in videos:
        status_text = "🔴 OFF" if video.is_active else "🟢 ON"

        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"🎬 {video.title}",callback_data="noop"),
            InlineKeyboardButton(text=status_text,callback_data=f"status_{video.pk}"),
            InlineKeyboardButton(text="🗑",callback_data=f"delete_{video.pk}")
        ])

    await message.answer(text="📂 Manage your videos:",reply_markup=kb)


async def all_my_videos_update(telegram_id, callback: CallbackQuery):
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    if not user:
        await callback.message.answer("No videos found ❌")
        return

    videos = await sync_to_async(list)(Video.objects.filter(user=user))

    if not videos:
        await callback.message.answer("🎥 Sizda hozircha hech qanday video yo‘q.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for video in videos:
        status_text = "🔴 OFF" if video.is_active else "🟢 ON"

        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"🎬 {video.title}",callback_data="noop"),
            InlineKeyboardButton(text=status_text,callback_data=f"status_{video.pk}"),
            InlineKeyboardButton(text="🗑",callback_data=f"delete_{video.pk}")
        ])

    await callback.message.edit_reply_markup(reply_markup=kb)










