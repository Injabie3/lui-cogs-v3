from asyncio import Lock
from logging import getLogger

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
        self.bgTask = self.bot.loop.create_task(self.setMaxImagePixels())

    async def setMaxImagePixels(self):
        pixels = await self.config.get_attr(KEY_MAX_IMAGE_PIXELS)()
        self.logger.debug("Setting max pixels to %s", pixels)
        Image.MAX_IMAGE_PIXELS = pixels
        self.initialized = True

    def cog_unload(self):
        self.bgTask.cancel()
