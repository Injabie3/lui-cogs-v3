#!/usr/bin/env python3.5
"""Custom format converter for Highlight
This converts data from the Highlights cog before this commit hash:
1b4c3e258280a665be86ce3b6271742d1327b460

Usage:
------
Copy old data into the same directory as this script.  This includes words.json.

Outputs:
--------
Saves a converted json file in the same directory with the filename newFormat.json.
Original data remains untouched.
"""
import json

KEY_GUILDS = "guilds"
BASE = \
{KEY_GUILDS: {}}

newFormatJson = BASE

with open("words.json") as words:
    print("Converting words.json...")
    words = json.load(words)
    for guildDicts in words["guilds"]:
        for guildId, data in guildDicts.items():
            newFormatJson[KEY_GUILDS][guildId] = {}
            for user in data["users"]:
                userId = user["id"]
                words = user["words"]
                newFormatJson[KEY_GUILDS][guildId][userId] = {}
                newFormatJson[KEY_GUILDS][guildId][userId]["words"] = words
with open("newFormat.json", "w") as output:
    json.dump(newFormatJson, output, indent=4)
    print("Highlights data converted to new format!")
