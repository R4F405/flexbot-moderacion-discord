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
                print(f"Error al parsear expires_at para el hilo {thread_id_str}: {expires_at_str}")
                continue

            if now_utc >= expires_at_dt:
                print(f"El hilo temporal {thread_id_str} ('{thread_info.get('name')}') ha expirado. Intentando archivar...")
                try:
                    guild = self.bot.get_guild(int(thread_info["guild_id"]))
                    if not guild:
                        print(f"No se encontró el servidor {thread_info['guild_id']} para el hilo {thread_id_str}")
                        # Considerar eliminar el hilo de active_threads si el servidor ya no existe o el bot no está en él
                        del self.active_threads[thread_id_str]
                        threads_updated = True
                        continue

                    # Intentar obtener el hilo desde la API de Discord
                    # discord.py v2.0+ usa guild.get_thread(thread_id) o bot.get_channel(thread_id) para hilos
                    # pero es mejor obtenerlo directamente si ya tenemos el ID.
                    # Necesitamos el objeto Thread para editarlo.

                    discord_thread = guild.get_thread(int(thread_id_str))
                    if not discord_thread:
                        # Si el hilo no se encuentra (quizás fue borrado manualmente), lo eliminamos de nuestros registros
                        print(f"Hilo {thread_id_str} no encontrado en el servidor. Eliminando de active_threads.")
                        del self.active_threads[thread_id_str]
                        threads_updated = True
                        continue

                    await discord_thread.edit(archived=True, locked=True)

                    # Opcional: Enviar un mensaje al hilo antes de archivarlo
                    try:
                        await discord_thread.send(f"Este hilo ('{thread_info['name']}') ha sido cerrado automáticamente porque su tiempo ha expirado.")
                    except discord.Forbidden:
                        print(f"No se pudo enviar mensaje de cierre al hilo {thread_id_str} (probablemente ya estaba archivado/bloqueado).")
                    except Exception as e:
                        print(f"Error enviando mensaje de cierre al hilo {thread_id_str}: {e}")


                    thread_info["status"] = "archived_expired"
                    # Podríamos eliminarlo de active_threads o simplemente cambiar el estado
                    # Por ahora, cambiamos el estado. Si se quisiera "limpiar" la lista, se eliminaría.
                    # del self.active_threads[thread_id_str]
                    threads_updated = True
                    print(f"Hilo {thread_id_str} archivado y bloqueado exitosamente.")

                except discord.Forbidden:
                    print(f"Error de permisos al intentar archivar el hilo {thread_id_str}.")
                    # Marcar para no reintentar constantemente si es un problema de permisos persistente
                    thread_info["status"] = "archival_failed_permissions"
                    threads_updated = True
                except discord.NotFound:
                    print(f"Hilo {thread_id_str} no encontrado al intentar archivar (quizás ya fue borrado). Eliminando de active_threads.")
                    if thread_id_str in self.active_threads: # Comprobar antes de borrar por si acaso
                        del self.active_threads[thread_id_str]
                    threads_updated = True
                except Exception as e:
                    print(f"Error inesperado al archivar el hilo {thread_id_str}: {e}")

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
            await ctx.send("Este comando solo puede usarse dentro de un hilo.")
            return

        thread_id_str = str(ctx.channel.id)
        thread_info = self.active_threads.get(thread_id_str)

        if not thread_info:
            await ctx.send("Este hilo no parece estar gestionado por el sistema de hilos personalizados, o ya ha sido cerrado y eliminado de los registros activos.")
            return

        if thread_info.get("status") != "open":
            await ctx.send(f"Este hilo ('{thread_info.get('name')}') ya no está activo (estado: {thread_info.get('status')}).")
            return

        try:
            discord_thread = ctx.channel # Ya estamos en el hilo

            if mensaje_opcional:
                try:
                    await discord_thread.send(f"**Anuncio de cierre:** {mensaje_opcional}\nEste hilo será archivado.")
                except discord.Forbidden:
                    await ctx.send("No pude enviar el mensaje opcional al hilo (quizás ya está archivado/bloqueado o no tengo permisos), pero intentaré cerrarlo.")
                except Exception as e:
                    await ctx.send(f"Error enviando mensaje opcional: {e}. Intentaré cerrar el hilo de todas formas.")

            await discord_thread.edit(archived=True, locked=True)

            thread_info["status"] = "archived_manual"
            # Opcionalmente, podríamos eliminarlo de active_threads si no queremos mantener un registro de hilos cerrados manualmente por mucho tiempo.
            # Por ahora, solo actualizamos el estado.
            save_json_data(ACTIVE_THREADS_FILE, self.active_threads)

            await ctx.send(f"Hilo '{thread_info['name']}' ({discord_thread.mention}) archivado y bloqueado manualmente.")
            # El mensaje de confirmación se envía al contexto original (el hilo mismo), lo que está bien.

        except discord.Forbidden:
            await ctx.send(f"Error: No tengo los permisos necesarios para archivar/bloquear este hilo.")
        except discord.HTTPException as e:
            await ctx.send(f"Error de API al intentar cerrar el hilo: {e}")
        except Exception as e:
            await ctx.send(f"Ocurrió un error inesperado al cerrar el hilo: {e}")
            print(f"Error en cerrarhilo: {e}")

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
        channel_id = str(channel.id)

        if guild_id not in self.thread_channels:
            self.thread_channels[guild_id] = []

        if channel_id in self.thread_channels[guild_id]:
            await ctx.send(f"El canal {channel.mention} ya está designado como un canal principal para hilos.")
            return

        self.thread_channels[guild_id].append(channel_id)
        save_json_data(THREAD_CHANNELS_FILE, self.thread_channels)
        await ctx.send(f"El canal {channel.mention} ha sido designado como un canal principal para hilos. Ahora se pueden crear hilos gestionados en él usando `!flex crearhilo`.")

    @commands.command(name="quitarhilocanal")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def remove_thread_channel(self, ctx, channel: discord.TextChannel):
        """Quita la designación de 'canal principal' para hilos de un canal de texto."""
        guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)

        if guild_id not in self.thread_channels or channel_id not in self.thread_channels[guild_id]:
            await ctx.send(f"El canal {channel.mention} no está designado actualmente como un canal principal para hilos.")
            return

        self.thread_channels[guild_id].remove(channel_id)
        if not self.thread_channels[guild_id]: # Si la lista queda vacía, eliminar la clave del servidor
            del self.thread_channels[guild_id]

        save_json_data(THREAD_CHANNELS_FILE, self.thread_channels)
        await ctx.send(f"El canal {channel.mention} ya no es un canal principal para hilos.")

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
            await ctx.send(f"Este comando solo puede usarse en un canal designado como 'principal para hilos'. Usa `!flex designarhilocanal` primero.")
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
                    await ctx.send("Unidad de tiempo no válida para `duracion_temporal`. Usa s, m, h, o d.")
                    return

                if seconds_duration <= 0:
                    await ctx.send("La duración temporal debe ser mayor que cero.")
                    return

                expires_at_dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_duration)
                expires_at_iso = expires_at_dt.isoformat()

            except ValueError:
                await ctx.send("Formato de `duracion_temporal` incorrecto. Ejemplo: 10m, 1h, 2d.")
                return
            except Exception as e: # Captura de otros posibles errores como slice en None si duracion_temporal es solo un caracter
                await ctx.send(f"Error procesando `duracion_temporal`: {e}")
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

            thread_info = {
                "name": nombre_del_hilo,
                "parent_channel_id": channel_id,
                "guild_id": guild_id,
                "creator_id": str(ctx.author.id),
                "discord_thread_id": str(discord_thread.id), # Guardamos el ID real del hilo de Discord
                "temporary": is_temporary,
                "duration_seconds": seconds_duration if seconds_duration else None,
                "created_at": created_at_iso,
                "expires_at": expires_at_iso, # Puede ser None si no es temporal
                "participants_to_notify": [str(ctx.author.id)] if notificar_participantes.lower() == 'si' else [],
                "notify_enabled": notificar_participantes.lower() == 'si',
                "status": "open" # open, archived
            }
            self.active_threads[str(discord_thread.id)] = thread_info
            save_json_data(ACTIVE_THREADS_FILE, self.active_threads)

            embed = discord.Embed(
                title="✅ Hilo Creado",
                description=f"Se ha creado el hilo: {discord_thread.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Nombre", value=nombre_del_hilo)
            if is_temporary and seconds_duration:
                embed.add_field(name="Duración", value=duracion_temporal)
                embed.add_field(name="Expira en (UTC)", value=expires_at_dt.strftime('%Y-%m-%d %H:%M:%S UTC') if expires_at_dt else "N/A")

            embed.add_field(name="Notificaciones", value="Activadas" if notificar_participantes.lower() == "si" else "Desactivadas")
            await ctx.send(embed=embed)
            # El mensaje inicial "Iniciando hilo..." puede ser borrado si se desea
            # await thread_message.delete()
            # O editado:
            await thread_message.edit(content=f"Hilo '{nombre_del_hilo}' creado por {ctx.author.mention}. ¡Únete a la conversación en {discord_thread.mention}!")


        except discord.Forbidden:
            await ctx.send("Error: No tengo los permisos necesarios para crear hilos en este canal.")
        except discord.HTTPException as e:
            await ctx.send(f"Error de API al crear el hilo: {e}")
        except Exception as e:
            await ctx.send(f"Ocurrió un error inesperado al crear el hilo: {e}")
            print(f"Error en crearhilo: {e}") # Log para el desarrollador


async def setup(bot):
    await bot.add_cog(ThreadManager(bot))
    # Crear archivos JSON si no existen al cargar el cog
    if not os.path.exists(THREAD_CHANNELS_FILE):
        save_json_data(THREAD_CHANNELS_FILE, {})
    if not os.path.exists(ACTIVE_THREADS_FILE):
        save_json_data(ACTIVE_THREADS_FILE, {})
