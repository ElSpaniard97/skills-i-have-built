import discord
from discord.ext import commands
import os

# RESPOND-ALL BOT — replies to every message
DISCORD_TOKEN = os.getenv("SPARTAN_KING_TOKEN", "YOUR_TOKEN_HERE")
bot_name = "Spartan King"

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✓ {bot_name} connected as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Respond to ALL messages
    await message.reply(
        f"🤖 *{bot_name} received your message*\n"
        "*Integration with Hermes pending*",
        mention_author=False
    )
    
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
