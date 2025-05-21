# Training Buffer

## Vue d'Ensemble
Le buffer d'entraînement gère la collecte et la préparation des données pour l'entraînement et la mise à jour du modèle de détection d'anomalies.

## Fonctionnalités

### Gestion du Buffer
- Collecte des données d'entraînement
- Gestion de la fenêtre glissante
- Préparation des batchs
- Persistance des données

### Configuration
```yaml
training_buffer:
  max_size: 100000
  window_size: 7d
  batch_size: 1000
  persistence:
    enabled: true
    path: "data/training_buffer.db"
    backup_interval: 3600  # secondes
  sampling:
    strategy: "random"  # random, time-based
    ratio: 0.1
    min_samples: 1000
```

## Utilisation

```python
from modsec_ai.src.core.training_buffer import TrainingBuffer

buffer = TrainingBuffer(
    config_path="config/training_buffer.yaml"
)

# Ajouter des données
buffer.add_samples(
    samples=[
        {
            "features": [...],
            "label": "normal",
            "timestamp": "2024-03-14T12:00:00Z"
        }
    ]
)

# Préparer un batch
batch = buffer.get_training_batch()
```

## Structure des Données

### Format d'Échantillon
```json
{
    "id": "sample_123",
    "timestamp": "2024-03-14T12:00:00Z",
    "features": [...],
    "metadata": {
        "source": "knowledge_base",
        "confidence": 0.98,
        "validation_status": "validated"
    }
}
```

### Types d'Échantillons
- Normal
- Anomaly
- Validated
- Unvalidated

## Gestion des Erreurs
- Validation des données
- Gestion de la surcharge
- Reprise après erreur

## Performance
- Indexation optimisée
- Cache des échantillons fréquents
- Nettoyage automatique

## Intégration
- Interface avec KnowledgeBase
- Flux vers ModelUpdater
- Synchronisation avec Dashboard 