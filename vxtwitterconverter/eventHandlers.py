from discord import Message

from redbot.core import commands

from .eventsCore import EventsCore


class EventHandlers(EventsCore):
    @commands.Cog.listener("on_message")
    async def twit_replacer(self, message: Message):
        await self._twit_replacer(message)
