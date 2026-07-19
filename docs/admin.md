# 🛡️ Cog `admin`

Fichier : `cogs/admin_cog.py`
Base de données : `cogs/admin/database.db` (déjà créée avec ses tables, tu n'as rien à générer toi-même)

C'est le cog de modération : ban, mute temporaire, purge, gestion des sanctions, anti-spam automatique, verrouillage de salons, gestion de rôles... Il n'a pas de fichier `config.json` séparé : tout se règle directement dans le code, via des petites variables laissées à `None` ou vides, accompagnées d'un commentaire qui te dit quoi faire.

---

## 🔐 Qui peut utiliser les commandes ?

Toutes les commandes de ce cog sont protégées par un décorateur `@has_role_permission(...)`. Actuellement, elles valent toutes `None`, ce qui veut dire **que tout le monde peut les utiliser** — pas idéal pour des commandes de modération ! Le commentaire à côté de chaque ligne est clair :

```python
@has_role_permission(None) #<-- Paste the IDs of the roles authorized to use this command inside the parentheses; if you leave it on None, everyone will be able to use the command
```

Il te suffit de remplacer `None` par les IDs (nombres) des rôles autorisés à utiliser la commande, séparés par des virgules. Par exemple, si tu as un rôle "Modérateur" (ID `123456789012345678`) et un rôle "Admin" (ID `987654321098765432`) :

```python
@has_role_permission(123456789012345678, 987654321098765432)
```

Tu peux mettre un rôle différent selon la commande — un `/purge` accessible aux modérateurs, un `/derank` réservé aux admins, à toi de voir. Voici toutes les lignes concernées, avec la commande associée :

| Ligne | Commande | Ce qu'elle fait |
|---|---|---|
| 164 | `/admin-help` | Affiche l'aide |
| 192 | `/ban` | Bannir un membre |
| 207 | `/unban` | Débannir via un ID |
| 217 | `/banlist` | Lister les bannis |
| 228 | `/include-spam` | Exclure un membre de l'anti-spam |
| 238 | `/exclude-spam` | Réinclure un membre dans l'anti-spam |
| 248 | `/lock` | Verrouiller un salon |
| 255 | `/unlock` | Déverrouiller un salon |
| 262 | `/sanctions` | Voir les sanctions d'un membre |
| 288 | `/clear-sanction` | Effacer toutes les sanctions d'un membre |
| 305 | `/delete-sanction` | Effacer une sanction précise |
| 333 | `/mute` | Ouvrir le menu de mute temporaire |
| 338 | `/unmute` | Retirer le mute |
| 348 | `/mute-list` | Lister les mutes actifs |
| 364 | `/add-role` | Ajouter un rôle |
| 370 | `/delete-role` | Retirer un rôle |
| 376 | `/derank` | Retirer tous les rôles |
| 382 | `/antispam` | Activer/désactiver l'anti-spam |
| 394 | `/set-antispam` | Régler la tolérance de l'anti-spam |
| 401 | `/purge` | Supprimer des messages |

Chaque ligne s'édite indépendamment, donc rien ne t'empêche de laisser certaines commandes ouvertes à tous (comme `/admin-help`) et de verrouiller les plus sensibles.

---

## 🎭 Le rôle de mute

Ici, il y a un point important à ne pas rater : le rôle donné quand on mute quelqu'un est défini à **un seul endroit**

Ligne 69, dans `MuteSelect.callback` :

```python
ROLE_ID = None #<-- Assign the role that is to be given to the mute person
```

Remplace `None` par l'ID du rôle "Muted" de ton serveur (celui qui doit avoir la permission `Envoyer des messages` désactivée dans tes salons) :

```python
ROLE_ID = 123456789012345678
```

---

## 🧹 L'anti-spam

L'anti-spam est géré automatiquement par le cog (écoute de `on_message`, lignes 129-159) : si un membre envoie trop de messages en peu de temps, ses messages sont supprimés et il reçoit un timeout de 10 secondes. Par défaut (ligne 98-100) :

```python
self.antispam_enabled = True
self.antispam_limit = 5
self.antispam_interval = 5
```

Autrement dit : 5 messages en 5 secondes déclenchent le timeout. Tu n'as rien à modifier ici si ces valeurs te conviennent — tu peux aussi les ajuster en direct sur le serveur avec `/antispam on|off` et `/set-antispam <messages> <secondes>`, pas besoin de retoucher au code.

---

## ✅ Ce qu'il n'y a pas besoin de configurer

La base de données SQLite (`cogs/admin/database.db`) existe déjà dans l'archive avec toutes ses tables (`messages`, `excluded_users`, `sanctions_user`, `temp_roles`) : tu n'as rien à créer, le cog s'en sert directement.
