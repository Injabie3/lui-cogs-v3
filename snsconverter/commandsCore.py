from redbot.core.commands.context import Context

from .constants import KEY_ENABLED
from .core import Core


class CommandsCore(Core):
    async def cmdToggle(self, ctx: Context):
        enabledCfg = self.config.guild(ctx.guild).get_attr(KEY_ENABLED)
        enabled = not await enabledCfg()
        await enabledCfg.set(enabled)

        status = "enabled" if enabled else "disabled"
        await ctx.send(f"VxTwitter replacements are now {status}.")
