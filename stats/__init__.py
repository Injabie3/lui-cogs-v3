"""stats module."""

from redbot.core.bot import Red
from .stats import Stats


def setup(bot: Red):
    """Add the cog to the bot."""
    bot.add_cog(Stats(bot))
