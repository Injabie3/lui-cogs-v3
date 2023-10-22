from redbot.core.bot import Red

from .snsconverter import SNSConverter


async def setup(bot: Red):
    """Add the cog to the bot."""
    await bot.add_cog(SNSConverter(bot))
