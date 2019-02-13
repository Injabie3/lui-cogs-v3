"""wordfilter module.

To filter words in a more smart/useful way than simply detecting and
deleting a message.

This cog requires paginator.py, obtainable from Rapptz/RoboDanny.
"""
import logging

from redbot.core.bot import Red
from .wordfilter import WordFilter


def setup(bot: Red):
    """Add the cog to the bot."""
    global LOGGER # pylint: disable=global-statement
    wordFilterCog = WordFilter(bot)
    wordFilterCog.logger = logging.getLogger("red.WordFilter")
    if wordFilterCog.logger.level == 0:
        # Prevents the LOGGER from being loaded again in case of module reload.
        wordFilterCog.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename="data/lui-cogs/wordfilter/info.log",
                                      encoding="utf-8",
                                      mode="a")
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s",
                                               datefmt="[%d/%m/%Y %H:%M:%S]"))
        wordFilterCog.logger.addHandler(handler)
    bot.add_cog(wordFilterCog)
