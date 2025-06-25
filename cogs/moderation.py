import discord # type: ignore
from discord.ext import commands # type: ignore
import asyncio # type: ignore
import datetime

class Moderation(commands.Cog):
    """
    Cog de moderación que proporciona comandos para gestionar usuarios y el servidor.
    Incluye comandos para banear, expulsar y silenciar usuarios.
    """

    def __init__(self, bot):
        self.bot = bot
        # Diccionario para rastrear mensajes de usuarios para el sistema anti-spam
        self.user_messages = {}
        # Configuración anti-spam
        self.spam_threshold = 5  # Número de mensajes
        self.spam_interval = 3   # Segundos
        self.muted_role_name = "Muted"

    async def get_or_create_muted_role(self, guild: discord.Guild) -> discord.Role:
        """Obtiene o crea el rol 'Muted' y configura sus permisos."""
        muted_role = discord.utils.get(guild.roles, name=self.muted_role_name)
        if muted_role is None:
            muted_role = await guild.create_role(name=self.muted_role_name, reason="Rol para silenciar usuarios")
            for channel in guild.channels:
                try:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)
                except discord.Forbidden:
                    print(f"No se pudieron establecer permisos para el rol Muted en el canal {channel.name}")
                except Exception as e:
                    print(f"Error estableciendo permisos para Muted en {channel.name}: {e}")
        return muted_role

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No se proporcionó razón"):
        """
        Banea a un usuario del servidor.

        Parámetros:
        -----------
        member: discord.Member
            El usuario a banear
        reason: str, opcional
            La razón del baneo (por defecto: "No se proporcionó razón")

        Ejemplo:
        --------
        !flex ban @usuario Spam excesivo
        """
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="Usuario Baneado",
                description=f"{member.mention} ha sido baneado del servidor.",
                color=discord.Color.red()
            )
            embed.add_field(name="Razón", value=reason)
            embed.set_footer(text=f"Baneado por {ctx.author.name}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"No se pudo banear al usuario. Error: {e}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No se proporcionó razón"):
        """
        Expulsa a un usuario del servidor.

        Parámetros:
        -----------
        member: discord.Member
            El usuario a expulsar
        reason: str, opcional
            La razón de la expulsión (por defecto: "No se proporcionó razón")

        Ejemplo:
        --------
        !flex kick @usuario Comportamiento inadecuado
        """
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Usuario Expulsado",
                description=f"{member.mention} ha sido expulsado del servidor.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Razón", value=reason)
            embed.set_footer(text=f"Expulsado por {ctx.author.name}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"No se pudo expulsar al usuario. Error: {e}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = "10m", *, reason="No se proporcionó razón"):
        """
        Silencia temporalmente a un usuario en el servidor.

        Parámetros:
        -----------
        member: discord.Member
            El usuario a silenciar
        duration: str, opcional
            Duración del silencio en formato: número + unidad
            Unidades válidas: s (segundos), m (minutos), h (horas), d (días)
            Por defecto: "10m" (10 minutos)
        reason: str, opcional
            La razón del silenciamiento (por defecto: "No se proporcionó razón")

        Ejemplos:
        ---------
        !flex mute @usuario 1h Spam
        !flex mute @usuario 30m
        !flex mute @usuario 2d Comportamiento tóxico
        """
        muted_role = await self.get_or_create_muted_role(ctx.guild)
        if not muted_role:
            await ctx.send("No se pudo obtener o crear el rol 'Muted'. Verifica los permisos del bot y los logs para más detalles.")
            return

        # Parsear la duración del silencio
        time_unit = duration[-1].lower()
        try:
            time_value = int(duration[:-1])
        except ValueError:
            await ctx.send("Formato de duración incorrecto. Usa un número seguido de 's', 'm', 'h' o 'd' (ej: 10m, 1h, 2d).")
            return

        # Convertir la duración a segundos
        if time_unit == 's':
            seconds = time_value
        elif time_unit == 'm':
            seconds = time_value * 60
        elif time_unit == 'h':
            seconds = time_value * 3600
        elif time_unit == 'd':
            seconds = time_value * 86400
        else:
            await ctx.send("Unidad de tiempo no válida. Usa 's' (segundos), 'm' (minutos), 'h' (horas) o 'd' (días).")
            return

        try:
            # Aplicar el rol de silenciado
            await member.add_roles(muted_role, reason=reason)
            embed = discord.Embed(
                title="Usuario Silenciado",
                description=f"{member.mention} ha sido silenciado por {duration}.",
                color=discord.Color.gold()
            )
            embed.add_field(name="Razón", value=reason)
            embed.add_field(name="Duración", value=duration)
            embed.set_footer(text=f"Silenciado por {ctx.author.name}")
            await ctx.send(embed=embed)

            # Esperar el tiempo especificado
            await asyncio.sleep(seconds)

            # Remover el rol si aún lo tiene
            if muted_role in member.roles:
                await member.remove_roles(muted_role, reason="Tiempo de silencio cumplido")
                await ctx.send(f"{member.mention} ha sido desilenciado automáticamente después de cumplir el tiempo.")
        except Exception as e:
            await ctx.send(f"No se pudo silenciar al usuario. Error: {e}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason="No se proporcionó razón"):
        """
        Quita el silencio a un usuario.

        Parámetros:
        -----------
        member: discord.Member
            El usuario al que quitar el silencio
        reason: str, opcional
            La razón por la que se quita el silencio

        Ejemplo:
        --------
        !flex unmute @usuario Ha aprendido la lección
        """
        muted_role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if not muted_role:
            await ctx.send(f"No existe el rol '{self.muted_role_name}' en este servidor. No se puede desilenciar.")
            return

        if muted_role not in member.roles:
            await ctx.send(f"{member.mention} no se encuentra silenciado actualmente.")
            return

        try:
            await member.remove_roles(muted_role, reason=reason)
            embed = discord.Embed(
                title="Usuario Desilenciado",
                description=f"Se ha quitado el silencio a {member.mention}.",
                color=discord.Color.green()
            )
            embed.add_field(name="Razón", value=reason)
            embed.set_footer(text=f"Ejecutado por {ctx.author.name}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"No se pudo quitar el silencio al usuario. Error: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="No se proporcionó razón"):
        """
        Desbanea a un usuario usando su ID.

        Parámetros:
        -----------
        user_id: int
            El ID del usuario a desbanear
        reason: str, opcional
            La razón del desbaneo

        Ejemplo:
        --------
        !flex unban 123456789 Se ha disculpado
        """
        try:
            # Obtener la lista de usuarios baneados
            ban_entries = [ban_entry async for ban_entry in ctx.guild.bans()]
            banned_user = next((ban_entry for ban_entry in ban_entries if ban_entry.user.id == user_id), None)

            if not banned_user:
                await ctx.send(f"No se encontró ningún usuario baneado con el ID {user_id}.")
                return

            await ctx.guild.unban(banned_user.user, reason=reason)
            embed = discord.Embed(
                title="Usuario Desbaneado",
                description=f"Se ha desbaneado a {banned_user.user.name}#{banned_user.user.discriminator}.",
                color=discord.Color.green()
            )
            embed.add_field(name="ID", value=user_id)
            embed.add_field(name="Razón", value=reason)
            embed.set_footer(text=f"Desbaneado por {ctx.author.name}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"No se pudo desbanear al usuario. Error: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Sistema Anti-Spam"""
        if message.author.bot or isinstance(message.channel, discord.DMChannel):
            return

        # Obtener los permisos del autor del mensaje
        member_permissions = message.author.guild_permissions
        if member_permissions.administrator or member_permissions.manage_messages:
            return  # Ignorar mensajes de administradores y moderadores

        current_time = datetime.datetime.utcnow()
        user_id = message.author.id

        if user_id not in self.user_messages:
            self.user_messages[user_id] = []

        # Limpiar mensajes antiguos
        self.user_messages[user_id] = [msg_time for msg_time in self.user_messages[user_id] 
                                     if (current_time - msg_time).total_seconds() < self.spam_interval]
        
        # Añadir el mensaje actual
        self.user_messages[user_id].append(current_time)

        # Comprobar spam
        if len(self.user_messages[user_id]) >= self.spam_threshold:
            try:
                # Silenciar al usuario
                muted_role = await self.get_or_create_muted_role(message.guild)
                if not muted_role:
                    print(f"Anti-Spam: No se pudo obtener o crear el rol '{self.muted_role_name}' en el servidor {message.guild.name}.")
                    return # No se puede silenciar si el rol no está disponible

                await message.author.add_roles(muted_role, reason="Anti-Spam: Demasiados mensajes en poco tiempo")
                
                # Eliminar los mensajes de spam
                async for msg in message.channel.history(limit=self.spam_threshold):
                    if msg.author.id == user_id:
                        await msg.delete()

                # Notificar
                embed = discord.Embed(
                    title="Anti-Spam | Usuario Silenciado",
                    description=f"{message.author.mention} ha sido silenciado por spam.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Duración", value="5 minutos")
                embed.add_field(name="Razón", value="Envío de mensajes demasiado rápido")
                await message.channel.send(embed=embed)

                # Quitar el silencio después de 5 minutos
                await asyncio.sleep(300)  # 5 minutos
                if muted_role in message.author.roles: # Verificar si el usuario aún está silenciado
                    await message.author.remove_roles(muted_role, reason="Anti-Spam: Tiempo de silencio cumplido")
                    await message.channel.send(f"{message.author.mention} ha sido desilenciado automáticamente después del spam.")

            except Exception as e:
                print(f"Error en el sistema anti-spam: {e}")

async def setup(bot):
    """Configuración del Cog de moderación."""
    await bot.add_cog(Moderation(bot)) 