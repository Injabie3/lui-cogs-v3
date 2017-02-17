import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import random #Used for selecting random catgirls

#Global variables
JSON_mainKey = "catgirls" #Key for JSON files.
JSON_imageURLKey = "url" #Key for URL
JSON_isPixiv = "is_pixiv"
JSON_pixivID = "id"

def checkFiles():
    """Used to initialize an empty database at first startup"""
    base = { JSON_mainKey : [{ JSON_imageURLKey :"https://cdn.awwni.me/utpd.jpg" , "id" : "null", "is_pixiv" : False}] }
	
    f = "data/catgirl/links-web.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-web.json...")
        dataIO.save_json(f, base)
		
    f = "data/catgirl/links-localx10.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-localx10.json...")
        dataIO.save_json(f, { JSON_mainKey : []})
		
    f = "data/catgirl/links-local.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-local.json...")
        dataIO.save_json(f, { JSON_mainKey : []})
			
class Catgirl_beta:
    """Display cute nyaas~"""


    def refreshDatabase(self):
        """Refreshes the JSON files"""
        #Local catgirls allow for prepending predefined domain, if you have a place where you're hosting your own catgirls.
        self.filepath_local = "data/catgirl/links-local.json"
        self.filepath_localx10 = "data/catgirl/links-localx10.json"
		
		#Web catgirls will take on full URLs.
        self.filepath_web = "data/catgirl/links-web.json"
		
        self.pictures_local = dataIO.load_json(self.filepath_local)
        self.pictures_localx10 = dataIO.load_json(self.filepath_localx10)
        self.pictures_web = dataIO.load_json(self.filepath_web)   
        
        #Custom key which holds an array of catgirl filenames/paths
        self.JSON_mainKey = "catgirls"
        
		#Prepend local listings with domain name.
        for x in range(0,len(self.pictures_local[JSON_mainKey])):
            self.pictures_local[JSON_mainKey][x][JSON_imageURLKey] = "https://nyan.injabie3.moe/p/" + self.pictures_local[JSON_mainKey][x][JSON_imageURLKey]
        for x in range(0,len(self.pictures_localx10[JSON_mainKey])):
            self.pictures_localx10[JSON_mainKey][x][JSON_imageURLKey] = "http://injabie3.x10.mx/p/" + self.pictures_localx10[JSON_mainKey][x][JSON_imageURLKey]


        self.catgirls_local = self.pictures_local[JSON_mainKey]
        self.catgirls = self.pictures_local[JSON_mainKey] + self.pictures_web[JSON_mainKey] + self.pictures_localx10[JSON_mainKey]

    def __init__(self, bot):
        self.bot = bot
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
            embed.add_field(name="Pixiv",value="http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatgirl[JSON_pixivID])
        embed.set_image(url=randCatgirl[JSON_imageURLKey])
        await self.bot.say("",embed=embed)

    @commands.group(name="nyaa", pass_context=True, no_pm=True)
    async def _nyaa(self, ctx):
        """Help menu for catgirls"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    #[p]nyaa about
    @_nyaa.command(pass_context=True, no_pm=True)
    async def about(self, ctx):
        """Displays information about this module"""
        embed = discord.Embed()
        embed.add_field(name="Name", value="Catgirl Module")
        embed.add_field(name="Author", value="@Injabie3#1660")
        embed.add_field(name="Initial Version Date", value="2017-02-11")
        embed.add_field(name="Description", value="See https://github.com/Injabie3/lui-cogs for more info")
        await self.bot.say(content="",embed=embed)

    #[p]nyaa numbers
    @_nyaa.command(pass_context=True, no_pm=True)
    async def numbers(self, ctx):
        """Displays the number of catgirls on file."""
        await self.bot.say("There are " + str(len(self.catgirls)) + " catgirls available at the moment, hopefully more to come!")

    #[p]nyaa refresh
    @_nyaa.command(pass_context=True, no_pm=True)
    async def refresh(self, ctx):
        """Refreshes the internal database of catgirls."""
        self.refreshDatabase()
        await self.bot.say("List reloaded. There are " + str(len(self.catgirls)) + " catgirls available.")

    @_nyaa.command(pass_context=True, no_pm=True)
    async def local(self):
        """Displays a random, cute catgirl from the local database."""

        randCatgirl = random.choice(self.catgirls_local)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Catgirl"
        embed.url = randCatgirl[JSON_imageURLKey]
        if randCatgirl[JSON_isPixiv]:
            embed.add_field(name="Pixiv",value="http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatgirl[JSON_pixivID])
        embed.set_image(url=randCatgirl[JSON_imageURLKey])

        await self.bot.say("",embed=embed)

    #[p] nyaa debug
    @_nyaa.command(pass_context=True, no_pm=True)
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
    checkFiles() #Make sure we have a local database!
    bot.add_cog(Catgirl_beta(bot))
