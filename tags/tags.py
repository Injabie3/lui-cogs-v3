# Cog from old v2 bot running async branch of discord.py
# https://github.com/Rapptz/RoboDanny/blob/master/cogs/tags.py
# Date first imported: 2017-04-10
# Ported to rewrite branch of discord.py for Red v3

from .config import Config
from .constants import *
from .data import TagAlias, TagEncoder, TagInfo
from .exceptions import *
from .helpers import checkLengthInRaw, createSimplePages, tagDecoder
from .rolecheck import roles_or_mod_or_permissions

from collections import defaultdict
from copy import deepcopy
import csv
import datetime
import difflib
import json
import logging
from threading import Lock

import asyncio
import discord
from os.path import isfile, join as pathJoin

from redbot.core import Config as ConfigV3, checks, commands, data_manager
from redbot.core.bot import Red
from redbot.core.commands.context import Context
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu


class Tags(commands.Cog):
    """The tag related commands."""

    allowed_roles = defaultdict(lambda: set([]))

    def addAllowedRole(self, guild: discord.Guild, role: discord.Role):
        self.allowed_roles[guild.id].add(str(role.id))

    def removeAllowedRole(self, guild: discord.Guild, role: discord.Role):
        self.allowed_roles[guild.id].discard(str(role.id))

    def __init__(self, bot: Red):
        self.bot = bot
        saveFolder = data_manager.cog_data_path(cog_instance=self)
        self.logger = logging.getLogger("red.luicogs.Tags")
        if not self.logger.handlers:
            logPath = pathJoin(saveFolder, "info.log")
            handler = logging.FileHandler(filename=logPath, encoding="utf-8", mode="a")
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(message)s", datefmt="[%d/%m/%Y %H:%M:%S]")
            )
            self.logger.addHandler(handler)

        # if tags.json doesnt exist, create it
        universal_path = pathJoin(str(saveFolder), "tags.json")
        if not isfile(universal_path):
            with open(universal_path, "w+") as f:
                empty = dict()
                json.dump(empty, f)

        self.config = Config(
            str(saveFolder),
            "tags.json",
            encoder=TagEncoder,
            object_hook=tagDecoder,
            loop=bot.loop,
            load_later=True,
        )
        self.configV3 = ConfigV3.get_conf(self, identifier=5842647, force_registration=True)
        self.configV3.register_guild(**BASE_GUILD)  # Register default (empty) settings.
        self.lock = Lock()
        tagGroup = self.get_commands()[0]
        self.tagCommands = tagGroup.all_commands.keys()
        self.syncLoopCreated = False
        if self.bot.guilds:
            self.bot.loop.create_task(self.syncAllowedRoles())

    @commands.Cog.listener("on_ready")
    async def initialSyncLoop(self):
        if not self.syncLoopCreated:
            self.logger.info("Synchronizing allowed roles")
            await self.syncAllowedRoles()
            self.syncLoopCreated = True

    async def syncAllowedRoles(self):
        guildIds = await self.configV3.all_guilds()
        for guildId in guildIds.keys():
            guild = discord.utils.get(self.bot.guilds, id=guildId)
            async with self.configV3.guild(guild).get_attr(KEY_TIERS)() as tiers:
                self.allowed_roles[guildId] = set(tiers.keys())
                self.logger.debug(
                    "Roles allowed to create commands on %s: %s",
                    guildId,
                    ", ".join(map(str, tiers)),
                )

    def get_database_location(self, message: discord.Message):
        """Get the database of tags.

        Parameters:
        -----------
        message: discord.Message
            The message that invoked the call.

        Returns:
        --------
        str
            The guild ID if the message was from a guild, else 'generic'
        """
        return (
            "generic" if isinstance(message.channel, discord.DMChannel) else str(message.guild.id)
        )

    def clean_tag_content(self, content):
        return content.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")

    def get_possible_tags(self, server):
        """Returns a dict of possible tags that the server can execute.
        If this is a private message then only the generic tags are possible.
        Server specific tags will override the generic tags.
        """
        generic = self.config.get("generic", {}).copy()
        if server is None:
            return generic

        generic.update(self.config.get(str(server.id), {}))
        return generic

    def get_tag(self, server, name, *, redirect=True):
        # Basically, if we're in a PM then we will use the generic tag database
        # if we aren't, we will check the server specific tag database.
        # If we don't have a server specific database, fallback to generic.
        # If it isn't found, fallback to generic.
        all_tags = self.get_possible_tags(server)
        try:
            tag = all_tags[name]
            if isinstance(tag, TagInfo):
                return tag
            elif redirect:
                return all_tags[tag.original.lower()]
            else:
                return tag
        except KeyError:
            possible_matches = difflib.get_close_matches(name, tuple(all_tags.keys()))
            if not possible_matches:
                raise RuntimeError("Tag not found.")
            raise RuntimeError("Tag not found. Did you mean...\n" + "\n".join(possible_matches))

    async def userExceedsTagLimit(self, server: discord.Guild, user: discord.Member):
        """Check to see if user has too many tags.

        This check compares against all relevant roles that the member has, and will
        take the maximum of all relevant roles.

        Parameters:
        -----------
        server: discord.Guild
            A specific server to check for too many tags
        user: discord.Member
            The user being checked for being over the limit

        Returns:
        --------
        (bool, int)
            bool: True if user has too many tags, else False.
            int: The maximum number of tags this user can have. If unlimited, then this
            will be float("inf").
        """
        if await self.bot.is_owner(user):
            # No limit for bot owner
            return (False, NO_LIMIT)

        if server:
            # No limit for mods and admins of server.
            # Methods below return role IDs.
            mod_roles = await self.bot.get_mod_roles(server)
            admin_roles = await self.bot.get_admin_roles(server)
            roles = user.roles
            if list(set(admin_roles) & set(roles)) or list(set(mod_roles) & set(roles)):
                return (False, NO_LIMIT)

        tags = [
            tag.name
            for tag in self.config.get("generic", {}).values()
            if tag.owner_id == str(user.id)
        ]
        if server:
            tags.extend(
                tag.name
                for tag in self.config.get(str(server.id), {}).values()
                if tag.owner_id == str(user.id)
            )
        tiers = await self.configV3.guild(server).get_attr(KEY_TIERS)()
        # Convert role IDs to string since keys are stored as strings.
        roleIds = [str(r.id) for r in user.roles]
        relevantTiers = list(set(tiers.keys()) & set(roleIds))
        if not relevantTiers:
            return (True, 0)
        limit = max([tiers[key] for key in relevantTiers])
        if len(tags) >= limit:
            return (True, limit)
        return (False, limit)

    async def checkAliasCog(self, ctx: Context, name: str = None):
        aliasCog = None
        if await self.configV3.guild(ctx.guild).get_attr(KEY_USE_ALIAS)():
            aliasCog = self.bot.get_cog("Alias")
            if not aliasCog:
                raise RuntimeError("Could not access the Alias cog. Please load it and try again.")
            elif name and aliasCog.is_command(name):
                raise RuntimeError(
                    "This name cannot be used because there is already an internal command with this name."
                )
        return aliasCog

    def checkValidCommandName(self, name: str):
        """Check to see if we can use the name as a tag"""
        if name in self.tagCommands:
            raise ReservedTagNameError("This tag name is reserved, please use a different name!")
        if any(char.isspace() for char in name):
            raise SpaceInTagNameError(
                "There is a space in the tag name, please use a different name!"
            )

    async def canModifyTag(self, tag, member: discord.Member, guild: discord.Guild):
        """Check to see if a user can modify a given tag.

        A user can modify a tag if:
        - They were the original creator.
        - The user is a server admin.
        - The user is a server moderator.
        - The user is a bot owner.

        Parameters
        ----------
        tag:
            The tag that we wish to modify.
        member: discord.Member
            The member that wishes to modify a tag.
        guild: discord.Guild
            The guild this tag is from.

        Returns
        -------
        bool:
            True if the user can modify the tag, else False.
        """
        mod_roles = await self.bot.get_mod_roles(guild)
        admin_roles = await self.bot.get_admin_roles(guild)

        # Check and see if the user requesting the transfer is not the tag owner, or
        # is not a mod, or is not an admin.
        if (
            tag.owner_id != str(member.id)
            and not list(set(admin_roles) & set(member.roles))
            and not list(set(mod_roles) & set(member.roles))
            and not await self.bot.is_owner(member)
        ):
            return False
        return True

    @commands.group(name="tag", invoke_without_command=True)
    @commands.guild_only()
    async def tag(self, ctx: Context, *, name: str):
        """Allows you to tag text for later retrieval.
        If a subcommand is not called, then this will search the tag database
        for the tag requested.
        """
        lookup = name.lower()
        server = ctx.message.guild
        try:
            tag = self.get_tag(server, lookup)
        except RuntimeError as e:
            return await ctx.send(e)

        tag.uses += 1
        await ctx.send(tag)

        # update the database with the new tag reference
        db = self.config.get(tag.location)
        await self.config.put(tag.location, db)

    @tag.error
    async def tag_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to pass in a tag name.")
            await ctx.send_help()
        else:
            raise error

    def verify_lookup(self, lookup):
        if "@everyone" in lookup or "@here" in lookup:
            raise RuntimeError("That tag is using blocked words.")

        if not lookup:
            raise RuntimeError("You need to actually pass in a tag name.")

        if len(lookup) > 100:
            raise RuntimeError("Tag name is a maximum of 100 characters.")

    @tag.group("settings")
    @commands.guild_only()
    @checks.mod_or_permissions()
    async def settings(self, ctx: Context):
        """Tag settings."""

    @settings.command(name="max")
    async def max(self, ctx: Context, role: discord.Role, num_tags: int):
        """Set the max number of tags per member per role.

        For each member of the specified role, each member will have a maximum
        number of tags they can create. If the member is part of more than one
        role, then they will take the MAXIMUM number from the roles that they
        have.

        This limit does not apply to admins or mods.

        Parameters:
        -----------
        role: discord.Role
            The role to set a maximum for.
        num_tags: int
            The maximum number of tags per member for that role.
            If 0, then the tier is removed.
        """
        if num_tags < 0:
            await ctx.send("Please set a value greater than 0.")
            return

        async with self.configV3.guild(ctx.guild).get_attr(KEY_TIERS)() as tiers:
            if num_tags == 0:
                if str(role.id) in tiers.keys():
                    del tiers[str(role.id)]
                    self.removeAllowedRole(ctx.guild, role)
                await ctx.send(f"{role.name} will not be allowed to add tags")
            else:
                tiers[role.id] = num_tags
                self.addAllowedRole(ctx.guild, role)
                await ctx.send(f"The tag limit for {role.name} was set to {num_tags}.")

    @settings.command(name="tiers")
    async def tiers(self, ctx: Context):
        """Show the tiers and their respective max tags."""
        tiers = await self.configV3.guild(ctx.guild).get_attr(KEY_TIERS)()
        validTiers = []
        msg = ""
        for roleId, maxTags in tiers.items():
            role = discord.utils.get(ctx.guild.roles, id=int(roleId))
            if not role:
                continue
            validTiers.append((role, maxTags))
        if validTiers:
            msgList = ["Below is a list of roles and their tag limits:"]
            validTiers.sort(key=lambda x: x[1])
            for role, maxTags in validTiers:
                msgList.append(f"{role.name}: {maxTags}")
            msg = "\n".join(msgList)
        else:
            msg = "There are no tiers configured."
        await ctx.send(msg)

    @settings.command(name="dump")
    async def dump(self, ctx: Context):
        """Dumps server-specific tags to a CSV file, sorted by number of uses."""
        sid = str(ctx.guild.id)
        with self.lock:
            with open(DUMP_IN, "r") as inputFile, open(DUMP_OUT, "w") as outputFile:
                tags = json.load(inputFile)
                if sid not in tags.keys():
                    await ctx.send("There are no tags on this server!")

                csvWriter = csv.writer(outputFile)
                headerCreated = False

                # Convert to list, and sort by ascending number of uses.
                tags = [contents for contents in tags[sid].values()]
                tags = sorted(tags, key=lambda k: k["uses"])

                # We only care about server tags
                for tag in tags:
                    tag["created_at"] = datetime.datetime.fromtimestamp(tag["created_at"])

                    if not headerCreated:
                        header = list(tag.keys()) + ["owner_name"]
                        csvWriter.writerow(header)
                        headerCreated = True

                    owner = discord.utils.get(ctx.guild.members, id=tag["owner_id"])
                    if not owner:
                        owner = "Unknown"
                    else:
                        owner = owner.name

                    data = list(tag.values()) + [owner]
                    csvWriter.writerow(data)

            await ctx.send(file=discord.File(DUMP_OUT))

    @tag.command(name="add", aliases=["create"])
    @commands.guild_only()
    @roles_or_mod_or_permissions(allowed_roles=allowed_roles, manage_messages=True)
    async def create(self, ctx: Context, name: str, *, content: str):
        """Creates a new tag owned by you.
        If you create a tag via private message then the tag is a generic
        tag that can be accessed in all servers. Otherwise the tag you
        create can only be accessed in the server that it was created in.
        """
        try:
            aliasCog = await self.checkAliasCog(ctx, name)
            self.checkValidCommandName(name)
        except RuntimeError as error:
            return await ctx.send(error)

        exceedsLimit, limit = await self.userExceedsTagLimit(ctx.guild, ctx.author)
        if exceedsLimit:
            await ctx.send(
                "You have too many commands. The maximum number of commands "
                f"you can create is {limit}, please delete some first!"
            )
            return

        content = self.clean_tag_content(content)

        if not checkLengthInRaw(content):
            await ctx.send("Your content is too long. Consider splitting it into two tags.")
            return

        lookup = name.lower().strip()
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            return await ctx.send(e)

        location = self.get_database_location(ctx.message)
        db = self.config.get(location, {})
        if lookup in db:
            await ctx.send('A tag with the name of "{}" already exists.'.format(name))
            return

        db[lookup] = TagInfo(
            name,
            content,
            str(ctx.message.author.id),
            location=location,
            created_at=datetime.datetime.utcnow().timestamp(),
        )

        await self.config.put(location, db)
        await ctx.send('Tag "{}" successfully created.'.format(name))

        if await self.configV3.guild(ctx.guild).get_attr(KEY_USE_ALIAS)():
            # Alias is already loaded.
            await aliasCog.add_alias(ctx, lookup, "tag {}".format(lookup))

    @create.error
    async def create_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Tag " + str(error))
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.UnexpectedQuoteError):
            await ctx.send("Please do not use quotes in the tag name!")
        else:
            await ctx.send(
                "Something went wrong, please try again or contact the bot owner(s) "
                "if this continues."
            )
            raise error

    @tag.command(name="generic")
    @checks.mod_or_permissions(administrator=True)
    async def generic(self, ctx: Context, name: str, *, content: str):
        """Creates a new generic tag owned by you.
        Unlike the create tag subcommand,  this will always attempt to create
        a generic tag and not a server-specific one.
        """
        content = self.clean_tag_content(content)

        if not checkLengthInRaw(content):
            await ctx.send("Your content is too long. Consider splitting it into two tags.")
            return

        lookup = name.lower().strip()
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            await ctx.send(str(e))
            return

        db = self.config.get("generic", {})
        if lookup in db:
            await ctx.send('A tag with the name of "{}" already exists.'.format(name))
            return

        db[lookup] = TagInfo(
            name,
            content,
            str(ctx.author.id),
            location="generic",
            created_at=datetime.datetime.utcnow().timestamp(),
        )
        await self.config.put("generic", db)
        await ctx.send('Tag "{}" successfully created.'.format(name))

        # aliasCog = self.bot.get_cog('Alias')
        # await aliasCog.add_alias(ctx.message.server, name, "tag {}".format(name))

    @generic.error
    async def generic_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Tag " + str(error))
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.UnexpectedQuoteError):
            await ctx.send("Please do not use quotes in the tag name!")
        else:
            await ctx.send(
                "Something went wrong, please try again or contact the bot owner(s) "
                "if this continues."
            )
            raise error

    @tag.command(name="alias")
    @commands.guild_only()
    @checks.mod_or_permissions(administrator=True)
    async def alias(self, ctx: Context, new_name: str, *, old_name: str):
        """Creates an alias for a pre-existing tag.
        You own the tag alias. However, when the original
        tag is deleted the alias is deleted as well.
        Tag aliases cannot be edited. You must delete
        the alias and remake it to point it to another
        location.
        You cannot have generic aliases.
        """

        message = ctx.message
        server = ctx.guild
        lookup = new_name.lower().strip()
        old = old_name.lower()

        tags = self.get_possible_tags(server)
        db = self.config.get(str(server.id), {})
        try:
            original = tags[old]
        except KeyError:
            return await ctx.send("Pointed to tag does not exist.")

        if isinstance(original, TagAlias):
            return await ctx.send("Cannot make an alias to an alias.")

        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            await ctx.send(e)
            return

        if lookup in db:
            await ctx.send("A tag with this name already exists.")
            return

        db[lookup] = TagAlias(
            name=new_name,
            original=old,
            owner_id=str(ctx.author.id),
            created_at=datetime.datetime.utcnow().timestamp(),
        )

        await self.config.put(str(server.id), db)
        await ctx.send(
            'Tag alias "{}" that points to "{.name}" successfully '
            "created.".format(new_name, original)
        )

    @tag.command(ignore_extra=False)
    @commands.guild_only()
    @roles_or_mod_or_permissions(allowed_roles=allowed_roles, administrator=True)
    async def make(self, ctx):
        """Interactive makes a tag for you.
        This walks you through the process of creating a tag with
        its name and its content. This works similar to the tag
        create command.
        """
        try:
            aliasCog = await self.checkAliasCog(ctx)
        except RuntimeError as error:
            return await ctx.send(error)

        exceedsLimit, limit = await self.userExceedsTagLimit(ctx.guild, ctx.author)
        if exceedsLimit:
            await ctx.send(
                "You have too many commands. The maximum number of commands "
                f"you can create is {limit}, please delete some first!"
            )
            return

        message = ctx.message
        location = self.get_database_location(message)
        db = self.config.get(location, {})

        await ctx.send("Hello. What would you like the name tag to be?")

        def check(msg: discord.Message):
            return msg.author == ctx.message.author and msg.channel == ctx.message.channel

        def name_check(msg: discord.Message):
            if not check(msg):
                return False
            # Original author and channel matches.
            try:
                self.verify_lookup(msg.content.lower())
                return True
            except:
                return False

        try:
            name = await self.bot.wait_for("message", timeout=60.0, check=name_check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long. Goodbye.")
            return

        lookup = name.content.lower()

        try:
            self.checkValidCommandName(lookup)
        except RuntimeError as error:
            await ctx.send(f"{error}")
            return

        if lookup in db:
            fmt = (
                "Sorry. A tag with that name exists already. Redo the command {0.prefix}tag make."
            )
            await ctx.send(fmt.format(ctx))
            return

        # Alias is already loaded
        if await self.configV3.guild(ctx.guild).get_attr(KEY_USE_ALIAS)() and aliasCog.is_command(
            lookup
        ):
            await ctx.send(
                "This name cannot be used because there is already "
                "an internal command with this name."
            )
            return

        await ctx.send(
            "Alright. So the name is {0.content}. What about the tag's content?".format(name)
        )
        try:
            content = await self.bot.wait_for("message", check=check, timeout=300.0)
        except asyncio.TimeoutError:
            await ctx.send("You took too long. Goodbye.")
            return

        if len(content.content) == 0 and len(content.attachments) > 0:
            # we have an attachment
            content = content.attachments[0].get("url", "*Could not get attachment data*")
        else:
            content = self.clean_tag_content(content.content)
            if not checkLengthInRaw(content):
                await ctx.send("Your content is too long. Consider splitting it into two tags.")
                return

        db[lookup] = TagInfo(
            name.content,
            content,
            name.author.id,
            location=location,
            created_at=datetime.datetime.utcnow().timestamp(),
        )
        await self.config.put(location, db)
        await ctx.send("Cool. I've made your {0.content} tag.".format(name))

        if await self.configV3.guild(ctx.guild).get_attr(KEY_USE_ALIAS)():
            # Alias is already loaded.
            await aliasCog.add_alias(ctx, lookup, "tag {}".format(lookup))

    @make.error
    async def tag_make_error(self, ctx: Context, error):
        if isinstance(error, commands.TooManyArguments):
            await ctx.send("Please call just {0.prefix}tag make".format(ctx))
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.UnexpectedQuoteError):
            await ctx.send("Please do not use quotes in the tag name!")
        else:
            await ctx.send("Something went wrong, please check the logs for details.")
            raise error

    def top_three_tags(self, db):
        emoji = 129351  # ord(':first_place:')
        popular = sorted(db.values(), key=lambda t: t.uses, reverse=True)
        for tag in popular[:3]:
            yield (chr(emoji), tag)
            emoji += 1

    @tag.command(name="stats")
    async def stats(self, ctx: Context):
        """Gives stats about the tag database."""
        server = ctx.message.guild
        generic = self.config.get("generic", {})
        e = discord.Embed()
        e.add_field(
            name="Generic",
            value="%s tags\n%s uses" % (len(generic), sum(t.uses for t in generic.values())),
        )

        total_tags = sum(len(c) for c in self.config.all().values())
        total_uses = sum(sum(t.uses for t in c.values()) for c in self.config.all().values())
        e.add_field(name="Global", value="%s tags\n%s uses" % (total_tags, total_uses))

        if server is not None:
            db = self.config.get(str(server.id), {})
            e.add_field(
                name="Server-Specific",
                value="%s tags\n%s uses" % (len(db), sum(t.uses for t in db.values())),
            )
        else:
            db = {}
            e.add_field(name="Server-Specific", value="No Info")

        fmt = "{0.name} ({0.uses} uses)"
        for emoji, tag in self.top_three_tags(generic):
            e.add_field(name=emoji + " Generic Tag", value=fmt.format(tag))

        for emoji, tag in self.top_three_tags(db):
            e.add_field(name=emoji + " Server Tag", value=fmt.format(tag))

        await ctx.send(embed=e)

    @tag.command()
    @roles_or_mod_or_permissions(allowed_roles=allowed_roles, manage_messages=True)
    async def edit(self, ctx: Context, name: str, *, content: str):
        """Modifies an existing tag that you own.
        This command completely replaces the original text. If you edit
        a tag via private message then the tag is looked up in the generic
        tag database. Otherwise it looks at the server-specific database.
        """

        content = self.clean_tag_content(content)

        if not checkLengthInRaw(content):
            await ctx.send("Your content is too long. Consider splitting it into two tags.")
            return

        lookup = name.lower()
        server = ctx.message.guild
        try:
            tag = self.get_tag(server, lookup, redirect=False)
        except RuntimeError as e:
            await ctx.send(e)
            return

        if isinstance(tag, TagAlias):
            await ctx.send("Cannot edit tag aliases. Remake it if you want to re-point it.")
            return

        if not await self.canModifyTag(tag, ctx.author, ctx.guild):
            await ctx.send("Only the tag owner can edit this tag.")
            return

        db = self.config.get(tag.location)
        tag.content = content
        await self.config.put(tag.location, db)
        await ctx.send("Tag successfully edited.")

    @tag.command(name="transfer")
    @commands.guild_only()
    @roles_or_mod_or_permissions(allowed_roles=allowed_roles, manage_messages=True)
    async def transfer(self, ctx: Context, tag_name, user: discord.Member):
        """Transfer your tag to another user.

        This can be done by the creator of the tag. Cannot transfer 
        if the user being transfered to is over the tag limit.

        Parameters:
        -----------
        tag_name: str
            The tag name.
        user: discord.Member
            The guild member you wish to transfer this tag to.
        """
        lookup = tag_name.lower().strip()
        server = ctx.message.guild
        try:
            tag = self.get_tag(server, lookup, redirect=False)
        except RuntimeError as e:
            await ctx.send(e)
            return

        if not await self.canModifyTag(tag, ctx.author, ctx.guild):
            await ctx.send("Only the tag owner can transfer this tag.")
            return

        # Check if the user to transfer to has permissions to create tags
        mod_roles = await self.bot.get_mod_roles(ctx.guild)
        admin_roles = await self.bot.get_admin_roles(ctx.guild)
        allowed_server_roles = [
            discord.utils.get(ctx.guild.roles, id=int(r))
            for r in self.allowed_roles.get(ctx.guild.id, [])
        ]

        if (
            not list(set(allowed_server_roles) & set(user.roles))
            and not list(set(admin_roles) & set(user.roles))
            and not list(set(mod_roles) & set(user.roles))
            and not await self.bot.is_owner(user)
        ):
            await ctx.send("The person you are trying to transfer to cannot create commands.")
            return

        # Check if the user to transfer to has exceeded the tag limit
        exceedsLimit, _ = await self.userExceedsTagLimit(ctx.guild, user)
        if exceedsLimit:
            await ctx.send(
                "The person you are trying to transfer a tag to is not allowed to have "
                "tags or already has too many tags!"
            )
            return

        await ctx.send(
            '{} please confirm by saying "yes" that you would like to '
            "receive this tag from {}. \nAny other message in this channel "
            "by the recipient will be treated as no.".format(
                user.mention, ctx.message.author.mention
            )
        )

        def check(msg: discord.Message):
            return msg.author == user and msg.channel == ctx.channel

        try:
            response = await self.bot.wait_for("message", check=check, timeout=15)
        except asyncio.TimeoutError:
            await ctx.send(f"No confirmation from {user.name}. Transfer has been " "cancelled.")
            return

        if response.content.lower() == "yes":
            # The user has answered yes; transfering tag
            db = self.config.get(tag.location)
            tag.owner_id = str(user.id)
            await self.config.put(tag.location, db)
            await ctx.send(
                "Tag successfully transferred from the current owner "
                "to {}.".format(user.mention)
            )
        else:
            await ctx.send(
                "Tag has been rejected by {}. Transfer has been " "cancelled.".format(user.name)
            )

    @tag.command(name="rename")
    async def rename(self, ctx: Context, oldName: str, newName: str):
        """Renames a tag.

        This is useful to help preserve tag statistics.

        Parameters
        ----------
        oldName: str
            The old tag name.
        newName: str
            The new tag name.
        """
        try:
            aliasCog = await self.checkAliasCog(ctx, newName)
            self.checkValidCommandName(newName)
        except RuntimeError as error:
            return await ctx.send(error)

        newName = newName.lower().strip()
        oldName = oldName.lower()
        try:
            self.verify_lookup(newName)
            tag = self.get_tag(ctx.guild, oldName, redirect=False)
        except RuntimeError as e:
            return await ctx.send(e)

        location = self.get_database_location(ctx.message)
        db = self.config.get(location, {})
        if newName in db:
            await ctx.send('A tag with the name of "{}" already exists.'.format(newName))
            return

        mod_roles = await self.bot.get_mod_roles(ctx.guild)
        admin_roles = await self.bot.get_admin_roles(ctx.guild)
        roles = ctx.author.roles

        # Check and see if the user is not the tag owner, or is not a mod, or is not an admin.
        if (
            tag.owner_id != str(ctx.message.author.id)
            and not list(set(admin_roles) & set(roles))
            and not list(set(mod_roles) & set(roles))
            and not await self.bot.is_owner(ctx.author)
        ):
            await ctx.send("Only the tag owner can rename this tag.")
            return

        db[newName] = deepcopy(db[oldName])
        db[newName].name = newName
        del db[oldName]

        await self.config.put(location, db)
        if await self.configV3.guild(ctx.guild).get_attr(KEY_USE_ALIAS)():
            # Alias is already loaded.
            await aliasCog.add_alias(ctx, newName, "tag {}".format(newName))
            await aliasCog.del_alias(ctx, oldName)
        await ctx.send('Tag "{}" successfully renamed to "{}".'.format(oldName, newName))

    @tag.command(name="delete", aliases=["del", "remove", "rm"])
    @roles_or_mod_or_permissions(allowed_roles=allowed_roles, manage_messages=True)
    async def remove(self, ctx: Context, *, name: str):
        """Removes a tag that you own.
        The tag owner can always delete their own tags. If someone requests
        deletion and has Manage Messages permissions or a Bot Mod role then
        they can also remove tags from the server-specific database. Generic
        tags can only be deleted by the bot owner or the tag owner.
        Deleting a tag will delete all of its aliases as well.
        """
        try:
            aliasCog = await self.checkAliasCog(ctx)
        except RuntimeError as error:
            return await ctx.send(error)

        lookup = name.lower()
        server = ctx.message.guild
        try:
            tag = self.get_tag(server, lookup, redirect=False)
        except RuntimeError as e:
            await ctx.send(e)
            return

        # Check and see if the user is not the tag owner, or is not a mod, or is not an admin.
        can_delete = await self.bot.is_owner(ctx.author)
        if not tag.is_generic:
            if list(set(await self.bot.get_mod_roles(ctx.guild)) & set(ctx.author.roles)):
                can_delete = True
            elif list(set(await self.bot.get_admin_roles(ctx.guild)) & set(ctx.author.roles)):
                can_delete = True

        can_delete = can_delete or tag.owner_id == str(ctx.message.author.id)

        if not can_delete:
            await ctx.send("You do not have permissions to delete this tag.")
            return

        if isinstance(tag, TagAlias):
            location = str(server.id)
            db = self.config.get(location)
            del db[lookup]
            msg = "Tag alias successfully removed."
        else:
            location = tag.location
            db = self.config.get(location)
            msg = "Tag and all corresponding aliases successfully removed."

            if server is not None:
                alias_db = self.config.get(str(server.id))
                aliases = [
                    key
                    for key, t in alias_db.items()
                    if isinstance(t, TagAlias) and t.original == lookup
                ]
                for alias in aliases:
                    alias_db.pop(alias, None)

            del db[lookup]

        await self.config.put(location, db)
        await ctx.send(msg)

        if await self.configV3.guild(ctx.guild).get_attr(KEY_USE_ALIAS)():
            # Alias is already loaded.
            await aliasCog.del_alias(ctx, lookup)

    @tag.command(name="info", aliases=["owner"])
    async def info(self, ctx: Context, *, name: str):
        """Retrieves info about a tag.
        The info includes things like the owner and how many times it was used.
        """

        lookup = name.lower()
        server = ctx.message.guild
        try:
            tag = self.get_tag(server, lookup, redirect=False)
        except RuntimeError as e:
            return await ctx.send(e)

        embed = await tag.embed(ctx, self.get_possible_tags(server))
        await ctx.send(embed=embed)

    @info.error
    async def info_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing tag name to get info of.")
        else:
            await ctx.send("Something went wrong, please check the logs for details.")
            raise error

    @tag.command(name="raw")
    async def raw(self, ctx: Context, *, name: str):
        """Gets the raw content of the tag.
        This is with markdown escaped. Useful for editing.
        """

        lookup = name.lower()
        server = ctx.message.guild
        try:
            tag = self.get_tag(server, lookup)
        except RuntimeError as e:
            await ctx.send(e)
            return

        await ctx.send(discord.utils.escape_markdown(tag.content))

    @tag.command(name="list")
    async def _list(self, ctx: Context, *, member: discord.Member = None):
        """Lists all the tags that belong to you or someone else.

        Parameters
        ----------
        member: discord.Member (optional)
            Another guild member that you wish to look up tags for.
        """
        owner = ctx.message.author if member is None else member
        server = ctx.message.guild
        tags = [
            tag.name
            for tag in self.config.get("generic", {}).values()
            if tag.owner_id == str(owner.id)
        ]
        if server is not None:
            tags.extend(
                tag.name
                for tag in self.config.get(str(server.id), {}).values()
                if tag.owner_id == str(owner.id)
            )

        tags.sort()

        if tags:
            pageList = await createSimplePages(items=tags, embedAuthor=owner)
            await menu(ctx, pageList, DEFAULT_CONTROLS)
        else:
            await ctx.send("{0.name} has no tags.".format(owner))

    @tag.command(name="all")
    @commands.guild_only()
    async def _all(self, ctx):
        """Lists all server-specific tags for this server."""

        tags = [tag.name for tag in self.config.get(str(ctx.message.guild.id), {}).values()]
        tags.sort()

        if tags:
            pageList = await createSimplePages(
                items=tags,
                embedTitle="All Tags",
            )
            await menu(ctx, pageList, DEFAULT_CONTROLS)
        else:
            await ctx.send("This server has no server-specific tags.")

    @tag.command(name="purge")
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    async def purge(self, ctx: Context, member: discord.Member):
        """Removes all server-specific tags by a user.
        You must have Manage Messages permissions to use this.
        """
        db = self.config.get(str(ctx.message.guild.id), {})
        tags = [key for key, tag in db.items() if tag.owner_id == str(member.id)]

        # TODO I'm pretty sure there's a decorator for the following.
        if not ctx.message.channel.permissions_for(ctx.message.guild.me).add_reactions:
            await ctx.send("Bot cannot add reactions.")
            return

        if not tags:
            await ctx.send("This user has no server-specific tags.")
            return

        msg = await ctx.send(
            "This will delete {} tags. Are you sure? **This action "
            "cannot be reversed**.\n\nReact with either "
            "\N{WHITE HEAVY CHECK MARK} to confirm or \N{CROSS MARK} "
            "to deny.".format(len(tags))
        )

        cancel = False
        author_id = ctx.message.author.id

        def check(reaction, user):
            nonlocal cancel
            if reaction.message.id != msg.id:
                return False
            if user.id != author_id:
                return False

            if reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
                return True
            elif reaction.emoji == "\N{CROSS MARK}":
                cancel = True
                return True
            return False

        for emoji in ("\N{WHITE HEAVY CHECK MARK}", "\N{CROSS MARK}"):
            await msg.add_reaction(emoji)

        try:
            # We set cancel in the check function
            await self.bot.wait_for("reaction_add", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("Cancelling")
            return

        if cancel:
            await msg.delete()
            await ctx.send("Cancelling.")
            return

        for key in tags:
            db.pop(key)

        await self.config.put(str(ctx.message.guild.id), db)
        await msg.delete()
        await ctx.send(
            "Successfully removed all {} tags that belong to {}".format(
                len(tags), member.display_name
            )
        )

    @tag.command(name="search")
    async def search(self, ctx: Context, *, query: str):
        """Searches for a tag.
        This searches both the generic and server-specific database. If it's
        a private message, then only generic tags are searched.
        The query must be at least 2 characters.
        """
        server = ctx.message.guild
        query = query.lower()
        if len(query) < 2:
            await ctx.send("The query length must be at least two characters.")
            return

        tags = self.get_possible_tags(server)
        results = [tag.name for key, tag in tags.items() if query in key]

        if results:
            try:
                pageList = await createSimplePages(
                    items=results,
                    embedTitle="Search Results",
                )
                await menu(ctx, pageList, DEFAULT_CONTROLS)
            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send("No tags found.")

    @search.error
    async def search_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing query to search for.")
        else:
            raise error

    @settings.command(name="togglealias")
    async def togglealias(self, ctx: Context):
        """Toggle creating aliases for tags."""
        if await self.configV3.guild(ctx.guild).get_attr(KEY_USE_ALIAS)():
            toAlias = False
            await ctx.send(
                "\N{WHITE HEAVY CHECK MARK} **Tags - Aliasing**: Tags will "
                "be created **without an alias**."
            )
        else:
            toAlias = True
            await ctx.send(
                "\N{WHITE HEAVY CHECK MARK} **Tags - Aliasing**: Tags will "
                "be created **with an alias**."
            )
        await self.configV3.guild(ctx.guild).get_attr(KEY_USE_ALIAS).set(toAlias)

    @tag.command(name="runtests")
    @checks.is_owner()
    async def runTests(self, ctx: Context):
        """Run tests."""
        # Test checkValidCommandName
        name = "validtagname"
        self.checkValidCommandName(name)
        name = "add"
        try:
            self.checkValidCommandName(name)
        except ReservedTagNameError:
            pass

        name = "name with space"
        try:
            self.checkValidCommandName(name)
        except SpaceInTagNameError:
            pass

        # Test rename command after creating
        await ctx.invoke(self.create, name="runTestCommandTest1", content="This is a test tag")
        location = self.get_database_location(ctx.message)
        db = self.config.get(location, {})
        assert "runTestCommandTest1".lower() in db
        await ctx.invoke(self.rename, oldName="runTestCommandTest1", newName="runTestCommandTest2")
        db = self.config.get(location, {})
        assert "runTestCommandTest1".lower() not in db
        assert "runTestCommandTest2".lower() in db

        # Test renaming to a command, this should not work.
        await ctx.invoke(self.rename, oldName="runTestCommandTest2", newName="add")
        db = self.config.get(location, {})
        assert "runTestCommandTest2".lower() in db
        assert "add".lower() not in db
        await ctx.invoke(self.remove, name="runTestCommandTest2")

        # Test renaming a non-existent command
        await ctx.invoke(self.rename, oldName="runTestCommandTest1", newName="runTestCommandTest2")
        db = self.config.get(location, {})
        assert "runTestCommandTest1".lower() not in db
        assert "runTestCommandTest2".lower() not in db

        await ctx.send("Tests passed!")
