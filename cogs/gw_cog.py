import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import sqlite3
import random
import asyncio

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gw", "database.db")

def has_role_permission(*role_ids):
        async def predicate(interaction: discord.Interaction):
            if any(role.id in role_ids for role in interaction.user.roles):
                return True
            await interaction.response.send_message("❌ Permission refusée", ephemeral=True)
            return False
        return commands.check(predicate)

class GWCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class GWView(discord.ui.View):
        def __init__(self, giveaway_id):
            super().__init__(timeout=None)
            self.giveaway_id = giveaway_id

        @discord.ui.button(
            label="🎁 Participer",
            style=discord.ButtonStyle.green,
            custom_id="join_giveaway_button"
        )
        async def join_giveaway(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):
            user = interaction.user

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
            SELECT 1 FROM participants
            WHERE giveaway_id = ?
            AND user_id = ?
            """, (self.giveaway_id, user.id))

            result = cursor.fetchone()

            if result:
                await interaction.response.send_message(
                    "❌ Vous participez déjà à ce giveaway.",
                    ephemeral=True
                )
                conn.close()
                return

            cursor.execute("""
            INSERT INTO participants(
                giveaway_id,
                user_id
            )
            VALUES (?, ?)
            """, (self.giveaway_id, user.id))

            conn.commit()
            conn.close()

            await interaction.response.send_message(
                "✅ Participation enregistrée.",
                ephemeral=True
            )

    @app_commands.command(name="gw-help", description="Afficher l'aide des giveaways")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def help_gw(self, interaction: discord.Interaction):
        helps = """
**Commandes de giveaway:**

`/giveaway <durée> <gagnants> <prix>` → Créer un giveaway avec la durée en minutes, le nombre de gagnants et le prix à gagner
`/winners` → Afficher les gagnants de tous les giveaway
"""
        await interaction.response.send_message(embed=discord.Embed(title="Aide Giveaways", description=helps, color=discord.Color.from_rgb(255, 255, 255)))

    @app_commands.command(name="giveaway", description="Créer un giveaway")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def giveaway(
        self,
        interaction: discord.Interaction,
        time: int,
        winners_count: int,
        prize: str
    ):
        from datetime import datetime, timedelta

        
        await interaction.response.defer(ephemeral=False)

        end_time = datetime.now() + timedelta(minutes=time)
        discord_timestamp = int(end_time.timestamp())

        embed = discord.Embed(
            title="🎁 Giveaway",
            description=(
                f"🎉 Prize : **{prize}**\n\n"
                f"👑 Gagnants : **{winners_count}**\n"
                f"⏳ Fin : <t:{discord_timestamp}:R>"
            ),
            color=discord.Color.blurple()
        )

        message = await interaction.followup.send(embed=embed)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO giveaways(
            message_id,
            channel_id,
            prize,
            winners_count,
            end_time
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            message.id,
            interaction.channel.id,
            prize,
            winners_count,
            discord_timestamp
        ))

        conn.commit()
        giveaway_id = cursor.lastrowid
        conn.close()

        await message.edit(
            view=self.GWView(giveaway_id)
        )

        await asyncio.sleep(time * 60)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT user_id FROM participants
        WHERE giveaway_id = ?
        """, (giveaway_id,))

        participants = cursor.fetchall()
        participants = [p[0] for p in participants]

        if len(participants) == 0:
            await interaction.followup.send(
                f"❌ Aucun participant pour **{prize}**"
            )
            conn.close()
            return

        winners_count = min(
            winners_count,
            len(participants)
        )

        selected_winners = random.sample(
            participants,
            winners_count
        )

        for winner_id in selected_winners:
            cursor.execute("""
            INSERT INTO winners(
                giveaway_id,
                user_id,
                prize
            )
            VALUES (?, ?, ?)
            """, (
                giveaway_id,
                winner_id,
                prize
            ))

        conn.commit()
        conn.close()

        mentions = [
            f"<@{winner_id}>"
            for winner_id in selected_winners
        ]

        await interaction.followup.send(
            f"🎉 Giveaway terminé !\n\n"
            f"🎁 Prize : **{prize}**\n"
            f"👑 Gagnant(s) : {', '.join(mentions)}"
        )

    @app_commands.command(name="winners", description="Afficher les gagnants des giveaways")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def winners(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT user_id, prize
        FROM winners
        """)

        results = cursor.fetchall()
        conn.close()

        if not results:
            await interaction.response.send_message(
                "❌ Aucun gagnant enregistré.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🏆 Gagnants des Giveaways",
            color=discord.Color.gold()
        )

        description = ""

        for user_id, prize in results:
            member = interaction.guild.get_member(user_id)
            if not member:
                continue

            description += (
                f"👑 <@{user_id}> "
                f"a gagné **{prize}**\n"
            )

        if len(description) > 4000:
            description = description[:4000]

        embed.description = description

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[OK] Giveaway cog loaded")


async def setup(bot):
    await bot.add_cog(GWCog(bot))
