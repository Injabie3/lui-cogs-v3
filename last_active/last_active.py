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
from .utils import config

KEY_CH_SPECIFIC = "channelSpecific"
KEY_SERVER_SPECIFIC = "serverSpecific"
KEY_GLOBAL = "global"

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
        self.config = config.Config("settings.json",
                                    cogname="lui-cogs/last_active")
        self.chSpecific = self.config.get(KEY_CH_SPECIFIC, {})
        self.serverSpecific = self.config.get(KEY_SERVER_SPECIFIC, {})
        self.userGlobal = self.config.get(KEY_GLOBAL, {})
        self.lock = Lock()

    @commands.group(name="lastactive", pass_context=True)
    async def lastActive(self, ctx):
        """Last active."""
        pprint(self.chSpecific)

    @lastActive.command(name="debug", pass_context=False)
    async def lastActiveDebug(self):
        """Turn on debugging."""
        LOGGER.setLevel(logging.DEBUG)
        await self.bot.say("Debug mode set.")

    ##################
    # Public Methods #
    ##################
    async def checkLastActive(self, uid, sid=None, cid=None):
        """Check to see when a user was last active in a specific channel and server.

        Parameters:
        -----------
        uid: int
            The ID of the user you are interested in.
        sid: int (optional)
            The ID of the server in which you are interested in.
        cid: int (optional)
            The ID of the channel you are interested in. Requires sid to be present.

        Returns:
        --------
        lastActive: datetime.datetime or None
            A datetime object of when the user was last active, or None if the user has
            not spoken or reacted.

        Raises:
        -------
        AttributeError
            When parameters are missing.

        """
        if cid:
            if not sid:
                raise AttributeError
            try:
                return self.chSpecific[sid][cid][uid]
            except KeyError:
                return None
        elif sid:
            try:
                return self.serverSpecific[sid][uid]
            except KeyError:
                return None
        else: # uid
            try:
                return self.userGlobal[uid]
            except KeyError:
                return None

    #############
    # Listeners #
    #############
    async def listenMessage(self, msg):
        """Listener for messages.

        Parameters:
        -----------
        msg: discord.Message
            The message that triggered this listener.
        """
        with self.lock:
            sid = msg.server.id
            cid = msg.channel.id
            uid = msg.author.id
            LOGGER.debug("Message: sid %s, cid %s, uid %s", sid, cid, uid)
            self._updateChannelSpecific(uid, sid, cid)
            self._updateServerSpecific(uid, sid)
            self._updateGlobal(uid)

    async def listenReaction(self, reaction, user):
        """Listener for reactions.

        Parameters:
        -----------
        reaction: discord.Reaction
            The reaction.
        user: discord.Member
            The user that reacted.
        """
        with self.lock:
            sid = reaction.message.server.id
            cid = reaction.message.channel.id
            uid = user.id
            LOGGER.debug("Reaction: sid %s, cid %s, uid %s", sid, cid, uid)
            self._updateChannelSpecific(uid, sid, cid)
            self._updateServerSpecific(uid, sid)
            self._updateGlobal(uid)

    def _updateChannelSpecific(self, uid, sid, cid):
        """Update the last active for a specific user on a specific channel.

        Parameters:
        -----------
        uid: int
            The ID of the user you want to update.
        sid: int
            The ID of the server you want to update.
        cid: int
            The ID of the channel you want to update..

        Returns:
        --------
        None, but updates self.chSpecific.
        """
        if sid not in self.chSpecific.keys():
            self.chSpecific[sid] = {}
        if cid not in self.chSpecific[sid].keys():
            self.chSpecific[sid][cid] = {}

        self.chSpecific[sid][cid][uid] = datetime.now()

    def _updateServerSpecific(self, uid, sid):
        """Update the last active for a specific user on a specific server.

        Parameters:
        -----------
        uid: int
            The ID of the user you want to update.
        sid: int
            The ID of the server you want to update.

        Returns:
        --------
        None, but updates self.serverSpecific.
        """
        if sid not in self.serverSpecific.keys():
            self.serverSpecific[sid] = {}

        self.serverSpecific[sid][uid] = datetime.now()

    def _updateGlobal(self, uid):
        """Update the last active for a specific user on ANY server.

        Parameters:
        -----------
        uid: int
            The ID of the user you want to update.

        Returns:
        --------
        None, but updates self.global.
        """
        self.userGlobal[uid] = datetime.now()

    async def flushToDisk(self):
        """Flush last active data to the disk."""
        pass

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
    bot.add_listener(customCog.listenMessage, "on_message")
    bot.add_listener(customCog.listenReaction, "on_reaction_add")
    bot.add_listener(customCog.listenReaction, "on_reaction_remove")
    bot.add_cog(customCog)
