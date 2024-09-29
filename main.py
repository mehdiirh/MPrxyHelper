#!./venv/bin/python
import asyncio
import logging
import re

from telethon.sync import events
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import User

import settings
from TGLogin import get_bot
from Types import ChatAction, Message
from plugins.database import get_database
from plugins.utils import (
    get_admins,
    get_entity,
    is_admin,
    add_admin,
    delete_all_admins,
    only_admins,
    only_sudoers,
    delete_admin,
    add_all_admins,
)

# =================  CONFIGURE  ================= #
bot = get_bot()
db = get_database()
proxy_pattern = re.compile(
    r"https://t\.me/proxy\?server=.+\..+&port=\d+&secret=(?:dd.{32}|[\w-%]+)"
)
logging.basicConfig(
    filename="logs/bot.log",
    filemode="a",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d - %H:%M:%S",
    level=logging.WARNING,
)

print("BOT STARTED")


# =================  CONFIGURE  ================= #


@bot.on(events.ChatAction())
async def action_handler(action: ChatAction):
    if action.new_pin:
        raise events.StopPropagation

    if is_admin(action):
        if action.user_joined or action.user_added:
            users = action.original_update.message.action.users
            chat = action.original_update.message.to_id.channel_id

            for user in users:
                if is_admin(user):
                    await bot.edit_admin(
                        chat, user, delete_messages=True, ban_users=True
                    )

    await asyncio.sleep(0.2)
    await action.delete()
    raise events.StopPropagation


@bot.on(events.NewMessage(incoming=True, chats=settings.GROUP_IDS))
async def process_messages(message: Message):
    if is_admin(message):
        return

    message_match = proxy_pattern.search(message.raw_text)

    if not message_match:
        await asyncio.sleep(0.2)
        await message.delete()

    raise events.StopPropagation


@bot.on(events.NewMessage(pattern="^/ping$", incoming=True))
@only_admins
async def ping(message: Message):
    await message.reply("Pong!")
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"(:?^/kick$|/kick @?[A-Za-z]\w{4,})", incoming=True))
@only_admins
async def kick_user(message: Message):
    try:
        user = await get_entity(message)
        await bot.kick_participant(message.chat, user.id)

    except AttributeError:
        pass

    except:
        bot_message = await message.reply("Failed to execute command.")
        await asyncio.sleep(3)
        await bot_message.delete()

    await asyncio.sleep(0.1)
    await message.delete()
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"(:?^/ban$|/ban @?[A-Za-z]\w{4,})", incoming=True))
@only_admins
async def ban_user(message: Message):
    try:
        user = await get_entity(message)
        await bot.edit_permissions(message.chat, user, view_messages=False)

    except AttributeError:
        pass

    except:
        bot_message = await message.reply("Failed to execute command.")
        await asyncio.sleep(3)
        await bot_message.delete()

    await asyncio.sleep(0.1)
    await message.delete()
    raise events.StopPropagation


@bot.on(
    events.NewMessage(pattern=r"(:?^/unban$|/unban @?[A-Za-z]\w{4,})", incoming=True)
)
@only_admins
async def unban_user(message: Message):
    try:
        user = await get_entity(message)
        await bot.edit_permissions(message.chat, user, view_messages=True)

    except AttributeError:
        pass

    except:
        bot_message = await message.reply("Failed to execute command.")
        await asyncio.sleep(3)
        await bot_message.delete()

    await asyncio.sleep(0.1)
    await message.delete()
    raise events.StopPropagation


@bot.on(
    events.NewMessage(pattern=r"(:?^/silent$|/silent @?[A-Za-z]\w{4,})", incoming=True)
)
@only_admins
async def silent_user(message: Message):
    try:
        user = await get_entity(message)
        await bot.edit_permissions(message.chat, user, send_messages=False)

    except AttributeError:
        pass

    except:
        bot_message = await message.reply("Failed to execute command.")
        await asyncio.sleep(3)
        await bot_message.delete()

    await asyncio.sleep(0.1)
    await message.delete()
    raise events.StopPropagation


@bot.on(
    events.NewMessage(
        pattern=r"(:?^/unsilent$|/unsilent @?[A-Za-z]\w{4,})", incoming=True
    )
)
@only_admins
async def unsilent_user(message: Message):
    try:
        user = await get_entity(message)
        await bot.edit_permissions(message.chat, user, view_messages=True)

    except AttributeError:
        pass

    except:
        bot_message = await message.reply("Failed to execute command.")
        await asyncio.sleep(3)
        await bot_message.delete()

    await asyncio.sleep(0.1)
    await message.delete()
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"(:?^/mod$|/mod @?[A-Za-z]\w{4,})"))
@only_sudoers
async def mod_user(message: Message):
    try:
        user = await get_entity(message)
        await bot.edit_admin(
            message.chat, user, delete_messages=True, ban_users=True, invite_users=True
        )
        add_admin(user.id)

        await message.reply(
            f"<a href='tg://user?id={user.id}'>{user.first_name}</a> [ <code>{user.id}</code> ] "
            f"Added to admins successfully.\n\n",
            parse_mode="html",
        )

    except AttributeError:
        pass

    except:
        bot_message = await message.reply("Failed to execute command.")
        await asyncio.sleep(3)
        await bot_message.delete()

    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"(:?^/demod$|/demod @?[A-Za-z]\w{4,})"))
@only_sudoers
async def demod_user(message: Message):
    try:
        user = await get_entity(message)
        await bot.edit_admin(message.chat, user, is_admin=False)
        delete_admin(user.id)

        await message.reply(
            f"<a href='tg://user?id={user.id}'>{user.first_name}</a> [ <code>{user.id}</code> ] "
            f"Removed from admins successfully.\n\n",
            parse_mode="html",
        )

    except AttributeError:
        pass

    except:
        bot_message = await message.reply("Failed to execute command.")
        await asyncio.sleep(3)
        await bot_message.delete()

    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^/umods$"))
@only_sudoers
async def update_mods(message: Message):
    delete_all_admins()

    try:
        text = ""
        admins = []
        admin: User
        async for admin in bot.iter_participants(
            message.chat, filter=ChannelParticipantsAdmins
        ):
            admins.append(admin.id)
            text += (
                f"<a href='tg://user?id={admin.id}'>{admin.first_name}</a> [ <code>{admin.id}</code> ] "
                f"Added to admins successfully.\n\n"
            )

        add_all_admins(admins)
        await message.reply(text, parse_mode="html")

    except AttributeError:
        pass

    except:
        bot_message = await message.reply("Failed to execute command.")
        await asyncio.sleep(3)
        await bot_message.delete()

    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^/mods$"))
@only_sudoers
async def get_mods(message: Message):

    admins = get_admins()

    text = ""
    for idx, admin in enumerate(admins):
        text += f"{idx + 1} - [ `{admin}` ]\n"

    await message.reply(text)
    raise events.StopPropagation


bot.run_until_disconnected()
