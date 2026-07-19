import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
import sqlite3
import time
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "admin", "database.db")

def has_role_permission(*role_ids):
    
    if role_ids == None:
        return
    
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



class MuteSelect(discord.ui.Select):
    def __init__(self, member: discord.Member, cog_instance):
        self.member = member
        self.cog_instance = cog_instance

        options = [
            discord.SelectOption(label="Insulte", value="insulte"),
            discord.SelectOption(label="Pub", value="pub"),
            discord.SelectOption(label="Spam", value="spam"),
            discord.SelectOption(label="Double Compte", value="dcompte"),
            discord.SelectOption(label="Soundboard", value="soundboard"),
            discord.SelectOption(label="Troll", value="troll")
        ]
        super().__init__(placeholder="Choisis une raison de mute", options=options)

    async def callback(self, interaction: discord.Interaction):
        choix = self.values[0]
        sanctions = {
            "insulte": (20, "insulte"),
            "pub": (40, "pub"),
            "spam": (25, "spam"),
            "dcompte": (60, "double compte"),
            "soundboard": (30, "soundboard"),
            "troll": (15, "troll")
        }

        minutes, raison = sanctions[choix]
        ROLE_ID = None #<-- Assign the role that is to be given to the mute person
        role = interaction.guild.get_role(ROLE_ID)

        if not role:
            await interaction.response.send_message("❌ Rôle de mute introuvable sur le serveur.", ephemeral=True)
            return

        await self.cog_instance.add_temp_role(self.member, role, minutes, raison)

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Mute 🔇",
                description=f"{self.member.mention} a été mute {minutes} minutes pour **{raison}**.",
                color=discord.Color.from_rgb(255, 255, 255)
            ),
            ephemeral=False
        )

class MuteView(discord.ui.View):
    def __init__(self, member: discord.Member, cog_instance):
        super().__init__(timeout=120)
        self.add_item(MuteSelect(member, cog_instance))




class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.antispam_enabled = True
        self.antispam_limit = 5
        self.antispam_interval = 5

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[OK] Admin cog loaded")
        if not self.check_temp_roles.is_running():
            self.check_temp_roles.start()

    async def add_temp_role(self, member: discord.Member, role: discord.Role, minutes: int, raison: str):
        await member.add_roles(role)
        end_time = int(time.time()) + (minutes * 60)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO temp_roles (user_id, role_id, guild_id, end_time, raison) VALUES (?, ?, ?, ?, ?)",
            (member.id, role.id, member.guild.id, end_time, raison)
        )
        conn.commit()
        conn.close()

    def is_excluded(self, user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM excluded_users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if not self.antispam_enabled or self.is_excluded(message.author.id):
            return

        now = time.time()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO messages (user_id, timestamp) VALUES (?, ?)", (message.author.id, now))
        cursor.execute("DELETE FROM messages WHERE timestamp < ?", (now - self.antispam_interval,))
        cursor.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (message.author.id,))
        count = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        if count >= self.antispam_limit:
            try:
                await message.delete()
                await message.author.timeout(timedelta(seconds=10), reason="Anti-Spam")
                await message.author.send(embed=discord.Embed(
                    title="Timeout ⚠️", 
                    description=f"{message.author.mention}, merci d'arrêter de spam.", 
                    color=discord.Color.red()
                ))
            except:
                pass



    @app_commands.command(name="admin-help", description="Afficher l'aide administrative")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def help(self, interaction: discord.Interaction):
        helps = """
**Commandes d'administration:**
`/ban <utilisateur> [raison]` → Bannir l'utilisateur donné
`/unban <id_utilisateur>` → Débannir l'utilisateur via son ID
`/banlist` → Afficher les utilisateurs bannis
`/include-spam <utilisateur>` → Ajouter un utilisateur à la liste d'exclusion
`/exclude-spam <utilisateur>` → Retirer un utilisateur de la liste d'exclusion
`/sanctions <id_utilisateur>` → Afficher les sanctions sur un membre
`/clear-sanction <id_utilisateur>` → Supprimer toutes les sanctions d'un membre
`/clear-all-sanctions` → Vider la table des sanctions
`/delete-sanction <id_utilisateur> <num>` → Supprimer une sanction spécifique
`/mute <utilisateur>` → Ouvrir le menu de mute temporaire
`/unmute <utilisateur>` → Retirer le rôle de mute de l'utilisateur
`/mute-list` → Afficher la liste des mutes actifs
`/lock [salon]` → Fermer le salon actuel ou spécifié
`/unlock [salon]` → Ouvrir le salon actuel ou spécifié
`/add-role <utilisateur> <role>` → Ajouter un rôle
`/delete-role <utilisateur> <role>` → Enlever un rôle
`/derank <utilisateur>` → Retirer tous les rôles d'un membre
`/antispam <on/off>` → Activer ou désactiver l'antispam global
`/set-antispam <messages> <secondes>` → Configurer le seuil de l'antispam
`/purge <nombre>` → Supprimer un nombre de messages donnés
"""
        await interaction.response.send_message(embed=discord.Embed(title="Aide Administrative", description=helps, color=discord.Color.from_rgb(255, 255, 255)))

    @app_commands.command(name="ban", description="Bannir un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def ban(self, interaction: discord.Interaction, member: discord.Member, raison: str = "Aucune raison"):
        date_str = datetime.now().strftime("%d/%m/%y")
        embed = discord.Embed(title="Ban 🔨", description=f"Le membre {member.mention} a été banni pour : {raison}", color=discord.Color.red())
        
        await member.ban(reason=raison)
        await interaction.response.send_message(embed=embed)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sanctions_user (user_id, sanction, date) VALUES (?, ?, ?)", (member.id, f"ban: {raison}", date_str))
        conn.commit()
        conn.close()

    @app_commands.command(name="unban", description="Débannir un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(embed=discord.Embed(title="UnBan 🔨", description=f"L'utilisateur {user.name} a été débanni.", color=discord.Color.green()))
        except Exception:
            await interaction.response.send_message("❌ Impossible de trouver ou débannir cet utilisateur. Vérifie l'ID.", ephemeral=True)

    @app_commands.command(name="banlist", description="Afficher la liste des utilisateurs bannis")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def banlist(self, interaction: discord.Interaction):
        bans = [entry async for entry in interaction.guild.bans()]
        if not bans:
            await interaction.response.send_message(embed=discord.Embed(title="Liste des bannis", description="Aucun utilisateur n'est banni actuellement. ✅", color=discord.Color.green()))
            return

        message = "\n".join([f"- {entry.user} (ID: {entry.user.id})" for entry in bans])
        await interaction.response.send_message(embed=discord.Embed(title="Liste des membres bannis 🔨", description=message, color=discord.Color.orange()))

    @app_commands.command(name="include-spam", description="Ajouter un utilisateur à la liste d'exclusion pour le spam")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def include_spam(self, interaction: discord.Interaction, membre: discord.Member):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO excluded_users (user_id) VALUES (?)", (membre.id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(embed=discord.Embed(title="Spam List", description=f"Le membre {membre.mention} a été ajouté à la liste d'exclusion.", color=discord.Color.green()))

    @app_commands.command(name="exclude-spam", description="Retirer un utilisateur de la liste d'exclusion pour le spam")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def exclude_spam(self, interaction: discord.Interaction, membre: discord.Member):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM excluded_users WHERE user_id = ?", (membre.id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(embed=discord.Embed(title="Spam List", description=f"Le membre {membre.mention} a été retiré de la liste d'exclusion.", color=discord.Color.orange()))

    @app_commands.command(name="lock", description="Fermer un salon")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        channel = channel or interaction.channel
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message(embed=discord.Embed(title="Lock 🔒", description=f"Le salon {channel.mention} a été verrouillé.", color=discord.Color.red()))

    @app_commands.command(name="unlock", description="Ouvrir un salon")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        channel = channel or interaction.channel
        await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message(embed=discord.Embed(title="Unlock 🔓", description=f"Le salon {channel.mention} a été réouvert.", color=discord.Color.green()))

    @app_commands.command(name="sanctions", description="Afficher les sanctions d'un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def sanctions(self, interaction: discord.Interaction, user_id: str):

        clean_id = user_id.replace("<@", "").replace(">", "").replace("!", "")
        
        try:
            target_id = int(clean_id)
            member = await self.bot.fetch_user(target_id)
        except ValueError:
            await interaction.response.send_message("❌ ID invalide. Donne un ID composé uniquement de chiffres.", ephemeral=True)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, sanction, date FROM sanctions_user WHERE user_id = ?", (target_id,))
        sc = cursor.fetchall()
        conn.close()

        if not sc:
            await interaction.response.send_message(f"❌ Aucune sanction enregistrée pour {member.name}.")
            return

        sanctions_text = "\n".join([f"**#{i}** | {s[1]} ({s[2]})" for i, s in enumerate(sc, start=1)])
        await interaction.response.send_message(embed=discord.Embed(title=f"Sanctions de {member.name}", description=sanctions_text, color=discord.Color.orange()))

    @app_commands.command(name="clear-sanction", description="Supprimer toutes les sanctions d'un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def clearsanction(self, interaction: discord.Interaction, user_id: str):
        clean_id = user_id.replace("<@", "").replace(">", "").replace("!", "")
        try:
            target_id = int(clean_id)
        except ValueError:
            await interaction.response.send_message("❌ ID invalide.", ephemeral=True)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sanctions_user WHERE user_id = ?", (target_id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(embed=discord.Embed(title="Sanctions effacées", description="Toutes les sanctions de l'utilisateur ont été supprimées.", color=discord.Color.green()))

    @app_commands.command(name="delete-sanction", description="Supprimer une sanction spécifique d'un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def delsanction(self, interaction: discord.Interaction, user_id: str, numero: int):
        clean_id = user_id.replace("<@", "").replace(">", "").replace("!", "")
        try:
            target_id = int(clean_id)
        except ValueError:
            await interaction.response.send_message("❌ ID invalide.", ephemeral=True)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, sanction, date FROM sanctions_user WHERE user_id = ?", (target_id,))
        sc = cursor.fetchall()

        if not sc or numero < 1 or numero > len(sc):
            await interaction.response.send_message("❌ Numéro invalide ou aucune sanction trouvée.", ephemeral=True)
            conn.close()
            return

        true_id = sc[numero - 1][0]
        cursor.execute("DELETE FROM sanctions_user WHERE id = ?", (true_id,))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"✅ La sanction **#{numero}** a bien été retirée.")
        
        
    @app_commands.command(name="mute", description="Muter un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def mute(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message("Choisissez une option :", view=MuteView(member, self), ephemeral=True)

    @app_commands.command(name="unmute", description="Démuter un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        role = member.guild.get_role(1489709474263339190)
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(embed=discord.Embed(title="UnMute 🔈", description=f"Le membre {member.mention} a été unmute.", color=discord.Color.green()))
        else:
            await interaction.response.send_message("❌ Ce membre n'est pas mute.", ephemeral=True)

    @app_commands.command(name="mute-list", description="Afficher la liste des mutes")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def mutelist(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, raison FROM temp_roles")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message(embed=discord.Embed(title="Mute List 🔇", description="Aucun mute actif actuellement.", color=discord.Color.green()))
            return

        lines = [f"{i+1}. <@{user_id}> ➜ {raison}" for i, (user_id, raison) in enumerate(rows)]
        await interaction.response.send_message(embed=discord.Embed(title="Mutes en cours 🔇", description="\n".join(lines), color=discord.Color.orange()))

    @app_commands.command(name="add-role", description="Ajouter un rôle à un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def addrole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await interaction.response.send_message(embed=discord.Embed(title="Rôle Ajouté", description=f"Le rôle {role.mention} a été attribué à {member.mention}."))

    @app_commands.command(name="delete-role", description="Supprimer un rôle d'un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def delrole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        await interaction.response.send_message(embed=discord.Embed(title="Rôle Retiré", description=f"Le rôle {role.mention} a été retiré à {member.mention}."))

    @app_commands.command(name="derank", description="Supprimer tous les rôles d'un utilisateur")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def derank(self, interaction: discord.Interaction, member: discord.Member):
        await member.edit(roles=[])
        await interaction.response.send_message(embed=discord.Embed(title="DeRank", description=f"Le membre {member.mention} a été dépouillé de tous ses rôles."))

    @app_commands.command(name="antispam", description="Activer ou désactiver l'antispam")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def antispam(self, interaction: discord.Interaction, mode: str):
        if mode.lower() in ["on", "active"]:
            self.antispam_enabled = True
            await interaction.response.send_message("✅ Anti-spam mondial activé.")
        elif mode.lower() in ["off", "desactive"]:
            self.antispam_enabled = False
            await interaction.response.send_message("❌ Anti-spam mondial désactivé.")
        else:
            await interaction.response.send_message("❌ Mode invalide. Utilisez `on` ou `off`.", ephemeral=True)

    @app_commands.command(name="set-antispam", description="Modifier la tolérance de spam")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def setantispam(self, interaction: discord.Interaction, messages: int, secondes: int):
        self.antispam_limit = messages
        self.antispam_interval = secondes
        await interaction.response.send_message(embed=discord.Embed(title="Configuration", description=f"⚙️ Anti-spam ajusté sur : `{messages}` messages maximum en `{secondes}` secondes."))

    @app_commands.command(name="purge", description="Supprimer des messages")
    @has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
    async def purge(self, interaction: discord.Interaction, amount: int):
       
        await interaction.response.send_message(f"🧼 Nettoyage de {amount} messages...", ephemeral=True)
        await interaction.channel.purge(limit=amount)


    @tasks.loop(seconds=30)
    async def check_temp_roles(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now = int(time.time())

        cursor.execute("SELECT user_id, role_id, guild_id FROM temp_roles WHERE end_time <= ?", (now,))
        rows = cursor.fetchall()

        for user_id, role_id, guild_id in rows:
            guild = self.bot.get_guild(guild_id)
            if guild:
                member = guild.get_member(user_id)
                role = guild.get_role(role_id)
                if member and role:
                    try:
                        await member.remove_roles(role)
                    except:
                        pass
            cursor.execute("DELETE FROM temp_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))

        conn.commit()
        conn.close()


async def setup(bot):
    await bot.add_cog(AdminCog(bot))