from redbot.core import commands

from .commandHandlers import CommandHandlers
from .eventHandlers import EventHandlers


class SNSConverter(commands.Cog, CommandHandlers, EventHandlers):
    """Converts Twitter, Instagram, Threads, Tiktok & Reddit links for better embeds"""

    pass
