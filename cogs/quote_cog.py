import discord
from discord import app_commands
from discord.ext import commands


QUOTE_CHANNEL_ID = None #<-- Enter the channel id where you want the quotes to be saved

class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Enregistrer la citation',
            callback=self.save_quote,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self):
        
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def save_quote(self, interaction: discord.Interaction, message: discord.Message):
        
        if not message.content:
            await interaction.response.send_message(
                "❌ Impossible d'enregistrer cette citation car le message ne contient pas de texte.", 
                ephemeral=True
            )
            return

        
        channel = self.bot.get_channel(QUOTE_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message(
                "❌ Le salon d'archivage des citations est introuvable. Vérifie la configuration du code !", 
                ephemeral=True
            )
            return

        
        embed = discord.Embed(
            description=f"« {message.content} »",
            color=discord.Color.from_rgb(255, 215, 0)  
        )
        
        
        embed.set_author(
            name=message.author.display_name, 
            icon_url=message.author.display_avatar.url
        )
        
        
        date_format = message.created_at.strftime("%d/%m/%Y à %H:%M")
        embed.set_footer(
            text=f"Propos tenus le {date_format} • Enregistré par {interaction.user.display_name}"
        )

        try:
            
            await channel.send(embed=embed)
            
            
            await interaction.response.send_message(
                f"✅ La citation de **{message.author.display_name}** a été immortalisée dans {channel.mention} !", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors de l'envoi de la citation : {e}", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))