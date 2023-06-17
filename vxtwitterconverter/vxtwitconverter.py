from redbot.core import commands

from .commandHandlers import CommandHandlers
from .eventHandlers import EventHandlers


class VxTwitConverter(commands.Cog, CommandHandlers, EventHandlers):
    """Converts Twitter link to VxTwitter for better video embeds"""

    pass
