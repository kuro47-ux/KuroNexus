# 📊 Cog `stats`

Fichier : `cogs/stats_cog.py`
Base de données : `cogs/stats/database.db` (déjà créée, tu n'as rien à générer)

Ce cog suit l'activité de chaque membre (messages envoyés, temps passé en vocal, commandes utilisées, giveaways gagnés) et propose des commandes pour afficher des jolis graphiques via `matplotlib`, un classement du serveur, et un compteur de membres mis à jour automatiquement dans le nom d'un salon. Aucun fichier `config.json` ici, une seule variable à remplir dans le code.

---

## 📍 La seule chose à configurer

Tout en haut du fichier, ligne 15 :

```python
MEMBER_CHANNEL_ID = None #<-- Place the voice or text channel id that will display the member count
```

Remplace `None` par l'ID d'un salon (vocal ou textuel, les deux fonctionnent) dont tu veux que le **nom** affiche automatiquement le nombre de membres du serveur, par exemple :

```python
MEMBER_CHANNEL_ID = 123456789012345678
```

Le bot renommera ce salon en `👥 Membres : XXX` de trois façons différentes selon le code :
- toutes les **10 secondes**, via une tâche automatique (`update_member_channel`, ligne 442)
- immédiatement quand quelqu'un **rejoint** le serveur (ligne 31)
- immédiatement quand quelqu'un **quitte** le serveur (ligne 41)

⚠️ Un point à garder en tête : Discord limite le renommage d'un salon à **2 fois toutes les 10 minutes** environ. Avec une vérification automatique toutes les 10 secondes, ce n'est un souci que si beaucoup de membres arrivent/partent en même temps — dans ce cas Discord retardera simplement la mise à jour du nom, rien de grave, mais évite de descendre l'intervalle de la tâche en dessous de 10 secondes si tu comptes le modifier.

💡 Si tu veux désactiver complètement ce compteur, tu peux laisser `MEMBER_CHANNEL_ID` à `None` : le bot essaiera simplement de trouver un salon avec l'ID `None`, ne trouvera rien, et ne fera rien (grâce aux `if channel:` placés avant chaque tentative de renommage) — pas de crash, juste une fonctionnalité inactive.

---

## 📈 Les commandes disponibles

- `/stats [membre]` → statistiques personnelles avec un graphique en barres
- `/servstats` → statistiques globales du serveur
- `/top-vocal` → classement des membres les plus présents en vocal
- `/top-messages` → classement des membres les plus actifs à l'écrit
- `/leaderboard` → classement global pondéré (messages + minutes vocales + giveaways × 500 + commandes × 5)

Aucune de ces commandes ne nécessite de configuration supplémentaire — elles lisent directement dans `cogs/stats/database.db`, dont les tables existent déjà.
