import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import os #Used to create folder at first load.

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
        
    @commands.group(name="ranks", pass_context=True, no_pm=False)
    async def _ranks(self, ctx):
        """Guild rank management system"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    
    @_ranks.command(name="test")
    async def _test(self):
        await self.bot.say("test")
    
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
