import discord
from discord.ext import commands
import asyncio
from data.data_handler import data_handler

class ModuleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.modules = ["bounty", "achievements"]

    @commands.group(name="server", aliases=["s"])
    async def server(self, ctx):
        if ctx.invoked_subcommand is not None:
            return

        servers = data_handler.load("servers")

        try:
            server = servers[str(ctx.guild.id)]
        except KeyError:
            servers[str(ctx.guild.id)] = {
                "modules": {
                    "bounty": False,
                    "achievements": False
                },
                "prefix": "&&"
            }
            data_handler.dump(servers, "servers")
            server = servers[str(ctx.guild.id)]


        embed = discord.Embed(title = ctx.guild.name,
        description = f"Server Prefix: `{server['prefix']}`",
        colour = ctx.guild.owner.colour)

        module_settings = ""
        # Achievements
        if server["modules"]["achievements"] == True:
            module_settings = "<:Yes:749999875130654750> Achievements"
        elif server["modules"]["achievements"] == False:
            module_settings = "<:No:749999875013345362> Achievements"
        else:
            module_settings = "<:Maybe:749999875147432066> Achievements"
        # Bounty
        if server["modules"]["bounty"] == True:
            module_settings += "\n<:Yes:749999875130654750> Bounty"
        elif server["modules"]["bounty"] == False:
            module_settings += "\n<:No:749999875013345362> Bounty"
        else:
            module_settings += "\n<:Maybe:749999875147432066> Bounty"
        

        embed.add_field(name="Modules",
        value = module_settings)

        embed.set_thumbnail(url = ctx.guild.icon_url_as(static_format="png"))

        await ctx.send(embed=embed)

    #Change/view the prefix
    @server.command(name='prefix')
    async def set_prefix(self,ctx,newPrefix=None):
        prefixData = data_handler.load("servers")
        try:
            prefix = prefixData[f'{ctx.guild.id}']['prefix']
        except KeyError:
            prefix = '&&'
        if newPrefix == None:
            await ctx.send(f"Your current prefix is `{prefix}`.")
            return
        prefixData[f'{ctx.guild.id}']['prefix'] = newPrefix
        await ctx.send(f"Your new prefix is `{newPrefix}`")
        data_handler.dump(prefixData, "servers")

    @server.command(name="enable")
    async def enableModule(self, ctx, module:str = None):
        if module is None:
            await ctx.send("Please include a module name to enable. https://Greenfoot5.github.io/Endeavour-wiki/Bot_Settings")
            return

        module = module.lower()

        if module not in self.modules:
            await ctx.send("Please include a valid module name to enable. https://Greenfoot5.github.io/Endeavour-wiki/Bot_Settings")

        servers = data_handler.load("servers")

        try:
            server = servers[str(ctx.guild.id)]
        except KeyError:
            servers[str(ctx.guild.id)] = {
                "modules": {
                    "bounty": False,
                    "achievements": False
                },
                "prefix": "&&"
            }
            data_handler.dump(servers, "servers")
            server = servers[str(ctx.guild.id)]

        server["modules"][module] = True
        servers[set(ctx.guild.id)] = server
        data_handler.dump(servers, "servers")

        await ctx.send(f"`{module}` has been enabled.`")

    @server.command(name="disable")
    async def disableModule(self, ctx, module:str = None):
        if module is None:
            await ctx.send("Please include a module name to enable. https://Greenfoot5.github.io/Endeavour-wiki/Bot_Settings")
            return

        module = module.lower()
        
        if module not in self.modules:
            await ctx.send("Please include a valid module name to enable. https://Greenfoot5.github.io/Endeavour-wiki/Bot_Settings")

        servers = data_handler.load("servers")

        try:
            server = servers[str(ctx.guild.id)]
        except KeyError:
            servers[str(ctx.guild.id)] = {
                "modules": {
                    "bounty": False,
                    "achievements": False
                },
                "prefix": "&&"
            }
            data_handler.dump(servers, "servers")
            server = servers[str(ctx.guild.id)]

        server["modules"][module] = False
        servers[set(ctx.guild.id)] = server
        data_handler.dump(servers, "servers")

        await ctx.send(f"`{module}` has been disabled.`")

    

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(ModuleManager(bot))