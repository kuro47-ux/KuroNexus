import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True
intents.voice_states = True

bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

with open("config_cogs.json", "r") as f:
    cogs_config = json.load(f)


@bot.event
async def on_ready():
    print(f"[OK] Bot connecte en tant que {bot.user}")
    try:

        synced = await bot.tree.sync()
        print(f"[SYNC] {len(synced)} commandes slash synchronisees")
    except Exception as e:
        print(f"[ERROR] Erreur de synchro tree: {e}")


async def setup_cogs():
    cogs_to_load = []
    
    if cogs_config["admin"] ==  True:
        cogs_to_load.append("cogs.admin_cog")
    
    if cogs_config["casino"] ==  True:
        cogs_to_load.append("cogs.casino_cog")
        
    if cogs_config["debate"] ==  True:
        cogs_to_load.append("cogs.debate_cog")
        
    if cogs_config["dilemma"] ==  True:
        cogs_to_load.append("cogs.dilemma_cog")
        
    if cogs_config["gw"] ==  True:
        cogs_to_load.append("cogs.gw_cog")
        
    if cogs_config["quote"] ==  True:
        cogs_to_load.append("cogs.quote_cog")
        
    if cogs_config["stats"] ==  True:
        cogs_to_load.append("cogs.stats_cog")
        
    if cogs_config["ticket"] ==  True:
        cogs_to_load.append("cogs.ticket_cog")
        
    if cogs_config["voc"] ==  True:
        cogs_to_load.append("cogs.voc_cog")
        
    if cogs_config["welcome"] ==  True:
        cogs_to_load.append("cogs.welcome_cog")
        

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog) 
            print(f"[OK] Cog charge : {cog}")
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement du cog {cog}: {e}")

async def main():
    async with bot:
        await setup_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())