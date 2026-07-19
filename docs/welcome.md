# 👋 Cog `welcome`

Fichier : `cogs/welcome_cog.py`
Configuration : `cogs/welcome/config.json`

Le plus simple des cogs configurables : il poste un message de bienvenue quand un membre arrive, et un message d'au revoir quand il part. Tout se règle dans le fichier de config, aucune ligne de code à toucher.

---

## 📝 Le fichier `config.json`

```json
{
    "arrived_channel_id": 1505488374264500454,
    "leave_channel_id": 1505488488781582416
}
```

### `arrived_channel_id`
L'ID du salon où sera posté le message de bienvenue quand quelqu'un rejoint le serveur (lu ligne 12 de `welcome_cog.py`, utilisé ligne 22).

### `leave_channel_id`
L'ID du salon où sera posté le message d'au revoir quand quelqu'un quitte le serveur (lu ligne 13, utilisé ligne 44).

Remplace les deux valeurs d'exemple par les IDs de tes propres salons (Mode développeur activé dans Discord → clic droit sur le salon → **Copier l'identifiant**). Rien d'autre à faire, les deux salons peuvent d'ailleurs être identiques si tu préfères tout centraliser dans un seul salon "arrivées/départs".


