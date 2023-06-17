from discord import Message

from redbot.core import commands

from .eventsCore import EventsCore


class EventHandlers(EventsCore):
    @commands.Cog.listener("on_message")
    async def twit_replacer(self, message: Message):
        await self._on_message_twit_replacer(message)

    @commands.Cog.listener("on_message_edit")
    async def twit_edit_replacer(self, message_before: Message, message_after):
        await self._on_edit_twit_replacer(message_before, message_after)
