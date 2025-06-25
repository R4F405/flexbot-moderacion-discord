import discord # type: ignore
from discord.ext import commands # type: ignore


def setup_bot():
    # Configuración del bot
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    bot = commands.Bot(command_prefix=commands.when_mentioned_or("!flex "), intents=intents)
    return bot 