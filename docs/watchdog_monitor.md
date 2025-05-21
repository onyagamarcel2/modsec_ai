# Watchdog Monitor

## Vue d'Ensemble
Le Watchdog Monitor est un composant essentiel qui surveille en continu les fichiers de logs ModSecurity pour détecter les nouvelles entrées et déclencher leur traitement.

## Fonctionnalités

### Surveillance Continue
- Détection en temps réel des modifications de fichiers
- Support des rotations de logs
- Gestion des fichiers compressés (.gz)

### Configuration
```yaml
watchdog:
  monitored_paths:
    - path: "/var/log/modsec_audit.log"
      pattern: "*.log"
      recursive: false
  check_interval: 1.0  # secondes
  max_file_size: 104857600  # 100MB
```

### Événements
- `on_created`: Nouveau fichier détecté
- `on_modified`: Modification détectée
- `on_deleted`: Fichier supprimé
- `on_moved`: Fichier déplacé

## Utilisation

```python
from modsec_ai.src.core.watchdog import WatchdogMonitor

monitor = WatchdogMonitor(
    paths=["/var/log/modsec_audit.log"],
    callback=process_new_logs
)
monitor.start()
```

## Gestion des Erreurs
- Vérification des permissions
- Gestion des fichiers verrouillés
- Reprise après erreur

## Performance
- Utilisation de threads dédiés
- Buffer de lecture optimisé
- Gestion de la mémoire

## Intégration
- Interface avec le Log Parser
- Notification des nouveaux logs
- Gestion des événements système 