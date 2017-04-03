import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import os #Used to create folder at first load.
import random #Used for selecting random catgirls

#Global variables
JSON_mainKey = "catgirls" #Key for JSON files.
JSON_imageURLKey = "url" #Key for URL
JSON_isPixiv = "is_pixiv" #Key that specifies if image is from pixiv. If true, pixivID should be set.
JSON_pixivID = "id" #Key for Pixiv ID, used to create URL to pixiv image page, if applicable.
saveFolder = "data/lui-cogs/catgirl/" #Path to save folder.

def checkFolder():
    """Used to create the data folder at first startup"""
    if not os.path.exists(saveFolder):
        print("Creating " + saveFolder + " folder...")
        os.makedirs(saveFolder)

def checkFiles():
    """Used to initialize an empty database at first startup"""
    base = { JSON_mainKey : [{ JSON_imageURLKey :"https://cdn.awwni.me/utpd.jpg" , "id" : "null", "is_pixiv" : False}] }
	
    f = saveFolder + "links-web.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-web.json...")
        dataIO.save_json(f, base)
		
    f = saveFolder + "links-localx10.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-localx10.json...")
        dataIO.save_json(f, { JSON_mainKey : []})
		
    f = saveFolder + "links-local.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-local.json...")
        dataIO.save_json(f, { JSON_mainKey : []})
			
class Catgirl_beta:
    """Display cute nyaas~"""


    def refreshDatabase(self):
        """Refreshes the JSON files"""
        #Local catgirls allow for prepending predefined domain, if you have a place where you're hosting your own catgirls.
        self.filepath_local = saveFolder + "links-local.json"
        self.filepath_localx10 = saveFolder + "links-localx10.json"
		
		#Web catgirls will take on full URLs.
        self.filepath_web = saveFolder + "links-web.json"
		
        self.pictures_local = dataIO.load_json(self.filepath_local)
        self.pictures_localx10 = dataIO.load_json(self.filepath_localx10)
        self.pictures_web = dataIO.load_json(self.filepath_web)   
        
        #Custom key which holds an array of catgirl filenames/paths
        self.JSON_mainKey = "catgirls"
        
		#Prepend local listings with domain name.
        for x in range(0,len(self.pictures_local[JSON_mainKey])):
            self.pictures_local[JSON_mainKey][x][JSON_imageURLKey] = "https://nekomimi.injabie3.moe/p/" + self.pictures_local[JSON_mainKey][x][JSON_imageURLKey]
            #self.pictures_local[JSON_mainKey][x][JSON_imageURLKey] = "https://nyan.injabie3.moe/p/" + self.pictures_local[JSON_mainKey][x][JSON_imageURLKey]
        for x in range(0,len(self.pictures_localx10[JSON_mainKey])):
            self.pictures_localx10[JSON_mainKey][x][JSON_imageURLKey] = "http://injabie3.x10.mx/p/" + self.pictures_localx10[JSON_mainKey][x][JSON_imageURLKey]


        self.catgirls_local = self.pictures_local[JSON_mainKey]
        self.catgirls = self.pictures_local[JSON_mainKey] + self.pictures_web[JSON_mainKey] + self.pictures_localx10[JSON_mainKey]

    def __init__(self, bot):
        self.bot = bot
        checkFolder()
        checkFiles()
        self.refreshDatabase()
		
        
    @commands.command(name="catgirl")
    async def _catgirl(self):
        """Displays a random, cute catgirl :3"""
        randCatgirl = random.choice(self.catgirls)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Catgirl"
        embed.url = randCatgirl[JSON_imageURLKey]
        if randCatgirl[JSON_isPixiv]:
            source = "[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatgirl[JSON_pixivID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randCatgirl[JSON_pixivID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randCatgirl:
            embed.add_field(name="Info",value=randCatgirl["character"], inline=False)
        embed.set_image(url=randCatgirl[JSON_imageURLKey])
        await self.bot.say("",embed=embed)

    @commands.group(name="nyaa", pass_context=True, no_pm=False)
    async def _nyaa(self, ctx):
        """Help menu for catgirls"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    #[p]nyaa about
    @_nyaa.command(pass_context=True, no_pm=False)
    async def about(self, ctx):
        """Displays information about this module"""
        customAuthor = "[{}]({})".format("@Injabie3#1660","https://injabie3.moe/")
        embed = discord.Embed()
        embed.title = "About this module"
        embed.add_field(name="Name", value="Catgirl Module")
        embed.add_field(name="Author", value=customAuthor)
        embed.add_field(name="Initial Version Date", value="2017-02-11")
        embed.add_field(name="Description", value="A module to display pseudo-random catgirl images.  Image links are stored in the local database, separated into different lists (depending on if they are hosted locally or on another domain).  See https://github.com/Injabie3/lui-cogs for more info.")
        embed.set_footer(text="lui-cogs/catgirl")
        await self.bot.say(content="",embed=embed)

    #[p]nyaa numbers
    @_nyaa.command(pass_context=True, no_pm=False)
    async def numbers(self, ctx):
        """Displays the number of catgirls in the database."""
        await self.bot.say("There are " + str(len(self.catgirls)) + " catgirls available at the moment, hopefully more to come!")

    #[p]nyaa refresh - Also allow for refresh in a DM to the bot.
    @_nyaa.command(pass_context=True, no_pm=False)
    async def refresh(self, ctx):
        """Refreshes the internal database of catgirls."""
        self.refreshDatabase()
        await self.bot.say("List reloaded. There are " + str(len(self.catgirls)) + " catgirls available.")
    
    #[p]nyaa local
    @_nyaa.command(pass_context=True, no_pm=False)
    async def local(self):
        """Displays a random, cute catgirl from the local database."""

        randCatgirl = random.choice(self.catgirls_local)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Catgirl"
        embed.url = randCatgirl[JSON_imageURLKey]
        if randCatgirl[JSON_isPixiv]:
            source="[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatgirl[JSON_pixivID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randCatgirl[JSON_pixivID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randCatgirl:
            embed.add_field(name="Info",value=randCatgirl["character"], inline=False)
        embed.set_image(url=randCatgirl[JSON_imageURLKey])
        await self.bot.say("",embed=embed)

    #[p] nyaa debug
    @_nyaa.command(pass_context=True, no_pm=False)
    async def debug(self, ctx):
        """Debug to see if list is okay"""
        msg = "Debug Mode\n```"
        for x in range(0,len(self.catgirls)):
            msg += self.catgirls[x][JSON_imageURLKey] + "\n"
            if len(msg) > 900:
               msg += "```"
               await self.bot.say(msg)
               msg = "```"
        msg += "```"
        await self.bot.say(msg)
        #await self.bot.say("This feature is disabled.")


def setup(bot):
    checkFolder()   #Make sure the data folder exists!
    checkFiles()    #Make sure we have a local database!
    bot.add_cog(Catgirl_beta(bot))
