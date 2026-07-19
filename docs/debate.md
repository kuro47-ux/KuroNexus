# 🎤 Cog `debate`

Fichier : `cogs/debate_cog.py`
Configuration : `cogs/debate/config.json`

Ce cog envoie automatiquement, chaque semaine, un sujet de débat aléatoire dans un salon donné, avec un embed et trois réactions (👍 👎 🤷) pour que les membres puissent réagir. Rien à modifier dans le code Python ici, tout se règle dans `config.json`.

---

## 📝 Le fichier `config.json`

```json
{
    "day": 2,
    "debate_channel_id": 1505491656806240388,
    "time": {
        "hour": 14,
        "minute": 0,
        "second": 0
    }
}
```

### `debate_channel_id`
L'ID du salon texte où le débat hebdomadaire sera publié (lu ligne 14 de `debate_cog.py`, puis utilisé ligne 48). Remplace la valeur d'exemple par l'ID de ton propre salon (clic droit dessus avec le Mode développeur activé → **Copier l'identifiant**).

### `day`
Le jour de la semaine où le débat doit être envoyé. C'est un chiffre de **0 à 6**, sur le même principe que `datetime.weekday()` en Python :

| Valeur | Jour |
|---|---|
| 0 | Lundi |
| 1 | Mardi |
| 2 | Mercredi |
| 3 | Jeudi |
| 4 | Vendredi |
| 5 | Samedi |
| 6 | Dimanche |

La valeur par défaut est `2` (mercredi), ce qui colle avec les textes de l'embed ("C'est mercredi, l'heure de donner votre avis") — si tu changes le jour, pense à adapter le texte à la ligne 58 de `debate_cog.py` pour que ça reste cohérent.

### `time`
L'heure d'envoi, découpée en heures/minutes/secondes (fuseau horaire du serveur qui fait tourner le bot). Par défaut : `14:00:00`, donc 14h précises.

⚠️ Petit détail technique : la tâche programmée (`@tasks.loop(time=DEBATE_TIME)`, ligne 43) se déclenche **chaque jour** à l'heure choisie, mais le code vérifie ensuite si on est bien le bon jour de la semaine avant d'envoyer quoi que ce soit (ligne 45). C'est normal que le bot "se réveille" tous les jours à 14h sans rien faire les jours où ce n'est pas mercredi — c'est voulu, pas un bug.

---

## 💬 Les sujets de débat

La liste des 10 sujets possibles est codée en dur dans `debate_cog.py` (`SUJETS_DEBATS`, lignes 29-40). Tu peux librement en ajouter, en retirer ou réécrire les textes existants — c'est une simple liste Python, aucune contrainte de format à respecter à part garder les guillemets et les virgules entre chaque ligne.
