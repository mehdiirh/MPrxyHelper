from typing import Union

from telethon import TelegramClient
from telethon.events import NewMessage, CallbackQuery, ChatAction as CAction
from telethon.tl.custom import Message, Conversation, Forward

ChatAction = CAction.Event
Message = Union[NewMessage.Event, Message]
Conversation = Union[NewMessage.Event, Conversation]
CallbackQuery = CallbackQuery.Event
TelegramClient = TelegramClient
Forward = Forward
