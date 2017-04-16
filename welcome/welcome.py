import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO

# Requires checks utility from:
# https://github.com/Rapptz/RoboDanny/tree/master/cogs/utils
from .utils import checks

import os #Used to create folder at first load.

#Global variables

saveFolder = "data/lui-cogs/welcome/" #Path to save folder.
saveFile = "settings.json"

def checkFolder():
    """Used to create the data folder at first startup"""
    if not os.path.exists(saveFolder):
        print("Creating " + saveFolder + " folder...")
        os.makedirs(saveFolder)

def checkFiles():
    """Used to initialize an empty database at first startup"""
    
    f = saveFolder + saveFile
    if not dataIO.is_valid_json(f):
        print("Creating default welcome settings.json...")
        dataIO.save_json(f, { "message" : "Welcome to the server!" })
        
            
class Welcome_beta:
    """Send a welcome DM on server join."""


    def loadSettings(self):
        """Loads settings from the JSON file"""
        self.settings = dataIO.load_json(saveFolder+saveFile)
        
    def saveSettings(self):
        """Loads settings from the JSON file"""
        dataIO.save_json(saveFolder+saveFile, self.settings)

    def __init__(self, bot):
        self.bot = bot
        checkFolder()
        checkFiles()
        self.loadSettings()
        
    
    async def send_welcome_message(self, newUser):
        """Sends the welcome message in DM."""
        try:
            welcomeEmbed = discord.Embed(title=self.settings[newUser.server.id]["title"])
            welcomeEmbed.description = self.settings[newUser.server.id]["message"]
            welcomeEmbed.colour = discord.Colour.red()
        except:
            print("Welcome: Could not send message, make sure the server has a title and message set!")
        else:
            await self.bot.send_message(newUser, embed=welcomeEmbed)
            print("Welcome: Welcome DM sent to " + newUser.name + "#" + newUser.discriminator + " (" + newUser.id + ").")
        
    async def send_leave_message(self, leavingUser):
        print("Server Leave: " + leavingUser.name + "#" + leavingUser.discriminator + "(" + leavingUser.id + ") has left")
        
    #[p]welcome
    @commands.group(name="welcome", pass_context=True, no_pm=False)
    @checks.serverowner()
    async def _welcome(self, ctx):
        """Server welcome message settings"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner()
    async def setmessage(self, ctx):
        """Interactively configure the contents of the welcome DM."""
        
        await self.bot.say("What would you like the welcome DM message to be?")
        message = await self.bot.wait_for_message(timeout=60, author=ctx.message.author, channel=ctx.message.channel)
        
        if message is None:
            await self.bot.say("No response received, not setting anything!")
            return
            
        if len(message.content) > 2048:
            await self.bot.say("Your message is too long!")
            return
        
        try:
            self.loadSettings()
            if ctx.message.author.server.id in self.settings:
                self.settings[ctx.message.author.server.id]["message"] = message.content
            else:
                self.settings[ctx.message.author.server.id] = {}
                self.settings[ctx.message.author.server.id]["message"] = message.content
            self.saveSettings()
        except:
            await self.bot.say("Could not save settings!")
        else:
            await self.bot.say("Message set to:")
            await self.bot.say("```" + message.content + "```")
        
        
    #[p]welcome settitle
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner()
    async def settitle(self, ctx):
        """Interactively configure the title for the welcome DM."""
        
        await self.bot.say("What would you like the welcome DM message to be?")
        title = await self.bot.wait_for_message(timeout=60, author=ctx.message.author, channel=ctx.message.channel)
        
        if title is None:
            await self.bot.say("No response received, not setting anything!")
            return
            
        if len(title.content) > 256:
            await self.bot.say("The title is too long!")
            return
        
        try:
            self.loadSettings()
            if ctx.message.author.server.id in self.settings:
                self.settings[ctx.message.author.server.id]["title"] = title.content
            else:
                self.settings[ctx.message.author.server.id] = {}
                self.settings[ctx.message.author.server.id]["title"] = title.content
            self.saveSettings()
        except:
            await self.bot.say("Could not save settings!")
        else:
            await self.bot.say("Title set to:")
            await self.bot.say("```" + title.content + "```")
        
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner()
    async def test(self, ctx):
        """Test the welcome DM by sending a DM to you."""
        try:
            welcomeEmbed = discord.Embed(title=self.settings[ctx.message.server.id]["title"])
            welcomeEmbed.title = self.settings[ctx.message.author.server.id]["title"]
            welcomeEmbed.description = self.settings[ctx.message.author.server.id]["message"]
            welcomeEmbed.colour = discord.Colour.red()
        except:
            await self.bot.say("Could not send message, try setting the title and message again!")
        else:
            await self.bot.send_message(ctx.message.author, embed=welcomeEmbed)
            await self.bot.say("I've slid it into your DMs ;)")
               

def setup(bot):
    checkFolder()   #Make sure the data folder exists!
    checkFiles()    #Make sure we have settings!
    customCog = Welcome_beta(bot)
    bot.add_listener(customCog.send_welcome_message, 'on_member_join')
    bot.add_listener(customCog.send_leave_message, 'on_member_remove')
    bot.add_cog(customCog)
    
