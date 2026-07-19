# 🎫 Cog `ticket`

Fichier : `cogs/ticket_cog.py`

Ce cog gère un système de support par tickets (un salon privé créé pour chaque demande, avec claim/logs/fermeture) ainsi qu'un bouton d'accès au casino. Pas de fichier `config.json` propre à ce cog, mais il **réutilise** celui du casino pour une seule information — détail expliqué plus bas.

---

## 📍 Les deux variables à configurer

Tout en haut du fichier :

**Ligne 18 — qui peut gérer les tickets :**

```python
claim_admin = [] #<-- Enter the IDs of the roles that can retrieve the tickets
```

Cette liste détermine qui peut voir les nouveaux tickets, les "claim" (se les attribuer), consulter les logs et les fermer à la place du créateur. Remplace la liste vide par les IDs de tes rôles de staff/support, sous forme de liste Python (entre crochets, séparés par des virgules) :

```python
claim_admin = [123456789012345678, 987654321098765432]
```

**Ligne 20 — où envoyer les logs des tickets fermés :**

```python
LOGS_CHANNEL_ID = None #<-- Set the ID of the ticket logs channel
```

Remplace `None` par l'ID du salon texte où le bouton "📄 Logs" doit envoyer l'historique complet d'un ticket avant sa fermeture :

```python
LOGS_CHANNEL_ID = 123456789012345678
```

---

## 🔗 Le lien avec le cog `casino`

Le bouton "🔐Accès" (commande `/acces`, ligne 187) donne un rôle permettant d'accéder au casino. Pour savoir quel rôle donner, le fichier va lire directement `casino_role_id` dans `cogs/CASINO/casino_config.json` (ligne 174) :

```python
role_id = casino_conf["casino_role_id"]
```

Concrètement, ça veut dire que **même si tu n'actives pas le cog `casino`** dans `config_cogs.json`, tu dois quand même garder le fichier `cogs/CASINO/casino_config.json` présent sur le disque avec un `casino_role_id` valide, sinon le cog `ticket` plantera au chargement en cherchant à lire un fichier ou une clé qui n'existe pas. Le détail de ce champ est expliqué dans [docs/casino.md](./casino.md#casino_role_id).

Si tu ne veux pas du tout de ce bouton d'accès casino, la commande `/acces` est indépendante de `/panel` (le panneau de tickets classique) : tu peux simplement ne jamais taper `/acces` sur ton serveur, le reste du cog fonctionnera normalement.

---

## 🎟️ Les deux commandes principales

- `/acces` → poste le bouton d'accès casino (réservé aux administrateurs Discord, via `has_permissions(administrator=True)`)
- `/panel` → poste le panneau "🎫 Créer un ticket" (réservé aux administrateurs Discord également)

Ces deux commandes utilisent la permission native **Administrateur** de Discord plutôt qu'un système de rôles personnalisé, donc rien à remplir de plus pour elles.
