# Validation Rules

## Vue d'Ensemble
Le composant Validation Rules gère les règles et le workflow de validation des anomalies détectées, permettant une validation automatique ou humaine.

## Fonctionnalités

### Règles de Validation
- Validation automatique
- Workflow de validation humaine
- Gestion des exceptions
- Mise à jour des règles

### Configuration
```yaml
validation_rules:
  automatic:
    enabled: true
    confidence_threshold: 0.95
    rules:
      - type: "IP_WHITELIST"
        action: "auto_validate"
      - type: "PATTERN_MATCH"
        action: "auto_validate"
      - type: "FREQUENCY_CHECK"
        action: "require_validation"
  
  human:
    enabled: true
    required_roles:
      - "security_admin"
      - "security_analyst"
    timeout: 3600  # secondes
    notification:
      enabled: true
      channels:
        - "email"
        - "slack"
```

## Utilisation

```python
from modsec_ai.src.core.validation_rules import ValidationRules

validator = ValidationRules(
    config_path="config/validation_rules.yaml"
)

# Vérifier une anomalie
validation_result = validator.validate_anomaly(
    anomaly_id="anom_123",
    features={
        "score": 0.95,
        "type": "SQL_INJECTION",
        "source_ip": "192.168.1.1"
    }
)

# Ajouter une règle
validator.add_rule(
    rule_type="IP_WHITELIST",
    pattern="192.168.1.*",
    action="auto_validate"
)
```

## Structure des Données

### Format de Règle
```json
{
    "id": "rule_123",
    "type": "IP_WHITELIST",
    "pattern": "192.168.1.*",
    "action": "auto_validate",
    "metadata": {
        "created_at": "2024-03-14T12:00:00Z",
        "created_by": "admin",
        "priority": 1,
        "enabled": true
    }
}
```

### Types de Règles
- IP_WHITELIST
- PATTERN_MATCH
- FREQUENCY_CHECK
- CUSTOM

## Gestion des Erreurs
- Validation des règles
- Gestion des conflits
- Reprise après erreur

## Performance
- Cache des règles
- Optimisation des patterns
- Mise à jour incrémentale

## Intégration
- Interface avec AnomaliesBuffer
- Flux vers KnowledgeBase
- Synchronisation avec Dashboard 