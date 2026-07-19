# 🎁 Cog `gw` (Giveaways)

Fichier : `cogs/gw_cog.py`
Base de données : `cogs/gw/database.db` (déjà créée, tu n'as rien à générer)

Ce cog permet de lancer des concours (giveaways) avec un bouton "🎁 Participer", un tirage au sort automatique à la fin du minuteur, et un historique des gagnants. Pas de fichier `config.json` séparé, tout se règle directement dans le code.

---

## 🔐 Qui peut créer un giveaway ?

Comme dans le cog `admin`, chaque commande est protégée par `@has_role_permission(None)`, avec le même commentaire à côté :

```python
@has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
```

Tu la retrouves à ces lignes :

| Ligne | Commande |
|---|---|
| 81 | `/gw-help` |
| 92 | `/giveaway` |
| 207 | `/winners` |

Remplace `None` par le ou les IDs de rôles autorisés, comme pour le cog admin :

```python
@has_role_permission(123456789012345678, 987654321098765432)
```

## 🎉 Lancer un giveaway

La commande `/giveaway <durée> <gagnants> <prix>` (ligne 91) ne demande aucune configuration préalable : elle prend en paramètres la durée en minutes, le nombre de gagnants et le nom du lot directement au moment de l'utiliser sur Discord. Le bot poste l'embed avec le bouton "🎁 Participer", attend le temps donné, puis tire au sort parmi les participants enregistrés en base et annonce les gagnants.

---

## 💾 À propos de la base de données

`cogs/gw/database.db` contient déjà les tables `giveaways`, `participants` et `winners` utilisées par ce cog — aucune création manuelle nécessaire, tout est prêt à l'emploi dès le premier lancement.
