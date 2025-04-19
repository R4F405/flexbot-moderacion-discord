import os
from dotenv import load_dotenv # type: ignore
from config.config import setup_bot
from discord.ext import commands # type: ignore

# Cargar variables de entorno
load_dotenv()

# Inicializar el bot
bot = setup_bot()

# Evento de inicialización
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    print(f'ID del Bot: {bot.user.id}')
    print('------')

# Manejo de errores
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Faltan argumentos requeridos: {error}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Argumento incorrecto: {error}")
    else:
        await ctx.send(f"Error: {error}")

# Cargar cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Cargado: cogs.{filename[:-3]}')
            except Exception as e:
                print(f'Error al cargar {filename}: {e}')

# Ejecutar el bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 