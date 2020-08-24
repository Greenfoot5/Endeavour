import discord
from discord.ext import commands
import asyncio

# Server ids for server specific commands.
# Should be stored in a config file.
ss = {'G5': 462842304638484481, 'PPTF': 541702393549684780}

class NotInServer(commands.CheckFailure):
    pass

# If the commands are server specific, make sure they are in that server.
def i_ss(server:str):
    async def predicate(ctx):
        if ctx.guild.id == ss[server]:
            return True
        else:
            raise NotInServer("You can't do that here.")
    return commands.check(predicate)


