import os
from collections.abc import Callable
from typing import Optional, Any, TypeVar

RT = TypeVar("RT")


def env_default(
    key: str,
    default: Optional[Any] = None,
    *,
    func: Callable[..., RT] = str,
) -> RT:
    value = os.environ.get(key, default)
    return func(value or default)


def env_list(key: str, *, func: Callable[..., RT] = str) -> list[RT]:
    value = os.environ.get(key)
    if value:
        return [func(value) for value in value.split(",")]
    return []


SUDO_IDS = env_list("SUDO_IDS", func=int)
GROUP_IDS = env_list("GROUP_IDS", func=int)

API_ID = env_default("API_ID", 0, func=int)
API_HASH = env_default("API_HASH")
BOT_TOKEN = env_default("BOT_TOKEN")
BOT_ID = env_default("BOT_ID", 0, func=int)

DB_HOST = env_default("DB_HOST")
DB_NAME = env_default("DB_NAME")
DB_USER = env_default("DB_USER")
DB_PASS = env_default("DB_PASS")
DB_PORT = env_default("DB_PORT", 0, func=int)

if not all(
    [
        SUDO_IDS,
        GROUP_IDS,
        API_ID,
        API_HASH,
        BOT_TOKEN,
        BOT_ID,
        DB_HOST,
        DB_NAME,
        DB_USER,
        DB_PASS,
        DB_PORT,
    ]
):
    raise ValueError("Bot configuration failed")
