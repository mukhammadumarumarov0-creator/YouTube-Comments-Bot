import re
import asyncio
import logging
from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from asgiref.sync import sync_to_async
from decouple import config
from aiogram.exceptions import TelegramRetryAfter

from bot.models import Video, Comment
from .conf import Bot  

API_KEY = config("YOUTUBE_API_KEY")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def fetch_comments(video_id: str, max_pages: int = 2, published_after: str = None):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    comments = []
    next_page_token = None
    attempt = 0

    while attempt < 3:
        try:
            for _ in range(max_pages):
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="plainText",
                    maxResults=100,
                    order="time",
                    pageToken=next_page_token,
                )
                if published_after:
                    request.uri += f"&publishedAfter={published_after}"
                response = request.execute()

                for item in response.get("items", []):
                    top_comment = item["snippet"]["topLevelComment"]
                    snippet = top_comment["snippet"]
                    channel_id = snippet["authorChannelId"]["value"]
                    comment_id = top_comment["id"]

                    comments.append({
                        "comment_id": comment_id,
                        "user_name": snippet["authorDisplayName"],
                        "user_link": f"https://www.youtube.com/channel/{channel_id}",
                        "text": snippet["textDisplay"],
                        "published_at": snippet.get("publishedAt")
                    })

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
            return comments
        except HttpError as e:
            attempt += 1
            wait = 2 ** attempt
            logger.warning(f"YouTube API error {e.resp.status}, retrying in {wait}s")
            asyncio.sleep(wait)
    logger.error(f"Failed to fetch comments for video {video_id} after 3 attempts")
    return []

def clean_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\u0400-\u04FF\s]", "", text).lower()

async def send_message_safe(bot: Bot, chat_id: int, text: str, parse_mode="HTML"):
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode,disable_web_page_preview=True)
    except TelegramRetryAfter as e:
        logger.warning(f"Flood control hit for chat_id={chat_id}, retrying in {e.timeout}s")
        await asyncio.sleep(e.timeout)
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode,disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Failed to send message to chat_id={chat_id}: {e}")

async def save_new_comments(bot: Bot, video: Video):
    if not video.is_active or not video.chat_id:
        return

    published_after = video.last_checked_at.isoformat() + "Z" if hasattr(video, "last_checked_at") and video.last_checked_at else None

    try:
        comments = await sync_to_async(fetch_comments)(video.youtube_id, published_after=published_after)
    except Exception as e:
        logger.error(f"Error fetching comments for video '{video.title}': {e}")
        return

    keywords = video.get_keywords()
    min_length = video.length or 0
    logger.info(f"COMMENTS FOUND: {len(comments)} for video '{video.title}'")

    batch_text = ""
    batch_count = 0
    new_comments = 0

    for c in comments:
        text = c["text"]
        clean_comment = clean_text(text)
        text_len = len(text.split())

        passes_filter = (keywords and any(k in clean_comment for k in keywords)) or text_len >= min_length
        if not passes_filter:
            continue

        exists = await sync_to_async(Comment.objects.filter(comment_id=c["comment_id"]).exists)()
        if exists:
            continue

        await sync_to_async(Comment.objects.create)(
            video=video,
            comment_id=c["comment_id"],
            user_name=c["user_name"],
            text=text,
            sent_to_telegram=True
        )
        new_comments += 1

        comment_url = f"https://www.youtube.com/watch?v={video.youtube_id}&lc={c['comment_id']}"

        batch_text += (
            f"📌 <b>{video.title}</b> uchun yangi comment\n\n"
            f"👤 YouTube: <a href='{c['user_link']}'>{c['user_name']}</a>\n"
            f"🛫 Telegram: {f'{c['user_name']}'}\n"
            f"💬 Comment: {text}\n"
            f"🔗 <a href='{comment_url}'>Go to comment</a>\n\n"
        )
        batch_count += 1

        if batch_count >= 5 or len(batch_text) > 3000:
            await send_message_safe(bot, video.chat_id, batch_text)
            batch_text = ""
            batch_count = 0
            await asyncio.sleep(1)

    if batch_text:
        await send_message_safe(bot, video.chat_id, batch_text)

    await sync_to_async(lambda: setattr(video, "last_checked_at", datetime.now(timezone.utc)))()
    await sync_to_async(video.save)()

    logger.info(f"✅ {new_comments} new comments processed for video '{video.title}'")

async def comment_checker(bot: Bot, interval: int = 300):
    while True:
        try:
            videos = await sync_to_async(list)(
                Video.objects.filter(is_active=True).exclude(chat_id__isnull=True)
            )
            if not videos:
                logger.warning("No active videos with chat_id found")
            else:
                logger.info(f"⏱ Checking {len(videos)} active videos for new comments")

            tasks = [save_new_comments(bot, video) for video in videos]
            if tasks:
                await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Comment checker cancelled, shutting down")
            break
        except Exception as e:
            logger.error(f"Error in comment_checker: {e}")

        await asyncio.sleep(interval)
