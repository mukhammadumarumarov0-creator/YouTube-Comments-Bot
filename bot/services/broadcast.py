import asyncio
from aiogram.exceptions import TelegramForbiddenError
from django.conf import settings
from bot.models import BroadcastMessage, User
from bot.instance.handlers.user_handlers import BOT

async def broadcast_messages():
    bot = BOT
    try:
        # Faqat jo'natilmagan xabarlar
        messages = BroadcastMessage.objects.filter(is_sent=False)

        for msg in messages:
            if msg.send_to_all:
                users = User.objects.all()  # Barchaga
            else:
                users = msg.users.all()  # Faqat tanlanganlar

            for user in users:
                try:
                    if msg.image_url and msg.text:
                        # Rasm + text → caption
                        await bot.send_photo(
                            chat_id=user.telegram_id,
                            photo=msg.image_url,
                            caption=msg.text
                        )
                    elif msg.image_url:
                        # Faqat rasm
                        await bot.send_photo(
                            chat_id=user.telegram_id,
                            photo=msg.image_url
                        )
                    elif msg.text:
                        # Faqat text
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=msg.text
                        )
                except TelegramForbiddenError:
                    # User blocklagan yoki ruxsat bermagan
                    print(f"{user} botni blocklagan, xabar jo‘natilmadi")
                except Exception as e:
                    print(f"Xato {user}: {e}")

            # Xabar barcha foydalanuvchilarga yuborilganidan keyin flagni o‘chirish
            msg.is_sent = True
            msg.save()

    finally:
        await bot.session.close()
