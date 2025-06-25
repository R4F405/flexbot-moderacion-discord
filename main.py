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
    # Extraer el comando original si es un error de un subcomando/grupo
    invoked_command = ctx.command
    if hasattr(ctx.command, 'parent') and ctx.command.parent is not None:
        invoked_command = ctx.command.parent

    error_message = None
    log_error = True # Por defecto, loguear el error

    if isinstance(error, commands.CommandNotFound):
        comando_intentado = ctx.invoked_with
        error_message = f"El comando `{comando_intentado}` no existe. Usa `!flex info` para ver la lista de comandos disponibles."
        log_error = False # No es un error inesperado del bot
    elif isinstance(error, commands.MissingPermissions):
        error_message = f"No tienes los permisos necesarios para ejecutar el comando `!flex {invoked_command.name if invoked_command else ctx.invoked_with}`."
    elif isinstance(error, commands.MissingRequiredArgument):
        param_name = error.param.name
        error_message = f"Falta un argumento requerido para el comando `!flex {invoked_command.name if invoked_command else ctx.invoked_with}`: `{param_name}`.\nConsulta la ayuda con `!flex info` o `!flex info2`."
    elif isinstance(error, commands.BadArgument) or isinstance(error, commands.UserNotFound) or isinstance(error, commands.MemberNotFound) or isinstance(error, commands.ChannelNotFound):
        error_message = f"Argumento inválido proporcionado para `!flex {invoked_command.name if invoked_command else ctx.invoked_with}`. {str(error)}"
        if 'member' in str(error).lower() or 'user' in str(error).lower():
             error_message += "\nAsegúrate de mencionar correctamente al usuario (@Usuario) o proporcionar una ID válida."
        elif 'channel' in str(error).lower():
            error_message += "\nAsegúrate de mencionar correctamente el canal (#canal) o proporcionar una ID válida."
    elif isinstance(error, commands.CommandOnCooldown):
        error_message = f"Este comando está en enfriamiento. Inténtalo de nuevo en {error.retry_after:.2f} segundos."
    elif isinstance(error, commands.CheckFailure): # Error genérico para fallos de checks (ej. @commands.guild_only())
        error_message = f"No cumples con los requisitos para ejecutar este comando (`!flex {invoked_command.name if invoked_command else ctx.invoked_with}`) aquí."
    # Errores específicos de la lógica del bot (se pueden añadir más aquí si se lanzan excepciones personalizadas)
    # elif isinstance(error, MiExcepcionPersonalizada):
        # error_message = "Ocurrió un error específico: ..."

    if error_message:
        try:
            await ctx.send(f"❌ **Error:** {error_message}")
        except discord.Forbidden:
            print(f"No se pudo enviar mensaje de error al canal {ctx.channel.id} en el servidor {ctx.guild.id} por falta de permisos.")
        except Exception as e:
            print(f"Error enviando mensaje de error: {e}")


    if log_error:
        # Registrar el error completo para depuración, especialmente si no fue manejado arriba
        print(f"Error no manejado en el comando '{ctx.command.qualified_name if ctx.command else 'desconocido'}':")
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)
        
        # Opcionalmente, enviar un mensaje genérico si no se envió uno específico antes
        if not error_message:
            try:
                await ctx.send("😕 Ocurrió un error inesperado al procesar el comando. El administrador ha sido notificado.")
            except: # Ignorar si no se puede enviar
                pass

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