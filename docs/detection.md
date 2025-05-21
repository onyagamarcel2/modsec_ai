# Guide de Détection d'Anomalies

Ce guide explique comment utiliser le système de détection d'anomalies en temps réel pour les logs ModSecurity. Il couvre la configuration, l'utilisation et l'interprétation des résultats de détection.

## Configuration de la Détection

### 1. Paramètres de Base

```python
from src.detection.anomaly_detector import AnomalyDetector

detector = AnomalyDetector(
    model_dir='models/detector_20240101_120000',  # Répertoire contenant le modèle entraîné
    cache_ttl=3600,           # Durée de vie du cache en secondes (1 heure)
    window_size=1000,         # Taille de la fenêtre glissante pour l'analyse
    min_anomaly_ratio=0.05,   # Ratio minimum d'anomalies pour déclencher une alerte
    adaptive_threshold=True   # Utiliser un seuil adaptatif basé sur les données récentes
)
```

**Explications des paramètres** :
- `cache_ttl` : Durée pendant laquelle les résultats sont mis en cache pour optimiser les performances
- `window_size` : Nombre de requêtes analysées simultanément pour la détection
- `min_anomaly_ratio` : Seuil minimum pour considérer une séquence comme anormale
- `adaptive_threshold` : Ajuste automatiquement les seuils en fonction des patterns récents

### 2. Règles de Détection

```python
# Exemple de fichier de règles (rules.json)
{
    "rules": [
        {
            "name": "high_frequency_requests",  # Nom de la règle
            "condition": "request_count > 1000", # Condition de déclenchement
            "window": "5m",                     # Fenêtre temporelle
            "severity": "high"                  # Niveau de sévérité
        },
        {
            "name": "suspicious_patterns",      # Détection de patterns suspects
            "pattern": ".*(union|select|exec).*", # Expression régulière
            "severity": "medium"                # Niveau de sévérité
        }
    ]
}
```

**Types de règles** :
- **Règles de fréquence** : Détectent les pics d'activité
- **Règles de pattern** : Identifient les comportements suspects
- **Règles composites** : Combinent plusieurs conditions

## Utilisation du Script de Détection

### Options de Base

```bash
python scripts/detect_anomalies.py \
    --log-file logs/modsec.log \                # Fichier de logs à analyser
    --model-dir models/detector_20240101_120000 \ # Répertoire du modèle
    --output-dir anomalies                      # Répertoire de sortie
```

### Options Avancées

```bash
python scripts/detect_anomalies.py \
    --log-file logs/modsec.log \
    --model-dir models/detector_20240101_120000 \
    --output-dir anomalies \
    --cache-ttl 3600 \              # Durée de vie du cache (1 heure)
    --window-size 1000 \            # Taille de la fenêtre d'analyse
    --min-anomaly-ratio 0.05 \      # Ratio minimum d'anomalies
    --adaptive-threshold \          # Seuil adaptatif
    --rules-file config/rules.json \ # Fichier de règles personnalisées
    --gui-data-dir gui_data \       # Données pour l'interface graphique
    --max-data-age 30               # Âge maximum des données (jours)
```

## Interprétation des Alertes

### 1. Format des Alertes

```json
{
    "timestamp": "2024-01-01T12:00:00Z",  # Horodatage de l'alerte
    "anomaly_score": 0.85,                # Score d'anomalie global
    "detection_method": "ensemble",        # Méthode de détection utilisée
    "details": {                          # Scores détaillés par modèle
        "isolation_forest_score": 0.82,
        "local_outlier_factor_score": 0.88,
        "elliptic_envelope_score": 0.79,
        "one_class_svm_score": 0.91
    },
    "matched_rules": [                    # Règles déclenchées
        {
            "name": "high_frequency_requests",
            "severity": "high"
        }
    ],
    "context": {                          # Contexte de l'alerte
        "request_count": 1200,
        "window_duration": "5m"
    }
}
```

**Composants de l'alerte** :
- **Horodatage** : Moment de la détection
- **Score d'anomalie** : Probabilité d'anomalie (0-1)
- **Méthode** : Algorithme ayant détecté l'anomalie
- **Détails** : Scores individuels des modèles
- **Règles** : Règles personnalisées déclenchées
- **Contexte** : Informations supplémentaires

### 2. Niveaux de Sévérité

- **Critique** : Score > 0.9
  * Menace immédiate
  * Action requise immédiatement
  * Notification prioritaire

- **Élevé** : 0.7 < Score ≤ 0.9
  * Menace significative
  * Action requise rapidement
  * Notification urgente

- **Moyen** : 0.5 < Score ≤ 0.7
  * Menace potentielle
  * Action requise
  * Notification normale

- **Faible** : Score ≤ 0.5
  * Menace mineure
  * Surveillance requise
  * Notification différée

### 3. Visualisations

Les graphiques suivants sont générés automatiquement pour l'analyse :

- **Scores d'anomalie** : Évolution des scores dans le temps
  * Tendance des anomalies
  * Périodes critiques
  * Patterns récurrents

- **Distribution des alertes** : Répartition par niveau de sévérité
  * Proportions des alertes
  * Évolution des niveaux
  * Points d'attention

- **Corrélation des modèles** : Comparaison des scores des différents modèles
  * Accord entre modèles
  * Points de divergence
  * Robustesse de la détection

- **Tendances** : Analyse des patterns d'anomalies
  * Cycles d'activité
  * Comportements suspects
  * Évolution temporelle

## Gestion des Faux Positifs

### 1. Ajustement des Seuils

```python
# Ajustement du seuil adaptatif
detector.set_adaptive_threshold(
    sensitivity=0.8,    # Sensibilité (0-1)
    specificity=0.9     # Spécificité (0-1)
)
```

**Paramètres de seuil** :
- **Sensibilité** : Capacité à détecter les vraies anomalies
- **Spécificité** : Capacité à éviter les faux positifs
- **Compromis** : Ajuster selon les besoins de sécurité

### 2. Filtrage des Alertes

```python
# Filtrage basé sur le contexte
detector.add_filter(
    name="ignore_known_patterns",
    condition="pattern in known_patterns"
)

# Filtrage basé sur la fréquence
detector.add_filter(
    name="frequency_threshold",
    condition="request_count < 1000"
)
```

**Types de filtres** :
- **Filtres de contexte** : Ignorent les patterns connus
- **Filtres de fréquence** : Limitent les alertes répétitives
- **Filtres composites** : Combinent plusieurs conditions

## Bonnes Pratiques

1. **Configuration**
   - Ajuster les seuils selon votre environnement
     * Adapter aux patterns normaux
     * Considérer la charge de travail
     * Équilibrer sensibilité/spécificité
   - Définir des règles spécifiques à votre cas d'usage
     * Identifier les patterns critiques
     * Prioriser les menaces
     * Adapter aux besoins métier
   - Configurer le cache selon vos besoins
     * Optimiser les performances
     * Gérer la mémoire
     * Maintenir la fraîcheur des données

2. **Surveillance**
   - Surveiller le taux de faux positifs
     * Ajuster les seuils
     * Affiner les règles
     * Mettre à jour les filtres
   - Ajuster les paramètres si nécessaire
     * Adapter aux changements
     * Optimiser les performances
     * Améliorer la précision
   - Maintenir un historique des alertes
     * Analyser les tendances
     * Identifier les patterns
     * Améliorer la détection

3. **Maintenance**
   - Mettre à jour régulièrement les modèles
     * Adapter aux nouveaux patterns
     * Améliorer la précision
     * Maintenir la pertinence
   - Réviser les règles de détection
     * Ajouter de nouvelles règles
     * Ajuster les existantes
     * Supprimer les obsolètes
   - Nettoyer les données obsolètes
     * Gérer l'espace disque
     * Maintenir les performances
     * Conserver l'historique pertinent

4. **Sécurité**
   - Protéger les fichiers de configuration
     * Limiter les accès
     * Chiffrer les données sensibles
     * Sauvegarder régulièrement
   - Limiter l'accès aux logs
     * Contrôler les permissions
     * Journaliser les accès
     * Sécuriser les transferts
   - Sauvegarder régulièrement les données
     * Préserver l'historique
     * Faciliter la restauration
     * Maintenir la traçabilité

## Intégration avec d'Autres Systèmes

### 1. Export des Alertes

```python
# Export vers un système de monitoring
detector.export_alerts(
    format='json',
    destination='monitoring_system',
    batch_size=100
)

# Export vers un SIEM
detector.export_to_siem(
    siem_type='splunk',
    endpoint='https://splunk.example.com',
    token='your_token'
)
```

**Options d'export** :
- **Format** : JSON, CSV, XML
- **Destination** : SIEM, Monitoring, Base de données
- **Fréquence** : Temps réel, Par lots, Planifié

### 2. Notifications

```python
# Configuration des notifications
detector.configure_notifications(
    email='admin@example.com',
    slack_webhook='https://hooks.slack.com/...',
    severity_threshold='high'
)
```

**Canaux de notification** :
- **Email** : Alertes détaillées
- **Slack** : Notifications en temps réel
- **Webhook** : Intégration personnalisée

## Dépannage

### 1. Problèmes Courants

- **Faux positifs élevés**
  - Ajuster les seuils
    * Augmenter la spécificité
    * Affiner les règles
    * Mettre à jour les filtres
  - Ajouter des règles de filtrage
    * Ignorer les patterns connus
    * Limiter les alertes répétitives
    * Combiner plusieurs conditions
  - Mettre à jour le modèle
    * Réentraîner avec de nouvelles données
    * Ajuster les paramètres
    * Améliorer la précision

- **Performance**
  - Optimiser la taille du cache
    * Ajuster la durée de vie
    * Gérer la mémoire
    * Équilibrer vitesse/précision
  - Ajuster la taille de la fenêtre
    * Adapter au volume de données
    * Optimiser le traitement
    * Maintenir la réactivité
  - Nettoyer les données anciennes
    * Archiver l'historique
    * Libérer l'espace
    * Maintenir les performances

### 2. Logs de Dépannage

```bash
# Activer les logs de débogage
python scripts/detect_anomalies.py \
    --log-file logs/modsec.log \
    --model-dir models/detector_20240101_120000 \
    --output-dir anomalies \
    --debug
```

**Niveaux de logs** :
- **DEBUG** : Informations détaillées
- **INFO** : Événements normaux
- **WARNING** : Problèmes mineurs
- **ERROR** : Problèmes critiques

### 3. Métriques de Performance

- **Latence de détection**
  * Temps de traitement
  * Délai d'alerte
  * Réactivité du système

- **Utilisation de la mémoire**
  * Occupation RAM
  * Taille du cache
  * Gestion des ressources

- **Taux de traitement**
  * Requêtes par seconde
  * Capacité de traitement
  * Goulots d'étranglement

- **Précision des alertes**
  * Taux de détection
  * Faux positifs/négatifs
  * Qualité des alertes 