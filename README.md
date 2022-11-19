# lui-cogs-v3
Custom cogs for Red-DiscordBot v3, used by the SFU Anime Club.

## Red-DiscordBot v3.5.x / discord.py v2.x Notes
We are aware of the move towards discord.py v2.x. This will introduce breaking
changes to our cogs, and as such, we have been migrating them over in the `dpy2`
branch.

This task is being tracked in [Injabie3/lui-cogs-v3#3][1]. Should you be using a cog
that hasn't been migrated yet, please leave a comment there and we will do our best
to expedite the changes. Otherwise, you are welcome to open a PR.

[1]: https://github.com/Injabie3/lui-cogs-v3/issues/3

## Cogs
Below are some of the cogs we have. 

### Ready
- `birthday`: Ping a guild member on their birthday, and assign a special role to
   them.
- `goodsmileinfo`: Post updates from Good Smile Company to a guild text channel.
- `highlight`: Get notified outside of at-mentions about words that you care about.
- `heartbeat`: Ping an uptime checker to report that all is well with the bot.
- `qrchecker`: Scan image attachments for QR codes, and post their contents.
- `respects`: Press f to pay respects. Has the ability to group multiple `f`s into
  one message, and supports replies.
- `roleassigner`: Randomly assign roles to guild members from a pool of roles. Can
  also remove roles from guild members from a pool of roles. 
- `servermanage`: A cog to manage a server's icon and banner images. It can schedule
  icon and banner changes on certain days at midnight.
- `sfu`: Access publicly available information from Simon Fraser University,
  including campus webcams, course information, and road report.
- `spoilers`: A v3 port of our legacy v2 emoji-based spoiler cog, before Discord
  implemented spoilers natively in the client.
- `tags`: A v3 port of tags from Rapptz's RoboDanny bot, with additional functions
  such as limiting the number of tags per role, ability to transfer ownership of
  tags. Generic tags are disabled.
- `triggered`: A triggered GIF image creator.
- `welcome`: Welcome a new guild member with a custom message in a guild text
  channel. Also has the ability to send them a DM with a custom message, and logging
  member names and IDs when they join and leave a guild to a particular text channel.
- `wordfilter`: Regular expression-based filtering, with the ability to turn it off
  in exceptional cases such as moderators or above, or in certain channels. Includes
  hooks for other cogs to use.
- `yourlsClient`: Control your YOURLS instance from Discord! Configurable on a per
  guild basis.

### Experimental
- `afterhours`: An SFU Anime Discord-specific cog used to add special exceptions. It
  is used in tandem with the `tempchannels` cog. Its usage is limited outside the
  scope of this guild.
- `avatar`: Save avatar images of all users when they change, which is useful for
  making videos for the server. Requires backend console access.
- `catgirl`: A v3 port of my previous catgirl cog on v2. Needs refactoring. Adding
  new images requires backend console access.
- `rss`: An RSS feed poster. Requires backend console access.
- `smartreact`: A v3 port of smartreact from flapjax/FlapJack-Cogs. There is probably
  a v3 port from the original author.
- `stats`: WIP.
- `tempchannels`: Create 1 temporary channel that is automatically deleted after the
  configured duration expires.

## Important Notes
1. `tags`
    - Using the alias toggle requires modification to Red's Alias cog.
2. `yourlsClient`
    - The `edit` and `rename` commands requires the [yourls-api-edit-url][api-edit]
      plugin to be installed on your YOURLS instance.
    - The `delete` command requires the [yourls-api-delete][api-delete] plugin to be
      installed on your YOURLS instance.
    - The `search` keyword requires the [yourls-api-search-keywords][api-search]
      plugin to be installed on your YOURLS instance.

## Installation
This assumes that you have a functioning deployment of Red-DiscordBot v3, and that
your prefix is `ren` (replace with your bot's prefix).

1. Make sure the Downloader cog is loaded:
   `renload downloader`
2. Add the repo to your instance:
   `renrepo add lui-cogs https://github.com/Injabie3/lui-cogs-v3`
3. Install the cog you want:
   `rencog install lui-cogs <cogName>`
4. Load the newly installed cog:
   `renload <cogName>`

## Support
As this is a side project, I am not able to provide support in a particularly timely
manner. That being said, if you find any issues, please feel free to open an issue in
the [SFUAnime/Ren][SFUAnime/Ren] repo, and we can take a look into it.

[SFUAnime/Ren]: https://github.com/SFUAnime/Ren
[api-edit]: https://github.com/SFUAnime/yourls-api-edit-url
[api-delete]: https://github.com/SFUAnime/yourls-api-delete
[api-search]: https://github.com/SFUAnime/yourls-api-search-keywords
