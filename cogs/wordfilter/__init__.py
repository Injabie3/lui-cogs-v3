from redbot.core.bot import Red
from .wordfilter import WordFilter


def setup(bot: Red):
    bot.add_cog(WordFilter(bot))
