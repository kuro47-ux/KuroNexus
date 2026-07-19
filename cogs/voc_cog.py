import discord
from discord.ext import commands
import asyncio

class VoiceManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.CREATOR_CHANNEL_ID = None #<-- Enter the voice channel ID to create a personal voice chat

        self.temporary_channels = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Voice Management Cog chargé avec le préfixe '+' !")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        if after.channel and after.channel.id == self.CREATOR_CHANNEL_ID:
            guild = member.guild
            category = after.channel.category

     
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
                member: discord.PermissionOverwrite(connect=True, view_channel=True, manage_channels=True, move_members=True)
            }

            
            channel_name = f"🔊 Salon de {member.display_name}"
            new_channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )

         
            self.temporary_channels[new_channel.id] = member.id

            
            await member.move_to(new_channel)

            
            await asyncio.sleep(1)

            
            await self.send_voice_help(new_channel, member)

        
        if before.channel and before.channel.id in self.temporary_channels:
            
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete(reason="Salon vocal temporaire vide.")
                except Exception as e:
                    print(f"Erreur lors de la suppression du salon vocal : {e}")
                
                
                if before.channel.id in self.temporary_channels:
                    del self.temporary_channels[before.channel.id]

    async def send_voice_help(self, channel: discord.VoiceChannel, owner: discord.Member):
        """Génère et envoie l'embed de bienvenue et d'aide dans le chat textuel du vocal."""
        embed = discord.Embed(
            title="🛠️ Votre Salon Vocal Personnel",
            description=f"Bienvenue {owner.mention} ! Tu es le propriétaire de ce salon.\n"
                        f"Voici la liste des commandes textuelles disponibles (préfixe `+`) pour configurer ton espace depuis ce chat :",
            color=discord.Color.blue()
        )
        embed.add_field(name="👥 `+limit <nombre>`", value="Définit la limite de places (0 pour illimité, max 99).", inline=False)
        embed.add_field(name="🔒 `+lock`", value="Verrouille le salon (empêche les nouveaux membres de se connecter).", inline=False)
        embed.add_field(name="🔓 `+unlock`", value="Déverrouille le salon pour tout le monde.", inline=False)
        embed.add_field(name="🚫 `+kick @membre`", value="Expulse un utilisateur de ton salon vocal.", inline=False)
        embed.add_field(name="👻 `+ghost`", value="Rend le salon invisible aux yeux des autres utilisateurs du serveur.", inline=False)
        embed.add_field(name="👁️ `+unghost`", value="Rend à nouveau le salon visible sur le serveur.", inline=False)
        embed.add_field(name="✍️ `+name <nouveau nom>`", value="Modifie le nom de ton salon vocal.", inline=False)
        embed.add_field(name="👑 `+claim`", value="Si le propriétaire quitte le salon, un membre présent peut taper cette commande pour récupérer la gestion.", inline=False)
        embed.set_footer(text="Le salon s'autodétruira dès que tout le monde l'aura quitté.")
        
        try:
            await channel.send(content=owner.mention, embed=embed)
        except Exception as e:
            print(f"Impossible d'envoyer le message de help dans le chat du vocal : {e}")

    
    def is_voice_owner():
        async def predicate(ctx):
            cog = ctx.cog
            
            if not ctx.author.voice or not ctx.author.voice.channel:
                await ctx.send("❌ Tu dois être connecté dans ton salon vocal pour utiliser cette commande !", delete_after=10)
                return False
            
            v_channel_id = ctx.author.voice.channel.id
            
            if v_channel_id not in cog.temporary_channels:
                await ctx.send("❌ Cette commande ne peut être utilisée que dans un salon temporaire privé !", delete_after=10)
                return False
            
            
            if cog.temporary_channels[v_channel_id] != ctx.author.id:
                await ctx.send("❌ Seul le propriétaire actuel de ce salon vocal peut utiliser cette commande !", delete_after=10)
                return False
            return True
        return commands.check(predicate)

    

    @commands.command(name="limit")
    @is_voice_owner()
    async def cmd_voice_limit(self, ctx, limit: int):
        """Définit la limite d'utilisateurs dans le salon"""
        if limit < 0 or limit > 99:
            await ctx.send("❌ La limite doit être comprise entre 0 (illimité) et 99.")
            return
        
        channel = ctx.author.voice.channel
        await channel.edit(user_limit=limit)
        await ctx.send(f"👥 La limite de places du salon a été fixée à : **{limit if limit > 0 else 'Illimitée'}**.")

    @commands.command(name="lock")
    @is_voice_owner()
    async def cmd_voice_lock(self, ctx):
        """Empêche les gens de se connecter au vocal"""
        channel = ctx.author.voice.channel
       
        await channel.set_permissions(ctx.guild.default_role, connect=False)
        await ctx.send("🔒 Le salon est maintenant **verrouillé**. Les utilisateurs ne peuvent plus le rejoindre sans y être invités.")

    @commands.command(name="unlock")
    @is_voice_owner()
    async def cmd_voice_unlock(self, ctx):
        """Réautorise tout le monde à se connecter au vocal"""
        channel = ctx.author.voice.channel
        await channel.set_permissions(ctx.guild.default_role, connect=True)
        await ctx.send("🔓 Le salon est maintenant **déverrouillé** et accessible à tous.")

    @commands.command(name="ghost")
    @is_voice_owner()
    async def cmd_voice_ghost(self, ctx):
        """Masque le salon de la liste des salons de la guilde"""
        channel = ctx.author.voice.channel
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.send("👻 Le salon est maintenant **invisible**. Seuls ceux déjà présents ou invités peuvent le voir.")

    @commands.command(name="unghost")
    @is_voice_owner()
    async def cmd_voice_unghost(self, ctx):
        """Réaffiche le salon dans la liste"""
        channel = ctx.author.voice.channel
        await channel.set_permissions(ctx.guild.default_role, view_channel=True)
        await ctx.send("👁️ Le salon est de nouveau **visible** par tout le monde.")

    @commands.command(name="name")
    @is_voice_owner()
    async def cmd_voice_name(self, ctx, *, new_name: str):
        """Change le nom du salon"""
        if len(new_name) > 32:
            await ctx.send("❌ Le nom du salon ne doit pas dépasser 32 caractères.")
            return
        
        channel = ctx.author.voice.channel
        await channel.edit(name=f"🔊 {new_name}")
        await ctx.send(f"✍️ Le salon a été renommé en : **🔊 {new_name}**")

    @commands.command(name="kick")
    @is_voice_owner()
    async def cmd_voice_kick(self, ctx, target: discord.Member):
        """Expulse un membre du salon vocal"""
        channel = ctx.author.voice.channel
        
        if target not in channel.members:
            await ctx.send(f"❌ {target.display_name} n'est pas présent dans votre salon vocal.")
            return
        
        if target.id == ctx.author.id:
            await ctx.send("❌ Tu ne peux pas t'auto-expulser !")
            return

        
        await target.move_to(None, reason="Expulsé par le propriétaire du salon vocal temporaire.")
        
        await channel.set_permissions(target, connect=False)
        await ctx.send(f"🚫 {target.mention} a été déconnecté du salon et ses droits d'accès ont été révoqués.")

    @commands.command(name="claim")
    async def cmd_voice_claim(self, ctx):
        """Permet de s'approprier le salon si le créateur est parti"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ Tu dois être à l'intérieur du salon vocal pour le réclamer !")
            return

        channel = ctx.author.voice.channel
        if channel.id not in self.temporary_channels:
            await ctx.send("❌ Ce salon n'est pas un salon dynamique modifiable.")
            return

        current_owner_id = self.temporary_channels[channel.id]
        
        
        owner_present = any(m.id == current_owner_id for m in channel.members)

        if owner_present:
            await ctx.send("❌ Le propriétaire actuel de ce salon est toujours connecté à l'intérieur !")
            return

        
        self.temporary_channels[channel.id] = ctx.author.id
        
        
        await channel.set_permissions(ctx.author, connect=True, view_channel=True, manage_channels=True, move_members=True)
        await ctx.send(f"👑 Félicitations {ctx.author.mention}, tu es maintenant le nouveau **propriétaire** officiel de ce salon vocal !")


async def setup(bot):
    await bot.add_cog(VoiceManagementCog(bot))