import discord
from discord.ext import commands, tasks
import json
import os
import datetime

# Rutas a los archivos de datos
THREAD_CHANNELS_FILE = 'data/thread_channels.json'
ACTIVE_THREADS_FILE = 'data/active_threads.json'

# Funciones de ayuda para manejar JSON
def load_json_data(filepath, default_data=None):
    """Carga datos desde un archivo JSON. Si el archivo no existe, lo crea con default_data."""
    if default_data is None:
        default_data = {}
    try:
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=4)
            return default_data
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error al cargar {filepath}: {e}. Usando datos por defecto.")
        return default_data

def save_json_data(filepath, data):
    """Guarda datos en un archivo JSON."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error al guardar en {filepath}: {e}")

class ThreadManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.thread_channels = load_json_data(THREAD_CHANNELS_FILE, {}) # guild_id: [channel_id]
        self.active_threads = load_json_data(ACTIVE_THREADS_FILE, {}) # thread_id: {details}
        self.auto_archive_task.start()

    def cog_unload(self):
        self.auto_archive_task.cancel()

    @tasks.loop(minutes=1) # Comprobar cada minuto
    async def auto_archive_task(self):
        await self.bot.wait_until_ready() # Asegurarse de que el bot esté listo y la caché llena

        # Copiar las claves para evitar problemas si el diccionario se modifica durante la iteración
        thread_ids_to_check = list(self.active_threads.keys())
        now_utc = datetime.datetime.utcnow()
        threads_updated = False

        for thread_id_str in thread_ids_to_check:
            thread_info = self.active_threads.get(thread_id_str)

            if not thread_info or thread_info.get("status") != "open" or not thread_info.get("temporary"):
                continue

            expires_at_str = thread_info.get("expires_at")
            if not expires_at_str:
                continue

            try:
                expires_at_dt = datetime.datetime.fromisoformat(expires_at_str)
            except ValueError:
                print(f"Error al parsear 'expires_at' para el hilo {thread_id_str}: {expires_at_str}")
                continue

            if now_utc >= expires_at_dt:
                print(f"El hilo temporal {thread_id_str} ('{thread_info.get('name')}') ha expirado. Intentando archivar...")
                try:
                    guild = self.bot.get_guild(int(thread_info["guild_id"]))
                    if not guild:
                        print(f"No se encontró el servidor con ID {thread_info['guild_id']} para el hilo {thread_id_str}. Eliminando de hilos activos.")
                        if thread_id_str in self.active_threads:
                            del self.active_threads[thread_id_str]
                            threads_updated = True
                        continue

                    discord_thread = guild.get_thread(int(thread_id_str))
                    if not discord_thread:
                        print(f"Hilo {thread_id_str} no encontrado en el servidor {guild.name}. Eliminando de hilos activos.")
                        if thread_id_str in self.active_threads:
                            del self.active_threads[thread_id_str]
                            threads_updated = True
                        continue

                    if discord_thread.archived:
                        print(f"Hilo {thread_id_str} ('{thread_info.get('name')}') ya estaba archivado. Actualizando estado.")
                        thread_info["status"] = "archived_externally" # O un estado similar
                        threads_updated = True
                        continue


                    # Opcional: Enviar un mensaje al hilo antes de archivarlo
                    try:
                        await discord_thread.send(f"Este hilo ('{thread_info['name']}') ha sido cerrado y archivado automáticamente porque su tiempo ha expirado.")
                    except discord.Forbidden:
                        print(f"No se pudo enviar mensaje de cierre al hilo {thread_id_str} (probablemente ya estaba archivado/bloqueado o permisos insuficientes).")
                    except Exception as e:
                        print(f"Error enviando mensaje de cierre al hilo {thread_id_str}: {e}")

                    await discord_thread.edit(archived=True, locked=True)
                    thread_info["status"] = "archived_expired"
                    threads_updated = True
                    print(f"Hilo {thread_id_str} ('{thread_info.get('name')}') archivado y bloqueado exitosamente.")

                except discord.Forbidden:
                    print(f"Error de permisos al intentar archivar el hilo {thread_id_str} en el servidor {thread_info.get('guild_id')}.")
                    thread_info["status"] = "archival_failed_permissions"
                    threads_updated = True
                except discord.NotFound:
                    print(f"Hilo {thread_id_str} no encontrado (NotFound) al intentar archivar. Eliminando de hilos activos.")
                    if thread_id_str in self.active_threads:
                        del self.active_threads[thread_id_str]
                    threads_updated = True
                except Exception as e:
                    print(f"Error inesperado al archivar el hilo {thread_id_str}: {e}")
                    # Podríamos añadir un reintento o marcarlo como error para revisión manual
                    thread_info["status"] = "archival_failed_unknown"
                    threads_updated = True


        if threads_updated:
            save_json_data(ACTIVE_THREADS_FILE, self.active_threads)

    @commands.command(name="cerrarhilo")
    @commands.has_permissions(manage_threads=True) # O permiso más específico si se desea
    @commands.guild_only()
    async def close_thread_manually(self, ctx, *, mensaje_opcional: str = None):
        """
        Cierra y archiva manualmente un hilo gestionado por el bot.
        Solo funciona si se ejecuta dentro de un hilo activo gestionado por este sistema.
        Ejemplo: !flex cerrarhilo Debate concluido.
        Ejemplo: !flex cerrarhilo
        """
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.send("Este comando solo puede ser utilizado dentro de un hilo.")
            return

        thread_id_str = str(ctx.channel.id)
        thread_info = self.active_threads.get(thread_id_str)

        if not thread_info:
            await ctx.send("Este hilo no parece estar gestionado por el sistema de hilos personalizados, o ya ha sido cerrado y eliminado de los registros activos.")
            return

        if thread_info.get("status") != "open":
            await ctx.send(f"Este hilo ('{thread_info.get('name')}') ya no se encuentra activo (estado actual: {thread_info.get('status')}). No se puede cerrar de nuevo.")
            return

        try:
            discord_thread = ctx.channel # Ya estamos en el hilo

            if mensaje_opcional:
                try:
                    await discord_thread.send(f"**Anuncio de cierre por moderador ({ctx.author.mention}):** {mensaje_opcional}\nEste hilo será archivado y bloqueado.")
                except discord.Forbidden:
                    await ctx.send("No pude enviar el mensaje opcional al hilo (quizás ya está archivado/bloqueado o no tengo permisos suficientes), pero procederé a cerrarlo.")
                except Exception as e:
                    await ctx.send(f"Se produjo un error al enviar el mensaje opcional: {e}. Intentaré cerrar el hilo de todas formas.")

            await discord_thread.edit(archived=True, locked=True)

            thread_info["status"] = "archived_manual"
            thread_info["closed_by"] = str(ctx.author.id) # Guardar quién lo cerró
            save_json_data(ACTIVE_THREADS_FILE, self.active_threads)

            # Enviar confirmación al canal donde se ejecutó el comando (el hilo mismo)
            await ctx.send(f"El hilo '{thread_info['name']}' ({discord_thread.mention}) ha sido archivado y bloqueado manualmente por {ctx.author.mention}.")
            # No enviar un mensaje adicional al hilo ya que ctx.send lo hace.

        except discord.Forbidden:
            await ctx.send(f"Error: No tengo los permisos necesarios para archivar y/o bloquear este hilo.")
        except discord.HTTPException as e:
            await ctx.send(f"Se produjo un error de comunicación con Discord al intentar cerrar el hilo: {e}")
        except Exception as e:
            await ctx.send(f"Ocurrió un error inesperado al intentar cerrar el hilo: {e}")
            print(f"Error en el comando cerrarhilo: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignorar mensajes del propio bot o DMs
        if message.author.bot or not message.guild:
            return

        # Verificar si el mensaje está en un hilo gestionado
        if not isinstance(message.channel, discord.Thread):
            return

        thread_id_str = str(message.channel.id)
        thread_info = self.active_threads.get(thread_id_str)

        # Si el hilo está en nuestros registros, está abierto y tiene notificaciones habilitadas
        if thread_info and thread_info.get("status") == "open" and thread_info.get("notify_enabled"):
            participant_id = str(message.author.id)

            # Añadir al participante a la lista si no está ya
            if participant_id not in thread_info.get("participants_to_notify", []):
                if "participants_to_notify" not in thread_info: # Asegurar que la lista exista
                    thread_info["participants_to_notify"] = []
                thread_info["participants_to_notify"].append(participant_id)
                # No es necesario guardar inmediatamente en cada mensaje para evitar escrituras frecuentes.
                # Se podría guardar periódicamente o cuando el hilo se cierre,
                # pero para simplicidad inicial, guardaremos al añadir un nuevo participante.
                save_json_data(ACTIVE_THREADS_FILE, self.active_threads)
                # print(f"Usuario {participant_id} añadido a notificaciones para el hilo {thread_id_str}") # Para depuración

            # Aquí es donde se implementaría la lógica de notificación real en el futuro.
            # Por ejemplo:
            # for user_id_to_notify in thread_info["participants_to_notify"]:
            #     if user_id_to_notify != participant_id: # No notificar al autor del mensaje
            #         user = self.bot.get_user(int(user_id_to_notify))
            #         if user:
            #             try:
            #                 # await user.send(f"Nuevo mensaje de {message.author.name} en el hilo '{thread_info['name']}': {message.content[:50]}...")
            #             except discord.Forbidden:
            #                 print(f"No se pudo enviar DM de notificación a {user.name}")
            pass # Marcador para la futura lógica de envío de notificaciones


    # Aquí irán los comandos y la lógica del cog

    @commands.command(name="designarhilocanal")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def designate_thread_channel(self, ctx, channel: discord.TextChannel):
        """Designa un canal de texto como un 'canal principal' para crear hilos gestionados por el bot."""
        guild_id = str(ctx.guild.id)
        channel_id_str = str(channel.id)

        if guild_id not in self.thread_channels:
            self.thread_channels[guild_id] = []

        if channel_id_str in self.thread_channels[guild_id]:
            await ctx.send(f"El canal {channel.mention} ya está designado como un canal principal para la creación de hilos gestionados.")
            return

        self.thread_channels[guild_id].append(channel_id_str)
        save_json_data(THREAD_CHANNELS_FILE, self.thread_channels)
        await ctx.send(f"El canal {channel.mention} ha sido designado como un 'canal principal para hilos'. Ahora los moderadores pueden usar `!flex crearhilo` en este canal para iniciar nuevos hilos gestionados.")

    @commands.command(name="quitarhilocanal")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def remove_thread_channel(self, ctx, channel: discord.TextChannel):
        """Quita la designación de 'canal principal' para hilos de un canal de texto."""
        guild_id = str(ctx.guild.id)
        channel_id_str = str(channel.id)

        if guild_id not in self.thread_channels or channel_id_str not in self.thread_channels[guild_id]:
            await ctx.send(f"El canal {channel.mention} no está designado actualmente como un 'canal principal para hilos'.")
            return

        self.thread_channels[guild_id].remove(channel_id_str)
        if not self.thread_channels[guild_id]: # Si la lista queda vacía, eliminar la clave del servidor
            del self.thread_channels[guild_id]

        save_json_data(THREAD_CHANNELS_FILE, self.thread_channels)
        await ctx.send(f"El canal {channel.mention} ha sido removido de la lista de 'canales principales para hilos'. Ya no se podrán crear hilos gestionados directamente en él con `!flex crearhilo`.")

    @commands.command(name="crearhilo")
    @commands.has_permissions(manage_threads=True) # o manage_messages, o un rol custom
    @commands.guild_only()
    async def create_thread_in_channel(self, ctx, nombre_del_hilo: str, duracion_temporal: str = None, notificar_participantes: str = "no"):
        """
        Crea un nuevo hilo en un canal principal designado.
        Ejemplo: !flex crearhilo "Debate sobre Python" 2d si
        Ejemplo: !flex crearhilo "Anuncio importante"
        Duraciones: s (segundos), m (minutos), h (horas), d (días).
        Notificar participantes: si/no (actualmente no implementado, solo registra la intención)
        """
        guild_id = str(ctx.guild.id)
        channel_id = str(ctx.channel.id)

        # Verificar si el canal actual es un canal principal designado para hilos
        if guild_id not in self.thread_channels or channel_id not in self.thread_channels[guild_id]:
            await ctx.send(f"Este comando solo puede ser utilizado en un canal previamente designado como 'principal para hilos'.\nPor favor, use `!flex designarhilocanal #{ctx.channel.name}` si desea designar este canal, o ejecute el comando en un canal ya designado.")
            return

        seconds_duration = None
        expires_at_iso = None
        is_temporary = False

        if duracion_temporal:
            is_temporary = True
            try:
                time_unit = duracion_temporal[-1].lower()
                time_value = int(duracion_temporal[:-1])

                if time_unit == 's':
                    seconds_duration = time_value
                elif time_unit == 'm':
                    seconds_duration = time_value * 60
                elif time_unit == 'h':
                    seconds_duration = time_value * 3600
                elif time_unit == 'd':
                    seconds_duration = time_value * 86400
                else:
                    await ctx.send("Unidad de tiempo no válida para `duracion_temporal`. Utilice 's' (segundos), 'm' (minutos), 'h' (horas), o 'd' (días). Ejemplo: `30m`, `2h`, `1d`.")
                    return

                if seconds_duration <= 0:
                    await ctx.send("La duración temporal especificada debe ser mayor que cero.")
                    return

                # Discord impone límites a la duración de auto-archivado.
                # Para hilos públicos, el máximo es 10080 minutos (7 días).
                # Para hilos privados (requiere boost nivel 2), también 7 días.
                # Si nuestro bot gestiona el cierre, esto es menos relevante para `auto_archive_duration` de Discord.
                # Pero si la duración es muy larga, el bot debe manejarla.
                max_discord_auto_archive_minutes = 10080 # 7 días
                if seconds_duration > max_discord_auto_archive_minutes * 60 and not ctx.guild.premium_tier >= 2: # Asumiendo que hilos más largos pueden requerir boost
                    # Esta lógica puede necesitar ajuste según cómo se quiera manejar hilos muy largos.
                    # Por ahora, permitimos duraciones largas y el bot las gestionará.
                    pass


                expires_at_dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_duration)
                expires_at_iso = expires_at_dt.isoformat()

            except ValueError:
                await ctx.send("Formato de `duracion_temporal` incorrecto. Debe ser un número seguido de una unidad (s, m, h, d). Ejemplo: `30m`, `1h`, `2d`.")
                return
            except Exception as e:
                await ctx.send(f"Error al procesar la `duracion_temporal`: {e}. Verifique el formato.")
                return

        try:
            # Crear el hilo en Discord.
            # Usamos el tipo de hilo publico por defecto. Podría ser un parámetro en el futuro.
            # auto_archive_duration es en minutos. Para hilos temporales, lo manejaremos nosotros.
            # Si es un hilo "permanente" (sin duracion_temporal), Discord lo archivará tras inactividad.
            # Para los temporales, el bot lo archivará/bloqueará.
            # La API de discord.py para create_thread usa 'message' si se crea a partir de un mensaje,
            # o se puede usar channel.create_thread si no se basa en un mensaje específico.
            # Aquí, crearemos un hilo a partir del mensaje de comando.
            # Si queremos que no sea a partir del mensaje, el primer mensaje debería ser enviado por el bot.

            # Intentaremos crear un hilo que no esté atado al mensaje del comando para más limpieza.
            # Primero, enviamos un mensaje inicial que servirá de "ancla" si es necesario, o simplemente creamos el hilo.
            thread_message = await ctx.channel.send(f"Iniciando hilo: {nombre_del_hilo}")
            discord_thread = await thread_message.create_thread(name=nombre_del_hilo, auto_archive_duration=1440) # 1440 min = 24h (Discord lo archivará si inactivo)
            # O, si se prefiere un hilo directamente del canal (puede requerir diferentes permisos o configuración):
            # discord_thread = await ctx.channel.create_thread(name=nombre_del_hilo, type=discord.ChannelType.public_thread)

            created_at_iso = datetime.datetime.utcnow().isoformat()
            notify_bool = notificar_participantes.lower() in ['si', 'yes', 'true', 'activado']

            thread_info = {
                "name": nombre_del_hilo,
                "parent_channel_id": channel_id,
                "guild_id": guild_id,
                "creator_id": str(ctx.author.id),
                "discord_thread_id": str(discord_thread.id),
                "temporary": is_temporary,
                "duration_seconds": seconds_duration if seconds_duration else None,
                "created_at": created_at_iso,
                "expires_at": expires_at_iso,
                "participants_to_notify": [str(ctx.author.id)] if notify_bool else [],
                "notify_enabled": notify_bool,
                "status": "open"
            }
            self.active_threads[str(discord_thread.id)] = thread_info
            save_json_data(ACTIVE_THREADS_FILE, self.active_threads)

            embed = discord.Embed(
                title="✅ ¡Hilo Creado Exitosamente!",
                description=f"Se ha iniciado el hilo: {discord_thread.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Nombre del Hilo", value=nombre_del_hilo, inline=False)
            if is_temporary and seconds_duration and expires_at_dt:
                embed.add_field(name="Duración Temporal", value=duracion_temporal, inline=True)
                # Formatear la fecha de expiración de forma más legible
                expira_str = expires_at_dt.strftime('%d de %B de %Y a las %H:%M:%S UTC')
                embed.add_field(name="Expira Aproximadamente", value=expira_str, inline=True)

            embed.add_field(name="Notificaciones para Participantes", value="Activadas" if notify_bool else "Desactivadas", inline=False)
            embed.set_footer(text=f"Hilo creado por: {ctx.author.display_name}")

            await ctx.send(embed=embed)

            # Editar el mensaje ancla del hilo
            await thread_message.edit(content=f"El hilo '{nombre_del_hilo}' ha sido iniciado por {ctx.author.mention}. ¡Únete a la conversación en {discord_thread.mention}!")

        except discord.Forbidden:
            await ctx.send("Error de permisos: No tengo los permisos necesarios para crear hilos en este canal. Asegúrate de que tengo el permiso 'Crear Hilos Públicos' (o 'Crear Hilos Privados' si aplica).")
        except discord.HTTPException as e:
            await ctx.send(f"Se produjo un error de comunicación con Discord al intentar crear el hilo: {e}")
        except Exception as e:
            await ctx.send(f"Ocurrió un error inesperado al crear el hilo: {e}. Revisa los logs para más detalles.")
            print(f"Error detallado en crearhilo: {e}")
            import traceback
            traceback.print_exc()


async def setup(bot):
    await bot.add_cog(ThreadManager(bot))
    # Crear archivos JSON si no existen al cargar el cog
    if not os.path.exists(THREAD_CHANNELS_FILE):
        save_json_data(THREAD_CHANNELS_FILE, {})
    if not os.path.exists(ACTIVE_THREADS_FILE):
        save_json_data(ACTIVE_THREADS_FILE, {})
