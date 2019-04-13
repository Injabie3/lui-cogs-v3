"""Last active cog
See when the last time someone spoke in a channel.
"""

from datetime import datetime
from threading import Lock
import logging
import os
from pprint import pprint
import discord
from discord.ext import commands

LOGGER = None

SAVE_FOLDER = "data/lui-cogs/lastactive/" # Path to save folder.
SAVE_FILE = "settings.json"

def checkFolder():
    """Used to create the data folder at first startup"""
    if not os.path.exists(SAVE_FOLDER):
        print("Creating " + SAVE_FOLDER + " folder...")
        os.makedirs(SAVE_FOLDER)

class LastActive: # pylint: disable=too-few-public-methods
    """Let's see when people were last active."""

    # Class constructor
    def __init__(self, bot):
        self.bot = bot
        self.messages = {}
        self.lock = Lock()

    @commands.command(name="lastactive", pass_context=True)
    async def lastactive(self, ctx):
        """Last active."""
        pprint(self.messages)

    async def listener(self, msg):
        """Listener for messages"""
        with self.lock:
            sid = msg.server.id
            cid = msg.channel.id
            uid = msg.author.id
            if sid not in self.messages.keys():
                self.messages[sid] = {}
            if cid not in self.messages[sid].keys():
                self.messages[sid][cid] = {}
            if uid not in self.messages[sid][cid].keys():
                self.messages[sid][cid][uid] = datetime.now()

def setup(bot):
    """Add the cog to the bot."""
    global LOGGER
    checkFolder()
    LOGGER = logging.getLogger("red.LastActive")
    if LOGGER.level == 0:
        # Prevents the LOGGER from being loaded again in case of module reload.
        LOGGER.setLevel(logging.INFO)
        handler = logging.FileHandler(filename=SAVE_FOLDER+"info.log",
                                      encoding="utf-8",
                                      mode="a")
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s",
                                               datefmt="[%d/%m/%Y %H:%M:%S]"))
        LOGGER.addHandler(handler)
    customCog = LastActive(bot)
    bot.add_listener(customCog.listener, "on_message")
    bot.add_cog(customCog)
