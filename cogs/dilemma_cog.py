import discord
from discord.ext import commands, tasks
import datetime
import random
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "dilemma", "config.json")

with open(CONFIG_PATH, "r") as f:
    dilemma_conf = json.load(f)

DILEMMA_CHANNEL_ID = dilemma_conf["debate_channel_id"]
DILEMMA_TIME = datetime.time(hour=dilemma_conf["time"].get("hour"), minute=dilemma_conf["time"].get("minute"), second=dilemma_conf["time"].get("second"))  

class DilemmaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.weekly_dilemma.start()

    def cog_unload(self):
        self.weekly_dilemma.cancel()

    
    SUJETS_DILEMMES = [
        "Avoir 1 million d'euros tout de suite 🔵 OU pile ou face pour gagner 100 millions (si tu perds, tu as 0) 🔴 ?",
        "Pouvoir lire dans les pensées de tout le monde en permanence 🔵 OU que tout le monde puisse lire dans tes pensées à toi 🔴 ?",
        "Être bloqué sur une île déserte tout seul pendant 5 ans 🔵 OU avec ton pire ennemi pendant 10 ans 🔴 ?",
        "Ne plus jamais pouvoir jouer aux jeux vidéo de ta vie 🔵 OU ne plus jamais pouvoir écouter de musique de ta vie 🔴 ?",
        "Savoir exactement le jour et l'heure de ta mort 🔵 OU connaître précisément la cause de ta mort sans savoir quand 🔴 ?",
        "Avoir le pouvoir de te téléporter n'importe où, mais tu arrives toujours complètement nu 🔵 OU pouvoir voler à seulement 10 km/h 🔴 ?",
        "Vivre dans un monde où il fait tout le temps 40°C et grand soleil 🔵 OU un monde où il fait tout le temps -10°C avec de la neige 🔴 ?",
        "Avoir un bouton qui efface instantanément ton pire souvenir 🔵 OU un bouton qui te donne 50 000€ mais qui efface ton meilleur souvenir 🔴 ?",
        "Être la personne la plus intelligente du monde mais tout le monde te trouve insupportable 🔵 OU être un parfait idiot mais adoré par la Terre entière 🔴 ?",
        "Pouvoir remonter dans le passé de 10 ans pour corriger tes erreurs 🔵 OU faire un bond de 20 ans dans le futur pour voir où tu en es 🔴 ?"
    ]

    @tasks.loop(time=DILEMMA_TIME)
    async def weekly_dilemma(self):

        if datetime.datetime.now().weekday() != dilemma_conf["day"]:
            return

        channel = self.bot.get_channel(DILEMMA_CHANNEL_ID)
        if not channel:
            print(f"[ERROR] Salon de dilemme introuvable (ID: {DILEMMA_CHANNEL_ID})")
            return

        dilemme = random.choice(self.SUJETS_DILEMMES)

        embed = discord.Embed(
            title="🤔 LE DILEMME DU MERCREDI !",
            description=(
                f"Bonjour à tous ! Il est 14h, l'heure de faire un choix impossible. 📢\n\n"
                f"**Quel est votre choix ?**\n>>> {dilemme}\n\n"
                f"Votez avec les réactions ci-dessous ! 🔵 ou 🔴 ?"
            ),
            color=discord.Color.from_rgb(230, 57, 70)  
        )
        embed.set_footer(text="KYOMA • Dilemme automatique")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        try:
            message = await channel.send(content="@everyone", embed=embed)

            await message.add_reaction("🔵")
            await message.add_reaction("🔴")
            print(f"[OK] Dilemme du mercredi envoyé avec succès.")
        except Exception as e:
            print(f"[ERROR] Impossible d'envoyer le dilemme : {e}")

    @weekly_dilemma.before_loop
    async def before_weekly_dilemma(self):

        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DilemmaCog(bot))