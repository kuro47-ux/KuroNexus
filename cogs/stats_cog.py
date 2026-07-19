import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "stats", "database.db")

MEMBER_CHANNEL_ID = None #<-- Place the voice or text channel id that will display the member count


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_join_times = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[OK] Stats cog loaded")
        if not self.update_member_channel.is_running():
            self.update_member_channel.start()

    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.get_channel(MEMBER_CHANNEL_ID)
        if channel:
            try:
                await channel.edit(name=f"👥 Membres : {member.guild.member_count}")
            except Exception as e:
                print(f"Erreur mise à jour salon (join) : {e}")

    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.get_channel(MEMBER_CHANNEL_ID)
        if channel:
            try:
                await channel.edit(name=f"👥 Membres : {member.guild.member_count}")
            except Exception as e:
                print(f"Erreur mise à jour salon (remove) : {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        await self.add_stat(
            message.author.id,
            "messages",
            1
        )

    @commands.Cog.listener()
    async def on_command(self, ctx):
        await self.add_stat(
            ctx.author.id,
            "commands_used",
            1
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            self.voice_join_times[member.id] = datetime.now()

        elif before.channel is not None and after.channel is None:
            if member.id in self.voice_join_times:
                join_time = self.voice_join_times[member.id]

                total_seconds = int(
                    (datetime.now() - join_time).total_seconds()
                )

                await self.add_stat(
                    member.id,
                    "vocal_seconds",
                    total_seconds
                )

                del self.voice_join_times[member.id]

    @app_commands.command(name="stats-help", description="Afficher l'aide des statistiques")
    async def help_stats(self, interaction: discord.Interaction):
        helps = """
**Commandes de statistiques:**

`/stats [membre]` → Afficher ses stats
`/servstats` → Afficher stats du serveur
`/top-vocal` → afficher le top vocal du serveur
`/top-messages` → afficher le top message du serveur
`/leaderboard` → afficher le top global du serveur
"""
        await interaction.response.send_message(embed=discord.Embed(title="Aide Statistiques", description=helps, color=discord.Color.from_rgb(255, 255, 255)))

    def create_user(self, user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR IGNORE INTO stats(user_id) VALUES (?)",
            (user_id,)
        )

        conn.commit()
        conn.close()

    def add_stat(self, user_id, column, amount):
        self.create_user(user_id)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(f"""
        UPDATE stats
        SET {column} = {column} + ?
        WHERE user_id = ?
        """, (amount, user_id))

        conn.commit()
        conn.close()

    def create_stats_graph(self, messages, vocal_hours, giveaways, commands_used, user_id):
        labels = [
            "Messages",
            "Vocal",
            "Giveaways",
            "Commandes"
        ]

        values = [
            messages,
            vocal_hours,
            giveaways,
            commands_used
        ]

        plt.style.use("dark_background")

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(
            labels,
            values,
            linewidth=2,
            edgecolor="white"
        )

        colors = [
            "#5865F2",
            "#57F287",
            "#FEE75C",
            "#EB459E"
        ]

        for bar, color in zip(bars, colors):
            bar.set_color(color)

        ax.set_title(
            "Discord Statistics",
            fontsize=22,
            fontweight="bold",
            pad=20
        )

        ax.grid(
            True,
            linestyle="--",
            alpha=0.3
        )

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        ax.tick_params(axis='x', labelsize=13)
        ax.tick_params(axis='y', labelsize=11)

        for bar in bars:
            height = bar.get_height()

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{height}',
                ha='center',
                va='bottom',
                fontsize=12,
                fontweight='bold'
            )

        fig.patch.set_facecolor('#111111')
        ax.set_facecolor('#1e1f22')

        plt.tight_layout()

        file_name = f"stats_{user_id}.png"

        plt.savefig(
            file_name,
            dpi=300,
            bbox_inches='tight'
        )

        plt.close()

        return file_name

    @app_commands.command(name="stats", description="Afficher ses statistiques")
    async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user

        self.create_user(member.id)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            messages,
            vocal_seconds,
            giveaways_won,
            commands_used
        FROM stats
        WHERE user_id = ?
        """, (member.id,))

        result = cursor.fetchone()
        conn.close()

        messages = result[0]
        vocal_seconds = result[1]
        giveaways = result[2]
        commands_used = result[3]

        vocal_hours = round(vocal_seconds / 3600, 2)

        graph = self.create_stats_graph(
            messages,
            vocal_hours,
            giveaways,
            commands_used,
            member.id
        )

        embed = discord.Embed(
            title=f"📊 Stats de {member}",
            description="Voici vos statistiques complètes.",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="💬 Messages", value=f"{messages}", inline=True)
        embed.add_field(name="🎙️ Temps vocal", value=f"{vocal_hours}h", inline=True)
        embed.add_field(name="🎁 Giveaways gagnés", value=f"{giveaways}", inline=True)
        embed.add_field(name="⚡ Commandes", value=f"{commands_used}", inline=True)

        file = discord.File(graph, filename="stats.png")
        embed.set_image(url="attachment://stats.png")

        await interaction.response.send_message(embed=embed, file=file)

        if os.path.exists(graph):
            os.remove(graph)

    @app_commands.command(name="servstats", description="Afficher les statistiques du serveur")
    async def servstats(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            SUM(messages),
            SUM(vocal_seconds),
            SUM(giveaways_won),
            SUM(commands_used)
        FROM stats
        """)

        result = cursor.fetchone()
        conn.close()

        total_messages = result[0] or 0
        total_vocal = result[1] or 0
        total_giveaways = result[2] or 0
        total_commands = result[3] or 0

        vocal_hours = round(total_vocal / 3600, 2)

        graph = self.create_stats_graph(
            total_messages,
            vocal_hours,
            total_giveaways,
            total_commands,
            "server"
        )

        embed = discord.Embed(
            title="📈 Stats du Serveur",
            description="Statistiques globales du serveur.",
            color=discord.Color.green()
        )

        embed.add_field(name="👥 Membres", value=interaction.guild.member_count, inline=False)
        embed.add_field(name="💬 Messages", value=total_messages, inline=True)
        embed.add_field(name="🎙️ Vocal", value=f"{vocal_hours}h", inline=True)
        embed.add_field(name="🎁 Giveaways", value=total_giveaways, inline=True)
        embed.add_field(name="⚡ Commandes", value=total_commands, inline=True)

        file = discord.File(graph, filename="server_stats.png")
        embed.set_image(url="attachment://server_stats.png")

        await interaction.response.send_message(embed=embed, file=file)

        if os.path.exists(graph):
            os.remove(graph)

    @app_commands.command(name="top-vocal", description="Afficher le top vocal du serveur")
    async def topvocal(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            user_id,
            vocal_seconds
        FROM stats
        ORDER BY vocal_seconds DESC
        LIMIT 10
        """)

        results = cursor.fetchall()
        conn.close()

        embed = discord.Embed(
            title="🎙️ Top Vocal",
            color=discord.Color.blurple()
        )

        description = ""
        medals = ["🥇", "🥈", "🥉"]

        for index, (user_id, vocal) in enumerate(results):
            member = interaction.guild.get_member(user_id)
            if not member:
                continue

            hours = vocal // 3600
            minutes = (vocal % 3600) // 60

            medal = medals[index] if index < 3 else f"`#{index+1}`"
            description += f"{medal} {member.mention}\n⏱️ {hours}h {minutes}m\n\n"

        embed.description = description
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="top-messages", description="Afficher le top messages du serveur")
    async def topmessages(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            user_id,
            messages
        FROM stats
        ORDER BY messages DESC
        LIMIT 10
        """)

        results = cursor.fetchall()
        conn.close()

        embed = discord.Embed(
            title="💬 Top Messages",
            color=discord.Color.green()
        )

        description = ""
        medals = ["🥇", "🥈", "🥉"]

        for index, (user_id, messages) in enumerate(results):
            member = interaction.guild.get_member(user_id)
            if not member:
                continue

            medal = medals[index] if index < 3 else f"`#{index+1}`"
            description += f"{medal} {member.mention}\n💬 {messages} messages\n\n"

        embed.description = description
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Afficher le leaderboard global")
    async def leaderboard(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            user_id,
            (
                messages +
                vocal_seconds / 60 +
                giveaways_won * 500 +
                commands_used * 5
            ) as score
        FROM stats
        ORDER BY score DESC
        LIMIT 10
        """)

        results = cursor.fetchall()
        conn.close()

        embed = discord.Embed(
            title="🏆 Leaderboard Global",
            color=discord.Color.gold()
        )

        description = ""
        medals = ["🥇", "🥈", "🥉"]

        for index, (user_id, score) in enumerate(results):
            member = interaction.guild.get_member(user_id)
            if not member:
                continue

            medal = medals[index] if index < 3 else f"`#{index+1}`"
            description += f"{medal} {member.mention} • `{int(score)} pts`\n"

        embed.description = description
        await interaction.response.send_message(embed=embed)

    @tasks.loop(seconds=10)
    async def update_member_channel(self):
        for guild in self.bot.guilds:
            channel = guild.get_channel(MEMBER_CHANNEL_ID)
            if channel:
                try:
                    await channel.edit(name=f"👥 Membres : {guild.member_count}")
                except Exception as e:
                    print(f"Erreur d'édition du salon de compteurs : {e}")


async def setup(bot):
    await bot.add_cog(StatsCog(bot))