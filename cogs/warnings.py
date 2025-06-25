import discord # type: ignore
from discord.ext import commands # type: ignore
import json
import os
import datetime

class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = 'data/warnings.json'

    def load_warnings(self):
        if os.path.exists(self.warnings_file):
            with open(self.warnings_file, 'r') as f:
                return json.load(f)
        return {}

    def save_warnings(self, warnings):
        with open(self.warnings_file, 'w') as f:
            json.dump(warnings, f)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No se proporcionó razón"):
        warnings = self.load_warnings()
        server_id = str(ctx.guild.id)
        user_id = str(member.id)

        if server_id not in warnings:
            warnings[server_id] = {}

        if user_id not in warnings[server_id]:
            warnings[server_id][user_id] = []

        warnings[server_id][user_id].append({
            "reason": reason,
            "timestamp": datetime.datetime.now().isoformat(),
            "moderator": str(ctx.author.id)
        })

        self.save_warnings(warnings)

        warning_count = len(warnings[server_id][user_id])

        embed = discord.Embed(
            title="⚠️ Usuario Advertido",
            description=f"El usuario {member.mention} ha recibido una advertencia.",
            color=discord.Color.yellow(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Razón de la Advertencia", value=reason, inline=False)
        embed.add_field(name="Número Total de Advertencias", value=str(warning_count), inline=False)
        embed.set_footer(text=f"Advertencia emitida por: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        try:
            await ctx.send(embed=embed)
            # Considerar enviar un DM al usuario advertido (opcional y configurable)
            # try:
            # await member.send(f"Has recibido una advertencia en el servidor '{ctx.guild.name}' por la siguiente razón: {reason}. Tienes {warning_count} advertencia(s) en total.")
            # except discord.Forbidden:
            # await ctx.send(f"No se pudo notificar a {member.mention} por DM sobre la advertencia.", delete_after=10)
        except discord.HTTPException as e:
            await ctx.send(f"Error al enviar el mensaje de advertencia: {e}")


        if warning_count >= 3: # Podría ser configurable
            await ctx.send(f"Atención moderadores: {member.mention} ha acumulado {warning_count} advertencias. Se recomienda revisar su caso y considerar medidas adicionales si es necesario.")

async def setup(bot):
    await bot.add_cog(Warnings(bot)) 