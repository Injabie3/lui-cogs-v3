import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import os #Used to create folder at first load.
import MySQLdb

# Requires checks utility from:
# https://github.com/Rapptz/RoboDanny/tree/master/cogs/utils
from .utils import checks

#Global variables
saveFolder = "data/lui-cogs/ranks/" #Path to save folder.

def checkFolder():
    """Used to create the data folder at first startup"""
    if not os.path.exists(saveFolder):
        print("Creating " + saveFolder + " folder...")
        os.makedirs(saveFolder)

def checkFiles():
    """Used to initialize an empty database at first startup"""
    base = { }
    empty = { }
    
    f = saveFolder + "settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default ranks settings.json...")
        dataIO.save_json(f, base)
        
    f = saveFolder + "lastspoke.json"
    if not dataIO.is_valid_json(f):
        print("Creating default ranks lastspoke.json...")
        dataIO.save_json(f, base)
            
class Ranks_beta:
    """Guild rank management system"""
    
    #Class constructor
    def __init__(self, bot):
        self.bot = bot
        checkFiles()
        checkFolder()
        self.settings = dataIO.load_json(saveFolder + 'settings.json')
        
        db = MySQLdb.connect(host=self.settings["mysql_host"],user=self.settings["mysql_username"],passwd=self.settings["mysql_password"])
        cursor = db.cursor()
    
    ############
    # COMMANDS #
    ############
    
    @commands.group(name="ranks", pass_context=True, no_pm=True)
    async def _ranks(self, ctx):
        """Guild rank management system"""
        #Display the help context menu
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    
    #[p]rank check
    @_ranks.command(name="check", pass_context=True, no_pm=True)
    async def _ranks_check(self, ctx):
        """Check your rank in the server."""
        #Execute a MySQL query to order and check.
        pass
        
    #[p]rank leaderboard
    @_ranks.command(name="leaderboard", pass_context=True, no_pm=True)
    async def _ranks_leaderboard(self, ctx):
        """Show the server ranking leaderboard"""
        #Execute a MySQL query to order and check.
        pass
    
    #######################
    # COMMANDS - SETTINGS #
    #######################
    #Ideally would be nice have this replaced by a web admin panel. 

    #[p]rank settings
    @_ranks.group(name="settings", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _settings(self, ctx):
        """Ranking system settings.  Only server admins should see this."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            
    
    #[p]rank settings test
    @_settings.command(name="test", pass_context=True)
    async def _settings_test(self):
        """Test"""
        await self.bot.say("test")
        
    #[p]rank settings cooldown
    @_settings.command(name="cooldown", pass_context=True)
    async def _settings_cooldown(self, ctx, seconds: int):
        """Set the cooldown required between XP gains (in seconds)"""
        if seconds is None:
            await self.bot.say("Please enter a cooldown time in seconds!")
            return
        
        self.settings["cooldown"] = seconds
        await self.bot.say("Cooldown set to {0}".format(seconds))
            
    
    #[p]rank settings setup
    @_settings.command(name="setup", pass_context=True)
    @checks.serverowner()
    async def _settings_setup(self, ctx):
        """Perform first time set up."""
        await self.bot.say("MySQL Set up:\nWhat is the host you wish to connect to?")
        host = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, channel=ctx.message.channel)
        
        if host is None:
            await self.bot.say("No response received, not setting anything!")
            return
        
        await self.bot.say("What is the username you want to use to connect?")
        username = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, channel=ctx.message.channel)
        
        if username is None:
            await self.bot.say("No response received, not setting anything!")
            return
        
        await self.bot.say("What is the password you want to use to connect?  You can use a dummy password and manually change it in the JSON config later.")
        password = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, channel=ctx.message.channel)
        
        if password is None:
            await self.bot.say("No response received, not setting anything!")
            return
        
        # Save settings
        self.settings["mysql_host"] = host.content
        self.settings["mysql_username"] = username.content
        self.settings["mysql_password"] = password.content
        
        dataIO.save_json(saveFolder + 'settings.json', self.settings)
        await self.bot.say("Settings saved.")
    
    ####################
    # HELPER FUNCTIONS #
    ####################

    def addPoints(userID):
        """Add rank points between 0 and MAX_POINTS to the user"""
        # Invoke the MySQL query to update the user.
        pass
        
    async def checkFlood(self, message):
        """Check to see if the user is sending messages that are flooding the server.  If yes, then do not add points."""
        # Decide whether to store last spoken user data in:
        #  - MySQL
        #  - JSON
        #  - or leave in RAM.
        # Check as follows:
        #  - Get the user ID and message time
        #  - Check the last message time that was used to add points to the current user.
        #  - If this time does not exceed MIN_FLOOD_TIME, return and do nothing.
        #  - If this time exceeds MIN_FLOOD_TIME, update the last spoken time of this user with the message time.
        #  - Add points between 0 and MAX_POINTS (use random).
        #  - Return.
        pass
    

def setup(bot):
    checkFolder()   #Make sure the data folder exists!
    checkFiles()    #Make sure we have a local database!
    rankingSystem = Ranks_beta(bot)
    bot.add_cog(rankingSystem)
    bot.add_listener(rankingSystem.checkFlood, 'on_message')
