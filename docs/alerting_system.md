# Alerting System

## Vue d'Ensemble
Le système d'alerte gère la notification des anomalies détectées via différents canaux (email, Slack, webhook) et assure le suivi des alertes.

## Fonctionnalités

### Canaux de Notification
- Email (SMTP)
- Slack
- Webhook personnalisé
- Logs système

### Configuration
```yaml
alerts:
  channels:
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "your-email@gmail.com"
      password: "your-app-password"
      from_address: "alerts@modsec-ai.com"
      to_addresses:
        - "admin@example.com"
        - "security@example.com"
    
    slack:
      enabled: true
      webhook_url: "https://hooks.slack.com/services/xxx/yyy/zzz"
      channel: "#security-alerts"
      username: "ModSec AI"
      icon_emoji: ":warning:"
    
    webhook:
      enabled: false
      url: "https://your-server.com/webhook"
      secret: "your-webhook-secret"
      timeout: 5
```

## Utilisation

```python
from modsec_ai.src.core.alerting import AlertingSystem

alerter = AlertingSystem(
    config_path="config/alerts.yaml"
)

alerter.send_alert(
    anomaly_id="anom_123",
    severity="HIGH",
    details={
        "score": 0.95,
        "type": "SQL_INJECTION",
        "source_ip": "192.168.1.1"
    }
)
```

## Gestion des Alertes

### Priorités
- CRITICAL
- HIGH
- MEDIUM
- LOW

### Format des Alertes
```json
{
    "id": "alert_123",
    "timestamp": "2024-03-14T12:00:00Z",
    "severity": "HIGH",
    "type": "SQL_INJECTION",
    "source_ip": "192.168.1.1",
    "details": {
        "score": 0.95,
        "confidence": 0.89,
        "recommendations": ["Block IP", "Update Rules"]
    }
}
```

### Règles d'Alerte
- Seuils de déclenchement
- Agrégation d'alertes
- Période de refroidissement

## Gestion des Erreurs
- Retry automatique
- Fallback des canaux
- Logging des échecs

## Performance
- File d'attente d'alertes
- Traitement asynchrone
- Rate limiting

## Intégration
- Interface avec AnomalyDetector
- Flux vers Dashboard
- Historique des alertes 