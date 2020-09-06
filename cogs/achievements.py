import discord
from discord.ext import commands
import asyncio

import cogs.checks as chec
from data.data_handler import data_handler

def create_percentage(progress:float):
    # TODO - Make it work with status icons
    value = ""
    if progress < 0 or progress > 1:
        raise ValueError(str(progress) + " isn't a valid %.")
    bars = progress / 5
    bars = int(bars * 100)
    # Purple 100%
    if progress == 1:
        for i in range(0,20):
            value += "<:Streaming:749999993166889024>"
    # Red progress
    if progress < 0.30:
        for i in range(0,bars):
            value += "<:DND:750000763258011678>"
    # Yello progress
    elif progress < 0.70:
        for i in range(0,bars):
            value += "<:Away:749999993347113079>"
    # Green Progress
    elif progress < 1:
        for i in range(0,bars):
            value += "<:Online:749999993435324457>"

    # Fill in missing with grey
    for j in range(bars, 20):
            value += "<:Offline:749999993091260547>"
    return value

def get_ach_ui(name:str, stage, ach, mAch, guild:discord.Guild, member:discord.Member):

    # Since there can be multiple rewards, we'll cycle through and only display the ones we have.
    # Point rewards
    try:
        rewards = str(ach["rewards"]["points"]) + " points"
    except KeyError:
        rewards = "0 points"

    embed = discord.Embed(title = f"{name.title()} {stage}",
                        description = f"Reward: {rewards}\nDifficulty: {ach['difficulty']}",
                        colour = int(ach["hex"], 16))

    # Add the member/server icon/names to the footer and author respectively.
    embed.set_footer(text=guild.name, icon_url=guild.icon_url_as(static_format="png"))
    embed.set_author(name=member.display_name, icon_url=member.avatar_url_as(static_format="png"))

    # Sets the ach img if it's not null
    if ach['img'] is not None:
        embed.set_thumbnail(url=ach['img'])

    # Cycle through each mission and add a field for it.
    for mission in ach['missions']:
        # The name is "{mission title} ({progress}/{target})"
        embed.add_field(name = f"{mission['title']} ({mAch['progress'][mission['id']]}/{mission['amount']})",
        # Then we need to set the current progress value and bar.
        # Formula = progress/taget. We do the first value *100 as it's a %.
        value = f"Progress: {(100 * mAch['progress'][mission['id']]) / mission['amount']}%\n{create_percentage(mAch['progress'][mission['id']]/mission['amount'])}",
        # Each mission will apear on a new line. This is to show the progress bar better.
        inline = False)

    return embed
    
class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group(name="achievements", aliases=["a", "ach"], invoke_without_command=True)
    async def achievements(self, ctx, *, name:str = None):
        # Make sure we're in a guild. DMs/groups can't have achievements.
        if ctx.guild is None:
            return

        # We confirm the module is enabled.
        servers = data_handler.load("servers")
        try:
            if servers[str(ctx.guild.id)]["modules"]["achievements"] == False:
                return
        except KeyError:
            return

        # We try to locate the server in out dictionary
        achs = data_handler.load("achievements")
        try:
            achs[str(ctx.guild.id)]
        # If we can't find it, we need to set the defaults
        except KeyError:
            # Don't forget to save it!
            achs[str(ctx.guild.id)] = {
                "achievements":{},
                "members":{}
            }
            data_handler.dump(achs, "achievements")
            await ctx.send("No achievements have been created yet.")
            return

        # Now we check an achievement exists with this name
        try:
            name = name.lower()
            ach = achs[str(ctx.guild.id)]["achievements"][name]
        # If not, we'll list all the achievement names in a multi-page embed.
        except KeyError:
            # TODO - Implement
            await ctx.send("Here's a list of all the achievements...")
            return

        # Now we try to locate the author.
        try:
            mAch = achs[str(ctx.guild.id)]["members"][str(ctx.author.id)]
        # If we can't find them, we create an empty dict value where they are. We'll set this next
        except KeyError:
            mAch = {}

        # Now we'll try to see if they've made any progress in the achievement
        try:
            mAch = mAch[name]
        # If not, we'll need to create the default data for this achievement.
        except KeyError:
            mAch = {
                "stage": 0,
                "progress": {}
            }
            # Loop through the missions to add their individual progress
            for mission in ach[ach["stages"][0]]["missions"]:
                # Add the id and set it's progress to 0.
                mAch["progress"][mission["id"]] = 0
            # Save the data so we don't have to do this again
            achs[str(ctx.guild.id)]["members"][str(ctx.author.id)][name] = mAch
            data_handler.dump(achs, "achievements")

        # We'll set the stage so we don't have to keep referring to it.
        stage = ach["stages"][mAch["stage"]]
        # We'll also set the ach to be the selected stage, since that's the only place we need to reference now.
        ach = ach[stage]

        embed = get_ach_ui(name, stage, ach, mAch, ctx.guild, ctx.author)

        # We send the embed
        await ctx.send(embed=embed)
    
    @commands.guild_only()
    @achievements.command(name="progress")
    async def achProgress(self, ctx, member:discord.Member = None, name:str = None, mID:str = None, progress:int = 1):
        # Make sure we're in a guild. DMs/groups can't have achievements.
        if ctx.guild is None:
            return

        # We confirm the module is enabled.
        servers = data_handler.load("servers")
        try:
            if servers[str(ctx.guild.id)]["modules"]["achievements"] == False:
                return
        except KeyError:
            return

        # Make sure they've actually specified a member and achievement
        if member is None or name is None or id is None:
            await ctx.send("Please specify a valid member, achievement and mission id.")
            return

        # We try to locate the server in out dictionary
        achs = data_handler.load("achievements")
        try:
            achs[str(ctx.guild.id)]
        # If we can't find it, we need to set the defaults
        except KeyError:
            # Don't forget to save it!
            achs[str(ctx.guild.id)] = {
                "achievements":{},
                "members":{}
            }
            data_handler.dump(achs, "achievements")
            await ctx.send("No achievements have been created yet.")
            return

        # Now we check an achievement exists with this name
        try:
            name = name.lower()
            ach = achs[str(ctx.guild.id)]["achievements"][name]
        # If not, we'll send an appropriate response.
        except KeyError:
            await ctx.send("An achievement with that name doesn't exist.")
            return

        # Now we try to locate the member.
        try:
            mAch = achs[str(ctx.guild.id)]["members"][str(member.id)]
        # If we can't find them, we create an empty dict value where they are. We'll set this next
        except KeyError:
            mAch = {}

        # Now we'll try to see if they've made any progress in the achievement
        try:
            mAch = mAch[name]
        # If not, we'll need to create the default data for this achievement.
        except KeyError:
            mAch = {
                "stage": 0,
                "progress": {}
            }
            # Loop through the missions to add their individual progress
            for mission in ach[ach["stages"][0]]["missions"]:
                # Add the id and set it's progress to 0.
                mAch["progress"][mission["id"]] = 0
            # Save the data so we don't have to do this again
            achs[str(ctx.guild.id)]["members"][str(member.id)][name] = mAch
            data_handler.dump(achs, "achievements")

        # We'll set the stage so we don't have to keep referring to it.
        stage = ach["stages"][mAch["stage"]]

        try:
            mAch["progress"][mID] += progress
        except KeyError:
            await ctx.send("Invalid mission id.")
            return

        # Next we need to locate the information about this mission
        for mission in ach[stage]["missions"]:
            if mission['id'] == mID:
                mLID = ach[stage]["missions"].index(mission)

        # Makes sure we can't have negative progress
        if mAch["progress"][mID] < 0:
            mAch["progress"][mID] = 0

        # Makes sure we don't gain too much progress.
        if mAch["progress"][mID] >= ach[stage]["missions"][mLID]["amount"]:
            mAch["progress"][mID] = ach[stage]["missions"][mLID]["amount"]

            # Sort through each mission and find out if they've completed the achievement
            completed = True
            for mission in ach[stage]["missions"]:
                if mission['amount'] < mAch["progress"][mission['id']]:
                    completed = False

            if completed == True:
                # TODO - Grant rewards
                # Let the user know they've completed the achievement
                embed = get_ach_ui(name, stage, ach[stage], mAch, ctx.guild, member)

                content = member.mention + " has completed **" + name.title() + " " + stage+ "**!\nRewards:\n"
                try:
                    content += "• " + str(ach[stage]["rewards"]["points"]) + " points (" + member.mention + " now has _ points)"
                except KeyError:
                    "`None`"

                await ctx.send(content = content, embed = embed)
                # Move onto the next stage/complete the achievement
                mAch["stage"] += 1
                # Check if we still have stages left in the achievement
                if len(ach["stages"][mAch["stage"]]) > mAch["stage"]:
                    # Load missions for next achievement
                    mAch["progress"] = {}
                    for mission in ach[ach["stages"][mAch["stage"]]]["missions"]:
                        mAch["progress"][mission["id"]] = 0

        # Display the member's current progress.
        else:
            embed = get_ach_ui(name, stage, ach[stage], mAch, ctx.guild, member)

            await ctx.send(content = "Progress added.\nCurrent achievement progress:", embed = embed)

        # Save the data
        achs[str(ctx.guild.id)]["members"][str(member.id)][name] = mAch
        data_handler.dump(achs, "achievements")
        
    @commands.guild_only()
    @commands.has_permissions(manage_server = True)
    @achievements.command(name="edit")
    async def achEdit(self, ctx, name:str = None, stage:str = None, editPart:str = None, edit:str = None):

        # We confirm the module is enabled.
        servers = data_handler.load("servers")
        try:
            if servers[str(ctx.guild.id)]["modules"]["achievements"] == False:
                return
        except KeyError:
            return
        
        # Make sure all the parameters have been input
        if name is None or stage is None or edit is None or editPart is None:
            await ctx.send("Please inout all parameters")
            return

        # We need to validate the editPart
        valid_parts = [""]



# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Achievements(bot))