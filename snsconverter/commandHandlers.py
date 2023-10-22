from redbot.core import checks, commands
from redbot.core.commands.context import Context

from .commandsCore import CommandsCore


class CommandHandlers(CommandsCore):
    @commands.group(name="snsconverter", aliases=["sns"])
    @checks.is_owner()
    async def _grpSns(self, ctx: Context):
        """SNSConverter settings"""

    @_grpSns.command(name="toggle")
    async def _cmdToggle(self, ctx: Context):
        """Toggle SNSConverter replacements on the server

        This will toggle the auto-reply of any Twitter or Instagram links with
        embeds, and replace them with vxtwitter or ddinstagram, respectively.
        """
        await self.cmdToggle(ctx)
