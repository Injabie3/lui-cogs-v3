from redbot.core.bot import Red

from .vxtwitconverter import VxTwitConverter


async def setup(bot: Red):
    """Add the cog to the bot."""
    await bot.add_cog(VxTwitConverter(bot))
