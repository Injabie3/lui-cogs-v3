from typing import Optional

from PIL import Image
from redbot.core.commands import Context
from redbot.core.utils.chat_formatting import success

from .constants import KEY_ENABLED, KEY_MAX_IMAGE_PIXELS
from .core import Core


class CommandsCore(Core):
    async def cmdQrCheckerToggle(self, ctx: Context):
        """Toggle QR code checking"""
        guild = ctx.guild
        if not guild:
            return
        guildConfig = self.config.guild(guild)

        enabled: bool = await guildConfig.get_attr(KEY_ENABLED)()
        if enabled:
            await guildConfig.get_attr(KEY_ENABLED).set(False)
            await ctx.send("QR code checking is now **disabled** for this guild.")
        else:
            await guildConfig.get_attr(KEY_ENABLED).set(True)
            await ctx.send("QR code checking is now **enabled** for this guild.")

    async def cmdQrCheckerShow(self, ctx: Context):
        """Show current settings"""
        pixels = await self.config.get_attr(KEY_MAX_IMAGE_PIXELS)()
        enabled = await self.config.guild(ctx.guild).get_attr(KEY_ENABLED)()
        msg = "**__Global settings:__**\n"
        msg += f"Max pixels: **{'Unlimited' if not pixels else pixels} pixels**\n\n"
        msg += "**__Guild settings:__**\n"
        msg += f"Enabled: **{'Yes' if enabled else 'No'}**"
        await ctx.send(msg)

    async def cmdQrCheckerMaxSize(self, ctx: Context, *, pixels: Optional[int]):
        """Set the maximum image pixels to check.

        Binary images are loaded into RAM in Pillow, which uses RAM. If your bot is
        running on a system with limited RAM, set this to a low value to avoid OOM
        killer from killing your bot.

        Parameters
        ----------
        size: Optional[int]
            The maximum number of pixels in an image to check.
        """
        if pixels and pixels < 0:
            await ctx.send("Please enter a positive number")
            return
        elif not pixels:
            await ctx.send(
                success("Disabled max pixels. The bot will check images of " "any size.")
            )
        else:
            await ctx.send(success(f"Max image pixels set to: **{pixels} pixels**."))

        await self.config.get_attr(KEY_MAX_IMAGE_PIXELS).set(pixels)
        Image.MAX_IMAGE_PIXELS = pixels
