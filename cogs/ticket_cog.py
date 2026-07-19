import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import has_permissions
import os
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "CASINO", "casino_config.json")

with open(CONFIG_PATH, "r") as f:
    casino_conf = json.load(f)

claim_admin = [] #<-- Enter the IDs of the roles that can retrieve the tickets

LOGS_CHANNEL_ID = None #<-- Set the ID of the ticket logs channel



def has_role_permission(*role_ids):
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            await interaction.response.send_message("❌ Pas en DM", ephemeral=True)
            return False

        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            await interaction.response.send_message("❌ Membre introuvable", ephemeral=True)
            return False

        user_roles = [role.id for role in member.roles]
        if any(r in role_ids for r in user_roles):
            return True

        await interaction.response.send_message("❌ Permission refusée", ephemeral=True)
        return False
    

    return app_commands.check(predicate)
    
    
class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed_by = None

    @discord.ui.button(
        label="🔑 Claim",
        style=discord.ButtonStyle.blurple,
        custom_id="claim_ticket_button"
    )
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_admin = any(role.id in claim_admin for role in interaction.user.roles)

        if not is_admin:
            await interaction.response.send_message("❌ Vous ne pouvez pas claim ce ticket.", ephemeral=True)
            return

        if self.claimed_by:
            await interaction.response.send_message("❌ Ticket déjà claim.", ephemeral=True)
            return

        self.claimed_by = interaction.user

        embed = discord.Embed(
            description=f"🔑 Ticket claim par {interaction.user.mention}",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(
        label="📄 Logs",
        style=discord.ButtonStyle.gray,
        custom_id="logs_ticket_button"
    )
    async def logs_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_admin = any(role.id in claim_admin for role in interaction.user.roles)

        if not is_admin:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser les logs.", ephemeral=True)
            return

        logs = ""
        async for message in interaction.channel.history(limit=None, oldest_first=True):
            logs += f"[{message.created_at}] {message.author} : {message.content}\n"

        with open("logs.txt", "w", encoding="utf-8") as f:
            f.write(logs)

        logs_channel = interaction.guild.get_channel(LOGS_CHANNEL_ID)
        if logs_channel:
            await logs_channel.send(f"📄 Logs du ticket {interaction.channel.name}", file=discord.File("logs.txt"))

        await interaction.response.send_message("✅ Logs envoyés.", ephemeral=True)

    @discord.ui.button(
        label="❌ Fermer",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket_button"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            ticket_owner_id = int(interaction.channel.topic)
        except (ValueError, TypeError):
            ticket_owner_id = None

        is_owner = interaction.user.id == ticket_owner_id
        is_admin = any(role.id in claim_admin for role in interaction.user.roles)

        if not is_owner and not is_admin:
            await interaction.response.send_message("❌ Vous ne pouvez pas fermer ce ticket.", ephemeral=True)
            return

        await interaction.response.send_message("🗑️ Le ticket sera supprimé dans 5 secondes...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎫 Créer un ticket",
        style=discord.ButtonStyle.green,
        custom_id="create_ticket_button"
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        existing = discord.utils.get(guild.channels, name=f"ticket-{user.name.lower()}")
        if existing:
            await interaction.response.send_message("❌ Vous avez déjà un ticket ouvert.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        for role_id in claim_admin:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name.lower()}",
            overwrites=overwrites,
            topic=str(user.id)
        )

        embed = discord.Embed(
            title="🎫 Ticket créé",
            description=f"Bienvenue {user.mention}\n\nUn membre du staff va vous répondre.",
            color=discord.Color.green()
        )

        await channel.send(embed=embed, view=TicketCloseView())
        await interaction.response.send_message(f"✅ Ticket créé : {channel.mention}", ephemeral=True)

    

class AccesCasinoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔐Accès", style=discord.ButtonStyle.blurple, custom_id="assec")
    async def acces(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        role_id = casino_conf["casino_role_id"]
        role = interaction.guild.get_role(role_id)

        if role and any(r.id == role_id for r in user.roles):
            await interaction.response.send_message("❌ Vous avez déjà accès au casino", ephemeral=True)
        elif role:
            await user.add_roles(role)


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="acces", description="Obtenir l'accès au casino")
    @has_permissions(administrator=True)
    async def acces(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔐Accès Casino",
            description="Pour avoir accès au Casino👇",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=AccesCasinoView())

    @app_commands.command(name="panel", description="Ouvrir le panel de support")
    @has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support",
            description="Si vous avez des questions!!!\n👇",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=TicketMainView())

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketMainView())
        self.bot.add_view(AccesCasinoView())
        self.bot.add_view(TicketCloseView())
        print(f"[OK] Ticket cog loaded")


async def setup(bot):
    await bot.add_cog(TicketCog(bot))