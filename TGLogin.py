from telethon.sessions import MemorySession
from telethon.sync import TelegramClient

import settings


def get_bot() -> TelegramClient:
    bot = TelegramClient(MemorySession(), settings.API_ID, settings.API_HASH)
    return bot.start(bot_token=settings.BOT_TOKEN)
