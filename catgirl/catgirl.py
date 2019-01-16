import os
import asyncio
import random
import discord
from discord.ext import commands
from cogs.utils.dataIO import dataIO

#Global variables
KEY_CATGIRL = "catgirls" # Key for JSON files.
KEY_CATBOY = "catboys" # Key containing other images.
KEY_IMAGE_URL = "url" # Key for URL
KEY_ISPIXIV = "is_pixiv" # Key that specifies if image is from pixiv.
KEY_ISSEIGA = "is_seiga"
KEY_PIXIV_ID = "id" # Key for Pixiv ID, used to create URL to pixiv image page, if applicable.
KEY_SEIGA_ID = "id"
SAVE_FOLDER = "data/lui-cogs/catgirl/" # Path to save folder.

BASE = \
{KEY_CATGIRL : [{KEY_IMAGE_URL: "https://cdn.awwni.me/utpd.jpg",
                 "id" : "null",
                 "is_pixiv" : False}],
 KEY_CATBOY : []
}
EMPTY = {KEY_CATGIRL : [], KEY_CATBOY : []}

def checkFolder():
    """Used to create the data folder at first startup"""
    if not os.path.exists(SAVE_FOLDER):
        print("Creating " + SAVE_FOLDER + " folder...")
        os.makedirs(SAVE_FOLDER)

def checkFiles():
    """Used to initialize an empty database at first startup"""
    f = SAVE_FOLDER + "links-web.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-web.json...")
        dataIO.save_json(f, BASE)

    f = SAVE_FOLDER + "links-localx10.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-localx10.json...")
        dataIO.save_json(f, EMPTY)

    f = SAVE_FOLDER + "links-local.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-local.json...")
        dataIO.save_json(f, EMPTY)

    f = SAVE_FOLDER + "links-pending.json"
    if not dataIO.is_valid_json(f):
        print("Creating default catgirl links-pending.json...")
        dataIO.save_json(f, EMPTY)

class Catgirl:
    """Display cute nyaas~"""


    def refreshDatabase(self):
        """Refreshes the JSON files"""
        # Local catgirls allow for prepending a domain if you have a place where
        # where you're hosting your own catgirls.
        self.filepathLocal = SAVE_FOLDER + "links-local.json"
        self.filepathLocalx10 = SAVE_FOLDER + "links-localx10.json"

        #Web catgirls will take on full URLs.
        self.filepathWeb = SAVE_FOLDER + "links-web.json"

        #List of pending catgirls waiting to be added.
        self.filepathPending = SAVE_FOLDER + "links-pending.json"

        #Catgirls
        self.picturesLocal = dataIO.load_json(self.filepathLocal)
        self.picturesLocalx10 = dataIO.load_json(self.filepathLocalx10)
        self.picturesWeb = dataIO.load_json(self.filepathWeb)
        self.picturesPending = dataIO.load_json(self.filepathPending)

        #Trap (kek)
        self.catgirls_local_trap = [];

        #Custom key which holds an array of catgirl filenames/paths
        self.KEY_CATGIRL = "catgirls"

        #Prepend local listings with domain name.
        for x in range(0,len(self.picturesLocal[KEY_CATGIRL])):
            self.picturesLocal[KEY_CATGIRL][x][KEY_IMAGE_URL] = "https://nekomimi.injabie3.moe/p/" + self.picturesLocal[KEY_CATGIRL][x][KEY_IMAGE_URL]

            if ("trap" in self.picturesLocal[KEY_CATGIRL][x]) and (self.picturesLocal[KEY_CATGIRL][x]['trap'] is True):
                self.catgirls_local_trap.append(self.picturesLocal[KEY_CATGIRL][x])
            #self.picturesLocal[KEY_CATGIRL][x][KEY_IMAGE_URL] = "https://nyan.injabie3.moe/p/" + self.picturesLocal[KEY_CATGIRL][x][KEY_IMAGE_URL]

        #Prepend hosted listings with domain name.
        for x in range(0,len(self.picturesLocalx10[KEY_CATGIRL])):
            self.picturesLocalx10[KEY_CATGIRL][x][KEY_IMAGE_URL] = "http://injabie3.x10.mx/p/" + self.picturesLocalx10[KEY_CATGIRL][x][KEY_IMAGE_URL]

        for x in range(0, len(self.picturesLocal[KEY_CATBOY])):
            self.picturesLocal[KEY_CATBOY][x][KEY_IMAGE_URL] = "http://nekomimi.injabie3.moe/p/b/" + self.picturesLocal[KEY_CATBOY][x][KEY_IMAGE_URL]

        self.catgirls_local = self.picturesLocal[KEY_CATGIRL]
        self.catgirls = self.picturesLocal[KEY_CATGIRL] + self.picturesWeb[KEY_CATGIRL] + self.picturesLocalx10[KEY_CATGIRL]
        self.catboys = self.picturesLocal[KEY_CATBOY] + self.picturesWeb[KEY_CATBOY] + self.catgirls_local_trap
        self.pending = self.picturesPending[KEY_CATGIRL]

    def __init__(self, bot):
        self.bot = bot
        checkFolder()
        checkFiles()
        self.refreshDatabase()

    #[p]catgirl
    @commands.command(name="catgirl", pass_context=True)
    async def _catgirl(self, ctx):
        """Displays a random, cute catgirl :3"""
        #Send typing indicator, useful for when Discord explicit filter is on.
        await self.bot.send_typing(ctx.message.channel)

        randCatgirl = random.choice(self.catgirls)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Catgirl"
        embed.url = randCatgirl[KEY_IMAGE_URL]
        if KEY_ISPIXIV in randCatgirl and randCatgirl[KEY_ISPIXIV]:
            source = "[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatgirl[KEY_PIXIV_ID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randCatgirl[KEY_PIXIV_ID]
            embed.set_footer(text=customFooter)
        if KEY_ISSEIGA in randCatgirl and randCatgirl[KEY_ISSEIGA]:
            source = "[{}]({})".format("Original Source","http://seiga.nicovideo.jp/seiga/im"+randCatgirl[KEY_SEIGA_ID])
            embed.add_field(name="Nico Nico Seiga",value=source)
            customFooter = "ID: " + randCatgirl[KEY_SEIGA_ID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randCatgirl:
            embed.add_field(name="Info",value=randCatgirl["character"], inline=False)
        embed.set_image(url=randCatgirl[KEY_IMAGE_URL])
        try:
            await self.bot.say("",embed=embed)
        except Exception as e:
            await self.bot.say("Please try again.")
            print("Catgirl exception:")
            print(randCatgirl)
            print(e)
            print("==========")

    #[p]catboy
    @commands.command(name="catboy", pass_context=True)
    async def _catboy(self, ctx):
        """This command says it all (database still WIP)"""
        #Send typing indicator, useful for when Discord explicit filter is on.
        await self.bot.send_typing(ctx.message.channel)

        randCatboy = random.choice(self.catboys)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Catboy"
        embed.url = randCatboy[KEY_IMAGE_URL]
        if randCatboy[KEY_ISPIXIV]:
            source="[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatboy[KEY_PIXIV_ID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randCatboy[KEY_PIXIV_ID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randCatboy:
            embed.add_field(name="Info",value=randCatboy["character"], inline=False)
        embed.set_image(url=randCatboy[KEY_IMAGE_URL])
        try:
            await self.bot.say("",embed=embed)
        except Exception as e:
            await self.bot.say("Please try again.")
            print("Catgirl exception:")
            print(randCatboy)
            print(e)
            print("==========")

    @commands.group(name="nyaa", pass_context=True, no_pm=False)
    async def _nyaa(self, ctx):
        """Nekomimi universe! \o/"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

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

    #[p]nyaa catgirl
    @_nyaa.command(pass_context=True, no_pm=False)
    async def catgirl(self, ctx):
        """Displays a random, cute catgirl :3"""
        #Send typing indicator, useful for when Discord explicit filter is on.
        await self.bot.send_typing(ctx.message.channel)

        randCatgirl = random.choice(self.catgirls)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Catgirl"
        embed.url = randCatgirl[KEY_IMAGE_URL]
        if KEY_ISPIXIV in randCatgirl and randCatgirl[KEY_ISPIXIV]:
            source = "[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatgirl[KEY_PIXIV_ID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randCatgirl[KEY_PIXIV_ID]
            embed.set_footer(text=customFooter)
        if KEY_ISSEIGA in randCatgirl and randCatgirl[KEY_ISSEIGA]:
            source = "[{}]({})".format("Original Source","http://seiga.nicovideo.jp/seiga/im"+randCatgirl[KEY_SEIGA_ID])
            embed.add_field(name="Nico Nico Seiga",value=source)
            customFooter = "ID: " + randCatgirl[KEY_SEIGA_ID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randCatgirl:
            embed.add_field(name="Info",value=randCatgirl["character"], inline=False)
        embed.set_image(url=randCatgirl[KEY_IMAGE_URL])
        try:
            await self.bot.say("",embed=embed)
        except Exception as e:
            await self.bot.say("Please try again.")
            print("Catgirl exception:")
            print(randCatgirl)
            print(e)
            print("==========")

    #[p]nyaa numbers
    @_nyaa.command(pass_context=True, no_pm=False)
    async def numbers(self, ctx):
        """Displays the number of images in the database."""
        await self.bot.say("There are:\n - **" + str(len(self.catgirls)) + "** catgirls available.\n - **" + str(len(self.catboys)) + "** catboys available.\n - **" + str(len(self.picturesPending[KEY_CATGIRL])) + "** pending images.")

    #[p]nyaa refresh - Also allow for refresh in a DM to the bot.
    @_nyaa.command(pass_context=True, no_pm=False)
    async def refresh(self, ctx):
        """Refreshes the internal database of nekomimi images."""
        self.refreshDatabase()
        await self.bot.say("List reloaded.  There are:\n - **" + str(len(self.catgirls)) + "** catgirls available.\n - **" + str(len(self.catboys)) + "** catboys available.\n - **" + str(len(self.picturesPending[KEY_CATGIRL])) + "** pending images.")

    #[p]nyaa local
    @_nyaa.command(pass_context=True, no_pm=False)
    async def local(self, ctx):
        """Displays a random, cute catgirl from the local database."""
        #Send typing indicator, useful for when Discord explicit filter is on.
        await self.bot.send_typing(ctx.message.channel)

        randCatgirl = random.choice(self.catgirls_local)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Catgirl"
        embed.url = randCatgirl[KEY_IMAGE_URL]
        if randCatgirl[KEY_ISPIXIV]:
            source="[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatgirl[KEY_PIXIV_ID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randCatgirl[KEY_PIXIV_ID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randCatgirl:
            embed.add_field(name="Info",value=randCatgirl["character"], inline=False)
        embed.set_image(url=randCatgirl[KEY_IMAGE_URL])
        try:
            await self.bot.say("",embed=embed)
        except Exception as e:
            await self.bot.say("Please try again.")
            print("Catgirl exception:")
            print(randCatgirl)
            print(e)
            print("==========")

    #[p]nyaa trap
    @_nyaa.command(pass_context=True, no_pm=False)
    async def trap(self, ctx):
        """Say no more fam, gotchu covered ;)"""
        #Send typing indicator, useful for when Discord explicit filter is on.
        await self.bot.send_typing(ctx.message.channel)

        randCatgirl = random.choice(self.catgirls_local_trap)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Nekomimi"
        embed.url = randCatgirl[KEY_IMAGE_URL]
        if randCatgirl[KEY_ISPIXIV]:
            source="[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatgirl[KEY_PIXIV_ID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randCatgirl[KEY_PIXIV_ID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randCatgirl:
            embed.add_field(name="Info",value=randCatgirl["character"], inline=False)
        embed.set_image(url=randCatgirl[KEY_IMAGE_URL])
        try:
            await self.bot.say("",embed=embed)
        except Exception as e:
            await self.bot.say("Please try again.")
            print("Catgirl exception:")
            print(e)
            print("==========")

    #[p]nyaa catboy
    @_nyaa.command(pass_context=True, no_pm=False)
    async def catboy(self, ctx):
        """Displays a random, cute catboy :3"""
        #Send typing indicator, useful for when Discord explicit filter is on.
        await self.bot.send_typing(ctx.message.channel)

        randCatboy = random.choice(self.catboys)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Catboy"
        embed.url = randCatboy[KEY_IMAGE_URL]
        if randCatboy[KEY_ISPIXIV]:
            source="[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randCatboy[KEY_PIXIV_ID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randCatboy[KEY_PIXIV_ID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randCatboy:
            embed.add_field(name="Info",value=randCatboy["character"], inline=False)
        embed.set_image(url=randCatboy[KEY_IMAGE_URL])
        try:
            await self.bot.say("",embed=embed)
        except Exception as e:
            await self.bot.say("Please try again.")
            print("Catgirl exception:")
            print(e)
            print("==========")

    #[p] nyaa debug
    @_nyaa.command(pass_context=True, no_pm=False)
    async def debug(self, ctx):
        """Sends entire list via DM for debugging."""
        msg = "Debug Mode\nCatgirls:\n```"
        for x in range(0,len(self.catgirls)):
            msg += self.catgirls[x][KEY_IMAGE_URL] + "\n"
            if len(msg) > 1900:
               msg += "```"
               await self.bot.send_message(ctx.message.author, msg)
               msg = "```"
        msg += "```"
        await self.bot.send_message(ctx.message.author, msg)

        msg = "Catboys:\n```"
        for x in range(0,len(self.catboys)):
            msg += self.catboys[x][KEY_IMAGE_URL] + "\n"
            if len(msg) > 1900:
               msg += "```"
               await self.bot.send_message(ctx.message.author, msg)
               msg = "```"
        msg += "```"
        await self.bot.send_message(ctx.message.author, msg)

    #[p]nyaa add
    @_nyaa.command(pass_context=True, no_pm=True)
    async def add(self, ctx, link: str, description: str=""):
        """
        Add a catgirl image to the pending database.
        Will be screened before it is added to the global list. WIP

        link          The full URL to an image, use \" \" around the link.
        description   Description of character (optional)
        """

        temp = {}
        temp["url"] = link
        temp["character"] = description
        temp["submitter"] = ctx.message.author.name
        temp["id"] = None
        temp["is_pixiv"] = False


        self.picturesPending[KEY_CATGIRL].append(temp)
        dataIO.save_json(self.filepathPending, self.picturesPending)

        #Get owner ID.
        owner = discord.utils.get(self.bot.get_all_members(),id=self.bot.settings.owner)

        try:
            await self.bot.send_message(owner, "New catgirl image is pending approval. Please check the list!")
        except discord.errors.InvalidArgument:
            await self.bot.say("Added, but could not notify owner.")
        else:
            await self.bot.say("Added, notified and pending approval. :ok_hand:")

    async def _randomize(self):
        """Shuffles images in the list."""
        while self:
            random.shuffle(self.catgirls)
            random.shuffle(self.catboys)
            random.shuffle(self.catgirls_local)
            await asyncio.sleep(3600)

def setup(bot):
    checkFolder()   #Make sure the data folder exists!
    checkFiles()    #Make sure we have a local database!
    nyanko = Catgirl(bot)
    bot.add_cog(nyanko)
    bot.loop.create_task(nyanko._randomize())
