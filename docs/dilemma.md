# 🤔 Cog `dilemma`

Fichier : `cogs/dilemma_cog.py`
Configuration : `cogs/dilemma/config.json`

Le jumeau du cog `debate` : chaque semaine, il envoie un dilemme ("tu préfères A ou B ?") avec deux réactions 🔵 et 🔴 pour voter. Le fonctionnement est identique à `debate`, donc si tu as déjà configuré ce dernier, tu es en terrain connu.

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

Note au passage que la clé s'appelle encore `debate_channel_id` même dans le config du dilemme (petit copier-coller du cog `debate` visiblement) — c'est normal, `dilemma_cog.py` lit bien cette clé à la ligne 14, ne la renomme surtout pas dans le JSON sinon le bot plantera au démarrage.

### `debate_channel_id`
L'ID du salon texte où le dilemme sera publié chaque semaine. Remplace la valeur d'exemple par l'ID de ton salon.

### `day`
Le jour de la semaine d'envoi, de `0` (lundi) à `6` (dimanche) — voir le tableau détaillé dans [docs/debate.md](./debate.md#day). Par défaut `2` = mercredi, ce qui correspond au texte de l'embed ("LE DILEMME DU MERCREDI", ligne 54). Si tu changes le jour, pense à adapter ce texte pour que ça reste logique.

### `time`
L'heure d'envoi (heures/minutes/secondes). Par défaut `14:00:00`.

💡 Si tu actives à la fois `debate` et `dilemma` avec le **même** salon et la **même** heure, les deux messages partiront quasiment en même temps — libre à toi de les décaler (par exemple débat à 14h, dilemme à 18h) en changeant simplement le `time` de l'un des deux fichiers.

---

## 🎲 Les dilemmes

Comme pour `debate`, la liste des 10 dilemmes est codée en dur dans `dilemma_cog.py` (`SUJETS_DILEMMES`, lignes 27-38). Tu peux les modifier ou en ajouter librement, tant que tu gardes le format d'une liste de chaînes de texte séparées par des virgules.
