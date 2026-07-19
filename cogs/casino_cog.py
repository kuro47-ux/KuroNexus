import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
from typing import Dict, Optional
from datetime import datetime
import asyncio
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "CASINO", "casino_data.json")
CONFIG_FILE = os.path.join(BASE_DIR, "CASINO", "casino_config.json")

DEFAULT_CONFIG = {
    "game_levels": {
        "coinflip": 0,
        "dice": 0,
        "slots": 25,
        "blackjack": 10,
        "roulette": 10,
        "crash": 25,
        "wheelspin": 50,
        "keno": 50,
    },
    "level_roles": {
        "0": None,
        "10": None,
        "25": None,
        "50": None,
    },
    "game_channels": {
        "coinflip": None,
        "dice": None,
        "slots": None,
        "blackjack": None,
        "roulette": None,
        "crash": None,
        "wheelspin": None,
        "keno": None,
    },
    "exp_per_win": 100,
    "exp_per_loss": 25,
    "exp_to_level": 1000,
}

class CasinoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_config(self) -> Dict:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return DEFAULT_CONFIG.copy()

    def save_config(self, config: Dict):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    def get_config(self) -> Dict:
        return self.load_config()

    def load_data(self) -> Dict:
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_data(self, data: Dict):
        with open(DATABASE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get_user_data(self, user_id: int) -> Dict:
        data = self.load_data()
        user_id_str = str(user_id)

        if user_id_str not in data:
            data[user_id_str] = {
                "coins": 10000,
                "gems": 100,
                "tickets": 5,
                "vip_tokens": 0,
                "level": 1,
                "exp": 0,
                "total_wins": 0,
                "total_losses": 0,
                "inventory": {},
                "active_effects": {}
            }
            self.save_data(data)

        default_items = [
            "bonus_tickets", "profile_color", "x2_multiplier", "free_spin", "common_chest",
            "exclusive_title", "animated_badge", "legendary_wheel", "mythic_chest", "animated_bg",
            "vip_bronze", "vip_silver", "vip_gold", "daily_bonus_permanent", "private_casino",
            "luck_boost", "economy_boost", "lucky_spin", "slots_premium", "blackjack_vip",
            "mines_extreme", "event_chest", "mega_jackpot"
        ]
        if "inventory" not in data[user_id_str]:
            data[user_id_str]["inventory"] = {}
        for item in default_items:
            if item not in data[user_id_str]["inventory"]:
                data[user_id_str]["inventory"][item] = 0

        if "active_effects" not in data[user_id_str]:
            data[user_id_str]["active_effects"] = {}

        self.clean_expired_effects(data[user_id_str])
        return data[user_id_str]

    def update_user_data(self, user_id: int, updates: Dict):
        data = self.load_data()
        user_id_str = str(user_id)
        if user_id_str in data:
            data[user_id_str].update(updates)
            self.save_data(data)

    def add_exp(self, user_id: int, amount: int):
        user_data = self.get_user_data(user_id)
        config = self.get_config()

        user_data["exp"] += amount
        exp_needed = config["exp_to_level"]

        level_up = None
        while user_data["exp"] >= exp_needed:
            user_data["level"] += 1
            user_data["exp"] -= exp_needed
            level_up = user_data["level"]

        self.update_user_data(user_id, user_data)
        return level_up

    def create_error_embed(self, title: str, description: str) -> discord.Embed:
        return discord.Embed(title=f"❌ {title}", description=description, color=discord.Color.red())

    def create_success_embed(self, title: str, description: str) -> discord.Embed:
        return discord.Embed(title=f"✅ {title}", description=description, color=discord.Color.green())

    def create_wallet_embed(self, user_id: int, user: discord.User) -> discord.Embed:
        user_data = self.get_user_data(user_id)
        
        embed_color = discord.Color.gold()
        if user_data["inventory"].get("profile_color", 0) > 0:
            embed_color = discord.Color.from_rgb(255, 215, 0)
        elif user_data["inventory"].get("animated_bg", 0) > 0:
            embed_color = discord.Color.purple()

        title_prefix = ""
        if user_data["inventory"].get("exclusive_title", 0) > 0:
            title_prefix = "🏆 [High Roller] "
        elif user_data["inventory"].get("vip_gold", 0) > 0:
            title_prefix = "👑 [VIP Gold] "

        embed = discord.Embed(
            title=f"💼 {title_prefix}Portefeuille de {user.name}",
            color=embed_color,
            timestamp=datetime.now()
        )

        if user_data["inventory"].get("animated_badge", 0) > 0:
            embed.description = "✨ *Membre Élite Étoilé* ✨"

        embed.add_field(name="💰 Coins", value=f"`{user_data['coins']:,}`", inline=True)
        embed.add_field(name="💎 Gems", value=f"`{user_data['gems']:,}`", inline=True)
        embed.add_field(name="🎟️ Tickets", value=f"`{user_data['tickets']:,}`", inline=True)
        embed.add_field(name="👑 Jetons VIP", value=f"`{user_data['vip_tokens']:,}`", inline=True)

        config = self.get_config()
        level = user_data["level"]
        exp = user_data["exp"]
        exp_needed = config["exp_to_level"]
        progress = int((exp / exp_needed) * 10)
        bar = "█" * progress + "░" * (10 - progress)

        embed.add_field(name="📊 Progression", value=f"Niveau: **{level}**\nEXP: `{exp}/{exp_needed}` {bar}", inline=False)
        embed.add_field(name="📈 Statistiques", value=f"Victoires: {user_data['total_wins']} | Défaites: {user_data['total_losses']}", inline=False)

        if user_data.get("active_effects"):
            effects_text = ""
            for eff, data in user_data["active_effects"].items():
                rem = int(data['expires_at'] - datetime.now().timestamp())
                if rem > 0:
                    effects_text += f"• **{eff.replace('_', ' ').title()}** ({rem}s restantes)\n"
            if effects_text:
                embed.add_field(name="🔥 Effets Actifs", value=effects_text, inline=False)

        embed.set_thumbnail(url=user.avatar.url)
        return embed

    class CasinoGames:
        @staticmethod
        def coinflip(bet: int, cog_instance, user_id: int = None) -> tuple[bool, int]:
            user_data = cog_instance.get_user_data(user_id) if user_id else None
            win_chance = 0.50
            if user_data and cog_instance.is_effect_active(user_data, "luck_boost"):
                win_chance = 0.60

            result = random.random() < win_chance
            gain = bet if result else -bet

            if user_id and user_data:
                multiplier = cog_instance.get_multiplier_bonus(user_data)
                gain = int(gain * multiplier) if gain > 0 else gain
                if gain > 0 and cog_instance.get_economy_boost(user_data):
                    gain = int(gain * 1.25)

            return result, gain

        @staticmethod
        def dice(bet: int, user_choice: int, cog_instance, user_id: int = None) -> tuple[bool, int]:
            roll = random.randint(1, 6)
            user_data = cog_instance.get_user_data(user_id) if user_id else None
            
            if user_data and cog_instance.is_effect_active(user_data, "luck_boost") and roll != user_choice:
                if random.random() < 0.20:
                    roll = user_choice

            win = roll == user_choice
            gain = bet * 5 if win else -bet

            if user_id and user_data:
                multiplier = cog_instance.get_multiplier_bonus(user_data)
                gain = int(gain * multiplier) if gain > 0 else gain
                if gain > 0 and cog_instance.get_economy_boost(user_data):
                    gain = int(gain * 1.25)

            return win, gain

        @staticmethod
        def slots(bet: int, cog_instance, user_id: int = None) -> tuple[list, int]:
            symbols = ["🍒", "🍋", "🍊", "🔔", "7️⃣", "💎", "⭐"]
            user_data = cog_instance.get_user_data(user_id) if user_id else None

            if user_data and cog_instance.is_effect_active(user_data, "luck_boost") and random.random() < 0.25:
                sym = random.choice(symbols)
                reels = [sym, sym, sym]
            else:
                reels = [random.choice(symbols) for _ in range(3)]

            if reels[0] == reels[1] == reels[2]:
                if reels[0] == "💎": multiplier = 12
                elif reels[0] == "⭐": multiplier = 10
                elif reels[0] == "7️⃣": multiplier = 8
                else: multiplier = 5
                gain = bet * multiplier
            elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
                gain = int(bet * 1.5)
            else:
                gain = -bet

            if user_id and user_data:
                if cog_instance.is_effect_active(user_data, "free_spin") and gain < 0:
                    gain = 0
                multiplier = cog_instance.get_multiplier_bonus(user_data)
                gain = int(gain * multiplier) if gain > 0 else gain
                if gain > 0 and cog_instance.get_economy_boost(user_data):
                    gain = int(gain * 1.25)

            return reels, gain

        @staticmethod
        def roulette(bet: int, choice: str, cog_instance, user_id: int = None) -> tuple[int, int]:
            number = random.randint(0, 36)
            win = False
            multiplier = 0

            if choice == "rouge" and number > 0 and number % 2 == 1:
                win = True
                multiplier = 2
            elif choice == "noir" and number > 0 and number % 2 == 0:
                win = True
                multiplier = 2
            elif choice == "pair" and number > 0 and number % 2 == 0:
                win = True
                multiplier = 2
            elif choice == "impair" and number > 0 and number % 2 == 1:
                win = True
                multiplier = 2
            elif choice.isdigit() and int(choice) == number:
                win = True
                multiplier = 36

            gain = bet * multiplier if win else -bet

            if user_id:
                user_data = cog_instance.get_user_data(user_id)
                multiplier = cog_instance.get_multiplier_bonus(user_data)
                gain = int(gain * multiplier) if gain > 0 else gain
                if gain > 0 and cog_instance.get_economy_boost(user_data):
                    gain = int(gain * 1.25)

            return number, gain

        @staticmethod
        def crash(bet: int, multiplier: float, cog_instance, user_id: int = None) -> tuple[float, int]:
            user_data = cog_instance.get_user_data(user_id) if user_id else None
            min_crash = 1.15 if (user_data and cog_instance.is_effect_active(user_data, "luck_boost")) else 1.0
            crash_at = random.uniform(min_crash, 6.0)
            
            if multiplier <= crash_at:
                gain = int(bet * multiplier) - bet
            else:
                gain = -bet

            if user_id and user_data:
                mult = cog_instance.get_multiplier_bonus(user_data)
                gain = int(gain * mult) if gain > 0 else gain
                if gain > 0 and cog_instance.get_economy_boost(user_data):
                    gain = int(gain * 1.25)

            return crash_at, gain

        @staticmethod
        def wheelspin(bet: int, cog_instance, user_id: int = None) -> tuple[str, int]:
            outcomes = [
                ("🍀 Petit gain", 1.5),
                ("💰 Gain normal", 2),
                ("✨ Bonus", 4),
                ("🌟 Gros gain", 6),
                ("👑 Jackpot!", 15),
            ]
            weights = [40, 30, 15, 10, 5]
            user_data = cog_instance.get_user_data(user_id) if user_id else None
            if user_data and cog_instance.is_effect_active(user_data, "luck_boost"):
                weights = [20, 30, 25, 15, 10]

            choice = random.choices(outcomes, weights=weights, k=1)[0]
            gain = int(bet * choice[1]) - bet

            if user_id and user_data:
                multiplier = cog_instance.get_multiplier_bonus(user_data)
                gain = int(gain * multiplier) if gain > 0 else gain
                if gain > 0 and cog_instance.get_economy_boost(user_data):
                    gain = int(gain * 1.25)

            return choice[0], gain

        @staticmethod
        def keno(bet: int, user_numbers: list, drawn: list, cog_instance, user_id: int = None) -> tuple[int, int]:
            matches = len(set(user_numbers) & set(drawn))
            multipliers = {0: 0, 1: 0, 2: 1, 3: 3, 4: 8, 5: 20}
            multiplier = multipliers.get(matches, 0)
            gain = int(bet * multiplier) - bet if multiplier > 0 else -bet

            if user_id:
                user_data = cog_instance.get_user_data(user_id)
                mult = cog_instance.get_multiplier_bonus(user_data)
                gain = int(gain * mult) if gain > 0 else gain
                if gain > 0 and cog_instance.get_economy_boost(user_data):
                    gain = int(gain * 1.25)

            return matches, gain

    class BlackjackGame:
        DECK = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4

        def __init__(self):
            self.player_hand = []
            self.dealer_hand = []
            self.deck = self.DECK.copy()
            random.shuffle(self.deck)

        def deal_card(self) -> str:
            if len(self.deck) < 5:
                self.deck = self.DECK.copy()
                random.shuffle(self.deck)
            return self.deck.pop()

        def start_game(self) -> tuple[list, list]:
            self.player_hand = [self.deal_card(), self.deal_card()]
            self.dealer_hand = [self.deal_card(), self.deal_card()]
            return self.player_hand, self.dealer_hand

        def hit(self) -> str:
            card = self.deal_card()
            self.player_hand.append(card)
            return card

        def hand_value(self, hand: list) -> tuple[int, bool]:
            total = 0
            aces = 0
            for card in hand:
                if card in ['J', 'Q', 'K']: total += 10
                elif card == 'A':
                    aces += 1
                    total += 11
                else: total += int(card)

            while total > 21 and aces:
                total -= 10
                aces -= 1
            return total, total <= 21

        def dealer_play(self):
            while True:
                value, valid = self.hand_value(self.dealer_hand)
                if value >= 17: break
                self.dealer_hand.append(self.deal_card())

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Casino cog loaded et entièrement fonctionnel !")

    def check_game_access(self, interaction: discord.Interaction, game_name: str) -> Optional[str]:
        user_data = self.get_user_data(interaction.user.id)
        config = self.get_config()

        if game_name == "slots" and user_data["inventory"].get("slots_premium", 0) <= 0 and user_data["level"] < 25:
            return "Ce jeu requiert le niveau 25 ou l'accès **Slots Premium** acheté dans la boutique !"
        if game_name == "blackjack" and user_data["inventory"].get("blackjack_vip", 0) <= 0 and user_data["level"] < 10:
            return "Ce jeu requiert le niveau 10 ou l'accès **Table Blackjack VIP** !"

        required_level = config["game_levels"].get(game_name, 0)
        if user_data["level"] < required_level and game_name not in ["slots", "blackjack"]:
            return f"Vous devez être au moins niveau {required_level} pour jouer à ce jeu! Vous êtes niveau {user_data['level']}"

        channel_id = config["game_channels"].get(game_name)
        if channel_id and interaction.channel_id != int(channel_id):
            return f"Ce jeu ne peut être joué que dans le canal <#{channel_id}>"

        return None

    async def handle_level_up(self, interaction: discord.Interaction, old_level: int, new_level: int):
        user = interaction.user
        config = self.get_config()
        guild = interaction.guild

        LEVEL_UP_CHANNEL_ID = config["level_up_channel"]

        embed = discord.Embed(
            title="⬆️ LEVEL UP!",
            description=f"{user.mention} a atteint le niveau **{new_level}**!",
            color=discord.Color.gold()
        )

        if guild:
            target_channel = guild.get_channel(LEVEL_UP_CHANNEL_ID)
            if target_channel:
                try:
                    await target_channel.send(embed=embed)
                except Exception as e:
                    print(f"Impossible d'envoyer le message de level up : {e}")
            else:
                try:
                    await interaction.followup.send(embed=embed)
                except:
                    pass

            role_id = config["level_roles"].get(str(new_level))
            if role_id:
                try:
                    role = guild.get_role(int(role_id))
                    if role: await user.add_roles(role)
                except: pass

    async def buy_item_callback(self, interaction: discord.Interaction, user_data: Dict, shop_items: Dict):
        item = interaction.data['values'][0]
        if item not in shop_items:
            await interaction.response.send_message(embed=self.create_error_embed("Erreur", f"Objet {item} inexistant"), ephemeral=True)
            return

        item_data = shop_items[item]
        currency = item_data["currency"]

        if user_data[currency] < item_data["price"]:
            await interaction.response.send_message(embed=self.create_error_embed("Erreur", f"Pas assez de ressources ! Il vous faut {item_data['price']} {currency}."), ephemeral=True)
            return

        user_data[currency] -= item_data["price"]
        user_data["inventory"][item] = user_data["inventory"].get(item, 0) + 1
        self.update_user_data(interaction.user.id, user_data)

        embed = discord.Embed(
            title=f"✅ {item.replace('_', ' ').title()} acheté!",
            color=discord.Color.green(),
            description=f"Vous possédez cet objet. Effet : *{item_data['effect']}*"
        )

        activatable_effects = {
            "x2_multiplier": "Doublez vos gains dans tous les jeux (30 minutes)",
            "free_spin": "Immunité de perte sur votre prochain Slots (30 secondes)",
            "luck_boost": "Boost de chance de +20% aux lancers (30 secondes)",
            "economy_boost": "Boost économique de +25% (1 heure)",
        }

        options = []
        for effect_name, effect_desc in activatable_effects.items():
            if user_data["inventory"].get(effect_name, 0) > 0:
                options.append(discord.SelectOption(
                    label=effect_name.replace('_', ' ').title(),
                    description=effect_desc,
                    value=effect_name
                ))

        view = None
        if options:
            select = discord.ui.Select(placeholder="Sélectionnez un effet de votre inventaire à activer", options=options)
            select.callback = lambda i: self.activate_item_callback(i, user_data, interaction.user.id)
            view = discord.ui.View()
            view.add_item(select)
            embed.add_field(name="🎒 Objets activables", value="Utilisez le menu déroulant ci-dessous pour déclencher un booster de votre inventaire.", inline=False)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def activate_item_callback(self, interaction: discord.Interaction, user_data: Dict, user_id: int):
        item = interaction.data['values'][0]
        if user_data["inventory"].get(item, 0) <= 0:
            await interaction.response.send_message(embed=self.create_error_embed("Erreur", "Vous n'avez pas cet objet"), ephemeral=True)
            return

        user_data["inventory"][item] -= 1
        duration = 30
        if item == "economy_boost": duration = 3600
        elif item == "x2_multiplier": duration = 1800

        self.activate_effect(user_data, item, duration)
        self.update_user_data(user_id, user_data)

        embed = discord.Embed(
            title=f"⚡ {item.replace('_', ' ').title()} Activé !",
            color=discord.Color.green(),
            description=f"L'effet est maintenant actif pour une durée de **{duration}** secondes !"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def clean_expired_effects(self, user_data: Dict):
        current_time = datetime.now().timestamp()
        active_effects = user_data.get("active_effects", {})
        for effect_name, effect_data in list(active_effects.items()):
            if effect_data.get("expires_at", 0) < current_time:
                del active_effects[effect_name]
        user_data["active_effects"] = active_effects

    def get_item_effect(self, item_name: str) -> str:
        effects = {
            "bonus_tickets": "Ajoute +5 tickets automatiques à votre inventaire.",
            "profile_color": "Débloque la couleur dorée permanente sur votre portefeuille.",
            "x2_multiplier": "Multiplicateur x2 temporaire à activer.",
            "free_spin": "Prochain tour perdant aux slots annulé.",
            "common_chest": "Peut être ouvert avec `/ouvrir_coffre`.",
            "exclusive_title": "Affiche le titre [High Roller] sur votre profil.",
            "animated_badge": "Affiche un indicateur d'élite scintillant sur votre profil.",
            "legendary_wheel": "Permet de lancer la roue exclusive via `/wheelspin_legendaire`.",
            "mythic_chest": "Peut être ouvert avec `/ouvrir_coffre`.",
            "animated_bg": "Change l'apparence et la couleur de votre profil.",
            "vip_bronze": "Rôle et prestige Casino Bronze.",
            "vip_silver": "Rôle et prestige Casino Argent.",
            "vip_gold": "Rôle et prestige Casino Or.",
            "daily_bonus_permanent": "Bonus passif permanent.",
            "private_casino": "Accès aux salons de jeux privilégiés.",
            "luck_boost": "Booste temporairement votre chance aux dés et coinflip.",
            "economy_boost": "+25% de coins gagnés pendant 1h.",
            "lucky_spin": "Donne accès au jeu de roue premium `/luckyspin`.",
            "slots_premium": "Bypasse la restriction de niveau pour les machines à sous.",
            "blackjack_vip": "Bypasse la restriction de niveau pour le Blackjack.",
            "mines_extreme": "Autorise le jeu sur des grilles à haut rendement.",
            "event_chest": "Coffre d'événement rare à ouvrir via `/ouvrir_coffre`.",
            "mega_jackpot": "Ticket d'entrée prioritaire pour les tirages au sort.",
        }
        return effects.get(item_name, "Effet mystère fonctionnel.")

    def is_effect_active(self, user_data: Dict, effect_name: str) -> bool:
        active_effects = user_data.get("active_effects", {})
        effect_data = active_effects.get(effect_name)
        if not effect_data: return False
        if effect_data.get("expires_at", 0) < datetime.now().timestamp():
            del active_effects[effect_name]
            return False
        return True

    def activate_effect(self, user_data: Dict, effect_name: str, duration_seconds: int = 30):
        active_effects = user_data.get("active_effects", {})
        expires_at = datetime.now().timestamp() + duration_seconds
        active_effects[effect_name] = {
            "activated_at": datetime.now().timestamp(),
            "expires_at": expires_at,
            "duration": duration_seconds
        }
        user_data["active_effects"] = active_effects

    def get_multiplier_bonus(self, user_data: Dict) -> float:
        return 2.0 if self.is_effect_active(user_data, "x2_multiplier") else 1.0

    def get_economy_boost(self, user_data: Dict) -> bool:
        return self.is_effect_active(user_data, "economy_boost")



    @app_commands.command(name="casino_admin", description="Gestion de l'économie (Give/Remove) (Admin uniquement)")
    @app_commands.describe(action="give ou remove", cible="L'utilisateur ciblé", ressource="coins, gems, tickets, vip_tokens", montant="Quantité")
    @app_commands.choices(action=[
        app_commands.Choice(name="Donner (Give)", value="give"),
        app_commands.Choice(name="Retirer (Remove)", value="remove")
    ], ressource=[
        app_commands.Choice(name="💰 Coins", value="coins"),
        app_commands.Choice(name="💎 Gems", value="gems"),
        app_commands.Choice(name="🎟️ Tickets", value="tickets"),
        app_commands.Choice(name="👑 Jetons VIP", value="vip_tokens")
    ])
    @commands.has_permissions(administrator=True)
    async def cmd_casino_admin(self, interaction: discord.Interaction, action: str, cible: discord.User, ressource: str, montant: int):
        await interaction.response.defer()
        if montant <= 0:
            await interaction.followup.send(embed=self.create_error_embed("Erreur", "Le montant doit être supérieur à 0 !"), ephemeral=True)
            return

        user_data = self.get_user_data(cible.id)
        
        if action == "give":
            user_data[ressource] += montant
            msg = f"Ajout de **{montant:,} {ressource}** sur le compte de {cible.mention} effectué !"
        else:
            if user_data[ressource] < montant:
                user_data[ressource] = 0
            else:
                user_data[ressource] -= montant
            msg = f"Retrait de **{montant:,} {ressource}** sur le compte de {cible.mention} effectué !"

        self.update_user_data(cible.id, user_data)
        await interaction.followup.send(embed=self.create_success_embed("Économie Modifiée", msg))

    @app_commands.command(name="casino_admin_xp", description="Gestion de l'EXP des joueurs (Admin uniquement)")
    @app_commands.describe(action="give ou remove", cible="L'utilisateur ciblé", montant="Quantité d'EXP")
    @app_commands.choices(action=[
        app_commands.Choice(name="Donner (Give)", value="give"),
        app_commands.Choice(name="Retirer (Remove)", value="remove")
    ])
    @commands.has_permissions(administrator=True)
    async def cmd_casino_admin_xp(self, interaction: discord.Interaction, action: str, cible: discord.User, montant: int):
        await interaction.response.defer()
        if montant <= 0:
            await interaction.followup.send(embed=self.create_error_embed("Erreur", "Le montant doit être supérieur à 0 !"), ephemeral=True)
            return

        user_data = self.get_user_data(cible.id)

        if action == "give":
            level_up = self.add_exp(cible.id, montant)
            msg = f"Ajout de **{montant:,} EXP** sur le compte de {cible.mention} effectué !"
            await interaction.followup.send(embed=self.create_success_embed("EXP Modifiée", msg))
            if level_up:
                await self.handle_level_up(interaction, level_up - 1, level_up)
        else:
            if user_data["exp"] < montant:
                user_data["exp"] = 0
            else:
                user_data["exp"] -= montant
            self.update_user_data(cible.id, user_data)
            msg = f"Retrait de **{montant:,} EXP** sur le compte de {cible.mention} effectué !"
            await interaction.followup.send(embed=self.create_success_embed("EXP Modifiée", msg))



    @app_commands.command(name="ouvrir_coffre", description="Ouvrir un coffre disponible dans votre inventaire")
    @app_commands.choices(coffre=[
        app_commands.Choice(name="📦 Coffre Commun", value="common_chest"),
        app_commands.Choice(name="🔥 Coffre Mythique", value="mythic_chest"),
        app_commands.Choice(name="🎁 Coffre Événement", value="event_chest")
    ])
    async def cmd_open_chest(self, interaction: discord.Interaction, coffre: str):
        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if user_data["inventory"].get(coffre, 0) <= 0:
            await interaction.followup.send(embed=self.create_error_embed("Coffre manquant", f"Vous ne possédez pas de {coffre.replace('_', ' ')} dans votre inventaire !"), ephemeral=True)
            return

        user_data["inventory"][coffre] -= 1
        embed = discord.Embed(title=f"🔑 Ouverture de votre {coffre.replace('_', ' ').title()}", color=discord.Color.blue())

        if coffre == "common_chest":
            win_coins = random.randint(5000, 20000)
            user_data["coins"] += win_coins
            embed.description = f"Vous avez trouvé **{win_coins:,} Coins** !"
        elif coffre == "mythic_chest":
            win_gems = random.randint(10, 50)
            win_coins = random.randint(20000, 50000)
            user_data["gems"] += win_gems
            user_data["coins"] += win_coins
            embed.description = f"Contenu incroyable :\n✨ **{win_gems} Gems**\n💰 **{win_coins:,} Coins**"
        elif coffre == "event_chest":
            win_tickets = random.randint(2, 6)
            user_data["tickets"] += win_tickets
            embed.description = f"Récompense exclusive d'événement :\n🎟️ **{win_tickets} Tickets Casino** !"

        self.update_user_data(interaction.user.id, user_data)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="wheelspin_legendaire", description="Lancer la Roue Légendaire (Requiert 1 objet Wheelspin légendaire)")
    async def cmd_legendary_wheel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if user_data["inventory"].get("legendary_wheel", 0) <= 0:
            await interaction.followup.send(embed=self.create_error_embed("Roue bloquée", "Vous devez posséder l'objet **Wheel Spin légendaire** (disponible au shop) !"), ephemeral=True)
            return

        user_data["inventory"]["legendary_wheel"] -= 1
        lots = [("💎 100 Gems Jackpot", 0, 100), ("💰 500,000 Coins Ultra Gain", 500000, 0), ("🎟️ 10 Tickets Privés", 0, 0)]
        gagné = random.choice(lots)

        user_data["coins"] += gagné[1]
        user_data["gems"] += gagné[2]
        if gagné[0].startswith("🎟️"): user_data["tickets"] += 10

        self.update_user_data(interaction.user.id, user_data)
        embed = discord.Embed(title="🎡 Roue Légendaire", description=f"La roue s'arrête... 🎉 Félicitations vous gagnez : **{gagné[0]}** !", color=discord.Color.purple())
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="luckyspin", description="Lancer un Lucky Spin (Consomme 1 ticket de type Lucky Spin)")
    async def cmd_lucky_spin(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if user_data["inventory"].get("lucky_spin", 0) <= 0:
            await interaction.followup.send(embed=self.create_error_embed("Aucun jeton", "Vous n'avez pas de **Lucky Spin** en stock dans votre inventaire."), ephemeral=True)
            return

        user_data["inventory"]["lucky_spin"] -= 1
        gain = random.randint(25000, 100000)
        user_data["coins"] += gain
        self.update_user_data(interaction.user.id, user_data)

        embed = discord.Embed(title="🔥 Lucky Spin 🔥", description=f"Le tirage amélioré vous octroie : **+{gain:,} Coins** !", color=discord.Color.orange())
        await interaction.followup.send(embed=embed)

 

    @app_commands.command(name="shop", description="Acheter et voir les objets du casino")
    async def cmd_shop(self, interaction: discord.Interaction):
        user_data = self.get_user_data(interaction.user.id)
        shop_items = {
            "bonus_tickets": {"price": 2500, "currency": "coins", "effect": "Ajoute +5 tickets directs à l'achat"},
            "profile_color": {"price": 5000, "currency": "coins", "effect": "Change la couleur du profil en doré permanent"},
            "x2_multiplier": {"price": 8000, "currency": "coins", "effect": "Double vos gains dans tous les jeux (30 minutes)"},
            "free_spin": {"price": 10000, "currency": "coins", "effect": "Annule les pertes du prochain tour de slots"},
            "common_chest": {"price": 15000, "currency": "coins", "effect": "Coffre commun aléatoire à ouvrir"},
            "exclusive_title": {"price": 25, "currency": "gems", "effect": "Titre High Roller visible sur votre portefeuille"},
            "animated_badge": {"price": 40, "currency": "gems", "effect": "Badge d'élite scintillant sur votre profil"},
            "legendary_wheel": {"price": 50, "currency": "gems", "effect": "Donne 1 accès utilisable via /wheelspin_legendaire"},
            "mythic_chest": {"price": 75, "currency": "gems", "effect": "Contient des multi-monnaies d'exception"},
            "animated_bg": {"price": 100, "currency": "gems", "effect": "Fond d'écran violet premium pour votre profil"},
            "slots_premium": {"price": 1, "currency": "tickets", "effect": "Débloque l'accès aux Slots avant le niveau 25"},
            "blackjack_vip": {"price": 2, "currency": "tickets", "effect": "Débloque la table Blackjack avant le niveau 10"},
            "mines_extreme": {"price": 3, "currency": "tickets", "effect": "Autorise l'accès aux multiplicateurs Mines"},
            "event_chest": {"price": 5, "currency": "tickets", "effect": "Coffre événementiel rempli de tickets"},
            "mega_jackpot": {"price": 10, "currency": "tickets", "effect": "Participation prioritaire aux Jackpots"},
            "vip_bronze": {"price": 5, "currency": "vip_tokens", "effect": "Rang honorifique Bronze"},
            "vip_silver": {"price": 15, "currency": "vip_tokens", "effect": "Rang honorifique Argent"},
            "vip_gold": {"price": 30, "currency": "vip_tokens", "effect": "Titre [VIP Gold] permanent sur le profil"},
            "daily_bonus_permanent": {"price": 50, "currency": "vip_tokens", "effect": "Augmente vos gains passifs globaux"},
            "private_casino": {"price": 100, "currency": "vip_tokens", "effect": "Prestige de Casino Privé"},
            "luck_boost": {"price": 20, "currency": "gems", "effect": "Booste votre chance de 20% pendant 30 secondes"},
            "economy_boost": {"price": 12000, "currency": "coins", "effect": "+25% de coins gagnés pendant 1h"},
            "lucky_spin": {"price": 3, "currency": "tickets", "effect": "Donne 1 jeton de tirage pour /luckyspin"},
        }

        embed = discord.Embed(title="🛒 Boutique du Casino", color=discord.Color.gold(), description="Sélectionnez un objet à acheter :")
        embed.add_field(name="💰 Objets Classiques (Coins)", value="🎟️ Ticket bonus — 2 500 Coins\n🎨 Couleur de profil — 5 000 Coins\n🪙 Multiplicateur x2 (30 min) — 8 000 Coins\n🎰 Spin gratuit — 10 000 Coins\n📦 Coffre commun — 15 000 Coins", inline=True)
        embed.add_field(name="💎 Gems Rares", value="👑 Titre exclusif — 25 Gems\n✨ Badge animé — 40 Gems\n🎡 Wheel Spin légendaire — 50 Gems\n📦 Coffre mythique — 75 Gems\n🌌 Background profil animé — 100 Gems", inline=True)
        embed.add_field(name="🎟️ Tickets Casino", value="🎰 Accès Slots Premium — 1 Ticket\n🃏 Table Blackjack VIP — 2 Tickets\n💣 Partie Mines Extrême — 3 Tickets\n🎁 Coffre événement — 5 Tickets\n👑 Participation Mega Jackpot — 10 Tickets", inline=True)
        embed.add_field(name="👑 Jetons VIP", value="💠 Rang VIP Bronze — 5 Jetons\n🔷 Rang VIP Silver — 15 Jetons\n💎 Rang VIP Gold — 30 Jetons\n🌟 Bonus Daily Permanent — 50 Jetons\n👑 Accès Casino Privé — 100 Jetons", inline=True)
        embed.add_field(name="🎁 Objets Spéciaux", value="🍀 Boost Chance — 20 Gems\n💰 Boost Économie — 12 000 Coins\n🔥 Lucky Spin — 3 Tickets", inline=True)

        view = discord.ui.View()
        options = [discord.SelectOption(label=name.replace('_', ' ').title(), description=f"Coût: {data['price']} {data['currency']}", value=name) for name, data in shop_items.items()]
        select = discord.ui.Select(placeholder="Choisissez un objet à acheter", options=options[:25])
        select.callback = lambda i: self.buy_item_callback(i, user_data, shop_items)
        view.add_item(select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="inventaire", description="Voir tous les objets que vous avez achetés")
    async def cmd_inventory(self, interaction: discord.Interaction):
        user_data = self.get_user_data(interaction.user.id)
        embed = discord.Embed(title="🎒 Votre Inventaire", color=discord.Color.blue())

        total_items = 0
        for item_name, quantity in user_data["inventory"].items():
            if quantity > 0:
                total_items += quantity
                embed.add_field(name=f"{item_name.replace('_', ' ').title()} ({quantity}x)", value=f"Effet: {self.get_item_effect(item_name)}", inline=False)

        if total_items == 0:
            embed.description = "Vous n'avez pas encore d'objets dans votre inventaire. Visitez le shop pour acheter des objets !"
        else:
            embed.set_footer(text=f"Total des objets: {total_items}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="portefeuille", description="Affiche votre portefeuille")
    async def cmd_wallet(self, interaction: discord.Interaction):
        embed = self.create_wallet_embed(interaction.user.id, interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)

 

    @app_commands.command(name="coinflip", description="Pile ou Face")
    @app_commands.describe(bet="Montant à parier")
    async def cmd_coinflip(self, interaction: discord.Interaction, bet: int):
        access_error = self.check_game_access(interaction, "coinflip")
        if access_error:
            await interaction.response.send_message(embed=self.create_error_embed("Accès refusé", access_error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if bet <= 0 or bet > user_data["coins"]:
            await interaction.followup.send(embed=self.create_error_embed("Pari invalide", f"Vous avez {user_data['coins']} coins"), ephemeral=True)
            return

        result, gain = self.CasinoGames.coinflip(bet, self, interaction.user.id)
        side = "Pile" if result else "Face"

        user_data["coins"] += gain
        if gain > 0:
            user_data["total_wins"] += 1
            level_up = self.add_exp(interaction.user.id, 100)
        else:
            user_data["total_losses"] += 1
            level_up = self.add_exp(interaction.user.id, 25)

        self.update_user_data(interaction.user.id, user_data)
        embed = discord.Embed(title="🪙 Coinflip", description=f"Résultat: **{side}**", color=discord.Color.green() if gain > 0 else discord.Color.red())
        embed.add_field(name="Gain", value=f"{gain:+d} coins", inline=True)
        embed.add_field(name="Nouveau solde", value=f"{user_data['coins']:,} coins", inline=True)
        await interaction.followup.send(embed=embed)
        if level_up: await self.handle_level_up(interaction, level_up - 1, level_up)

    @app_commands.command(name="dice", description="Jeu de dés")
    @app_commands.describe(bet="Montant", choice="Votre choix 1-6")
    async def cmd_dice(self, interaction: discord.Interaction, bet: int, choice: int):
        access_error = self.check_game_access(interaction, "dice")
        if access_error:
            await interaction.response.send_message(embed=self.create_error_embed("Accès refusé", access_error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        if choice < 1 or choice > 6:
            await interaction.followup.send(embed=self.create_error_embed("Erreur", "Choisissez un chiffre entre 1 et 6"), ephemeral=True)
            return

        user_data = self.get_user_data(interaction.user.id)
        if bet <= 0 or bet > user_data["coins"]:
            await interaction.followup.send(embed=self.create_error_embed("Pari invalide", f"Vous avez {user_data['coins']} coins"), ephemeral=True)
            return

        win, gain = self.CasinoGames.dice(bet, choice, self, interaction.user.id)

        user_data["coins"] += gain
        if gain > 0:
            user_data["total_wins"] += 1
            level_up = self.add_exp(interaction.user.id, 100)
        else:
            user_data["total_losses"] += 1
            level_up = self.add_exp(interaction.user.id, 25)

        self.update_user_data(interaction.user.id, user_data)
        embed = discord.Embed(title="🎲 Dice", description=f"Votre choix : {choice}", color=discord.Color.green() if win else discord.Color.red())
        embed.add_field(name="Résultat", value="✅ Gagné!" if win else "❌ Perdu!", inline=True)
        embed.add_field(name="Gain", value=f"{gain:+d} coins", inline=True)
        await interaction.followup.send(embed=embed)
        if level_up: await self.handle_level_up(interaction, level_up - 1, level_up)

    @app_commands.command(name="slots", description="Machine à sous")
    @app_commands.describe(bet="Montant à parier")
    async def cmd_slots(self, interaction: discord.Interaction, bet: int):
        access_error = self.check_game_access(interaction, "slots")
        if access_error:
            await interaction.response.send_message(embed=self.create_error_embed("Accès refusé", access_error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if bet <= 0 or bet > user_data["coins"]:
            await interaction.followup.send(embed=self.create_error_embed("Pari invalide", f"Vous avez {user_data['coins']} coins"), ephemeral=True)
            return

        message = await interaction.followup.send("🎰 Alignement des rouleaux en cours...")
        await asyncio.sleep(1)

        reels, gain = self.CasinoGames.slots(bet, self, interaction.user.id)

        user_data["coins"] += gain
        if gain > 0:
            user_data["total_wins"] += 1
            level_up = self.add_exp(interaction.user.id, 100)
        else:
            user_data["total_losses"] += 1
            level_up = self.add_exp(interaction.user.id, 25)

        self.update_user_data(interaction.user.id, user_data)
        embed = discord.Embed(title="🎰 Slots", description=f"**[ {reels[0]} | {reels[1]} | {reels[2]} ]**", color=discord.Color.gold() if gain > 0 else discord.Color.red())
        embed.add_field(name="Gain", value=f"{gain:+d} coins", inline=True)
        embed.add_field(name="Nouveau solde", value=f"{user_data['coins']:,} coins", inline=True)

        await message.edit(content="", embed=embed)
        if level_up: await self.handle_level_up(interaction, level_up - 1, level_up)

    @app_commands.command(name="roulette", description="Jeu de roulette")
    @app_commands.describe(bet="Montant", choice="rouge/noir/pair/impair/0-36")
    async def cmd_roulette(self, interaction: discord.Interaction, bet: int, choice: str):
        access_error = self.check_game_access(interaction, "roulette")
        if access_error:
            await interaction.response.send_message(embed=self.create_error_embed("Accès refusé", access_error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if bet <= 0 or bet > user_data["coins"]:
            await interaction.followup.send(embed=self.create_error_embed("Pari invalide", f"Vous avez {user_data['coins']} coins"), ephemeral=True)
            return

        choice = choice.lower()
        valid = ["rouge", "noir", "pair", "impair"] + [str(i) for i in range(37)]
        if choice not in valid:
            await interaction.followup.send(embed=self.create_error_embed("Choix invalide", "rouge/noir/pair/impair/0-36"), ephemeral=True)
            return

        number, gain = self.CasinoGames.roulette(bet, choice, self, interaction.user.id)

        user_data["coins"] += gain
        if gain > 0:
            user_data["total_wins"] += 1
            level_up = self.add_exp(interaction.user.id, 100)
        else:
            user_data["total_losses"] += 1
            level_up = self.add_exp(interaction.user.id, 25)

        self.update_user_data(interaction.user.id, user_data)
        embed = discord.Embed(title="🎡 Roulette", description=f"La bille s'arrête sur le : **{number}**", color=discord.Color.green() if gain > 0 else discord.Color.red())
        embed.add_field(name="Votre Pari", value=choice, inline=True)
        embed.add_field(name="Gain", value=f"{gain:+d} coins", inline=True)
        await interaction.followup.send(embed=embed)
        if level_up: await self.handle_level_up(interaction, level_up - 1, level_up)

    @app_commands.command(name="crash", description="Jeu Crash")
    @app_commands.describe(bet="Montant", multiplier="À quel multiplicateur retirer (ex: 2.5)")
    async def cmd_crash(self, interaction: discord.Interaction, bet: int, multiplier: float):
        access_error = self.check_game_access(interaction, "crash")
        if access_error:
            await interaction.response.send_message(embed=self.create_error_embed("Accès refusé", access_error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if bet <= 0 or bet > user_data["coins"] or multiplier < 1.0:
            await interaction.followup.send(embed=self.create_error_embed("Paramètres invalides", "Vérifiez votre pari."), ephemeral=True)
            return

        crash_at, gain = self.CasinoGames.crash(bet, multiplier, self, interaction.user.id)

        user_data["coins"] += gain
        if gain > 0:
            user_data["total_wins"] += 1
            level_up = self.add_exp(interaction.user.id, 100)
        else:
            user_data["total_losses"] += 1
            level_up = self.add_exp(interaction.user.id, 25)

        self.update_user_data(interaction.user.id, user_data)
        embed = discord.Embed(title="📈 Crash Multiplier", description=f"La courbe a explosé à: **x{crash_at:.2f}**", color=discord.Color.green() if gain > 0 else discord.Color.red())
        embed.add_field(name="Seuil de retrait fixé", value=f"x{multiplier:.2f}", inline=True)
        embed.add_field(name="Gain", value=f"{gain:+d} coins", inline=True)
        await interaction.followup.send(embed=embed)
        if level_up: await self.handle_level_up(interaction, level_up - 1, level_up)

    @app_commands.command(name="wheelspin", description="Roue de la fortune classique")
    @app_commands.describe(bet="Montant à parier")
    async def cmd_wheelspin(self, interaction: discord.Interaction, bet: int):
        access_error = self.check_game_access(interaction, "wheelspin")
        if access_error:
            await interaction.response.send_message(embed=self.create_error_embed("Accès refusé", access_error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if bet <= 0 or bet > user_data["coins"]:
            await interaction.followup.send(embed=self.create_error_embed("Pari invalide", f"Vous avez {user_data['coins']} coins"), ephemeral=True)
            return

        outcome, gain = self.CasinoGames.wheelspin(bet, self, interaction.user.id)

        user_data["coins"] += gain
        if gain > 0: user_data["total_wins"] += 1
        else: user_data["total_losses"] += 1
        level_up = self.add_exp(interaction.user.id, 100)

        self.update_user_data(interaction.user.id, user_data)
        embed = discord.Embed(title="🎡 Wheel Spin", description=f"Résultat du tour : **{outcome}**", color=discord.Color.gold())
        embed.add_field(name="Gain final", value=f"{gain:+d} coins", inline=True)
        await interaction.followup.send(embed=embed)
        if level_up: await self.handle_level_up(interaction, level_up - 1, level_up)

    @app_commands.command(name="blackjack", description="Blackjack")
    @app_commands.describe(bet="Montant à parier")
    async def cmd_blackjack(self, interaction: discord.Interaction, bet: int):
        access_error = self.check_game_access(interaction, "blackjack")
        if access_error:
            await interaction.response.send_message(embed=self.create_error_embed("Accès refusé", access_error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if bet <= 0 or bet > user_data["coins"]:
            await interaction.followup.send(embed=self.create_error_embed("Pari invalide", f"Vous avez {user_data['coins']} coins"), ephemeral=True)
            return

        game = self.BlackjackGame()
        player_hand, dealer_hand = game.start_game()
        player_value, _ = game.hand_value(player_hand)

        embed = discord.Embed(title="♠️ Table de Blackjack", color=discord.Color.green())
        embed.add_field(name="🤖 Dealer", value=f"{dealer_hand[0]} + ?", inline=True)
        embed.add_field(name="👤 Votre Main", value=f"{' '.join(player_hand)}\nValeur: {player_value}", inline=True)

        if player_value == 21:
            game.dealer_play()
            dealer_value, _ = game.hand_value(game.dealer_hand)
            gain = int(bet * 1.5) if dealer_value != 21 else 0
            multiplier = self.get_multiplier_bonus(user_data)
            gain = int(gain * multiplier)

            user_data["coins"] += gain
            user_data["total_wins"] += 1
            level_up = self.add_exp(interaction.user.id, 100)
            self.update_user_data(interaction.user.id, user_data)

            embed.description = "🎉 Blackjack Naturel !"
            embed.add_field(name="Gain", value=f"{gain:+d} coins", inline=False)
            await interaction.followup.send(embed=embed)
            if level_up: await self.handle_level_up(interaction, level_up - 1, level_up)
        else:
            view = self.BlackjackView(interaction.user.id, game, bet, self)
            await interaction.followup.send(embed=embed, view=view)

    class BlackjackView(discord.ui.View):
        def __init__(self, user_id: int, game: "CasinoCog.BlackjackGame", bet: int, cog_instance: "CasinoCog"):
            super().__init__(timeout=300)
            self.user_id = user_id
            self.game = game
            self.bet = bet
            self.cog = cog_instance

        @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary, emoji="🎯")
        async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Ce n'est pas votre session !", ephemeral=True)
                return

            await interaction.response.defer()
            self.game.hit()
            player_value, valid = self.game.hand_value(self.game.player_hand)

            if not valid:
                user_data = self.cog.get_user_data(self.user_id)
                user_data["coins"] -= self.bet
                user_data["total_losses"] += 1
                level_up = self.cog.add_exp(self.user_id, 25)
                self.cog.update_user_data(self.user_id, user_data)

                embed = discord.Embed(title="💥 BUST ! (Plus de 21)", color=discord.Color.red())
                embed.add_field(name="Votre main finale", value=f"{' '.join(self.game.player_hand)} ({player_value})", inline=False)
                for child in self.children: child.disabled = True
                await interaction.followup.send(embed=embed, view=self)
            else:
                embed = discord.Embed(title="♠️ Blackjack", color=discord.Color.green())
                embed.add_field(name="Votre main", value=f"{' '.join(self.game.player_hand)}\nValeur actuelle: {player_value}", inline=False)
                await interaction.followup.send(embed=embed, view=self)

        @discord.ui.button(label="Stand", style=discord.ButtonStyle.success, emoji="🛑")
        async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Ce n'est pas votre session !", ephemeral=True)
                return

            await interaction.response.defer()
            self.game.dealer_play()
            player_value, _ = self.game.hand_value(self.game.player_hand)
            dealer_value, _ = self.game.hand_value(self.game.dealer_hand)

            if dealer_value > 21 or player_value > dealer_value: result = "gagné"
            elif player_value == dealer_value: result = "égalité"
            else: result = "perdu"

            gain = self.bet if result == "gagné" else (0 if result == "égalité" else -self.bet)
            user_data = self.cog.get_user_data(self.user_id)
            
            if gain > 0:
                multiplier = self.cog.get_multiplier_bonus(user_data)
                gain = int(gain * multiplier)
                user_data["total_wins"] += 1
                level_up = self.cog.add_exp(self.user_id, 100)
            else:
                user_data["total_losses"] += 1
                level_up = self.cog.add_exp(self.user_id, 25)

            user_data["coins"] += gain
            self.cog.update_user_data(self.user_id, user_data)

            embed = discord.Embed(title="♠️ Résultat Blackjack", color=discord.Color.green() if gain >= 0 else discord.Color.red())
            embed.add_field(name="Votre main", value=f"{' '.join(self.game.player_hand)} = {player_value}", inline=True)
            embed.add_field(name="Main du Dealer", value=f"{' '.join(self.game.dealer_hand)} = {dealer_value}", inline=True)
            embed.add_field(name="Verdict", value=f"{result.upper()} : {gain:+d} coins", inline=False)

            for child in self.children: child.disabled = True
            await interaction.followup.send(embed=embed, view=self)

    @app_commands.command(name="keno", description="Jeu du Keno")
    @app_commands.describe(bet="Montant")
    async def cmd_keno(self, interaction: discord.Interaction, bet: int):
        access_error = self.check_game_access(interaction, "keno")
        if access_error:
            await interaction.response.send_message(embed=self.create_error_embed("Accès refusé", access_error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        user_data = self.get_user_data(interaction.user.id)

        if bet <= 0 or bet > user_data["coins"]:
            await interaction.followup.send(embed=self.create_error_embed("Pari invalide", f"Vous avez {user_data['coins']} coins"), ephemeral=True)
            return

        user_numbers = random.sample(range(1, 26), 10)
        drawn = random.sample(range(1, 26), 20)

        matches, gain = self.CasinoGames.keno(bet, user_numbers, drawn, self, interaction.user.id)

        user_data["coins"] += gain
        if gain > 0:
            user_data["total_wins"] += 1
            level_up = self.add_exp(interaction.user.id, 100)
        else:
            user_data["total_losses"] += 1
            level_up = self.add_exp(interaction.user.id, 25)

        self.update_user_data(interaction.user.id, user_data)
        embed = discord.Embed(title="🎫 Grille de Keno", description=f"Vos numéros: {', '.join(map(str, user_numbers))}\n\nNuméros tirés: {', '.join(map(str, drawn))}", color=discord.Color.gold() if gain > 0 else discord.Color.red())
        embed.add_field(name="Correspondances", value=f"🎯 {matches} bonne(s) pioche(s)", inline=True)
        embed.add_field(name="Gain", value=f"{gain:+d} coins", inline=True)
        await interaction.followup.send(embed=embed)
        if level_up: await self.handle_level_up(interaction, level_up - 1, level_up)

async def setup(bot):
    await bot.add_cog(CasinoCog(bot))