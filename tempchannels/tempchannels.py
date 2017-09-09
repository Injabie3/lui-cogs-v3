import discord
from discord.ext import commands
from .utils import checks
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import time
import os
import asyncio
import aiohttp # Using this to build own request to Discord API for NSFW.
import json # Will need this to use in conjunction with aiohttp below.

def check_filesystem():
    folders = ["data/lui-cogs/tempchannels"]
    for folder in folders:
        if not os.path.exists(folder):
            print("Temporary Channels: Creating folder: {} ...".format(folder))
            os.makedirs(folder)
            
    files = ["data/lui-cogs/tempchannels/settings.json"]
    for file in files:
        if not os.path.exists(file):
            #build a default filter.json
            dict = {}
            dataIO.save_json(file,dict)    
            print("Temporary Channels: Creating file: {} ...".format(file))

class TempChannels:
    """Creates a temporary channel."""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/lui-cogs/tempchannels/settings.json")
    
    def _sync_settings(self):
        dataIO.save_json("data/lui-cogs/tempchannels/settings.json", self.settings)
        self.settings = dataIO.load_json("data/lui-cogs/tempchannels/settings.json")
    
    @commands.group(name="tempchannels", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels(self, ctx):
        """
        Temporary text-channel creation (only 1 at the moment).
        """
        #Display the help context menu
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    
    @_tempchannels.command(name="default", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_default(self, ctx):
        """RUN FIRST: Sets default settings.
        - Start at 00:00.
        - Duration of channel is 1 minute.
        - The creation and deletion of TempChannel is disabled.
        - If present, the previous TempChannel (if any) will be forgotten, and not deleted.
        """
        try:
            self.settings[ctx.message.server.id]
        except:
            self.settings[ctx.message.server.id] = {}
            
        self.settings[ctx.message.server.id]["channelName"] = "tempchannel"
        self.settings[ctx.message.server.id]["channelTopic"] = "Created with TempChannels cog."
        self.settings[ctx.message.server.id]["channelPosition"] = 0
        self.settings[ctx.message.server.id]["channelCreated"] = False
        self.settings[ctx.message.server.id]["durationHours"] = 0
        self.settings[ctx.message.server.id]["durationMinutes"] = 1
        self.settings[ctx.message.server.id]["startHour"] = 20
        self.settings[ctx.message.server.id]["startMinute"] = 0
        self.settings[ctx.message.server.id]["enabled"] = False
        self.settings[ctx.message.server.id]["nsfw"] = False
        self.settings[ctx.message.server.id]["channel"] = None
        
        self._sync_settings()
        await self.bot.say(":white_check_mark: TempChannel: Setting default settings.")
        
    @_tempchannels.command(name="show", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_show(self,ctx):
        """Show current settings"""
        self._sync_settings()
        try:
            msg  = ":information_source: TempChannel - Current Settings\n```"
            if self.settings[ctx.message.server.id]["enabled"] is True:
                msg += "Enabled?          Yes\n"
            else:
                msg += "Enabled?          No\n"
            if self.settings[ctx.message.server.id]["nsfw"] is True:
                msg += "NSFW Prompt:      Yes\n"
            else:
                msg += "NSFW Prompt:      No\n"
            msg += "Channel Name:     {0}\n".format(self.settings[ctx.message.server.id]["channelName"])
            msg += "Channel Topic:    {0}\n".format(self.settings[ctx.message.server.id]["channelTopic"])
            msg += "Creation time:    {0:002d}:{1:002d}\n".format(self.settings[ctx.message.server.id]["startHour"],self.settings[ctx.message.server.id]["startMinute"])
            msg += "Duration:         {0}h {1}m\n".format(self.settings[ctx.message.server.id]["durationHours"],self.settings[ctx.message.server.id]["durationMinutes"])
            msg += "Channel Position: {0}```".format(self.settings[ctx.message.server.id]["channelPosition"])
            await self.bot.say(msg)
        except:
            await self.bot.say(":negative_squared_cross_mark: TempChannel: Cannot display settings.  Please set default settings by typing `{}tempchannels default` first.".format(ctx.prefix))            
    
    @_tempchannels.command(name="toggle", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_toggle(self, ctx):
        """Toggle the creation/deletion of the temporary channel."""
        try:
            if self.settings[ctx.message.server.id]["enabled"] is True:
                self.settings[ctx.message.server.id]["enabled"] = False
                set = False
            else:
                self.settings[ctx.message.server.id]["enabled"] = True
                set = True
        except: #Typically a KeyError
            self.settings[ctx.message.server.id]["enabled"] = True
            set = True
        self._sync_settings()
        if set:
            await self.bot.say(":white_check_mark: TempChannel: Enabled.")
        else:
            await self.bot.say(":negative_squared_cross_mark: TempChannel: Disabled.")
            
    @_tempchannels.command(name="nsfw", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_nsfw(self, ctx):
        """Toggle NSFW requirements"""
        try:
            if self.settings[ctx.message.server.id]["nsfw"] is True:
                self.settings[ctx.message.server.id]["nsfw"] = False
                set = False
            else:
                self.settings[ctx.message.server.id]["nsfw"] = True
                set = True
        except: #Typically a KeyError
            self.settings[ctx.message.server.id]["nsfw"] = True
            set = True
        self._sync_settings()
        if set:
            await self.bot.say(":white_check_mark: TempChannel: NSFW requirement enabled.")
        else:
            await self.bot.say(":negative_squared_cross_mark: TempChannel: NSFW requirement disabled.")
    
    @_tempchannels.command(name="setstart", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_setstart(self, ctx, hour: int, minute: int):
        """Set the temp channel creation time. Use 24 hour time."""
        if (hour > 23) or (hour < 0):
            await self.bot.say(":negative_squared_cross_mark: TempChannel - Start Time: Please enter a valid time.")
            return
        if (minute > 59) or (minute < 0):
            await self.bot.say(":negative_squared_cross_mark: TempChannel - Start Time: Please enter a valid time.")
            return
            
        self.settings[ctx.message.server.id]["startHour"] = hour
        self.settings[ctx.message.server.id]["startMinute"] = minute
        self._sync_settings()
        await self.bot.say(":white_check_mark: TempChannel - Start Time: Start time set to {0:002d}:{1:002d}.".format(hour,minute))

    @_tempchannels.command(name="setduration", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_setduration(self, ctx, hours: int, minutes: int):
        """
        Sets the duration of the temp channel.  Maximum 100 hours.
        hours:    # of hours to make this channel available, and
        minutes:  # of minutes to make this channel available.
        
        Example:
        If hours = 1, and minutes = 3, then the channel will be available for
        1 hour 3 minutes.
        """
        if (hours >= 100) or (hours < 0):
            await self.bot.say(":negative_squared_cross_mark: TempChannel - Duration: Please enter valid hours!")
            return
        elif (minutes >= 60) or (minutes < 0):
            await self.bot.say(":negative_squared_cross_mark: TempChannel - Duration: Please enter valid minutes!")
            return
        elif (hours >= 99) and (minutes >= 60):
            await self.bot.say(":negative_squared_cross_mark: TempChannel - Duration: Please enter a valid duration!")
            return
        
        self.settings[ctx.message.server.id]["durationHours"] = hours
        self.settings[ctx.message.server.id]["durationMinutes"] = minutes
        self._sync_settings()
        
        await self.bot.say(":white_check_mark: TempChannel - Duration: Duration set to **{0} hours, {1} minutes**.".format(hours, minutes))

    @_tempchannels.command(name="settopic", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_settopic(self, ctx, topic: str):
        """Sets the topic of the channel."""
        if len(topic) > 1024:
            await self.bot.say(":negative_squared_cross_mark: TempChannel - Topic: Topic is too long.  Try again.")
            return
        
        self.settings[ctx.message.server.id]["channelTopic"] = topic
        self._sync_settings()
        
        await self.bot.say(":white_check_mark: TempChannel - Topic: Topic set to:\n```{0}```".format(topic))

    @_tempchannels.command(name="setname", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_setname(self, ctx, name: str):
        """Sets the #name of the channel."""
        if len(name) > 25:
            await self.bot.say(":negative_squared_cross_mark: TempChannel - Name: Name is too long.  Try again.")
            return
        
        self.settings[ctx.message.server.id]["channelName"] = name
        self._sync_settings()
        
        await self.bot.say(":white_check_mark: TempChannel - Name: Channel name set to: ``{0}``".format(name))

    @_tempchannels.command(name="setposition", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_setposition(self, ctx, position: int):
        """Sets the position of the text channel in the list."""
        if position > 100 or position < 0:
            await self.bot.say(":negative_squared_cross_mark: TempChannel - Position: Invalid position.  Try again.")
            return
        
        self.settings[ctx.message.server.id]["channelPosition"] = position
        self._sync_settings()
        
        await self.bot.say(":white_check_mark: TempChannel - Position: This channel will be at position {0}".format(position))

    @_tempchannels.command(name="delete", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _tempchannels_delete(self, ctx):
        """Deletes the temp channel, if it exists."""
        if self.settings[ctx.message.server.id]["channelCreated"] is True:
            # Channel created, see when we should delete it.
            self._sync_settings()
            try:
                if self.settings[ctx.message.server.id]["channel"] is not None:
                    try:
                        await self.bot.delete_channel(self.bot.get_channel(self.settings[ctx.message.server.id]["channel"]))
                        self.settings[ctx.message.server.id]["channel"] = None
                    except Exception as e:
                        print(e)
                    await self.bot.say(":white_check_mark: TempChannel: Channel deleted")
                else:
                    await self.bot.say(":negative_squared_cross_mark: TempChannel: No temp channel to delete.")
            except:
                self.settings[ctx.message.server.id]["channel"] = None
                await self.bot.say(":negative_squared_cross_mark: No temp channel to delete.")
            print("TempChannel: Channel deleted at "+format(time.strftime("%H:%M:%S")))
            self.settings[ctx.message.server.id]["channelCreated"] = False
            self._sync_settings()
        
    async def _check_channels(self):
        while self == self.bot.get_cog("TempChannels"):
            await asyncio.sleep(30)
            # Create/maintain the channel during a valid time and duration, else delete it.
            try:
                for server in self.settings:
                    try:
                        # Check for valid settings
                        self.settings[server]["channelName"]
                        self.settings[server]["channelPosition"]
                        self.settings[server]["channelTopic"]
                        self.settings[server]["channelCreated"]
                        self.settings[server]["startHour"]
                        self.settings[server]["startMinute"]
                        self.settings[server]["durationHours"]
                        self.settings[server]["durationMinutes"]
                        self.settings[server]["nsfw"]
                        if (self.settings[server]["enabled"] is False):
                            continue
                    except:
                        print("TempChannels: Error, missing keys for {}".format(server))
                        continue
                    
                    if ( int(time.strftime("%H")) == self.settings[server]["startHour"]) and (int(time.strftime("%M")) == self.settings[server]["startMinute"]) and (self.settings[server]["channelCreated"] is False):
                        # Create the channel, and store the ID, and time to delete channel in the settings.
                        
                        if self.settings[server]["channel"] is None:
                            if self.settings[server]["nsfw"] is True:
                                created_channel = await self.bot.create_channel(self.bot.get_server(server), "nsfw-{}".format(self.settings[server]["channelName"]))
                                
                                # This is most definitely not the best way of doing it, but since no NSFW method, we have this:
                                header = { "Authorization" : "Bot {}".format(self.bot.settings.token), "content-type" : "application/json" }
                                body = { "name" : self.settings[server]["channelName"], "nsfw" : True }
                                
                                async with aiohttp.ClientSession() as session:
                                    async with session.put('https://discordapp.com/api/channels/{}'.format(created_channel.id),headers=header,data=json.dumps(body)) as resp:
                                        print(resp.status)
                                        print(await resp.text())
                            else:
                                created_channel = await self.bot.create_channel(self.bot.get_server(server), self.settings[server]["channelName"])
                                
                            self.settings[server]["channel"] = created_channel.id
                            self._sync_settings()
                            print("TempChannel: Channel created at "+format(time.strftime("%H:%M:%S")))
                            
                            await self.bot.edit_channel(created_channel, topic=self.settings[server]["channelTopic"],name=self.settings[server]["channelName"])
                            
                            try:
                                await self.bot.move_channel(created_channel, self.settings[server]["channelPosition"])
                            except:
                                print("TempChannel: Could not move channel position")

                            self.settings[server]["stopTime"] = time.time() + (self.settings[server]["durationHours"]*60*60) + (self.settings[server]["durationMinutes"]*60)
                            self.settings[server]["channelCreated"] = True
                            self._sync_settings()
                            
                    elif self.settings[server]["channelCreated"] is True:
                        # Channel created, see when we should delete it.
                        self._sync_settings()
                        if time.time() >= self.settings[server]["stopTime"]:
                            try:
                                if self.settings[server]["channel"] is not None:
                                    try:
                                        await self.bot.delete_channel(self.bot.get_channel(self.settings[server]["channel"]))
                                        self.settings[server]["channel"] = None
                                    except Exception as e:
                                        print(e)
                            except:
                                self.settings[server]["channel"] = None
                            print("TempChannel: Channel deleted at "+format(time.strftime("%H:%M:%S")))
                            self.settings[server]["channelCreated"] = False
                            self._sync_settings()
            except Exception as e:
                print("TempChannels: No servers. {}".format(e))

def setup(bot):
    check_filesystem()
    tempchannels = TempChannels(bot)
    bot.add_cog(tempchannels)
    bot.loop.create_task(tempchannels._check_channels())