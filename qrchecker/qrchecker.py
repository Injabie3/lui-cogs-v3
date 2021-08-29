import io
from typing import List
import logging

import discord
from pyzbar.pyzbar import decode
from PIL import Image
from redbot.core import commands
from redbot.core.bot import Red


class QRChecker(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.logger = logging.getLogger("red.luicogs.QRChecker")
        self.logger.setLevel(logging.INFO)

    @commands.Cog.listener("on_message")
    async def listener(self, message: discord.Message):
        if not message.attachments:
            self.logger.debug("No attachments, return early")
            return
        for attachment in message.attachments:
            contentType = attachment.content_type
            if not contentType:
                self.logger.debug("Unknown content type, continue")
                continue
            elif contentType and not "image" in contentType:
                self.logger.debug("Not an image, continue")
                continue
            # At this point we decern that it's an image.
            try:
                fp = io.BytesIO(await attachment.read())
                image = Image.open(fp)
                codes: List[pyzbar.pyzbar.Decoded] = decode(image)
                self.logger.debug("Found %s codes", len(codes))
            except Exception:
                self.logger.error("Couldn't check file.", exc_info=True)

            for code in codes:
                msg = f"Found a QR code, the contents are: ```{code.data.decode()}```"
                if len(msg) > 2000:
                    msg = msg[:1999]
                await message.reply(msg, mention_author=False)
