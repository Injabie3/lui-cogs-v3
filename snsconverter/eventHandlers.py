from discord import Message
from redbot.core import commands

from .eventsCore import EventsCore


class EventHandlers(EventsCore):
    @commands.Cog.listener("on_message")
    async def twit_replacer(self, message: Message):
        await self._on_message_twit_replacer(message)
        await self._on_message_insta_replacer(message)
        await self._on_message_tik_replacer(message)
        await self._on_message_reddit_replacer(message)
        await self._on_message_threads_replacer(message)

    @commands.Cog.listener("on_raw_message_edit")
    async def twit_edit_replacer(self, message_before: Message, message_after):
        await self._on_edit_twit_replacer(message_before, message_after)
        await self._on_edit_insta_replacer(message_before, message_after)
        await self._on_edit_tik_replacer(message_before, message_after)
        await self._on_edit_reddit_replacer(message_before, message_after)
        await self._on_edit_threads_replacer(message_before, message_after)
