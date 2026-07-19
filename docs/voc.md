# 🔊 Cog `voc`

Fichier : `cogs/voc_cog.py`

Ce cog met en place des salons vocaux temporaires à la demande : un membre rejoint un salon "générateur", et le bot lui crée instantanément son propre salon vocal privé, qu'il peut ensuite personnaliser (`+limit`, `+lock`, `+name`, `+kick`...) via des commandes textuelles préfixées par `+`. Le salon se supprime tout seul dès qu'il se vide. Aucun fichier `config.json`, une seule variable à remplir.

---

## 📍 La seule chose à configurer

Dans le constructeur du cog, ligne 9 :

```python
self.CREATOR_CHANNEL_ID = None #<-- Enter the voice channel ID to create a personal voice chat
```

Remplace `None` par l'ID du salon vocal qui servira de "générateur" — celui que tes membres devront rejoindre pour déclencher la création automatique de leur salon personnel :

```python
self.CREATOR_CHANNEL_ID = 123456789012345678
```

💡 Idée pratique : crée un salon vocal appelé par exemple **"➕ Créer un salon"**, récupère son ID (Mode développeur activé → clic droit → **Copier l'identifiant**), et mets-le ici. Dès qu'un membre le rejoint, il est automatiquement déplacé dans son propre salon fraîchement créé (ligne 32-42), et un message d'aide listant toutes les commandes disponibles est posté dans son chat vocal (fonction `send_voice_help`, ligne 63).

---

## 🎛️ Les commandes disponibles une fois dans son salon

Une fois son salon créé, le propriétaire (et lui seul, sauf pour `+claim`) peut utiliser ces commandes textuelles avec le préfixe `+` :

- `+limit <nombre>` → limite de places (0 à 99, 0 = illimité)
- `+lock` / `+unlock` → verrouille/déverrouille l'entrée du salon
- `+ghost` / `+unghost` → rend le salon invisible/visible dans la liste des salons
- `+name <nouveau nom>` → renomme le salon (32 caractères max)
- `+kick @membre` → expulse quelqu'un du salon
- `+claim` → permet à un membre présent de récupérer la propriété du salon si le créateur original est parti

Tout ceci fonctionne sans configuration additionnelle dès que `CREATOR_CHANNEL_ID` est rempli — c'est la seule variable dont ce cog a besoin.
