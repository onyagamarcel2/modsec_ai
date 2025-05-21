# Anomalies Buffer

## Vue d'Ensemble
Le buffer d'anomalies gère le stockage temporaire et la file d'attente des anomalies détectées en attente de validation.

## Fonctionnalités

### Gestion du Buffer
- Stockage temporaire des anomalies
- File d'attente prioritaire
- Gestion de la capacité
- Persistance des données

### Configuration
```yaml
anomalies_buffer:
  max_size: 1000
  persistence:
    enabled: true
    path: "data/anomalies_buffer.db"
    backup_interval: 3600  # secondes
  priority_levels:
    - CRITICAL
    - HIGH
    - MEDIUM
    - LOW
  retention:
    max_age: 86400  # 24 heures
    cleanup_interval: 3600  # 1 heure
```

## Utilisation

```python
from modsec_ai.src.core.anomalies_buffer import AnomaliesBuffer

buffer = AnomaliesBuffer(
    config_path="config/anomalies_buffer.yaml"
)

# Ajouter une anomalie
buffer.add_anomaly(
    anomaly_id="anom_123",
    priority="HIGH",
    data={
        "score": 0.95,
        "type": "SQL_INJECTION",
        "timestamp": "2024-03-14T12:00:00Z"
    }
)

# Récupérer la prochaine anomalie
next_anomaly = buffer.get_next_anomaly()
```

## Structure des Données

### Format d'Anomalie
```json
{
    "id": "anom_123",
    "timestamp": "2024-03-14T12:00:00Z",
    "priority": "HIGH",
    "status": "PENDING",
    "data": {
        "score": 0.95,
        "type": "SQL_INJECTION",
        "source_ip": "192.168.1.1",
        "details": {
            "confidence": 0.89,
            "features": [...],
            "context": {...}
        }
    }
}
```

### États
- PENDING
- IN_VALIDATION
- VALIDATED
- IGNORED
- EXPIRED

## Gestion des Erreurs
- Gestion de la surcharge
- Reprise après erreur
- Validation des données

## Performance
- Indexation optimisée
- Cache en mémoire
- Nettoyage automatique

## Intégration
- Interface avec AnomalyDetector
- Flux vers ValidationRules
- Synchronisation avec Dashboard 