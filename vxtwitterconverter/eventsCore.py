from discord import Embed, Message, channel

from .constants import KEY_ENABLED
from .core import Core


class EventsCore(Core):
    @staticmethod
    def _convert_to_vx_twitter_url(embeds: list[Embed]):
        """
        Parameters
        ----------
        embeds: list of discord embeds

        Returns
        -------
            filtered list of twitter URLs that have been converted to vxtwitter
        """

        # pulls only video embeds from list of embeds
        urls = [entry.url for entry in embeds if entry.video]

        vxtwitter_urls = [
            result.replace("https://twitter.com", "https://vxtwitter.com")
            for result in urls
            if "https://twitter.com" in result
        ]

        return vxtwitter_urls

    @staticmethod
    def _urls_to_string(vx_twit_links: list[str]):
        """
        Parameters
        ----------
        vx_twit_links: list of urls

        Returns
        -------
            Formatted output
        """

        return "".join(
            [
                "OwO what's this?\n",
                "*notices your terrible twitter embeds*\n",
                "Here's a better alternative:\n",
                "\n".join(vx_twit_links),
            ]
        )

    @staticmethod
    def _valid(message: Message):
        """
        Parameters
        ----------
        message: Discord input message object

        Returns
        -------
            True if the message is from a human in a guild and contains video embeds
            False otherwise
        """

        # skips if the message is sent by any bot
        if message.author.bot:
            return False

        # skips if message is in dm
        if isinstance(message.channel, channel.DMChannel):
            return False

        # skips if the message has no embeds
        if not any(embed.video for embed in message.embeds):
            return False

        return True

    async def _on_message_twit_replacer(self, message: Message):
        if not self._valid(message):
            return

        if not await self.config.guild(message.guild).get_attr(KEY_ENABLED)():
            self.logger.debug(
                "VxTwit disabled for guild %s (%s), skipping", message.guild.name, message.guild.id
            )
            return

        # the actual code part
        vx_twtter_urls = self._convert_to_vx_twitter_url(message.embeds)

        # no changed urls detected
        if not vx_twtter_urls:
            return

        # constructs the message and replies with a mention
        ok = await message.reply(self._urls_to_string(vx_twtter_urls))

        # Remove embeds from user message if reply is successful
        if ok:
            await message.edit(suppress=True)

    async def _on_edit_twit_replacer(self, message_before: Message, message_after: Message):
        # skips if the message is sent by any bot
        if not self._valid(message_after):
            return

        if not await self.config.guild(message_after.guild).get_attr(KEY_ENABLED)():
            self.logger.info(
                "VxTwit disabled for guild %s (%s), skipping",
                message_after.guild.name,
                message_after.guild.id,
            )
            return

        video_embed_before = [embed for embed in message_before.embeds if embed.video]
        video_embed_after = [embed for embed in message_after.embeds if embed.video]
        new_video_embeds = [
            embed for embed in video_embed_after if embed not in video_embed_before
        ]

        # skips if the message has no new embeds
        if not new_video_embeds:
            return

        vx_twtter_urls = self._convert_to_vx_twitter_url(new_video_embeds)

        # no changed urls detected
        if not vx_twtter_urls:
            return

        # constructs the message and replies with a mention
        ok = await message_after.reply(self._urls_to_string(vx_twtter_urls))

        # Remove embeds from user message if reply is successful
        if ok:
            await message_after.edit(suppress=True)
