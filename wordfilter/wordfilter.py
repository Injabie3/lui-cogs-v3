"""Word Filter cog.
To filter words in a more smart/useful wya than simply detecting and
deleting a message.
"""
import re
from threading import Lock
import logging
import asyncio
import random
import discord
from redbot.core import Config, checks, commands
from redbot.core.bot import Red

COLOUR = discord.Colour
COLOURS = [COLOUR.purple(),
           COLOUR.red(),
           COLOUR.blue(),
           COLOUR.orange(),
           COLOUR.green()]
LOGGER = None
PATTERN_CHANNEL_ID = r'<#(\d+)>'
BASE = \
{
 "channelDenied" : {},
 "channelAllowed" : {},
 "filters" : [],
 "commandDenied" : [],
 "toggleMod" : False
}

class WordFilter(commands.Cog): # pylint: disable=too-many-instance-attributes
    """Word Filter cog, for all your word filtering needs."""

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=5842647, force_registration=True)
        self.config.register_guild(**BASE) # Register default (empty) settings.

        # self.commandBlacklist = dataIO.load_json(PATH_BLACKLIST)
        # self.filters = dataIO.load_json(PATH_FILTER)
        # self.whitelist = dataIO.load_json(PATH_WHITELIST)
        # self.settings = dataIO.load_json(PATH_SETTINGS)

    @commands.group(name="wordfilter", aliases=["wf"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def wordFilter(self, ctx):
        """Smart word filtering"""

    @wordFilter.command(name="add")
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def addFilter(self, ctx, word: str):
        """Add word to filter"""
        guildId = ctx.message.guild.id
        user = ctx.message.author
        guildName = ctx.message.guild.name
        filters = await self.config.guild(ctx.guild).filters()

        if word not in filters:
            filters.append(word)
            await self.config.guild(ctx.guild).filters.set(filters)
            await user.send("`Word Filter:` `{0}` was added to the filter in the "
                            "guild **{1}**".format(word, guildName))
        else:
            await user.send("`Word Filter:` The word `{0}` is already in the filter "
                            "for guild **{1}**".format(word, guildName))

    @wordFilter.command(name="del", aliases=["delete", "remove", "rm"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def removeFilter(self, ctx, word: str):
        """Remove word from filter"""
        guildId = ctx.message.guild.id
        user = ctx.message.author
        guildName = ctx.message.guild.name
        filters = await self.config.guild(ctx.guild).filters()

        if not filters or word not in filters:
            await user.send("`Word Filter:` The word `{0}` is not in the filter for "
                            "guild **{1}**".format(word, guildName))
        else:
            filters.remove(word)
            await self.config.guild(ctx.guild).filters.set(filters)
            await user.send("`Word Filter:` `{0}` removed from the filter in the "
                            "guild **{1}**".format(word, guildName))

    @wordFilter.command(name="list", aliases=["ls"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def listFilter(self, ctx):
        """List filtered words in raw format.
        NOTE: do this in a channel outside of the viewing public
        """
        guildId = ctx.message.guild.id
        guildName = ctx.message.guild.name
        user = ctx.message.author
        filters = await self.config.guild(ctx.guild).filters()

        if filters:
            display = []
            for regex in filters:
                display.append("`{}`".format(regex))
            # msg = ""
            # for word in self.filters[guildId]:
                # msg += word
                # msg += "\n"
            # title = "Filtered words for: **{}**".format(guildName)
            # embed = discord.Embed(title=title,description=msg,colour=discord.Colour.red())
            # await self.bot.send_message(user,embed=embed)

            page = Pages(self.bot, message=ctx.message, entries=display)
            page.embed.title = "Filtered words for: **{}**".format(guildName)
            page.embed.colour = discord.Colour.red()
            await page.paginate()
        else:
            await user.send("Sorry you have no filtered words in **{}**".format(guildName))

    @wordFilter.command(name="togglemod")
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def toggleMod(self, ctx):
        """Toggle global override of filters for server admins/mods."""
        toggleMod = await self.config.guild(ctx.guild).toggleMod()

        if toggleMod:
            toggleMod = False
            await ctx.send(":negative_squared_cross_mark: Word Filter: Moderators "
                           "(and higher) **will be** filtered.")
        else:
            toggleMod = True
            await ctx.send(":white_check_mark: Word Filter: Moderators (and higher "
                           "**will not be** filtered.")
        await self.config.guild(ctx.guild).toggleMod.set(toggleMod)

    #########################################
    # COMMANDS - COMMAND BLACKLIST SETTINGS #
    #########################################
    @wordFilter.group(name="command", aliases=["cmd"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def _command(self, ctx):
        """Blacklist command settings. (help for more info)
        Settings for controlling filtering on commands.
        """
        if str(ctx.invoked_subcommand).lower() == "word_filter command":
            await send_cmd_help(ctx)

    @_command.command(name="add")
    @commands.guild_only()
    async def _commandAdd(self, ctx, cmd: str):
        """Add a command (without prefix) to the blacklist.
        If the invoked command contains any filtered words, the entire message
        is filtered and the contents of the message will be sent back to the
        user via DM.
        """
        guildId = ctx.message.guild.id
        cmdDenied = await self.config.guild(ctx.guild).commandDenied()

        if cmd not in cmdDenied:
            cmdDenied.append(cmd)
            await self.config.guild(ctx.guild).commandDenied.set(cmdDenied)
            await ctx.send(":white_check_mark: Word Filter: Command `{1}` is now "
                           "blacklisted.  It will have the entire message filtered "
                           "if it contains any filterable words, and its contents "
                           "DM'd back to the user.".format(cmd))
        else:
            await ctx.send(":negative_squared_cross_mark: Word Filter: Command "
                           "`{0}` is already blacklisted.".format(cmd))

    @_command.command(name="del", aliases=["delete", "remove", "rm"])
    @commands.guild_only()
    async def _commandRemove(self, ctx, cmd: str):
        """Remove a command from the blacklist.
        The command that is removed from the list will be filtered as normal
        messages.  That is, if the invoked command contains any filtered words,
        only the filtered words will be censored and replaced (as opposed to the
        entire message being deleted).
        """
        guildName = ctx.message.guild.name

        cmdDenied = await self.config.guild(ctx.guild).commandDenied()

        if not cmdDenied or cmd not in cmdDenied:
            await self.bot.say(":negative_squared_cross_mark: Word Filter: Command "
                               "`{0}` wasn't on the blacklist.".format(cmd))
        else:
            cmdDenied.remove(cmd)
            await self.config.guild(ctx.guild).commandDenied.set(cmdDenied)
            await ctx.send(":white_check_mark: Word Filter: `{0}` removed from "
                           "the command blacklist.".format(cmd))

    @_command.command(name="list", aliases=["ls"])
    @commands.guild_only()
    async def _commandList(self, ctx):
        """List blacklisted commands.
        If the commands on this list are invoked with any filtered words, the
        entire message is filtered and the contents of the message will be sent
        back to the user via DM.
        """
        guildName = ctx.message.guild.name

        cmdDenied = await self.config.guild(ctx.guild).commandDenied()

        if cmdDenied:
            display = []
            for cmd in self.commandBlacklist[guildId]:
                display.append("`{}`".format(cmd))

            page = Pages(self.bot, message=ctx.message, entries=display)
            page.embed.title = "Blacklisted commands for: **{}**".format(guildName)
            page.embed.colour = discord.Colour.red()
            await page.paginate()
        else:
            await ctx.send("Sorry, there are no blacklisted commands in "
                           "**{}**".format(guildName))

    ############################################
    # COMMANDS - CHANNEL WHITELISTING SETTINGS #
    ############################################
    @wordFilter.group(name="whitelist", aliases=["wl"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def _whitelist(self, ctx):
        """Channel whitelisting settings."""

    @_whitelist.command(name="add")
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def _whitelistAdd(self, ctx, channelName):
        """Add channel to whitelist.
        All messages in the channel will not be filtered.
        """
        guildId = ctx.message.guild.id
        channelAllowed = await self.config.guild(ctx.guild).channelAllowed()

        match = re.search(PATTERN_CHANNEL_ID, channelName)
        if match: # channel ID
            channel = discord.utils.get(ctx.message.guild.channels, id=match.group(1))
            channelName = channel.name

        if channelName not in channelAllowed:
            channelAllowed.append(channelName)
            await self.config.guild(ctx.guild).channelAllowed.set(channelAllowed)
            await ctx.send(":white_check_mark: Word Filter: Channel with name "
                           "`{0}` will not be filtered.".format(channelName))
        else:
            await ctx.send(":negative_squared_cross_mark: Word Filter: Channel "
                           "`{0}` is already whitelisted.".format(channelName))

    @_whitelist.command(name="del", aliases=["delete", "remove", "rm"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def _whitelistRemove(self, ctx, channelName):
        """Remove channel from whitelist
        All messages in the removed channel will be subjected to the filter.
        """
        guildId = ctx.message.guild.id
        guildName = ctx.message.guild.name

        channelAllowed = await self.config.guild(ctx.guild).channelAllowed()

        match = re.search(PATTERN_CHANNEL_ID, channelName)
        if match: # channel ID
            channel = discord.utils.get(ctx.message.guild.channels, id=match.group(1))
            channelName = channel.name

        if not channelAllowed or channelName not in channelAllowed:
            await ctx.send(":negative_squared_cross_mark: Word Filter: Channel "
                           "`{0}` was already not whitelisted.".format(channelName))
        else:
            channelAllowed.remove(channelName)
            await self.config.guild(ctx.guild).channelAllowed.set(channelAllowed)
            await ctx.send(":white_check_mark: Word Filter: `{0}` removed from "
                           "the channel whitelist.".format(channelName))

    @_whitelist.command(name="list", aliases=["ls"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def _whitelistList(self, ctx):
        """List whitelisted channels.
        NOTE: do this in a channel outside of the viewing public
        """
        guildId = ctx.message.guild.id
        guildName = ctx.message.guild.name

        channelAllowed = await self.config.guild(ctx.guild).channelAllowed()

        if channelAllowed:
            display = []
            for channel in channelAllowed:
                display.append("`{}`".format(channel))
            # msg = ""
            # for word in self.whitelist[guildId]:
                # msg += word
                # msg += "\n"
            # title = "Filtered words for: **{}**".format(guildName)
            # embed = discord.Embed(title=title,description=msg,colour=discord.Colour.red())
            # await self.bot.send_message(user,embed=embed)

            page = Pages(self.bot, message=ctx.message, entries=display)
            page.embed.title = "Whitelisted channels for: **{}**".format(guildName)
            page.embed.colour = discord.Colour.red()
            await page.paginate()
        else:
            await ctx.send("Sorry, there are no whitelisted channels in "
                           "**{}**".format(guildName))

    def checkMessageServerAndChannel(self, msg):
        """Checks to see if the message is in a server/channel eligible for
        filtering.

        Parameters
        ----------
        msg : discord.Message
            The message that we want to check.

        Returns
        -------
        Boolean
            True if the message is eligible for filtering, else False.
        """
        modRole = self.bot.settings.get_server_mod(msg.server).lower()
        adminRole = self.bot.settings.get_server_admin(msg.server).lower()

        # Filter only configured servers, not private DMs.
        if isinstance(msg.channel, discord.PrivateChannel) or msg.server.id not \
            in list(self.filters):
            return False

        guildId = msg.server.id

        # Do not filter whitelisted channels
        try:
            whitelist = self.whitelist[guildId]
            for channels in whitelist:
                if channels.lower() == msg.channel.name.lower():
                    return False
        except Exception as error: # pylint: disable=broad-except
            # Most likely no whitelisted channels.
            LOGGER.error("Exception occured while checking whitelist channels!")
            LOGGER.error(error)

        # Check if mod or admin, and do not filter if togglemod is enabled.
        try:
            if self.settings[msg.author.server.id][self.keyToggleMod]:
                for role in msg.author.roles:
                    if role.name.lower() == modRole or role.name.lower() == adminRole:
                        return False
        except Exception as error: # pylint: disable=broad-except
            LOGGER.error("Exception occurred in checking keyToggleMod!")
            LOGGER.error(error)

        return True

    def containsFilterableWords(self, msg):
        """Checks to see if the message contains words that we need to filter out.
        If the message is in a server/channel that does not exist or is whitelisted,
        this function will return False.

        Parameters
        ---------
        msg : discord.Message
            The message that we want to check.

        Returns
        -------
        Boolean
            True if message contains words that can be filtered, else False.
        """
        if not self.checkMessageServerAndChannel(msg):
            return False
        guildId = msg.server.id

        filteredMsg = msg.content
        for word in self.filters[guildId]:
            filteredMsg = _filterWord(word, filteredMsg)

        if msg.content == filteredMsg:
            return False
        return True

    async def checkWords(self, msg, newMsg=None): \
        # pylint: disable=too-many-locals, too-many-branches
        """This method, given a message, will check to see if the message contains
        any filterable words, and if it does, deletes the original message and
        sends another message with the filterable words censored.
        """
        if newMsg and not self.checkMessageServerAndChannel(newMsg):
            return

        if not self.checkMessageServerAndChannel(msg):
            return

        guildId = msg.server.id
        blacklistedCmd = False

        filteredWords = self.filters[guildId]
        if newMsg:
            checkMsg = newMsg.content
        else:
            checkMsg = msg.content
        originalMsg = checkMsg
        filteredMsg = originalMsg
        oneWord = _isOneWord(checkMsg)

        if guildId in self.commandBlacklist:
            for prefix in self.bot.command_prefix(self.bot, msg):
                for cmd in self.commandBlacklist[guildId]:
                    if checkMsg.startswith(prefix+cmd):
                        blacklistedCmd = True

        for word in filteredWords:
            try:
                filteredMsg = _filterWord(word, filteredMsg)
            except Exception as error: # pylint: disable=broad-except
                LOGGER.error("Exception!")
                LOGGER.error(error)
                LOGGER.info("Word: %s", word)
                LOGGER.info("Filtered message: %s", filteredMsg)

        allFiltered = _isAllFiltered(filteredMsg)

        if filteredMsg == originalMsg:
            return # no bad words, don't need to do anything else

        await self.bot.delete_message(msg)
        if blacklistedCmd:
            # If the it contains a filtered word AND the blacklisted command flag was
            # set above, then:
            # - Delete the message,
            # - Notify on the channel that the message was filtered without showing context
            # - DM user with the filtered context as per what we see usually.
            filterNotify = "{0.author.mention} was filtered!".format(msg)
            notifyMsg = await self.bot.send_message(msg.channel, filterNotify)
            filterNotify = "You were filtered! Your message was: \n"
            embed = discord.Embed(colour=random.choice(self.colours),
                                  description="{0.author.name}#{0.author.discriminator}: "
                                  "{1}".format(msg, filteredMsg))
            try:
                await self.bot.send_message(msg.author, filterNotify, embed=embed)
            except discord.errors.Forbidden as error:
                LOGGER.error("Could not DM user, perhaps they have blocked DMs?")
                LOGGER.error(error)
            await asyncio.sleep(3)
            await self.bot.delete_message(notifyMsg)
        elif (filteredMsg != originalMsg and oneWord) or allFiltered:
            filterNotify = "{0.author.mention} was filtered!".format(msg)
            notifyMsg = await self.bot.send_message(msg.channel, filterNotify)
            await asyncio.sleep(3)
            await self.bot.delete_message(notifyMsg)
        else:
            filterNotify = "{0.author.mention} was filtered! Message was: \n".format(msg)
            embed = discord.Embed(colour=random.choice(self.colours),
                                  description="{0.author.name}#{0.author.discriminator}: "
                                  "{1}".format(msg, filteredMsg))
            await self.bot.send_message(msg.channel, filterNotify, embed=embed)

        LOGGER.info("Author : %s#%s (%s)", msg.author.name, msg.author.discriminator,
                    msg.author.id)
        LOGGER.info("Message: %s", originalMsg)

def _filterWord(word, string):
    regex = r'\b{}\b'.format(word)

    # Replace the offending string with the correct number of stars.  Note that
    # this only considers the length of the first time an offending string is
    # found with the current regex.  It will replace every string found with
    # this regex with the number of stars corresponding to the first offending
    # string.

    try:
        number = len(re.search(regex, string, flags=re.IGNORECASE).group(0))
    except Exception: # pylint: disable=broad-except
        # Nothing to replace, return original string
        return string

    stars = '*'*number
    repl = "{0}{1}{0}".format('`', stars)
    return re.sub(regex, repl, string, flags=re.IGNORECASE)

def _isOneWord(string):
    return len(string.split()) == 1

def _isAllFiltered(string):
    words = string.split()
    cnt = 0
    for word in words:
        if bool(re.search("[*]+", word)):
            cnt += 1
    return cnt == len(words)

def setup(bot):
    """Add the cog to the bot."""
    global LOGGER # pylint: disable=global-statement
    wordFilterCog = WordFilter(bot)
    bot.add_listener(wordFilterCog.checkWords, 'on_message')
    bot.add_listener(wordFilterCog.checkWords, 'on_message_edit')
    LOGGER = logging.getLogger("red.WordFilter")
    if LOGGER.level == 0:
        # Prevents the LOGGER from being loaded again in case of module reload.
        LOGGER.setLevel(logging.INFO)
        handler = logging.FileHandler(filename="data/word_filter/info.log",
                                      encoding="utf-8",
                                      mode="a")
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s",
                                               datefmt="[%d/%m/%Y %H:%M:%S]"))
        LOGGER.addHandler(handler)
    bot.add_cog(wordFilterCog)