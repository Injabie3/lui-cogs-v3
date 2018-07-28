import discord
from discord.ext import commands
from __main__ import send_cmd_help
import asyncio
import os # Used to create folder path.
from .utils import config, checks, formats 
import itertools

saveFolder = "data/lui-cogs/roleAssigner"

def checkFolder():
    """Used to create the data folder at first startup"""
    if not os.path.exists( saveFolder ):
        print( "Creating {} folder...".format( saveFolder ) )
        os.makedirs( saveFolder )

class RoleAssigner:
    """Randomly assign roles to users."""
 
    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config( "settings.json",
                                     cogname="lui-cogs/roleAssigner" )
        self.roles = self.config.get( "roles" )

    @checks.mod_or_permissions( manage_messages=True )
    @commands.group( name="roleassigner", aliases=[ "ra" ], pass_context=True,
                     no_pm=True )
    async def _roleAssigner( self, ctx ):
        """Role assigner, one role per user from a list of roles."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help( ctx )

    @_roleAssigner.command( name="add", pass_context=True )
    async def _rA_add( self, context, roleName : discord.Role ):
        """Add a role to be randomly assigned."""
        
        if not self.roles:
            roles = []
        elif roleName.id in self.roles:
            await self.bot.say( ":warning: **Role Assigner - Add:** The role "
                                "already exists in the list!" )
            return
        self.roles.append( roleName.id )

        await self.config.put( "roles", self.roles )
        await self.bot.say( ":white_check_mark: **Role Assigner - Add:** Role "
                            "added" )

    @_roleAssigner.command( name="remove", pass_context=True,
                            aliases=[ "del", "rm" ] )
    async def _rA_remove( self, context, roleName : discord.Role ):
        """Remove a role to be randomly assigned."""
        if not self.roles:
            await self.bot.say( ":warning: **Role Assigner - Remove:** There are "
                                "no roles on the list.  Please add one first!" )
            return
        elif roleName.id not in self.roles:
            await self.bot.say( ":warning: **Role Assigner - Remove:** The role "
                                "doesn't exist on the list!" )
            return

        self.roles.remove( roleName.id )
        await self.config.put( "roles", self.roles )
        await self.bot.say( ":white_check_mark: **Role Assigner - Remove:** "
                            "Role removed." )
        


    @_roleAssigner.command( name="list", pass_context=True )
    async def _rA_list( self, ctx ):
        """List roles for random assignment.""" 
        msg = ":information_source: **Role Assigner - List:** One of the " \
              "following roles will be assigned to each user:\n"
        if not self.roles:
            await self.bot.say( ":warning: **Role Assigner - List:** No roles "
                                "added!" )
            return
        msg += "```\n"
        for roleId in self.roles:
            roleName = discord.utils.get( ctx.message.server.roles, id=roleId )
            msg += "{}\n".format( roleName )
        msg += "```"
        await self.bot.say( msg )

    @_roleAssigner.command( name="assign", pass_context=True )
    async def _rA_assign( self, ctx, role : discord.Role=None ):
        """
        Randomly assign roles to users.
        Optionally apply to a subset of users with a certain role.
        """
        users = ctx.message.server.members
        if role:
            users = [ user for user in users if role in user.roles ]
        numberOfRoles = len( self.roles )

        msgId = await self.bot.say( ":hourglass: **Role Assigner - Assign:** "
                                    "Assigning roles, please wait..." )

        roles = []
        roleList = ctx.message.server.roles
        for roleId in self.roles:
            roleObject = discord.utils.get( roleList, id=roleId )
            roles.append( roleObject )

        for index, user in enumerate( users ):
            await self.bot.add_roles( user, roles[ index % numberOfRoles ] )
        msg = ":white_check_mark: **Role Assigner - Assign:** Roles assigned"
        if role:
            msg += " to users with the {} role.".format( role.name )
        else:
            msg += "."
        await self.bot.edit_message( msgId, msg )
    
    @_roleAssigner.command( name="unassign", pass_context=True )
    async def _rA_unassign( self, ctx, role : discord.Role=None ):
        """Remove roles on the list from ALL users"""
        users = ctx.message.server.members
        if role:
            users = [ user for user in users if role in user.roles ]

        msgId = await self.bot.say( ":hourglass: **Role Assigner - Unassign:** "
                                    "Unassigning roles, please wait..." )

        roles = []
        roleList = ctx.message.server.roles
        for roleId in self.roles:
            roleObject = discord.utils.get( roleList, id=roleId )
            roles.append( roleObject )

        for userObject, roleObject in itertools.product( users, roles ):
            if roleObject in userObject.roles:
                await self.bot.remove_roles( userObject, roleObject )
        msg = ":white_check_mark: **Role Assigner - Unassign:** Roles removed"
        if role:
            msg += " from users with the {} role.".format( role.name )
        else:
            msg += "."
        await self.bot.edit_message( msgId, msg )

def setup( bot ):
    checkFolder()
    bot.add_cog( RoleAssigner( bot ) )
