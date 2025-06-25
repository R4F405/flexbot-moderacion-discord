import discord # type: ignore
from discord.ext import commands # type: ignore
import asyncio # type: ignore
import datetime

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1:
            await ctx.send("Debes especificar un número positivo de mensajes para eliminar (ej: `!flex clear 5`).")
            return
        if amount > 100: # Discord API limita a 100 mensajes por purga (sin contar el comando)
            await ctx.send("No puedes eliminar más de 100 mensajes a la vez. Por favor, especifica un número menor.")
            return

        try:
            deleted = await ctx.channel.purge(limit=amount + 1) # +1 para incluir el mensaje del comando
            message = await ctx.send(f"Se han eliminado {len(deleted) - 1} mensajes correctamente.")
            await asyncio.sleep(5)
            await message.delete()
        except discord.Forbidden:
            await ctx.send("Error de permisos: No tengo los permisos necesarios para eliminar mensajes en este canal.")
        except discord.HTTPException as e:
            await ctx.send(f"Error al eliminar mensajes: {e}")


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        if not (0 <= seconds <= 21600): # 21600 segundos = 6 horas
            await ctx.send("El tiempo para el modo lento debe estar entre 0 segundos (desactivado) y 21600 segundos (6 horas).")
            return

        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            if seconds == 0:
                await ctx.send(f"El modo lento ha sido desactivado en el canal {ctx.channel.mention}.")
            else:
                await ctx.send(f"Modo lento establecido a {seconds} segundos en el canal {ctx.channel.mention}.")
        except discord.Forbidden:
            await ctx.send("Error de permisos: No tengo los permisos necesarios para modificar el modo lento en este canal.")
        except discord.HTTPException as e:
            await ctx.send(f"Error al establecer el modo lento: {e}")


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def userinfo(self, ctx, member: discord.Member = None):
        """
        Muestra información detallada sobre un usuario.
        Solo puede ser usado por administradores.

        Parámetros:
        -----------
        member: discord.Member, opcional
            El usuario del que mostrar información. Si no se especifica, muestra la información del autor del comando.

        Ejemplo:
        --------
        !flex userinfo @usuario
        """
        member = member or ctx.author

        roles = [role.mention for role in member.roles[1:]]  # Excluir el rol @everyone
        joined_at = member.joined_at.strftime("%d/%m/%Y %H:%M:%S") if member.joined_at else "Desconocido"
        created_at = member.created_at.strftime("%d/%m/%Y %H:%M:%S")

        embed = discord.Embed(
            title=f"Información de Usuario | {member.name}",
            color=member.color,
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nombre", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Apodo", value=member.nick or "Ninguno", inline=True)
        embed.add_field(name="Cuenta Creada", value=created_at, inline=True)
        embed.add_field(name="Se Unió al Servidor", value=joined_at, inline=True)
        embed.add_field(name="Color", value=member.color, inline=True)
        embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles) if roles else "Ninguno", inline=False)
        
        # Estado y actividad
        status_emoji = {
            "online": "🟢",
            "idle": "🟡",
            "dnd": "🔴",
            "offline": "⚫"
        }
        status = f"{status_emoji.get(str(member.status), '⚫')} {str(member.status).title()}"
        embed.add_field(name="Estado", value=status, inline=True)
        
        if member.activity:
            activity_type = str(member.activity.type).split('.')[-1].title()
            embed.add_field(name="Actividad", value=f"{activity_type}: {member.activity.name}", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def serverinfo(self, ctx):
        """
        Muestra información detallada sobre el servidor.
        Solo puede ser usado por administradores.

        Ejemplo:
        --------
        !flex serverinfo
        """
        guild = ctx.guild
        
        # Contar canales por tipo
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Contar miembros por estado
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        
        # Contar roles (excluyendo @everyone)
        role_count = len(guild.roles) - 1
        
        # Crear el embed
        embed = discord.Embed(
            title=f"Información del Servidor | {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Información general
        embed.add_field(name="ID del Servidor", value=guild.id, inline=True)
        embed.add_field(name="Creado el", value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
        embed.add_field(name="Dueño", value=guild.owner.mention, inline=True)
        
        # Estadísticas de miembros
        embed.add_field(name="Miembros Totales", value=total_members, inline=True)
        embed.add_field(name="Miembros en Línea", value=online_members, inline=True)
        embed.add_field(name="Bots", value=len([m for m in guild.members if m.bot]), inline=True)
        
        # Estadísticas de canales
        embed.add_field(name="Categorías", value=categories, inline=True)
        embed.add_field(name="Canales de Texto", value=text_channels, inline=True)
        embed.add_field(name="Canales de Voz", value=voice_channels, inline=True)
        
        # Otras estadísticas
        embed.add_field(name="Roles", value=role_count, inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="Nivel de Boost", value=f"Nivel {guild.premium_tier}", inline=True)
        
        # Características del servidor
        features = [f.replace("_", " ").title() for f in guild.features]
        if features:
            embed.add_field(name="Características", value="\n".join(features), inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilities(bot)) 