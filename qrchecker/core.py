from asyncio import Lock
from logging import getLogger
from typing import Optional

from PIL import Image
from redbot.core import Config
from redbot.core.bot import Red

from .constants import BASE_GLOBAL, BASE_GUILD, KEY_MAX_IMAGE_PIXELS


class Core:
    def __init__(self, bot: Red):
        self.bot = bot
        self.lock = Lock()
        self.logger = getLogger("red.luicogs.QRChecker")
        self.config = Config.get_conf(self, identifier=5842647, force_registration=True)
        self.config.register_global(**BASE_GLOBAL)
        self.config.register_guild(**BASE_GUILD)
        self.initialized: bool = False
        self.bgTask = self.bot.loop.create_task(self.init())

    def cog_unload(self):
        self.bgTask.cancel()

    async def init(self):
        await self.setMaxImagePixels()
        self.initialized = True

    async def setMaxImagePixels(self, value: Optional[int] = None):
        """Set PIL/Pillow's max image pixels to prevent `DecompressionBombWarning`.
        If `value` is `None`, the max image pixels value from config will be used."""

        if value is None:
            value = await self.config.get_attr(KEY_MAX_IMAGE_PIXELS)()
        else:
            await self.config.get_attr(KEY_MAX_IMAGE_PIXELS).set(value)
        Image.MAX_IMAGE_PIXELS = value
        self.logger.debug("Set max pixels to %s.", value)
