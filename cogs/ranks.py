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
            
class Ranks_beta:
    """Guild rank management system"""

def setup(bot):
    checkFolder()   #Make sure the data folder exists!
    checkFiles()    #Make sure we have a local database!
    bot.add_cog(Ranks_beta(bot))
