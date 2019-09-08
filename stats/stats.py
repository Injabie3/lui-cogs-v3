"""Stats module.

Collect some stats for ourselves.
"""

from redbot.core import Config, checks, commands, data_manager
from redbot.core.utils import paginator
from redbot.core.bot import Red

BASE_MEMBER = \
{
    "messageCount": {}
}


class Stats(commands.Cog):
    """A cog to collect statistics within a guild."""
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self,
                                      identifier=5842647,
                                      force_registration=True)
        self.config.register_member(**BASE_MEMBER)

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
