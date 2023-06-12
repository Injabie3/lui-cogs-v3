import logging
import os

from redbot.core import data_manager
from redbot.core.bot import Red


class Core:
    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot

        # Initialize logger, and save to cog folder.
        save_folder = data_manager.cog_data_path(cog_instance=self)
        self.logger = logging.getLogger("red.luicogs.vxtwitconverter")
        if not self.logger.handlers:
            log_path = os.path.join(save_folder, "info.log")
            handler = logging.FileHandler(filename=log_path, encoding="utf-8", mode="a")
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(message)s", datefmt="[%d/%m/%Y %H:%M:%S]")
            )
            self.logger.addHandler(handler)
