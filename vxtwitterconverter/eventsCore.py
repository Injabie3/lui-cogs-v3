from discord import Message, channel
from urlextract import URLExtract

from .constants import KEY_ENABLED
from .core import Core


class EventsCore(Core):
    async def _twit_replacer(self, message: Message):
        # skips if the message is sent by any bot
        if message.author.bot:
            return

        # skips if message is in dm
        if isinstance(message.channel, channel.DMChannel):
            return

        if not await self.config.guild(message.guild).get_attr(KEY_ENABLED)():
            self.logger.debug(
                "VxTwit disabled for guild %s (%s), skipping", message.guild.name, message.guild.id
            )
            return

        # skips if the message has no embeds
        if not any(embed.video for embed in message.embeds):
            return

        # the actual code part
        vx_twit_links = [
            result.replace("https://twitter.com", "https://vxtwitter.com")
            for result in URLExtract().find_urls(message.content)
            if "https://twitter.com" in result
        ]

        # if we can't find any twitter links
        if not vx_twit_links:
            self.logger.debug("Embed found, but cannot find any valid links in the message")
            return

        # constructs the message and replies with a mention
        ok = await message.reply(
            "OwO what's this?\n"
            "*notices your terrible twitter embeds*\n"
            "Here's a better alternative:\n" + "\n".join(vx_twit_links),
        )

        # Remove embeds from user message if reply is successful
        if ok:
            await message.edit(suppress=True)
