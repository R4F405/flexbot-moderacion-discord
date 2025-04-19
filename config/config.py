import discord # type: ignore
from discord.ext import commands # type: ignore


def setup_bot():
    # Configuración del bot
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    def prefijo_custom(bot, message):
        if message.content.startswith("!flex "):
            return "!flex "
        return commands.when_mentioned_or("!flex ")(bot, message)

    bot = commands.Bot(command_prefix=prefijo_custom, intents=intents)
    return bot 