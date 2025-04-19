import discord # type: ignore
from discord.ext import commands # type: ignore

class Info(commands.Cog):
    """
    Sistema de información del bot.
    Proporciona comandos para ver la información disponible tanto para usuarios como para moderadores.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info")
    async def user_info(self, ctx):
        """
        Muestra información sobre los comandos disponibles para usuarios.
        
        Uso:
        !flex info
        """
        embed = discord.Embed(
            title="📚 Comandos Disponibles para Usuarios",
            description="Lista de comandos que puedes utilizar en el servidor",
            color=discord.Color.blue()
        )

        # Comandos Generales
        embed.add_field(
            name="🔰 Comandos Generales",
            value=(
                "**!flex info** - Muestra este mensaje de ayuda\n"
                "**!flex report @usuario razón** - Reporta a un usuario por mal comportamiento\n"
            ),
            inline=False
        )

        # Pie de página con información adicional
        embed.set_footer(text="Si necesitas reportar algún problema, usa !flex report")
        
        await ctx.send(embed=embed)

    @commands.command(name="info2")
    @commands.has_permissions(manage_messages=True)
    async def mod_info(self, ctx):
        """
        Muestra información sobre los comandos disponibles para moderadores.
        Requiere permisos de moderación.
        
        Uso:
        !flex info2
        """
        embed = discord.Embed(
            title="🛡️ Comandos de Moderación",
            description="Lista de comandos disponibles para el equipo de moderación",
            color=discord.Color.red()
        )

        # Comandos de Moderación Básicos
        embed.add_field(
            name="⚔️ Moderación Básica",
            value=(
                "**!flex kick @usuario [razón]** - Expulsa a un usuario del servidor\n"
                "**!flex ban @usuario [razón]** - Banea a un usuario del servidor\n"
                "**!flex unban ID_usuario [razón]** - Desbanea a un usuario\n"
                "**!flex mute @usuario [duración] [razón]** - Silencia a un usuario\n"
                "**!flex unmute @usuario [razón]** - Remueve el silencio de un usuario\n"
            ),
            inline=False
        )

        # Sistema de Reportes
        embed.add_field(
            name="📋 Sistema de Reportes",
            value=(
                "**!flex reports** - Muestra los reportes pendientes\n"
                "**!flex reports resuelto** - Muestra los reportes resueltos\n"
                "**!flex reports todos** - Muestra todos los reportes\n"
            ),
            inline=False
        )

        # Comandos de Información
        embed.add_field(
            name="🔍 Comandos de Información",
            value=(
                "**!flex userinfo @usuario** - Muestra información detallada de un usuario\n"
                "• ID, roles, fecha de ingreso, infracciones, etc.\n"
                "**!flex serverinfo** - Muestra información detallada del servidor\n"
                "• Estadísticas, configuración, roles, canales, etc.\n"
            ),
            inline=False
        )

        # Anti-Spam y Configuración
        embed.add_field(
            name="⚙️ Configuración y Anti-Spam",
            value=(
                "El sistema anti-spam está activo automáticamente:\n"
                "• Detecta spam (5 mensajes en 3 segundos)\n"
                "• Silencia automáticamente por 5 minutos\n"
                "• Los moderadores están exentos\n"
            ),
            inline=False
        )

        # Consejos para moderadores
        embed.add_field(
            name="💡 Consejos para Moderadores",
            value=(
                "• Siempre proporciona una razón al tomar acciones de moderación\n"
                "• Revisa regularmente el canal #reportes\n"
                "• Documenta las acciones tomadas en el canal de logs\n"
                "• Sigue el protocolo de moderación establecido\n"
            ),
            inline=False
        )

        embed.set_footer(text="Recuerda: Con el poder viene la responsabilidad. Usa estos comandos sabiamente.")
        
        # Enviar el mensaje en el canal actual
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot)) 