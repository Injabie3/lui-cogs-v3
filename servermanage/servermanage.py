"""Server Manage Cog, to help manage server icon and banners."""
import logging
import time
import asyncio
from datetime import datetime, timedelta
import discord
from redbot.core import Config, checks, commands, data_manager
from redbot.core.commands.context import Context
from redbot.core.utils import paginator
from redbot.core.bot import Red

BASE_GUILD = {"icons": {}, "dates": {}}


class ServerManage(commands.Cog):
    """Auto-assign server banner and icon on configurable days."""

    # Class constructor
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=5842647, force_registration=True)
        # Register default (empty) settings.
        self.config.register_guild(**BASE_GUILD)

        # Initialize logger, and save to cog folder.
        saveFolder = data_manager.cog_data_path(cog_instance=self)
        self.logger = logging.getLogger("red.luicogs.ServerManage")
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

        # On cog load, we want the loop to run once.
        self.lastChecked = datetime.now() - timedelta(days=1)
        # self.bgTask = self.bot.loop.create_task(self.birthdayLoop())

    # Cancel the background task on cog unload.
    def __unload(self):  # pylint: disable=invalid-name
        # TODO add task later
        # self.bgTask.cancel()
        pass

    @commands.group(name="servermanage", aliases=["sm"])
    @commands.guild_only()
    @checks.mod_or_permissions()
    async def serverManage(self, ctx: Context):
        """Manage server icons and banners."""

    @serverManage.group(name="icons")
    async def serverIcons(self, ctx: Context):
        """Manage server icons."""

    @serverIcons.command(name="add", aliases=["create"])
    async def iconAdd(self, ctx: Context, iconName: str):
        """Add a server icon to the database.

        Parameters
        ----------
        iconName: str
            The name of the icon you wish to add.
        image: attachment
            The server icon, included as an attachment.
        """

    @serverIcons.command(name="remove", aliases=["del", "delete", "rm"])
    async def iconRemove(self, ctx: Context, iconName: str):
        """Remove a server icon from the database.

        Parameters
        ----------
        iconName: str
            The icon name you wish to remove.
        """

    @serverIcons.command(name="show")
    async def iconShow(self, ctx: Context, iconName: str):
        """Show a server icon from the database.

        Parameters
        ----------
        iconName: str
            The icon name you wish to show.
        """

    @serverIcons.command(name="list", aliases=["ls"])
    async def iconList(self, ctx: Context):
        """List the dates associated with server icons."""
