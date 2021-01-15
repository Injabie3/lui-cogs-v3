"""YOURLS module

Control Your Own URL Shortener instance.
"""
import logging
import discord
from redbot.core import Config, checks, commands, data_manager
from redbot.core.bot import Red
from redbot.core.commands.context import Context

import yourls
from requests.exceptions import HTTPError


BASE_GUILD = {
    "api": None,
    "signature": None,
}


class YOURLS(commands.Cog):
    def __init__(self, bot: Red):
        super().__init__()
        self.config = Config.get_conf(self, identifier=5842647, force_registration=True)
        self.config.register_guild(**BASE_GUILD)

        saveFolder = data_manager.cog_data_path(cog_instance=self)
        self.logger = logging.getLogger("red.luicogs.YOURLS")
        if self.logger.level == 0:
            # Prevents the self.logger from being loaded again in case of module reload.
            self.logger.setLevel(logging.INFO)
            handler = logging.FileHandler(
                filename=str(saveFolder) + "/info.log", encoding="utf-8", mode="a"
            )
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(message)s", datefmt="[%d/%m/%Y %H:%M:%S]")
            )
            self.logger.addHandler(handler)

    @commands.group(name="yourls")
    @commands.guild_only()
    @checks.mod_or_permissions()
    async def yourlsBase(self, ctx: Context):
        """Manage the YOURLS instance"""

    @yourlsBase.command(name="stats")
    async def stats(self, ctx: Context):
        """Get YOURLS statistics."""
        # TODO Put into helper.
        api = await self.config.guild(ctx.guild).api()
        sig = await self.config.guild(ctx.guild).signature()
        if not (api and sig):
            await ctx.send("Please configure the YOURLS API first.")
            return
        try:
            shortener = yourls.YOURLSClient(api, signature=sig)
            stats = shortener.db_stats()
        except HTTPError:
            await ctx.send("An error occurred")
        else:
            await ctx.send(
                f"Tracking **{stats.total_links}** links, **{stats.total_clicks}** "
                "clicks, and counting!"
            )

    @yourlsBase.group(name="settings")
    async def settingsBase(self, ctx: Context):
        """Configure the YOURLS connection"""

    @settingsBase.command(name="api")
    async def api(self, ctx: Context, apiEndpoint: str):
        """Configure the API endpoint for YOURLS.

        Parameters
        ----------
        apiEndpoint: str
            The URL to the YOURLS API endpoint.
        """
        await self.config.guild(ctx.guild).api.set(apiEndpoint)
        await ctx.send(f"API endpoint set to {apiEndpoint}")

    @settingsBase.command(name="signature", aliases=["sig"])
    async def sig(self, ctx: Context, signature: str):
        """Configure the API endpoint for YOURLS.

        Parameters
        ----------
        signature: str
            The signature to access the YOURLS API endpoint.
        """
        await self.config.guild(ctx.guild).signature.set(signature)
        await ctx.send(f"API signature set.")
        await ctx.message.delete()
