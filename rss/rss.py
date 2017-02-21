import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import aiohttp #probably dont need
import requests
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
# TODO: finish check_filesystem() impl and run it in the setup() method
# TODO: switch to time based feed updates instead of content based feed updates
"""
Time Based feed update alogrithm:
- grab items from feed,
- from those items, determine the most recent datetime
- store that in a JSON file as the marker.
- next time it runs, grab items from feed, if any of items are published later than the marker datetime, send them out to channel
- update the marker with the newest most recent datetime if applicable
"""
def date2epoch(date):
    epoch = datetime.strptime(date,'%a, %d %b %Y %H:%M:%S %z').timestamp()
    return epoch

def epoch2date(epoch):
    date = datetime.fromtimestamp(epoch).strftime('%a, %d %b %Y %I:%M%p')
    return date
    
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
                
class RSSFeed(object):
    def __init__(self, bot):
        self.settings = dataIO.load_json("data/rss/config.json")
        self.bot = bot
        self.rss_feed = self.settings['rss_feed_url']
        self.channel_id = self.settings['post_channel']
        #self.rss_feed_urls = self.settings['rss_feed_urls']
        
    def _is_new_item(self,id,feeds):
        is_new = True
        for item in feeds['feed_ids']:
            if id == item['id']:
                is_new = False
        return is_new
    
    # searching for time based feed updates instead of content based feed updates
    def _is_new_item_test(self,latest_post_time,item_post_time):
        return latest_post_time < item_post_time
    
    def _get_latest_post_time(self,feed_items):
        published_times = []
        for item in feed_items:
            published_times.append(date2epoch(item['published']))
        return max(published_times)
            
    def _get_xml(self,rss_url):
        return requests.get(rss_url).text

    def _get_feed(self,rss_url,channel,index=None): #(self,rss_url,index,channel) for when supporting multiple feeds
        """ COMMENT """
        
        if channel is None:
            print("RSS Cog: Can't find channel, Bot is not yet logged in.")
            return []
        
        
        feeds = dataIO.load_json("data/rss/feeds.json")
        feeds_test = dataIO.load_json("data/rss/feeds-test.json")
        
        #ensure every rss url has a specified id and most recent post epoch
        """
        try
            latest_post_time = feeds_test['feeds'][index]['latest_post_time']
        except IndexError:
            dict = {}
            dict['id'] = index
            dict['latest_post_time'] = 0
            feeds_test['feeds'].append(dict)
            dataIO.save_json("data/rss/feeds-test.json",feeds_test)
            feeds_test = dataIO.load_json("data/rss/feeds-test.json")
            latest_post_time = feeds_test['feeds'][index]['latest_post_time']
        """

        latest_post_time = feeds_test['feeds'][0]['latest_post_time'] #delete this when switching to multip rss urls
        news = []
        feed = feedparser.parse(rss_url)
        
        #testing
        xml_res = self._get_xml(rss_url)
        feedie = feedparser.parse(xml_res)
        dataIO.save_json("data/rss/feedie-test.json",feedie['items'])
        
        dataIO.save_json("data/rss/feeds-all.json",feed['items']) #does nothing important, will remove soon
        
        for item in feed['items']:
            if self._is_new_item(item['id'],feeds):
                
                entry = {'id': item['id']}
                feeds['feed_ids'].append(entry)
                dataIO.save_json("data/rss/feeds.json",feeds)
                """
                dict = {}
                dict['title'] = item['title']
                dict['link'] = item['link']
                dict['published'] = item['published']
                dict['summary'] = item['summary']
                news.append(dict)
                """
            
            item_post_time = date2epoch(item['published'])
            if self._is_new_item_test(latest_post_time,item_post_time):
                
                dict = {}
                dict['title'] = item['title']
                dict['link'] = item['link']
                dict['published'] = item['published']
                dict['summary'] = item['summary']
                news.append(dict)
                
                print("new item in feed...")
        if len(news) == 0:
            print("no new items in feed...")
        print("----------------")
        latest_post_time = self._get_latest_post_time(feed['items'])
        feeds_test['feeds'][0]['latest_post_time'] = latest_post_time #feeds_test['feeds'][index]['latest_post_time']
        dataIO.save_json("data/rss/feeds-test.json",feeds_test)
        
        return news
        
    async def _rss(self):
        """ Checks for rss updates periodically and posts any new content to the specific channel"""
        rss_delay = 30
        
        print("RSS Cog: Scanning RSS Feed(s)")
        
        while self == self.bot.get_cog("RSSFeed"):
            post_channel = self.bot.get_channel(self.channel_id)
            updates = self._get_feed(self.rss_feed,post_channel)
            
            #code for multiple feed support
            """
            updates = []
            idx = 0
            for feed_url in self.rss_feed_urls:
                feed_updates = self._get_feed(feed_url,post_channel,index=idx)
                updates += feed_updates
                idx += 1
            """
            
            for item in reversed(updates): #reversed so updates display from latest to earliest, since they are appended earliest to latest
                embed = discord.Embed()
                embed.colour = discord.Colour.green()
                embed.title = item['title']
                embed.url = item['link']
                
                page = request.urlopen(item['link']).read()
                soup = BeautifulSoup(page,"html.parser")
                image_url = soup.find("meta", property="og:image")['content']
                embed.set_image(url=image_url)
                
                formatted_date = epoch2date(date2epoch(item['published'])) #ugly, but want a nicer "human readable" date
                embed.add_field(name="Date Published",value=formatted_date,inline=False)
                embed.add_field(name="Summary",value=item['summary'],inline=False)
                
                await self.bot.send_message(post_channel, embed=embed,content="")
                
            await asyncio.sleep(rss_delay)
        
def setup(bot):
    #check_filesystem()
    rss_obj = RSSFeed(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(rss_obj._rss())
    bot.add_cog(rss_obj)

    