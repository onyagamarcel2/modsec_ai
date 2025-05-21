# Knowledge Base

## Vue d'Ensemble
La base de connaissances stocke et gère les patterns légitimes et les décisions de validation pour améliorer la détection d'anomalies.

## Fonctionnalités

### Gestion des Patterns
- Stockage des patterns légitimes
- Historique des décisions
- Apprentissage continu
- Mise à jour des règles

### Configuration
```yaml
knowledge_base:
  storage:
    type: "sqlite"  # sqlite, postgresql
    path: "data/knowledge_base.db"
    backup_interval: 86400  # 24 heures
  patterns:
    max_age: 2592000  # 30 jours
    min_confidence: 0.95
    update_interval: 3600  # 1 heure
  learning:
    enabled: true
    min_samples: 100
    max_samples: 10000
    window_size: 7d
```

## Utilisation

```python
from modsec_ai.src.core.knowledge_base import KnowledgeBase

kb = KnowledgeBase(
    config_path="config/knowledge_base.yaml"
)

# Ajouter un pattern
kb.add_pattern(
    pattern_type="HTTP_REQUEST",
    features={
        "method": "GET",
        "path": "/api/v1/users",
        "headers": {...}
    },
    confidence: 0.98
)

# Vérifier un pattern
is_known = kb.check_pattern(features)
```

## Structure des Données

### Format de Pattern
```json
{
    "id": "pattern_123",
    "type": "HTTP_REQUEST",
    "features": {
        "method": "GET",
        "path": "/api/v1/users",
        "headers": {...},
        "parameters": {...}
    },
    "metadata": {
        "created_at": "2024-03-14T12:00:00Z",
        "last_seen": "2024-03-14T12:00:00Z",
        "confidence": 0.98,
        "occurrences": 100
    }
}
```

### Types de Patterns
- HTTP_REQUEST
- SQL_QUERY
- FILE_ACCESS
- AUTH_ATTEMPT
- CUSTOM

## Gestion des Erreurs
- Validation des patterns
- Gestion des conflits
- Reprise après erreur

## Performance
- Indexation optimisée
- Cache des patterns fréquents
- Nettoyage automatique

## Intégration
- Interface avec AnomalyDetector
- Flux vers TrainingBuffer
- Synchronisation avec Dashboard 