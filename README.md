# KuroNexus 🌙

Un bot Discord "multitâche" écrit par Kuro un jeune dev Français : modération, casino, statistiques, tickets, vocaux temporaires, giveaways, débats hebdomadaires... bref, un vrai couteau suisse pour ton serveur.

Ce dépôt est découpé en **cogs** (un cog = un module indépendant, un peu comme un plugin). Chaque cog peut être activé ou désactivé sans toucher au reste du bot, et certains ont leur propre fichier de configuration. Ce README t'explique comment tout installer et démarrer, et un fichier séparé détaille chaque cog un par un dans le dossier [`docs/`](./docs).

---

## 📁 Sommaire des cogs

| Cog | Rôle | Doc dédiée |
|---|---|---|
| `admin` | Modération (ban, mute, purge, sanctions, anti-spam...) | [docs/admin.md](./docs/admin.md) |
| `casino` | Système d'économie complet avec mini-jeux | [docs/casino.md](./docs/casino.md) |
| `debate` | Débat automatique hebdomadaire | [docs/debate.md](./docs/debate.md) |
| `dilemma` | Dilemme automatique hebdomadaire | [docs/dilemma.md](./docs/dilemma.md) |
| `gw` | Giveaways (concours) | [docs/gw.md](./docs/gw.md) |
| `quote` | Sauvegarde de citations via menu contextuel | [docs/quote.md](./docs/quote.md) |
| `stats` | Statistiques des membres et du serveur | [docs/stats.md](./docs/stats.md) |
| `ticket` | Système de tickets de support | [docs/ticket.md](./docs/ticket.md) |
| `voc` | Salons vocaux temporaires personnalisables | [docs/voc.md](./docs/voc.md) |
| `welcome` | Messages de bienvenue / départ | [docs/welcome.md](./docs/welcome.md) |

---

## 🧰 Prérequis

Il te faut simplement :

- **Python 3.10 ou plus récent** (le bot tourne sur `discord.py` 2.x, qui a besoin d'une version relativement récente de Python)
- **pip**, qui vient normalement avec Python

Pour vérifier ce que tu as déjà :

```bash
python3 --version
pip3 --version
```

---

## ⚙️ Installation

Place-toi dans le dossier du projet (celui qui contient `main.py`), puis installe les dépendances listées dans `requirements.txt` :

```bash
cd KuroNexus
python3 -m venv venv
source venv/bin/activate      # sous Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Le fichier `requirements.txt` demande trois choses :

- `discord.py` → la librairie qui permet au bot de parler à Discord
- `python-dotenv` → pour lire le fichier `.env` où sera rangé le token
- `matplotlib` → utilisé par le cog `stats` pour générer les petits graphiques de statistiques

---

## 🔑 Configurer le token du bot (`.env`)

À la racine du projet, tu as un fichier `.env` qui contient actuellement ceci :

```
TOKEN=YOUR TOKEN BOT
```

Remplace `YOUR TOKEN BOT` par le vrai token de ton bot, récupérable sur le [Discord Developer Portal](https://discord.com/developers/applications) → ton application → onglet **Bot** → **Reset Token** (ou **Copy** s'il est déjà visible). Ça donne par exemple :

```
TOKEN=MTA1234567890abcdefgh.GhIjKl.mNoPqRsTuVwXyZ1234567890abcdefg
```

⚠️ **Ne partage jamais ce fichier** (ni le token qu'il contient) — c'est littéralement le mot de passe de ton bot. Si jamais il fuite, régénère-le immédiatement depuis le portail développeur.

### Les intents privilégiés

En regardant `main.py` , le bot demande plusieurs intents, dont trois qui sont **privilégiés** et doivent être activés manuellement sur le portail développeur (sinon le bot plantera au démarrage avec une erreur `PrivilegedIntentsRequired`) :

```python
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True
intents.voice_states = True
```

Pour les activer : sur le [Developer Portal](https://discord.com/developers/applications), ton application → onglet **Bot** → section **Privileged Gateway Intents** → coche **Presence Intent**, **Server Members Intent** et **Message Content Intent**.

---

## 🧩 Choisir les cogs actifs (`config_cogs.json`)

Le fichier `config_cogs.json` à la racine détermine quels modules se chargent au démarrage. Mets `true` pour activer un cog, `false` pour le désactiver :

```json
{
    "admin": true,
    "casino": false,
    "debate": false,
    "dilemma": false,
    "gw": true,
    "quote": true,
    "stats": true,
    "ticket": true,
    "voc": false,
    "welcome": false
}
```

Pas besoin de toucher au code pour ça, `main.py` lit simplement ce fichier et charge un par un les cogs marqués sur `true`.

Une fois que tu as coché tes cogs, va faire un tour dans le fichier de doc de chacun (table plus haut) : certains ont des IDs de salons ou de rôles à renseigner avant de fonctionner correctement.

---

## ▶️ Lancer le bot

Une fois le token renseigné et les cogs configurés :

```bash
python3 main.py
```

Si tout se passe bien, tu devrais voir dans ta console :

```
[OK] Bot connecte en tant que TonBot#0000
[SYNC] X commandes slash synchronisees
[OK] Cog charge : cogs.admin_cog
...
```

La synchronisation des commandes slash (`/`) peut prendre jusqu'à une heure pour apparaître partout selon Discord, mais elle est en général quasi instantanée en pratique.

---

## 📄 Licence

Ce projet est distribué sous la licence présente dans le fichier [`LICENSE`](./LICENSE).
