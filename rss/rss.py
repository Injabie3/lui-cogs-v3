import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import aiohttp #probably wont need
import requests #probably wont need
import asyncio
import feedparser
from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup

"""
Cogs Purpose: To be able to hook up any RSS feed to the bot and Post it in a channel
Requirements: 
    - sudo pip install bs4
    - sudo pip install feedparser
"""
#---------------------------------------------------------------------------------------------#
def date2epoch(date):
    try:
        epoch = datetime.strptime(date,'%a, %d %b %Y %H:%M:%S %z').timestamp()
    except ValueError:
        epoch = datetime.strptime(date,'%a, %d %b %Y %H:%M:%S %Z').timestamp()
        return epoch
        
    return epoch

#---------------------------------------------------------------------------------------------#
def epoch2date(epoch):
    date = datetime.fromtimestamp(epoch).strftime('%a, %d %b %Y %I:%M%p')
    return date
 
#---------------------------------------------------------------------------------------------#
def check_filesystem():

    folders = ("data/rss")
    for folder in folders:
        if not os.path.exists(folder):
            print("RSS Cog: Creating folder: " + folder + " ...")
            os.makedirs(folder)
            
    files = ("data/rss/config.json", "data/rss/feeds.json")
    for file in files:
        if not os.path.exists(file):
            print("RSS Cog: Creating file: " + file + " ...")
          
            if "feeds" in file:
                #build a default feeds.json
                dict = {}
                default_feed = {}
                default_feed['id'] = 0
                default_feed['latest_post_time'] = 0
                dict['feeds'] = []
                dict['feeds'].append(default_feed)
                dataIO.save_json("data/rss/feeds.json",dict)
            elif "config" in file:
                #build a default config.json
                dict = {}
                dict['post_channel'] = "change_me"
                dict['rss_feed_urls'] = ["change_me"]
                dataIO.save_json("data/rss/config.json",dict)

#---------------------------------------------------------------------------------------------#                
class RSSFeed(object):
    def __init__(self, bot):
        self.settings = dataIO.load_json("data/rss/config.json")
        self.bot = bot
        self.rss_feed_urls = self.settings['rss_feed_urls']
        self.channel_id = self.settings['post_channel']
#---------------------------------------------------------------------------------------------#   
    # searching for time based feed updates instead of content based feed updates
    def _is_new_item(self,latest_post_time,item_post_time):
        return latest_post_time < item_post_time
        
#---------------------------------------------------------------------------------------------#   
    def _get_latest_post_time(self,feed_items):
        published_times = []
        for item in feed_items:
            published_times.append(date2epoch(item['published']))
        return max(published_times)
        
#---------------------------------------------------------------------------------------------#   
    def _get_xml(self,rss_url):
        return requests.get(rss_url).text
        
#---------------------------------------------------------------------------------------------#   
    def _get_feed(self,rss_url,channel,index=None): 
        
        if channel is None:
            print("RSS: Can't find channel, Bot is not yet logged in.")
            return []
        
        feeds = dataIO.load_json("data/rss/feeds.json")
        
        #ensure every rss url has a specified id and most recent post epoch
        try:
            latest_post_time = feeds['feeds'][index]['latest_post_time']
        except IndexError:
            dict = {}
            dict['id'] = index
            dict['latest_post_time'] = 0
            feeds['feeds'].append(dict)
            dataIO.save_json("data/rss/feeds.json",feeds)
            feeds = dataIO.load_json("data/rss/feeds.json")
            latest_post_time = feeds['feeds'][index]['latest_post_time']
        
        news = []
        feed = feedparser.parse(rss_url)
        
        ### testing ###
        xml_res = self._get_xml(rss_url)
        feedie = feedparser.parse(xml_res)
        dataIO.save_json("data/rss/feedie-test.json",feedie['items'])
        ### ###
        
        #does nothing important, will remove soon
        dataIO.save_json("data/rss/feeds-all.json",feed['items'])
        
        for item in feed['items']:
           
            item_post_time = date2epoch(item['published'])
            if self._is_new_item(latest_post_time,item_post_time):
                
                dict = {}
                dict['title'] = item['title']
                dict['link'] = item['link']
                dict['published'] = item['published']
                dict['summary'] = item['summary']
                news.append(dict)
                
                print("RSS: new item in feed...")
        if len(news) == 0:
            print("RSS: no new items in feed...")
        print("----------------")
        
        latest_post_time = self._get_latest_post_time(feed['items'])
        feeds['feeds'][index]['latest_post_time'] = latest_post_time #feeds['feeds'][0]['latest_post_time']
        dataIO.save_json("data/rss/feeds.json",feeds)
        
        return news
        
#---------------------------------------------------------------------------------------------#       
    async def _rss(self):
        """ Checks for rss updates periodically and posts any new content to the specific channel"""
        rss_delay = 30
        
        print("RSS: Scanning Feed(s)")
        
        while self == self.bot.get_cog("RSSFeed"):
            post_channel = self.bot.get_channel(self.channel_id)
            updates = []
            idx = 0
            
            for feed_url in self.rss_feed_urls:
                feed_updates = self._get_feed(feed_url,post_channel,index=idx)
                updates += feed_updates
                idx += 1
            
            #reversed so updates display from latest to earliest, since they are appended earliest to latest
            for item in reversed(updates): 
                embed = discord.Embed()
                embed.colour = discord.Colour.green()
                embed.title = item['title']
                embed.url = item['link']
                
                page = request.urlopen(item['link']).read()
                soup = BeautifulSoup(page,"html.parser")
                image_url = soup.find("meta", property="og:image")['content']
                embed.set_image(url=image_url)
                
                #ugly, but want a nicer "human readable" date
                formatted_date = epoch2date(date2epoch(item['published']))
                embed.add_field(name="Date Published",value=formatted_date,inline=False)
                embed.add_field(name="Summary",value=item['summary'],inline=False)
                
                print("RSS: Sending update to channel :D!")
                await self.bot.send_message(post_channel, embed=embed,content="")
                
            await asyncio.sleep(rss_delay)
            
#---------------------------------------------------------------------------------------------# 
def setup(bot):
    #check_filesystem()
    rss_obj = RSSFeed(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(rss_obj._rss())
    bot.add_cog(rss_obj)

#---------------------------------------------------------------------------------------------#
