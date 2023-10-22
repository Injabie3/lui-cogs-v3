from redbot.core import checks, commands
from redbot.core.commands.context import Context

from .commandsCore import CommandsCore


class CommandHandlers(CommandsCore):
    @commands.group(name="vxtwitter", aliases=["vxtwit"])
    @checks.is_owner()
    async def _grpVxTwit(self, ctx: Context):
        """VxTwitter settings"""

    @_grpVxTwit.command(name="toggle")
    async def _cmdToggle(self, ctx: Context):
        """Toggle VxTwitter replacements on the server

        This will toggle the auto-reply of any Twitter links with embeds, and
        replace them with VxTwitter.
        """
        await self.cmdToggle(ctx)
