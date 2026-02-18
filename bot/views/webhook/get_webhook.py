import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from config import settings
from bot.service import BotService

logger = logging.getLogger(__name__)

# Faqat bitta bot token bosh qismi
EXPECTED_BOT_ID = settings.BOT_TOKEN.split(":", 1)[0]

@csrf_exempt
async def handle_updates(request, bot_id: str):
    """
    Handle incoming Telegram webhook updates for a single bot.
    """

    # Faqat POST ruxsat
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    # Faqat bitta bot token tekshiruvi
    if bot_id != EXPECTED_BOT_ID:
        logger.warning("Ignored webhook for unknown bot_id=%s", bot_id)
        return JsonResponse({"status": "ignored"}, status=200)

    # Telegram update ni olish
    try:
        update_data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        return JsonResponse({"status": "error", "error": "Invalid JSON"}, status=400)

    # Update ni BotService ga yuborish
    try:
        await BotService.feed_update(
            token=settings.BOT_TOKEN,
            update=update_data
        )
        return JsonResponse({"status": "ok"})
    except Exception as exc:
        logger.exception("Error handling webhook")
        return JsonResponse({"status": "error", "error": str(exc)}, status=500)
