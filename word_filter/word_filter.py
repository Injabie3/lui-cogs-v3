import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
from .utils import checks
from .utils.paginator import Pages
import asyncio
from threading import Lock
import os
import re
import random

"""
Cog Purpose: 
    - To filter words in a more smart/useful way then simply detecting and deleting a message
"""

colour = discord.Colour

def check_filesystem():

    folders = ["data/word_filter"]
    for folder in folders:
        if not os.path.exists(folder):
            print("Word Filter: Creating folder: {} ...".format(folder))
            os.makedirs(folder)
            
    files = ["data/word_filter/filter.json", "data/word_filter/settings.json"]
    for file in files:
        if not os.path.exists(file):
            #build a default filter.json
            dict = {}
            dataIO.save_json(file,dict)    
            print("Highlight: Creating file: {} ...".format(file))

class WordFilter(object):
    def __init__(self, bot):
        self.bot = bot
        self.lock = Lock()
        self.lock_settings = Lock()
        self.filters = dataIO.load_json("data/word_filter/filter.json")
        self.settings = dataIO.load_json("data/word_filter/settings.json")
        self.colours = [colour.purple(),colour.red(),colour.blue(),colour.orange(),colour.green()]
        
        #JSON keys for settings:
        self.key_toggleMod = "toggleMod"
    
    def _update_filters(self, new_obj):
        self.lock.acquire()
        try:
            dataIO.save_json("data/word_filter/filter.json", new_obj)
            self.filters = dataIO.load_json("data/word_filter/filter.json")
        finally:
            self.lock.release()
    
    def _update_settings(self, new_obj):
        self.lock_settings.acquire()
        try:
            dataIO.save_json("data/word_filter/settings.json", new_obj)
            self.settings = dataIO.load_json("data/word_filter/settings.json")
        finally:
            self.lock_settings.release()
            
    @commands.group(name="word_filter", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def word_filter(self, ctx):
        """Smart word filtering"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    
    @word_filter.command(name="add", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def add_filter(self, ctx, word: str):
        """Add word to filter"""
        guild_id = ctx.message.server.id
        user = ctx.message.author
        guild_name = ctx.message.server.name
        
        if guild_id not in list(self.filters):
            dict = {}
            dict[guild_id] = []
            self.filters.update(dict)
            self._update_filters(self.filters)
            
        if word not in self.filters[guild_id]:
            self.filters[guild_id].append(word)
            self._update_filters(self.filters)
            await self.bot.send_message(user,"`Word Filter:` `{0}` was added to the filter in the guild **{1}**".format(word,guild_name))
        else:
            await self.bot.send_message(user,"`Word Filter:` The word `{0}` is already in the filter for guild **{1}**".format(word,guild_name))
        
    @word_filter.command(name="remove", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def remove_filter(self, ctx, word: str):
        """Remove word  from filter"""
        guild_id = ctx.message.server.id
        user = ctx.message.author
        guild_name = ctx.message.server.name
        
        if guild_id not in list(self.filters):
            await self.bot.send_message(user,"`Word Filter:` The guild **{}** is not registered, please add a word first".format(guild_name))
            return
        
        if len(self.filters[guild_id]) == 0 or word not in self.filters[guild_id]:
            await self.bot.send_message(user,"`Word Filter:` The word `{0}` is not in the filter for guild **{1}**".format(word,guild_name))
            return
        else:
            self.filters[guild_id].remove(word)
            self._update_filters(self.filters)
            await self.bot.send_message(user,"`Word Filter:` `{0}` removed from the filter in the guild **{1}**".format(word,guild_name))
    
    @word_filter.command(name="list", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def list_filter(self, ctx):
        """List filtered words in raw format, NOTE: do this in a channel outside of the viewing public"""
        guild_id = ctx.message.server.id
        guild_name = ctx.message.server.name
        user = ctx.message.author
        
        if guild_id not in list(self.filters):
            await self.bot.send_message(user,"`Word Filter:` The guild **{}** is not registered, please add a word first".format(guild_name))
            return
        
        if len(self.filters[guild_id]) > 0:
            display = []
            for n in range(0, len(self.filters[guild_id])):
                display.append("`"+self.filters[guild_id][n]+"`")
            # msg = ""
            # for word in self.filters[guild_id]:
                # msg += word
                # msg += "\n"
            # title = "Filtered words for: **{}**".format(guild_name)   
            # embed = discord.Embed(title=title,description=msg,colour=discord.Colour.red())
            # await self.bot.send_message(user,embed=embed)
            
            p = Pages(self.bot,message=ctx.message,entries=display)
            p.embed.title = "Filtered words for: **{}**".format(guild_name)
            p.embed.colour = discord.Colour.red()
            await p.paginate()
        else:
            await self.bot.send_message(user, "Sorry you have no filtered words in **{}**".format(guild_name))
    
    @word_filter.command(name="togglemod", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def toggle_mod(self, ctx):
        """Toggle global override of filters for server admins/mods."""
        self._update_settings(self.settings)
        try:
            if self.settings[ctx.message.author.server.id][self.key_toggleMod] is True:
                self.settings[ctx.message.author.server.id][self.key_toggleMod] = False
                set = False
            else:
                self.settings[ctx.message.author.server.id][self.key_toggleMod] = True
                set = True
        except:
            if ctx.message.author.server.id not in self.settings:
                self.settings[ctx.message.author.server.id] = {}
            self.settings[ctx.message.author.server.id][self.key_toggleMod] = True
            set = True
        self._update_settings(self.settings)
        if set:
            await self.bot.say(":white_check_mark: Word Filter: Moderators (and higher) **will not be** filtered.")
        else:
            await self.bot.say(":negative_squared_cross_mark: Word Filter: Moderators (and higher) **will be** filtered.")
        
        self._update_settings(self.settings)

    
    async def check_words(self, msg, new_msg=None):
        mod_role = self.bot.settings.get_server_mod(msg.server).lower()
        admin_role = self.bot.settings.get_server_admin(msg.server).lower()
        
        #Filter only configured servers, not private DMs.
        if isinstance(msg.channel,discord.PrivateChannel) or msg.server.id not in list(self.filters):
            return
        
        #Check if mod or admin, and do not filter if togglemod is enabled.
        try:
            if self.settings[msg.author.server.id][self.key_toggleMod] is True:
                for x in range(0, len(msg.author.roles)):
                    if msg.author.roles[x].name.lower() == mod_role or msg.author.roles[x].name.lower() == admin_role:
                        return
        except Exception as e: #Most likely key error, so ignore.
            print(e)
            pass
        
        guild_id = msg.server.id
        filtered_words = self.filters[guild_id]
        if new_msg:
            check_msg = new_msg.content
        else:
            check_msg = msg.content
        original_msg = check_msg
        filtered_msg = original_msg
        one_word = self._is_one_word(check_msg)
        
        for word in filtered_words:
            try:
                filtered_msg = self._filter_word(word,filtered_msg)
            except Exception as e:
                print("Word Filter exception:")
                print(e)
                print(word)
                print(filtered_msg)
                print("==========")
            
            
        all_filtered = self._is_all_filtered(filtered_msg)
        
        if filtered_msg == original_msg:
            return # no bad words, dont need to do anything else
        elif (filtered_msg != original_msg and one_word) or all_filtered:
            await self.bot.delete_message(msg) # delete message but don't show full message context
            filter_notify = "{0.author.mention} was filtered!".format(msg)
            n_msg = await self.bot.send_message(msg.channel,filter_notify)
            await asyncio.sleep(3)
            await self.bot.delete_message(n_msg)
        else:
            await self.bot.delete_message(msg)
            filter_notify = "{0.author.mention} was filtered! Message was: \n".format(msg)
            embed = discord.Embed(colour=random.choice(self.colours),description="{0.author.name}#{0.author.discriminator}: {1}".format(msg,filtered_msg))
            await self.bot.send_message(msg.channel,filter_notify,embed=embed)
            
    def _filter_word(self, word, string):
        regex = r'\b{}\b'.format(word)
        
        # Replace the offending string with the correct number of stars.  Note that this only considers the length of the first time
        # an offending string is found with the current regex.  It will replace every string found with this regex with the number of
        # stars corresponding to the first offending string.
        
        try:
            number = len(re.search(regex,string,flags=re.IGNORECASE).group(0))
        except:
            # Nothing to replace, return original string
            return string
        
        stars = '*'*number
        repl = "{0}{1}{0}".format('`',stars)
        return re.sub(regex,repl,string,flags=re.IGNORECASE)
    
    def _is_one_word(self, string):
        return len(string.split()) == 1
    
    def _is_all_filtered(self, string):
        words = string.split()
        cnt = 0
        for word in words:
            if bool(re.search("[*]+",word)):
                cnt += 1
        return cnt == len(words)
        
def setup(bot):
    check_filesystem()
    filter = WordFilter(bot)
    bot.add_listener(filter.check_words, 'on_message')
    bot.add_listener(filter.check_words, 'on_message_edit')
    bot.add_cog(filter)
