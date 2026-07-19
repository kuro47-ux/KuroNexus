# 📜 Commandes de KuroNexus

Listing complet de toutes les commandes du bot, classées par cog. Les commandes slash (`/`) fonctionnent partout sur le serveur, les commandes préfixées (`+`) ne fonctionnent que dans les salons vocaux temporaires du cog `voc`.

> 🔒 = commande restreinte par rôle ou permission (voir la doc du cog concerné dans `docs/` pour savoir comment configurer qui y a accès)

---

## 🛡️ Admin

*Modération du serveur — cog `admin`*

| Commande | Description |
|---|---|
| 🔒 `/admin-help` | Affiche la liste des commandes d'administration |
| 🔒 `/ban <utilisateur> [raison]` | Bannit un membre, avec une raison optionnelle |
| 🔒 `/unban <id_utilisateur>` | Débannit un utilisateur via son ID |
| 🔒 `/banlist` | Affiche la liste des utilisateurs bannis |
| 🔒 `/include-spam <utilisateur>` | Exclut un membre de la détection anti-spam |
| 🔒 `/exclude-spam <utilisateur>` | Réintègre un membre dans la détection anti-spam |
| 🔒 `/lock [salon]` | Verrouille le salon actuel ou celui indiqué |
| 🔒 `/unlock [salon]` | Déverrouille le salon actuel ou celui indiqué |
| 🔒 `/sanctions <id_utilisateur>` | Affiche l'historique des sanctions d'un membre |
| 🔒 `/clear-sanction <id_utilisateur>` | Supprime toutes les sanctions d'un membre |
| 🔒 `/delete-sanction <id_utilisateur> <numéro>` | Supprime une sanction précise |
| 🔒 `/mute <utilisateur>` | Ouvre un menu pour muter temporairement un membre (motif au choix) |
| 🔒 `/unmute <utilisateur>` | Retire le mute d'un membre |
| 🔒 `/mute-list` | Affiche la liste des mutes actifs |
| 🔒 `/add-role <utilisateur> <rôle>` | Ajoute un rôle à un membre |
| 🔒 `/delete-role <utilisateur> <rôle>` | Retire un rôle à un membre |
| 🔒 `/derank <utilisateur>` | Retire tous les rôles d'un membre |
| 🔒 `/antispam <on/off>` | Active ou désactive l'anti-spam global |
| 🔒 `/set-antispam <messages> <secondes>` | Règle le seuil de déclenchement de l'anti-spam |
| 🔒 `/purge <nombre>` | Supprime un nombre de messages donné dans le salon |

---

## 🎰 Casino

*Économie virtuelle et mini-jeux — cog `casino`*

**💰 Économie**

| Commande | Description |
|---|---|
| `/portefeuille` | Affiche ton solde (coins, gems, tickets, jetons VIP) |
| `/inventaire` | Affiche tous les objets achetés en boutique |
| `/shop` | Ouvre la boutique du casino |
| `/ouvrir_coffre <coffre>` | Ouvre un coffre présent dans ton inventaire |
| `/wheelspin_legendaire` | Lance la Roue Légendaire (nécessite un objet dédié) |
| `/luckyspin` | Lance un Lucky Spin (consomme un ticket) |
| 🔒 `/casino_admin <action> <cible> <ressource> <montant>` | Donne ou retire des coins/gems/tickets/jetons VIP à un joueur *(admin)* |
| 🔒 `/casino_admin_xp <action> <cible> <montant>` | Donne ou retire de l'expérience à un joueur *(admin)* |

**🎲 Mini-jeux**

| Commande | Description |
|---|---|
| `/coinflip <mise>` | Pile ou face |
| `/dice <mise> <choix>` | Jeu de dés |
| `/slots <mise>` | Machine à sous *(niveau 25 requis, ou objet Slots Premium)* |
| `/roulette <mise> <choix>` | Roulette |
| `/crash <mise> <multiplicateur>` | Jeu Crash, encaisser avant le krach |
| `/wheelspin <mise>` | Roue de la fortune classique |
| `/blackjack <mise>` | Blackjack *(niveau 10 requis, ou objet Table VIP)* |
| `/keno <mise>` | Keno |

Chaque jeu a un niveau minimum et un salon dédié définis dans `casino_config.json` (voir [docs/casino.md](./docs/casino.md)).

---

## 🎤 Débat & 🤔 Dilemme

*Publications automatiques hebdomadaires — cogs `debate` et `dilemma`*

Ces deux cogs n'ont **aucune commande** : ils postent tout seuls, chaque semaine, un sujet de débat ou un dilemme dans le salon configuré. Voir [docs/debate.md](./docs/debate.md) et [docs/dilemma.md](./docs/dilemma.md) pour régler le jour et l'heure d'envoi.

---

## 🎁 Giveaways

*Concours et tirages au sort — cog `gw`*

| Commande | Description |
|---|---|
| 🔒 `/gw-help` | Affiche l'aide des giveaways |
| 🔒 `/giveaway <durée> <gagnants> <prix>` | Lance un giveaway (durée en minutes) avec un bouton "🎁 Participer" |
| 🔒 `/winners` | Affiche l'historique des gagnants de tous les giveaways |

---

## 💬 Citations

*Archivage de messages marquants — cog `quote`*

| Commande | Description |
|---|---|
| *Clic droit sur un message → Applications → **Enregistrer la citation*** | Archive le message dans le salon configuré, avec l'auteur et la date |

Ce n'est pas une commande slash mais un menu contextuel, accessible directement depuis n'importe quel message du serveur.

---

## 📊 Statistiques

*Suivi d'activité — cog `stats`*

| Commande | Description |
|---|---|
| `/stats-help` | Affiche l'aide des statistiques |
| `/stats [membre]` | Affiche les statistiques d'un membre (ou les tiennes) avec un graphique |
| `/servstats` | Affiche les statistiques globales du serveur |
| `/top-vocal` | Classement des membres les plus présents en vocal |
| `/top-messages` | Classement des membres les plus actifs à l'écrit |
| `/leaderboard` | Classement global pondéré (messages, vocal, giveaways, commandes) |

---

## 🎫 Tickets

*Support et accès casino — cog `ticket`*

| Commande | Description |
|---|---|
| 🔒 `/acces` | Poste le bouton d'accès au rôle casino *(admin)* |
| 🔒 `/panel` | Poste le panneau "🎫 Créer un ticket" *(admin)* |

**Boutons associés (une fois les panneaux postés) :**

| Bouton | Description |
|---|---|
| 🎫 Créer un ticket | Ouvre un salon privé de support pour le membre |
| 🔑 Claim | Un membre du staff s'attribue le ticket |
| 📄 Logs | Envoie l'historique du ticket dans le salon de logs |
| ❌ Fermer | Ferme et supprime le ticket (par le créateur ou le staff) |
| 🔐 Accès | Donne le rôle casino au membre qui clique |

---

## 🔊 Salons vocaux temporaires

*Salons vocaux à la demande — cog `voc`*

Aucune commande slash ici : il suffit de rejoindre le salon "générateur" configuré pour obtenir son propre salon vocal. Une fois dedans, ces commandes textuelles (préfixe `+`) sont disponibles pour le propriétaire du salon :

| Commande | Description |
|---|---|
| `+limit <nombre>` | Définit la limite de places (0 à 99, 0 = illimité) |
| `+lock` | Verrouille le salon (empêche les nouvelles connexions) |
| `+unlock` | Déverrouille le salon |
| `+ghost` | Rend le salon invisible dans la liste des salons |
| `+unghost` | Rend le salon de nouveau visible |
| `+name <nouveau nom>` | Renomme le salon (32 caractères max) |
| `+kick @membre` | Expulse un membre du salon |
| `+claim` | Permet de récupérer la propriété du salon si le créateur est parti |

---

## 👋 Bienvenue

*Messages d'arrivée et de départ — cog `welcome`*

Aucune commande : le cog poste automatiquement un embed de bienvenue quand un membre rejoint le serveur, et un embed d'au revoir quand il le quitte.

---

## 🗒️ Récapitulatif express

| Cog | Nb. de commandes slash | Commandes textuelles | Boutons/Menus |
|---|---|---|---|
| `admin` | 19 | — | — |
| `casino` | 16 | — | — |
| `debate` | 0 | — | — |
| `dilemma` | 0 | — | — |
| `gw` | 3 | — | 1 bouton |
| `quote` | 0 | — | 1 menu contextuel |
| `stats` | 6 | — | — |
| `ticket` | 2 | — | 5 boutons |
| `voc` | 0 | 7 | — |
| `welcome` | 0 | — | — |
| **Total** | **46** | **7** | **7** |
