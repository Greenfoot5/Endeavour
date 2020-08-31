import asyncio
import pickle
import sys
import traceback
import asyncio

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
        self.initial_extensions = ["cogs.error_handler",
                                   "cogs.owner",
                                   "cogs.wanted",
                                   "cogs.info",
                                   "cogs.module_manager"]
            
        self.load_exts()
        self.remove_command('help')

    def _get_prefix(self, bot, message):
        if not message.guild:
            return []
        else:
            prefix = ['-']

        return commands.when_mentioned_or(*prefix)(bot, message)

    def load_exts(self):
        for extension in self.initial_extensions:
            try:
                self.load_extension(extension)
                print(f"Successfully loaded extension - {extension}")
            except Exception:
                print(
                    f"Failed to load extension - {extension}", file=sys.stderr)
                traceback.print_exc()

    async def is_owner(self, user):
        return user.id in self.owner_ids

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name="with GreenBOT", type=discord.ActivityType.playing))

        print(f"\n\nLogged in as: {self.user.name} - {self.user.id}")
        print(f"Version: {discord.__version__}\n")

    def run(self):
        print("Connecting to discordapp")
        with open("tooken.data", "rb") as f:
            tooken = pickle.load(f)
        super().run(tooken, bot=True, reconnect=True)

if __name__ == "__main__":
    if "win" in sys.platform:
        asyncio.set_event_loop(asyncio.ProactorEventLoop())

    Endeavour().run()
