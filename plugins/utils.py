import asyncio
from functools import wraps
from typing import Union

from telethon.tl.types import User

import settings
from Types import Message, ChatAction
from plugins.database import Settings, get_database

Peer = Union[ChatAction | Message | int | str]


async def get_entity(message: Message) -> User:
    if message.is_reply:
        reply_message: Message = await message.get_reply_message()
        user = reply_message.sender

    else:
        user = message.text.split()[1]
        user = await message.client.get_entity(user)

    if user.id == settings.BOT_ID:
        bot_message = await message.reply("Leave Me Alone -_-")
        await asyncio.sleep(3)
        await bot_message.delete()
        raise AttributeError

    return user


def get_sender_id(sender: Peer) -> int:

    if isinstance(sender, ChatAction):
        sender_id = sender.action_message.sender_id

    elif isinstance(sender, (int, str)):
        sender_id = int(sender)

    else:
        sender_id = sender.sender_id

    return sender_id


def is_admin(peer: Peer) -> bool:
    sender_id = get_sender_id(peer)

    if is_sudo(peer):
        return True

    if sender_id in settings.GROUP_IDS:
        return True

    return sender_id in get_admins()


def is_sudo(peer: Peer) -> bool:
    return get_sender_id(peer) in settings.SUDO_IDS


def only_admins(f):

    @wraps(f)
    async def decorator(event):
        if is_admin(event):
            return await f(event)

    return decorator


def only_sudoers(f):

    @wraps(f)
    async def decorator(event):
        if is_sudo(event):
            return await f(event)

    return decorator


def get_admins() -> list[int]:
    db = get_database()
    admins = db.query(Settings).get("admin").value
    admins = admins.split()
    admins = list(map(lambda x: int(x), admins))
    db.close()

    return admins


def add_admin(user_id) -> bool:
    db = get_database()
    admins = get_admins()
    if user_id in admins:
        raise ValueError("This user is already admin")

    admins.append(user_id)
    admins = list(map(lambda x: str(x), admins))
    admins = " ".join(admins)

    db.query(Settings).filter_by(name="admin").update({"value": admins})
    db.commit()
    db.close()
    return True


def delete_admin(user_id) -> None:
    db = get_database()
    admins = get_admins()
    if user_id not in admins:
        raise ValueError("This user is not admin")

    admins.remove(user_id)
    admins = list(map(lambda x: str(x), admins))
    admins = " ".join(admins)

    db.query(Settings).filter_by(name="admin").update({"value": admins})
    db.commit()
    db.close()


def add_all_admins(admins: list) -> None:
    db = get_database()

    admins = list(map(lambda x: str(x), admins))
    admins = " ".join(admins)

    db.query(Settings).filter_by(name="admin").update({"value": admins})
    db.commit()
    db.close()


def delete_all_admins() -> None:
    db = get_database()
    db.query(Settings).filter_by(name="admin").update({"value": None})
    db.commit()
    db.close()
