# 🎰 Cog `casino`

Fichier : `cogs/casino_cog.py`
Configuration : `cogs/CASINO/casino_config.json`
Données des joueurs : `cogs/CASINO/casino_data.json` (généré et rempli automatiquement, tu n'y touches jamais à la main)

C'est le plus gros cog du bot : économie virtuelle (coins, gems, tickets, jetons VIP), système de niveaux/XP, boutique, coffres, et une bonne brochette de mini-jeux (coinflip, dés, machine à sous, blackjack, roulette, crash, roue de la fortune, keno). Bonne nouvelle : il n'y a **aucun bout de code à compléter** dans `casino_cog.py`, tout se pilote depuis le fichier `casino_config.json`.

---

## 📝 Le fichier `casino_config.json`

```json
{
    "game_levels": {
        "coinflip": 0,
        "dice": 0,
        "slots": 25,
        "blackjack": 10,
        "roulette": 10,
        "crash": 25,
        "wheelspin": 50,
        "keno": 50
    },
    "level_roles": {
        "0": null,
        "10": "1505542480014344233",
        "25": "1505542872794140742",
        "50": "1505542965756690502"
    },
    "game_channels": {
        "coinflip": "1505535407071170583",
        "dice": "1505535464717680640",
        "slots": "1505534861841137754",
        "blackjack": "1505534969957847230",
        "roulette": "1505535091076632595",
        "crash": "1505535193652527225",
        "wheelspin": "1505535779185754152",
        "keno": "1505535619055620206"
    },
    "level_up_channel": "1505535619055620206",
    "casino_role_id": 1505535619055620206,
    "exp_per_win": 100,
    "exp_per_loss": 25,
    "exp_to_level": 1000
}
```

Ce fichier contient actuellement des IDs d'exemple (de mon serv) : il faut que tu les remplaces par les tiens, sinon le bot pointera vers des salons/rôles qui n'existent pas sur ton serveur. Voici ce que fait chaque champ, avec la ligne du code qui l'utilise pour que tu comprennes bien l'effet :

### `game_levels`
Le niveau minimum requis pour débloquer chaque jeu (le cog vérifie ça à la ligne 418 de `casino_cog.py`). `coinflip` et `dice` sont à `0` donc accessibles à tous dès le départ ; `slots` et `blackjack` peuvent aussi être débloqués plus tôt via un objet acheté en boutique (`slots_premium` / `blackjack_vip`).

### `level_roles`
Un rôle Discord donné automatiquement à chaque palier de niveau (utilisé ligne 454, dans `handle_level_up`). Les clés sont les niveaux (en texte, entre guillemets), les valeurs sont les IDs de rôles (ou `null` si tu ne veux rien donner à ce palier). Tu peux ajouter d'autres paliers si tu veux (ex. `"75": "..."`), il suffit que la clé corresponde à un niveau atteignable.

### `game_channels`
Le salon dans lequel chaque jeu doit obligatoirement être joué (vérifié ligne 422). Si un joueur tape `/slots` ailleurs que dans le salon indiqué, le bot lui répondra qu'il doit se rendre dans le bon salon. Mets l'ID du salon texte dédié à chaque jeu — tu peux réutiliser le même salon pour plusieurs jeux si tu préfères tout centraliser.

### `level_up_channel`
Le salon où sera annoncé un passage de niveau (ligne 433). Mets l'ID d'un salon texte visible par tout le monde, par exemple un salon "annonces-casino".

### `casino_role_id`
Le rôle donné aux membres qui cliquent sur le bouton "🔐Accès" du cog `ticket` pour débloquer l'accès au casino (voir [docs/ticket.md](./ticket.md)). C'est le seul champ écrit sans guillemets dans le JSON (un nombre brut, pas une chaîne de texte) — garde bien ce format.

### `exp_per_win` / `exp_per_loss` / `exp_to_level`
Le nombre de points d'expérience gagnés à chaque victoire, à chaque défaite, et le total d'XP nécessaire pour passer au niveau suivant (utilisés lignes 127 et 176). Avec les valeurs par défaut, il faut 10 victoires pour monter d'un niveau.

---

## 🔎 Comment récupérer un ID Discord

Si tu ne sais pas encore comment récupérer un ID de salon ou de rôle : active le **Mode développeur** dans Discord (Paramètres → Avancés → Mode développeur), puis fais un clic droit sur le salon ou le rôle en question → **Copier l'identifiant**.

---

## 🛠️ Commandes d'administration

Contrairement au cog `admin`, les commandes sensibles du casino (`/casino_admin` pour donner/retirer des coins, gems, tickets ou jetons VIP, et `/casino_admin_xp` pour l'expérience) sont déjà protégées par la permission Discord native **Administrateur** — pas besoin de configurer d'IDs de rôles ici, elles fonctionnent telles quelles.

---

## 💾 À propos de `casino_data.json`

Ce fichier stocke le portefeuille, l'inventaire et le niveau de chaque joueur. Il est vide (`{}`) à l'origine et se remplit tout seul dès qu'un joueur utilise une commande pour la première fois (fonction `get_user_data`, ligne 68) — tu n'as absolument rien à y faire manuellement.
