import asyncio
import logging
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async

from bot.models import Video
from bot.instance.handlers.service import save_new_comments
from bot.instance.handlers.conf import BOT  

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

class Command(BaseCommand):
    help = "YouTube videolar uchun yangi commentlarni tekshiradi"

    def handle(self, *args, **options):
        asyncio.run(self.run())

    async def run(self):
        videos = await sync_to_async(list)(
            Video.objects.filter(is_active=True).exclude(chat_id__isnull=True)
        )

        if not videos:
            logger.info("No active videos with chat_id found. Exiting.")
            await BOT.session.close()
            return

        logger.info(f"⏱ Checking {len(videos)} active videos for new comments")

        tasks = []
        for video in videos:
            tasks.append(save_new_comments(BOT, video))

        await asyncio.gather(*tasks)

        logger.info("✅ Barcha videolar uchun commentlar tekshirildi!")

        await BOT.session.close()
