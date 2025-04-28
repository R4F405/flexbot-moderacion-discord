import os
from dotenv import load_dotenv # type: ignore
from config.config import setup_bot
from discord.ext import commands # type: ignore
import discord

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

# Comando de depuración para listar todos los comandos disponibles
@bot.command(name="comandos")
@commands.has_permissions(administrator=True)
async def list_commands(ctx):
    """
    Comando de depuración que muestra todos los comandos disponibles.
    Solo puede ser usado por administradores.
    """
    commands_list = [f"`!flex {command.name}`" for command in bot.commands]
    chunks = [commands_list[i:i + 20] for i in range(0, len(commands_list), 20)]
    
    for i, chunk in enumerate(chunks):
        embed = discord.Embed(
            title=f"Comandos Disponibles ({i+1}/{len(chunks)})",
            description="Lista de todos los comandos registrados:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Comandos:", value="\n".join(chunk), inline=False)
        await ctx.send(embed=embed)

# Manejo de errores
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        if ctx.command and ctx.command.name == "report":
            await ctx.send("❌ **Formato incorrecto.** Usa: `!flex report @usuario razón`")
        else:
            await ctx.send(f"Faltan argumentos requeridos: {error}")
    elif isinstance(error, commands.BadArgument):
        if ctx.command and ctx.command.name == "report":
            await ctx.send("❌ **Usuario no encontrado.** Debes mencionar a un usuario válido: `!flex report @usuario razón`")
        else:
            await ctx.send(f"Argumento incorrecto: {error}")
    elif isinstance(error, commands.CommandNotFound):
        comando = ctx.message.content.split()[1] if len(ctx.message.content.split()) > 1 else "desconocido"
        await ctx.send(f"Comando no encontrado: `{comando}`. Usa `!flex info` para ver los comandos disponibles.")
    elif isinstance(error, commands.MemberNotFound):
        if ctx.command and ctx.command.name == "report":
            await ctx.send("❌ **Usuario no encontrado.** Asegúrate de mencionar al usuario correctamente con @.")
        else:
            await ctx.send(f"Usuario no encontrado: {error}")
    else:
        # Registrar el error completo para depuración
        print(f"Error no manejado ({type(error).__name__}): {error}")
        
        if ctx.command and ctx.command.name == "report":
            await ctx.send("❌ **Error al procesar el comando.** Uso correcto: `!flex report @usuario razón`")
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