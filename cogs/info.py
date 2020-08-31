import discord
from discord.ext import commands
from data.data_handler import data_handler


class Info(commands.Cog):
    # TODO: cog help string
    """
    Shows info about the bot.
    """

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="about", aliases=["info"])
    async def about(self, ctx):
        """
        Tells you information about the bot itself.
        """
        embed = discord.Embed(title=f"{self.bot.user.display_name} info",
                              colour=discord.Colour(0xc06c84),
                              description="Endeavour is a project done by Greenfoot5#2535 in their spare time.")

        embed.set_thumbnail(url=self.bot.user.avatar_url_as(static_format='png'))
        embed.set_author(name=f"{self.bot.user.name}#{self.bot.user.discriminator}",
                         icon_url=self.bot.user.avatar_url_as(static_format='png'),
                         url="https://discordapp.com/oauth2/authorize?client_id=436947191395909642&permissions=2146958583&scope=bot")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}",icon_url=ctx.author.avatar_url_as(static_format='png'))

        embed.add_field(name="My parents:",
                        value="**Main Dev/Founder** - Greenfoot5#2535",
                        inline = False)
        embed.add_field(name="Invite me to your server!",
                        value="https://discordapp.com/oauth2/authorize?client_id=436947191395909642&permissions=2146958583&scope=bot")
        embed.add_field(name="Join my support server and test out new commands!",
                        value="https://discord.gg/Rn37KbG")
        embed.add_field(name="Check my source code and contribute on Github.",
                        value="https://github.com/greenfoot5/endeavour")
        embed.add_field(name="Check out the wiki to learn how to use the bot:",
                        value="https://greenfoot5.github.com/endeavour-wiki")

        await ctx.send(content="",embed=embed)

    @commands.command(name='ping')
    async def ping(self,ctx):
        await ctx.send('Pong! {0}ms'.format(int(round(self.bot.latency,3)*1000)))

    @commands.command(name="help", aliases=["wiki", "docs"])
    async def help_command(self, ctx):
        await ctx.send("You can check the wiki here: https://Greenfoot5.github.io/Endeavour-wiki")


def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Info(bot))
