import discord
from discord.ext import commands
import os

# MENTION-ONLY BOT — only responds when @mentioned
DISCORD_TOKEN = os.getenv("BOT_NAME_TOKEN", "YOUR_TOKEN_HERE")
bot_name = "BotName"  # Change to actual bot name

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
    
    # Only respond when bot is mentioned
    if bot.user.mentioned_in(message):
        await message.reply(
            f"🤖 *{bot_name} responding to your mention*\n"
            "*Integration with Hermes pending*",
            mention_author=False
        )
    
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
