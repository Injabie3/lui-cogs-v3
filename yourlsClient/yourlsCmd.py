"""YOURLS module

Control Your Own URL Shortener instance.
"""
from datetime import timezone
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
        """Get instance-wide statistics."""
        try:
            shortener = await self.fetchYourlsClient(ctx.guild)
            urls, stats = shortener.stats("top", limit=3)
            embed = discord.Embed()
            emoji = 129351  # first_place
            for url in urls:
                actualEmoji = chr(emoji)
                print(url)
                value = f"**URL**: {url.shorturl}\n"
                value += f"**Clicks**: {url.clicks}"
                embed.add_field(name=f"{actualEmoji} URL", value=value, inline=False)
                emoji += 1

        except HTTPError:
            await ctx.send("An error occurred")
        except RuntimeError as error:
            await ctx.send(error)
        else:
            await ctx.send(
                content=f"Tracking **{stats.total_links}** links, **{stats.total_clicks}** "
                "clicks, and counting!",
                embed=embed,
            )

    @yourlsBase.command(name="info")
    async def urlInfo(self, ctx: Context, keyword: str):
        """Get keyword-specific information.

        Parameters
        ----------
        keyword: str
            The keyword used for the shortened URL.
            e.g. The keyword of `https://example.com/discord` is `discord`.
        """
        try:
            shortener = await self.fetchYourlsClient(ctx.guild)
            urlStats = shortener.url_stats(keyword)
            urlDate = urlStats.date.replace(tzinfo=timezone.utc).astimezone(tz=None)
            urlDate = urlDate.strftime("%a, %d %b %Y %I:%M%p %Z")
            embed = discord.Embed()
            embed.title = f"URL stats for {keyword}"
            embed.add_field(name="Short URL", value=f"{urlStats.shorturl}", inline=False)
            if len(urlStats.url) > 1024:
                embed.add_field(name="Long URL", value=f"Too long to be displayed.", inline=False)
            else:
                embed.add_field(name="Long URL", value=f"{urlStats.url}", inline=False)
            embed.add_field(name="Date Created", value=f"{urlDate}", inline=False)
            embed.add_field(name="Clicks", value=f"{urlStats.clicks}", inline=False)
            # TODO escape the shorturl?
            embed.add_field(
                name="More Info (Login Required)",
                value=f"[Detailed Statistics]({urlStats.shorturl}+)",
                inline=False,
            )
        except HTTPError as error:
            await ctx.send(f"{error}")
            self.logger.error(error)
        except RuntimeError as error:
            await ctx.send(error)
        else:
            await ctx.send(embed=embed)

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

    async def fetchYourlsClient(self, guild: discord.Guild):
        """Create the YOURLS client.

        Parameters
        ----------
        guild: discord.Guild
            The guild to look up the YOURLS API configuration for.

        Raises
        ------
        RuntimeError
            Unable to create the YOURLS client because of missing information.
        """
        api = await self.config.guild(guild).api()
        sig = await self.config.guild(guild).signature()
        if not (api and sig):
            raise RuntimeError("Please configure the YOURLS API first.")
        return yourls.YOURLSClient(api, signature=sig)
