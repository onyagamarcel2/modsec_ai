# Dashboard

## Vue d'Ensemble
Le Dashboard est l'interface utilisateur principale de ModSec AI, fournissant une visualisation en temps réel des anomalies et des outils de validation.

## Fonctionnalités

### Visualisation
- Statistiques en temps réel
- Graphiques d'anomalies
- Filtres et recherche
- Export de données

### Configuration
```yaml
dashboard:
  theme:
    primary_color: "#1f77b4"
    secondary_color: "#ff7f0e"
    dark_mode: false
  
  refresh:
    interval: 5  # secondes
    real_time: true
  
  features:
    anomaly_validation: true
    model_management: true
    alert_configuration: true
    data_export: true
  
  security:
    authentication: true
    authorization:
      roles:
        - "admin"
        - "analyst"
        - "viewer"
```

## Utilisation

```python
from modsec_ai.src.api.dashboard import Dashboard

dashboard = Dashboard(
    config_path="config/dashboard.yaml"
)

# Démarrer le dashboard
dashboard.run(
    host="0.0.0.0",
    port=8501,
    debug=False
)
```

## Composants

### Vue d'Ensemble
- Nombre total de requêtes
- Taux d'anomalies
- Performance du modèle
- Alertes actives

### Analyse des Anomalies
- Liste des anomalies
- Détails et contexte
- Actions recommandées
- Historique des décisions

### Configuration
- Paramètres du modèle
- Règles de validation
- Canaux d'alerte
- Préférences utilisateur

## Gestion des Données

### Format d'Export
```json
{
    "anomalies": [
        {
            "id": "anom_123",
            "timestamp": "2024-03-14T12:00:00Z",
            "type": "SQL_INJECTION",
            "score": 0.95,
            "status": "PENDING",
            "details": {...}
        }
    ],
    "statistics": {
        "total_requests": 1000,
        "anomaly_rate": 0.05,
        "false_positives": 0.01
    }
}
```

### Types d'Export
- CSV
- JSON
- PDF (rapports)
- API

## Gestion des Erreurs
- Gestion des timeouts
- Reprise de session
- Validation des données

## Performance
- Mise en cache
- Chargement asynchrone
- Optimisation des requêtes

## Intégration
- Interface avec AnomaliesBuffer
- Flux vers ValidationRules
- Synchronisation avec KnowledgeBase 