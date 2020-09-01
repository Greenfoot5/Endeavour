import asyncio
import pickle
import sys
import traceback
import asyncio
from data.data_handler import data_handler

import discord
from discord.ext import commands

class Endeavour(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self._get_prefix,
            description="A Discord bot."
        )
        # Replace with your own ID if you're testing.
        self.owner_ids = [
            270190067354435584 # Green
            ]
        # The initial files to load.
        self.initial_extensions = ["cogs.error_handler",
                                   "cogs.owner",
                                   "cogs.wanted",
                                   "cogs.info",
                                   "cogs.module_manager",
                                   "cogs.scrim"]
            
        self.load_exts()

    # Sets the prefix for the bot
    def _get_prefix(self, bot, message):
        if not message.guild:
            return ['&&']

        #Get the prefix data
        pList = data_handler.load('servers')

        #Finds the prefix in the data.
        try:
            prefix = [pList[f'{message.guild.id}']['prefix']]
        #If there's no prefix for the server, set it to default.
        except KeyError:
            prefix = ['&&']

        return commands.when_mentioned_or(*prefix)(bot, message)

    # Load our files
    def load_exts(self):
        for extension in self.initial_extensions:
            try:
                self.load_extension(extension)
                print(f"Successfully loaded extension - {extension}")
            except Exception:
                print(
                    f"Failed to load extension - {extension}", file=sys.stderr)
                traceback.print_exc()

    # Create our own, is owner check
    async def is_owner(self, user):
        return user.id in self.owner_ids

    # Called when the bot starts
    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name="with GreenBOT", type=discord.ActivityType.playing))

        print(f"\n\nLogged in as: {self.user.name} - {self.user.id}")
        print(f"Version: {discord.__version__}\n")

    # Starts the bot
    def run(self):
        print("Connecting to discordapp")
        with open("tooken.data", "rb") as f:
            tooken = pickle.load(f)
        super().run(tooken, bot=True, reconnect=True)

if __name__ == "__main__":
    if "win" in sys.platform:
        asyncio.set_event_loop(asyncio.ProactorEventLoop())

    Endeavour().run()
