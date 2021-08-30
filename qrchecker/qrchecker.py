"""QR Code Checker

Requires:
- pyzbar from PyPI
- libzbar0 from your distro's package repo
"""
import io
from typing import List
import logging

import discord
from pyzbar.pyzbar import Decoded, decode
from PIL import Image
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify


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
                codes: List[Decoded] = decode(image)
                self.logger.debug("Found %s codes", len(codes))
            except Exception:
                self.logger.error("Couldn't check file.", exc_info=True)

            if not codes:
                self.logger.debug("No QR codes found.")
                return
            numQrCodes = len(codes)
            if numQrCodes == 1:
                code = codes[0]
                msg = f"Found a QR code, the contents are: ```{code.data.decode()}```"
                await message.reply(msg, mention_author=False)
            else:
                pages: List[str] = []
                pages.append("Found several QR codes, their contents are:")
                for code in codes:
                    data = code.data.decode()
                    if len(data) > 1990:
                        contents = f"```{data[:1990]}...```"
                    else:
                        contents = f"```{data}```"
                    pages.append(contents)
                firstMessage = True
                ctx = await self.bot.get_context(message)
                for textToSend in pagify("\n".join(pages)):
                    if firstMessage:
                        await message.reply(textToSend, mention_author=False)
                        firstMessage = False
                    else:
                        await ctx.send(textToSend)
