🎯 YouTube → Telegram Comment Notifier

A lightweight automation bot that bridges YouTube and Telegram.

Track new comments from any YouTube video and receive them instantly inside Telegram.

Simple. Fast. Reliable.

💡 Why This Project?

Managing YouTube engagement can be time-consuming.

This bot solves that by:

Monitoring video comments automatically

Sending new comments directly to Telegram

Eliminating manual checking

Preventing duplicate notifications

Perfect for:

Content creators

Social media managers

Community moderators

Agencies

⚙️ Built With

Python

Django

Aiogram

SQLite

Webhook Architecture

YouTube Data API v3

🧠 System Flow
Telegram User
      ↓
Telegram Bot (Webhook)
      ↓
Django Backend
      ↓
YouTube API (Polling)
      ↓
New Comment Detected
      ↓
Message Sent to Telegram
🔍 Core Functionality
1️⃣ Add Video

User sends YouTube link to bot.

2️⃣ Store Video

Bot saves:

video_id

chat_id

last_comment_time

3️⃣ Monitor Comments

Background process checks:

commentThreads.list

If new comment is detected:

Send message to Telegram

Update last tracked timestamp



📦 Fully documented open-source standard

formatda qilib beraman.
