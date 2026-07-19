import discord
from discord.ext import commands, tasks
import datetime
import random
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "debate", "config.json")

with open(CONFIG_PATH, "r") as f:
    debate_conf = json.load(f)

DEBATE_CHANNEL_ID = debate_conf["debate_channel_id"]
DEBATE_TIME = datetime.time(hour=debate_conf["time"].get("hour"), minute=debate_conf["time"].get("minute"), second=debate_conf["time"].get("second"))  



class DebateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.weekly_debate.start()

    def cog_unload(self):
        self.weekly_debate.cancel()

   
    SUJETS_DEBATS = [
        "Le casino en ligne sur Discord : pur divertissement ou engrenage dangereux ? 🎰",
        "Les intelligences artificielles vont-elles finir par tuer la créativité humaine ? 🤖",
        "PC Master Race ou la simplicité des Consoles de salon (PS5/Xbox) ? 🎮",
        "Les réseaux sociaux : est-ce qu'ils nous rapprochent ou nous isolent les uns des autres ? 📱",
        "Est-ce que le système de notation à l'école (sur 20) est encore adapté aujourd'hui ? 📝",
        "Les jeux vidéo en Free-to-play avec micro-transactions, est-ce devenu un cancer pour le gaming ? 💸",
        "Pour ou contre le télétravail à 100% dans la société moderne ? 🏠",
        "Vaut-il mieux vivre sa vie à fond au jour le jour, ou tout planifier pour l'avenir ? ⏳",
        "Le streaming (Twitch/Netflix) a-t-il définitivement tué la télévision classique ? 📺",
        "Est-ce que l'argent fait le bonheur, ou contribue-t-il simplement à y participer ? 💎"
    ]

    
    @tasks.loop(time=DEBATE_TIME)
    async def weekly_debate(self):
        if datetime.datetime.now().weekday() != debate_conf["day"]:
            return

        channel = self.bot.get_channel(DEBATE_CHANNEL_ID)
        if not channel:
            print(f"[ERROR] Salon de débat introuvable (ID: {DEBATE_CHANNEL_ID})")
            return

        sujet = random.choice(self.SUJETS_DEBATS)

        embed = discord.Embed(
            title="🎤 LE DÉBAT DE LA SEMAINE !",
            description=(
                f"Bonjour à tous ! C'est mercredi, l'heure de donner votre avis. 📢\n\n"
                f"**Sujet du jour :**\n> {sujet}\n\n"
                f"Exprimez-vous dans le respect, débattez et réagissez avec les émois ci-dessous ! 💬"
            ),
            color=discord.Color.from_rgb(255, 165, 0)
        )
        embed.set_footer(text="KYOMA • Débat automatique")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        try:
            message = await channel.send(content="@everyone", embed=embed)
            
            await message.add_reaction("👍")
            await message.add_reaction("👎")
            await message.add_reaction("🤷")
            print(f"[OK] Débat du mercredi envoyé avec succès.")
        except Exception as e:
            print(f"[ERROR] Impossible d'envoyer le débat : {e}")

    @weekly_debate.before_loop
    async def before_weekly_debate(self):

        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DebateCog(bot))