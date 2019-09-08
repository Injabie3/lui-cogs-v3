"""Stats module.

Collect some stats for ourselves.
"""

from redbot.core import Config, checks, commands, data_manager
from redbot.core.bot import Red
from redbot.core.commands.context import Context
from redbot.core.utils import paginator

BASE_MEMBER = \
{
    "messageCount": {}
}

BASE_GUILD = \
{
    "initialized": False,
}

BASE_CHANNEL = \
{
    "lastUpdated": None
}


class Stats(commands.Cog):
    """A cog to collect statistics within a guild."""
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self,
                                      identifier=5842647,
                                      force_registration=True)
        self.config.register_member(**BASE_MEMBER)
        self.config.register_channel(**BASE_CHANNEL)
        self.config.register_guild(**BASE_GUILD)

        # Initialize logger, and save to cog folder.
        saveFolder = data_manager.cog_data_path(cog_instance=self)
        self.logger = logging.getLogger("red.Stats")
        if self.logger.level == 0:
            # Prevents the self.logger from being loaded again in case of module reload.
            self.logger.setLevel(logging.INFO)
            handler = logging.FileHandler(filename=str(saveFolder) +
                                          "/info.log",
                                          encoding="utf-8",
                                          mode="a")
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(message)s",
                                  datefmt="[%d/%m/%Y %H:%M:%S]"))
            self.logger.addHandler(handler)


    @commands.group(name="stats")
    @commands.guild_only()
    async def statsGroup(self, ctx: Context):
        """Stats for the guild."""
        pass

    @stats.command(name="update")
    async def update(self, ctx: Context):
        """Update the message count for all users on the guild.

        This operation may take a long time.
        """
        self.logger.debug("Starting stats update on guild %s (%s)",
                          ctx.guild.name, ctx.guild.id)
        status = ctx.send(":information_source: Updating, please wait...")
        membersLock = self.config.get_members_lock()
        channelsLock = self.config.get_channels_lock()

        await membersLock.acquire()
        await channelsLock.acquire()

        self.logger.debug("Member and channel locks acquired")

        for guild in self.bot.guilds:
            pass


    @commands.Cog.listener("on_message")
    async def messageListener(self, message: discord.Message):
        """Check each message and update the info for the guild member."""
        pass
