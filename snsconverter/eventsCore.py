from discord import Message, RawMessageUpdateEvent

from .constants import KEY_ENABLED, SocialMedia
from .core import Core
from .helpers import (
    convert_to_ddinsta_url,
    convert_to_fx_twitter_url,
    convert_to_rxddit_url,
    convert_to_vx_threads_url,
    convert_to_vx_tiktok_url,
    urls_to_string,
    valid,
)


class EventsCore(Core):
    async def _on_message_insta_replacer(self, message: Message):
        if not valid(message):
            return

        # skips if the message has no embeds
        if not message.embeds:
            return

        if not await self.config.guild(message.guild).get_attr(KEY_ENABLED)():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                message.guild.name,
                message.guild.id,
            )
            return

        ddinsta_urls = convert_to_ddinsta_url(message.embeds)

        if not ddinsta_urls:
            return

        # constructs the message and replies with a mention
        ok = await message.reply(urls_to_string(ddinsta_urls, SocialMedia.INSTAGRAM))

        # Remove embeds from user message if reply is successful
        if ok:
            await message.edit(suppress=True)

    async def _on_edit_insta_replacer(self, payload: RawMessageUpdateEvent):
        if not valid(payload.cached_message):
            return

        # skips if the message has no embeds
        if not payload.data["embeds"]:
            return

        if not await self.config.guild(payload.cached_message.guild).get_attr(
            KEY_ENABLED
        )():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                payload.cached_message.guild.name,
                payload.cached_message.guild.id,
            )
            return

        new_embeds = [
            embed
            for embed in payload.data["embeds"]
            if embed not in payload.cached_message.embeds
        ]

        # skips if the message has no new embeds
        if not new_embeds:
            return

        ddinsta_urls = convert_to_ddinsta_url(new_embeds)

        if not ddinsta_urls:
            return

        # constructs the message and replies with a mention
        ok = await payload.cached_message.reply(
            urls_to_string(ddinsta_urls, SocialMedia.INSTAGRAM)
        )

        # Remove embeds from user message if reply is successful
        if ok:
            await payload.cached_message.edit(suppress=True)

    async def _on_message_twit_replacer(self, message: Message):
        if not valid(message):
            return

        if not await self.config.guild(message.guild).get_attr(KEY_ENABLED)():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                message.guild.name,
                message.guild.id,
            )
            return

        # the actual code part
        fx_twtter_urls = convert_to_fx_twitter_url(message.content)

        # no changed urls detected
        if not fx_twtter_urls:
            return

        # constructs the message and replies with a mention
        await message.reply(urls_to_string(fx_twtter_urls, SocialMedia.TWITTER))

    async def _on_edit_twit_replacer(self, payload: RawMessageUpdateEvent):
        # skips if the message is sent by any bot
        if not valid(payload.cached_message):
            return

        if not await self.config.guild(payload.cached_message.guild).get_attr(
            KEY_ENABLED
        )():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                payload.cached_message.guild.name,
                payload.cached_message.guild.id,
            )
            return

        fx_twtter_urls = convert_to_fx_twitter_url(payload.data["content"])

        # no changed urls detected
        if not fx_twtter_urls:
            return

        # constructs the message and replies with a mention
        await payload.cached_message.reply(
            urls_to_string(fx_twtter_urls, SocialMedia.TWITTER)
        )

    async def _on_message_tik_replacer(self, message: Message):
        if not valid(message):
            return

        if not message.embeds:
            return

        if not await self.config.guild(message.guild).get_attr(KEY_ENABLED)():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                message.guild.name,
                message.guild.id,
            )
            return

        # the actual code part
        vx_tiktok_urls = convert_to_vx_tiktok_url(message.embeds)

        # no changed urls detected
        if not vx_tiktok_urls:
            return

        # constructs the message and replies with a mention
        ok = await message.reply(urls_to_string(vx_tiktok_urls, SocialMedia.TIKTOK))

        # Remove embeds from user message if reply is successful
        if ok:
            await message.edit(suppress=True)

    async def _on_edit_tik_replacer(self, payload: RawMessageUpdateEvent):
        # skips if the message is sent by any bot
        if not valid(payload.cached_message):
            return

        # skips if the message has no embeds
        if not payload.data["embeds"]:
            return

        if not await self.config.guild(payload.cached_message.guild).get_attr(
            KEY_ENABLED
        )():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                payload.cached_message.guild.name,
                payload.cached_message.guild.id,
            )
            return

        video_embed_before = [
            embed for embed in payload.cached_message.embeds if embed.video
        ]
        video_embed_after = [embed for embed in payload.data["embeds"] if embed.video]
        new_video_embeds = [
            embed for embed in video_embed_after if embed not in video_embed_before
        ]

        # skips if the message has no new embeds
        if not new_video_embeds:
            return

        vx_tiktok_urls = convert_to_vx_tiktok_url(new_video_embeds)

        # no changed urls detected
        if not vx_tiktok_urls:
            return

        # constructs the message and replies with a mention
        ok = await payload.cached_message.reply(
            urls_to_string(vx_tiktok_urls, SocialMedia.TIKTOK)
        )

        # Remove embeds from user message if reply is successful
        if ok:
            await payload.cached_message.edit(suppress=True)

    async def _on_message_reddit_replacer(self, message: Message):
        if not valid(message):
            return

        if not message.embeds:
            return

        if not await self.config.guild(message.guild).get_attr(KEY_ENABLED)():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                message.guild.name,
                message.guild.id,
            )
            return

        # the actual code part
        rxddit_urls = convert_to_rxddit_url(message.embeds)

        # no changed urls detected
        if not rxddit_urls:
            return

        # constructs the message and replies with a mention
        ok = await message.reply(urls_to_string(rxddit_urls, SocialMedia.REDDIT))

        # Remove embeds from user message if reply is successful
        if ok:
            await message.edit(suppress=True)

    async def _on_edit_reddit_replacer(self, payload: RawMessageUpdateEvent):
        # skips if the message is sent by any bot
        if not valid(payload.cached_message):
            return

        # skips if the message has no embeds
        if not payload.data["embeds"]:
            return

        if not await self.config.guild(payload.cached_message.guild).get_attr(
            KEY_ENABLED
        )():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                payload.cached_message.guild.name,
                payload.cached_message.guild.id,
            )
            return

        video_embed_before = [
            embed for embed in payload.cached_message.embeds if embed.video
        ]
        video_embed_after = [embed for embed in payload.data["embeds"] if embed.video]
        new_video_embeds = [
            embed for embed in video_embed_after if embed not in video_embed_before
        ]

        # skips if the message has no new embeds
        if not new_video_embeds:
            return

        rxddit_urls = convert_to_rxddit_url(new_video_embeds)

        # no changed urls detected
        if not rxddit_urls:
            return

        # constructs the message and replies with a mention
        ok = await payload.cached_message.reply(
            urls_to_string(rxddit_urls, SocialMedia.REDDIT)
        )

        # Remove embeds from user message if reply is successful
        if ok:
            await payload.cached_message.edit(suppress=True)

    async def _on_message_threads_replacer(self, message: Message):
        if not valid(message):
            return

        if not message.embeds:
            return

        if not await self.config.guild(message.guild).get_attr(KEY_ENABLED)():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                message.guild.name,
                message.guild.id,
            )
            return

        # the actual code part
        vx_threads_urls = convert_to_vx_threads_url(message.embeds)

        # no changed urls detected
        if not vx_threads_urls:
            return

        # constructs the message and replies with a mention
        ok = await message.reply(urls_to_string(vx_threads_urls, SocialMedia.THREADS))

        # Remove embeds from user message if reply is successful
        if ok:
            await message.edit(suppress=True)

    async def _on_edit_threads_replacer(self, payload: RawMessageUpdateEvent):
        # skips if the message is sent by any bot
        if not valid(payload.cached_message):
            return

        # skips if the message has no embeds
        if not payload.data["embeds"]:
            return

        if not await self.config.guild(payload.cached_message.guild).get_attr(
            KEY_ENABLED
        )():
            self.logger.debug(
                "SNSConverter disabled for guild %s (%s), skipping",
                payload.cached_message.guild.name,
                payload.cached_message.guild.id,
            )
            return

        video_embed_before = [
            embed for embed in payload.cached_message.embeds if embed.video
        ]
        video_embed_after = [embed for embed in payload.data["embeds"] if embed.video]
        new_video_embeds = [
            embed for embed in video_embed_after if embed not in video_embed_before
        ]

        # skips if the message has no new embeds
        if not new_video_embeds:
            return

        vx_threads_urls = convert_to_vx_threads_url(new_video_embeds)

        # no changed urls detected
        if not vx_threads_urls:
            return

        # constructs the message and replies with a mention
        ok = await payload.cached_message.reply(
            urls_to_string(vx_threads_urls, SocialMedia.THREADS)
        )

        # Remove embeds from user message if reply is successful
        if ok:
            await payload.cached_message.edit(suppress=True)
