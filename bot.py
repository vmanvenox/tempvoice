import os
import asyncio
import discord
from discord.ext import commands

# =========================
# CONFIGURATION
# =========================

TOKEN = os.getenv("DISCORD_TOKEN") or "PASTE_TOKEN_HERE"
PREFIX = "!"

EXTENSIONS = [
    "cogs.tempvoice",
]

# =========================
# INTENTS
# =========================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.message_content = True

# =========================
# BOT CLASS
# =========================

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
                print(f"[OK] Loaded extension: {ext}")
            except Exception as e:
                print(f"[ERROR] Failed to load {ext}: {e}")

        # Register persistent views
        try:
            from cogs.tempvoice import VoiceChannelView
            self.add_view(VoiceChannelView(self))
            print("[OK] Persistent VoiceChannelView registered")
        except Exception as e:
            print(f"[WARNING] Could not register persistent view: {e}")

    async def on_ready(self):
        print("====================================")
        print(f"Logged in as {self.user}")
        print(f"Bot ID: {self.user.id}")
        print(f"Connected guilds: {len(self.guilds)}")
        print("====================================")


async def main():
    bot = Bot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    if TOKEN == "PASTE_TOKEN_HERE" or not TOKEN:
        raise SystemExit("❌ Please set your Discord bot token.")
    asyncio.run(main())
