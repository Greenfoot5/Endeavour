import discord
from discord.ext import commands
import asyncio
import random
import sys
import math
import time
from PIL import Image, ImageFont, ImageDraw
from functools import partial
from io import BytesIO
from typing import Union
import aiohttp
from discord.ext.commands.cooldowns import BucketType
import cogs.checks as chec
from data.data_handler import data_handler

class Wanted(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def get_avatar(self, user: Union[discord.User, discord.Member]) -> bytes:
        #generally an avatar will be 1024x1024, but we shouldn't rely on this.
        avatar_url = user.avatar_url_as(format="png")
        avatar_url = str(avatar_url)
        
        async with self.session.get(avatar_url) as response:
            #this gives us our response object, and now we can read the bytes from it.
            avatar_bytes = await response.read()

        return avatar_bytes

    @staticmethod
    def processing(avatar_bytes: bytes, colour: tuple, ctx, member, xp) -> BytesIO:

        #we must use BytesIO to load the image here as PIL expects a stream instead of just raw bytes.
        with Image.open(BytesIO(avatar_bytes)) as im:

            #this creates a new image the same size as the user's avatar, with the background colour being the user's colour.
            with Image.open('media/OnePieceWantedPosters.png') as background:

                #this ensures that the user's avatar lacks an alpha channel as we're going to be submitting our own here
                rgb_avatar = im.convert("RGB")

                #Resizes the avatar
                rgb_avatar = rgb_avatar.resize(size=(339,258))

                #this is the mask image we will be using to create the circle cutout effect on the avatar
                with Image.new("L", rgb_avatar.size, 0) as mask:

                    #ImageDraw lets us draw on the image. In this instance we will be using it to draw a white circle on the mask image.
                    mask_draw = ImageDraw.Draw(mask)

                    #draw the white circle from 0, 0 to the bottom right corner of the image.
                    mask_draw.rectangle([(0,0),500,300],fill=255)

                    #paste the alpha-less avatar on the background using the new circle mask we just created.
                    background.paste(rgb_avatar, (35,125), mask=mask)

                if xp is None:

                    #this is the mask image we will be using to create the text
                    with Image.new("L", rgb_avatar.size,0) as mask:

                        #ImageDraw lets us draw on the image. In this instance we will be using it to draw text on the image
                        fontDraw = ImageDraw.Draw(mask)

                        #we get the font.
                        nameFont = ImageFont.truetype(font='media/Vanib.ttf',size=35)

                        #Make sure only 15 chars of the member's nickname is selected. If there aren't 15 chars then all are displayed without errors
                        if len(member.display_name) < 15:
                            maxLen = len(member.display_name)
                        else:
                            maxLen = 15

                        #we draw it on
                        fontDraw.multiline_text(xy=(0,0),text=f"{member.display_name[0:maxLen]}",fill=0x008800,font=nameFont,align="center",spacing=2)

                        background.paste((56, 46, 46),(45,440),mask=mask)

                    with Image.new("L", rgb_avatar.size,0) as mask:

                        #ImageDraw lets us draw on the image. In this instance we will be using it to draw text on the image
                        fontDraw = ImageDraw.Draw(mask)

                        #we get the font.
                        numberFont = ImageFont.truetype(font='media/verdanab.ttf',size=32)
                        
                        #Obtain the user's wanted score.
                        scores = data_handler.load("wanted")
                        try:
                            score = scores["wanted"][str(member.id)]
                        except KeyError:
                            score = random.randint(1, 9) * (10 ** random.randint(0, 10))
                            scores["wanted"][str(member.id)] = score
                            data_handler.dump(scores, "wanted")
                            

                        #we draw it on
                        fontDraw.multiline_text(xy=(0,0),text='{:,}'.format(score),fill=0x008800,font=numberFont,align="center",spacing=2)

                        background.paste((56, 46, 46),(70,500),mask=mask)

                else:

                    #this is the mask image we will be using to create the text
                    with Image.new("L", rgb_avatar.size,0) as mask:

                        #ImageDraw lets us draw on the image. In this instance we will be using it to draw text on the image
                        fontDraw = ImageDraw.Draw(mask)

                        #we get the font.
                        nameFont = ImageFont.truetype(font='media/Vanib.ttf',size=35)

                        #Make sure only 15 chars of the member's nickname is selected. If there aren't 15 chars then all are displayed without errors
                        if len(member.display_name) < 15:
                            maxLen = len(member.display_name)
                        else:
                            maxLen = 15

                        #we draw it on
                        fontDraw.multiline_text(xy=(0,0),text=f"{member.display_name[0:maxLen]}",fill=0x008800,font=nameFont,align="center",spacing=2)

                        background.paste((56, 46, 46),(45,440),mask=mask)

                    with Image.new("L", rgb_avatar.size,0) as mask:

                        #ImageDraw lets us draw on the image. In this instance we will be using it to draw text on the image
                        fontDraw = ImageDraw.Draw(mask)

                        #we get the font.
                        numberFont = ImageFont.truetype(font='media/verdanab.ttf',size=32)
                        
                        #We get the suffix
                        XPList = data_handler.load("wanted")
                        try:
                            suffix = XPList[str(ctx.guild.id)]["suffix"]
                        except:
                            suffix = 3
                        value = xp * (10 ** suffix)
                        
                        #we draw it on
                        fontDraw.multiline_text(xy=(0,0),text='{:,}'.format(value),fill=0x008800,font=numberFont,align="center",spacing=2)

                        background.paste((56, 46, 46),(70,500),mask=mask)

                #prepare the stream to save this image into
                final_buffer = BytesIO()

                #save into the stream, using png format.
                background.save(final_buffer, "png")

            #seek back to the start of the stream
            final_buffer.seek(0)

            return final_buffer

    @commands.command(name='wanted')
    async def Wanted(self,ctx,*,member:discord.Member = None):
        member = member or ctx.author
        async with ctx.typing():
            #this means that the bot will type while it is processing and uploading the image

            if isinstance(member, discord.Member):
                #get the user's colour, pretty self explanatory
                member_colour = member.colour.to_rgb()
            else:
                #if this is in a DM or something went seriously wrong
                member_colour = (0,0,0)

            #grab theuser's avatar as bytes
            avatar_bytes = await self.get_avatar(member)

            #create partial function so we don't have to stack the args in run_in_executor
            fn = partial(self.processing,avatar_bytes,member_colour,ctx,member,None)

            #this runs our processing in an executor, stopping it from blocking the thread loop as we already seeked back the buffer in the other thread.
            final_buffer = await self.bot.loop.run_in_executor(None,fn)

            #prepares the file
            file = discord.File(filename="wanted.png", fp=final_buffer)

            #send it
            await ctx.send(file=file)

    @commands.group(name='bounty',aliases=['reward','worth','value'])
    async def bounty(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("You haven't sent a bounty subcommand. Subcommands are: `check` and `rank`.")

    @bounty.command(name='check')
    async def BCheck(self, ctx, *, member:discord.Member = None):
        """Display the user's avatar on their colour"""

        #this means that if the user does not supply a member, it will default to the author of the message.
        member = member or ctx.author

        servers = data_handler.load('servers')
        
        # Check the server has wanted enabled.
        try:
            if servers[str(ctx.guild.id)]['modules']["bounty"] == False:
                await ctx.send("Bounty not enabled.")
                return
        except KeyError:
            await ctx.send("Bounty not enabled.")
            return

        XPList = data_handler.load("wanted")
            
        try:
            MemberXP = XPList[str(ctx.guild.id)]["members"][str(member.id)]['xp']
        except:
            MemberXP = 0
            
        async with ctx.typing():
            #this means that the bot will type while it is processing and uploading the image

            if isinstance(member, discord.Member):
                #get the user's colour, pretty self explanatory
                member_colour = member.colour.to_rgb()
            else:
                #if this is in a DM or something went seriously wrong
                member_colour = (0,0,0)

            #grab theuser's avatar as bytes
            avatar_bytes = await self.get_avatar(member)

            #create partial function so we don't have to stack the args in run_in_executor
            fn = partial(self.processing,avatar_bytes,member_colour,ctx,member,MemberXP)

            #this runs our processing in an executor, stopping it from blocking the thread loop as we already seeked back the buffer in the other thread.
            final_buffer = await self.bot.loop.run_in_executor(None,fn)

            #prepares the file
            file = discord.File(filename="wanted.png", fp=final_buffer)
            
            rankings = []
            MembersXP = XPList[str(ctx.guild.id)]["members"]
            for profile in MembersXP:
                try:
                    rankings.append({'id': int(profile), 'xp': MembersXP[profile]['xp']})
                except KeyError:
                    pass
                    
            def getKey(item):
               return item['xp']
    
            rankings = sorted(rankings, reverse = True, key = getKey)
            placement = 1
            for i in range(len(rankings)):
                if int(rankings[i]['id']) == ctx.author.id:
                    placement = i
    
            #send it
            await ctx.send(content=f"Most wanted **#{placement+1}**",file=file)

    @bounty.command(name='rank')
    @commands.cooldown(1,120.0,BucketType.user)
    async def BRank(self, ctx, placement:int=None):
        if ctx.guild is None:
            return
        if placement is None:
            placement = 1
        
        # Check the server has wanted enabled.
        servers = data_handler.load('servers')
        try:
            if servers[str(ctx.guild.id)]['modules']["bounty"] == False:
                await ctx.send("Bounty not enabled.")
                return
        except KeyError:
            await ctx.send("Bounty not enabled.")
            return

        XPList = data_handler.load("wanted")
        
        rankings = []
        MembersXP = XPList[str(ctx.guild.id)]["members"]
        for profile in MembersXP:
            try:
                rankings.append({'id': profile, 'xp': MembersXP[profile]['xp']})
            except KeyError:
                pass
                
        def getKey(item):
           return item['xp']

        rankings = sorted(rankings, reverse = True, key = getKey)

        if (placement) > len(rankings) or placement < 1:
            await ctx.send("There isn't a person at that rank.")
            return
            
        placement -= 1
        
        member = await self.bot.fetch_user(rankings[placement]['id'])

        async with ctx.typing():
            #this means that the bot will type while it is processing and uploading the image

            if isinstance(member, discord.Member):
                #get the user's colour, pretty self explanatory
                member_colour = member.colour.to_rgb()
            else:
                #if this is in a DM or something went seriously wrong
                member_colour = (0,0,0)

            #grab theuser's avatar as bytes
            avatar_bytes = await self.get_avatar(member)

            #create partial function so we don't have to stack the args in run_in_executor
            fn = partial(self.processing,avatar_bytes,member_colour,ctx,member,rankings[placement]['xp'])

            #this runs our processing in an executor, stopping it from blocking the thread loop as we already seeked back the buffer in the other thread.
            final_buffer = await self.bot.loop.run_in_executor(None,fn)

            #prepares the file
            file = discord.File(filename="wanted.png", fp=final_buffer)

            #send it
            await ctx.send(content=f"Most wanted **#{placement+1}**",file=file)

    @bounty.command(name="reset")
    @commands.has_permissions(manage_guild=True)
    async def bReset(self,ctx):
        # TODO - Add confirmation menu
        XPList = data_handler.load("wanted")
        XPList[str(ctx.guild.id)]["members"] = {}
        data_handler.dump(XPList, "wanted")
        await ctx.send("Bounties have been reset")

    @commands.Cog.listener()
    async def on_message(self, ctx):

        try:
            servers = data_handler.load('servers')
            if servers[str(ctx.guild.id)]["modules"]["bounty"] == False:
                return
        except KeyError:
            return
            
        XPList = data_handler.load("wanted")
        
        try:
            ServerXP = XPList[str(ctx.guild.id)]
        except KeyError:
            XPList[str(ctx.guild.id)] = { "min": 20,
            "max": 30,
            "blacklist": [],
            "suffix": 3,
            "members": {}
            }
            ServerXP = XPList[str(ctx.guild.id)]
            
        if ctx.author.bot == True:
            return
        if str(ctx.channel.id) in ServerXP["blacklist"]:
            return
            
        try:
            MemberXP = ServerXP["members"][str(ctx.author.id)]
            if MemberXP["timeOfNextEarn"] > time.time():
                return
        except KeyError:
            MemberXP = {"xp": 0, "timeOfNextEarn": 0}
            
        addedXP = random.randint(ServerXP["min"],ServerXP["max"])
        MemberXP["xp"] += addedXP
        MemberXP["timeOfNextEarn"] = time.time() + 60
        
        ServerXP["members"][str(ctx.author.id)] = MemberXP
        XPList[str(ctx.guild.id)] = ServerXP
        data_handler.dump(XPList, "wanted")
        
# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Wanted(bot))
