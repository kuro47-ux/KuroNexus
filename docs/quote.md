# 💬 Cog `quote`

Fichier : `cogs/quote_cog.py`

Le plus court des cogs : il ajoute un menu contextuel Discord ("clic droit sur un message → Applications → Enregistrer la citation") qui recopie le message dans un salon dédié, avec l'auteur, la date et la personne qui a fait l'archivage. Aucun fichier `config.json`, une seule ligne à modifier.

---

## 📍 La seule chose à configurer

Tout en haut du fichier, ligne 6 :

```python
QUOTE_CHANNEL_ID = None #<-- Enter the channel id where you want the quotes to be saved
```

Remplace `None` par l'ID du salon texte où tu veux que les citations archivées atterrissent :

```python
QUOTE_CHANNEL_ID = 123456789012345678
```

Pour récupérer cet ID : active le Mode développeur dans Discord (Paramètres → Avancés), puis clic droit sur le salon → **Copier l'identifiant**.

Si tu oublies cette étape, le bot te le rappellera gentiment : la commande renverra un message d'erreur ("Le salon d'archivage des citations est introuvable") plutôt que de planter silencieusement (ligne 33-38).

---

## ✅ Rien d'autre à faire

Pas de base de données, pas de fichier annexe : une fois l'ID renseigné, le menu contextuel apparaît automatiquement sur tous les messages du serveur dès que le cog est chargé.
