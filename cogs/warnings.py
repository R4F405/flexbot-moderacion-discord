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
            title="Usuario Advertido",
            description=f"{member.mention} ha recibido una advertencia.",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Razón", value=reason)
        embed.add_field(name="Advertencias totales", value=str(warning_count))
        embed.set_footer(text=f"Advertido por {ctx.author.name}")
        await ctx.send(embed=embed)

        if warning_count == 3:
            await ctx.send(f"{member.mention} ha recibido 3 advertencias. Considera tomar medidas adicionales.")

async def setup(bot):
    await bot.add_cog(Warnings(bot)) 