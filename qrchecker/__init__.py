"""qrchecker module.

Checks QR code images.

"""

from redbot.core.bot import Red
from .qrchecker import QRChecker


def setup(bot: Red):
    """Add the cog to the bot."""
    bot.add_cog(QRChecker(bot))
