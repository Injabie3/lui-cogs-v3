from redbot.core.commands.context import Context

from .core import Core
from .constants import KEY_ENABLED


class CommandsCore(Core):
    async def cmdToggle(self, ctx: Context):
        enabled = not await self.config.guild(ctx.guild).get_attr(KEY_ENABLED)()
        await self.config.guild(ctx.guild).get_attr(KEY_ENABLED).set(enabled)

        status = "enabled" if enabled else "disabled"
        await ctx.send(f"VxTwitter replacements are now {status}.")
