import discord
from discord.ext import commands
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "welcome", "config.json")

with open(CONFIG_PATH, "r") as f:
    conf = json.load(f)

WELCOME_CHANNEL_ID = conf["arrived_channel_id"]
LEAVE_CHANNEL_ID = conf["leave_channel_id"]


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="?? Bienvenue chez KYOMA !",
            description=(
                f"Bienvenue {member.mention} ! ?\n\n"
                f"Installe-toi confortablement, discute dans les salons pour monter de niveau et tente ta chance au casino !\n\n"
                f"Nous sommes maintenant **{member.guild.member_count}** membres."
            ),
            color=discord.Color.from_rgb(114, 55, 178) 
        )
        
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID du membre : {member.id}")

        await channel.send(content=member.mention, embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.get_channel(LEAVE_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="?? Un membre nous a quittés",
            description=(
                f"Au revoir {member.name}... \n\n"
                f"Merci pour ton passage sur KYOMA.\n"
                f"Il reste désormais {member.guild.member_count} membres sur le serveur."
            ),
            color=discord.Color.red()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID du membre : {member.id}")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[OK] Welcome cog loaded")


async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))