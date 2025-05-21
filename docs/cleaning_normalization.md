# Cleaning & Normalization

## Vue d'Ensemble
Le composant Cleaning & Normalization est responsable du nettoyage et de la standardisation des données brutes des logs ModSecurity pour assurer une analyse cohérente.

## Fonctionnalités

### Nettoyage des Données
- Suppression des caractères spéciaux
- Normalisation des encodages
- Gestion des valeurs manquantes
- Standardisation des formats

### Normalisation
- Uniformisation des timestamps
- Normalisation des URLs
- Standardisation des en-têtes HTTP
- Formatage des paramètres

### Configuration
```yaml
cleaning:
  remove_special_chars: true
  normalize_encoding: true
  handle_missing_values: "skip"  # skip, fill, drop
  timestamp_format: "ISO8601"
  url_normalization: true
  header_case: "lower"
```

## Utilisation

```python
from modsec_ai.src.core.cleaning import CleaningNormalization

cleaner = CleaningNormalization(
    config_path="config/cleaning.yaml"
)

cleaned_data = cleaner.process(log_entry)
```

## Règles de Nettoyage

### En-têtes HTTP
- Conversion en minuscules
- Suppression des espaces superflus
- Normalisation des valeurs

### Paramètres
- Décodage URL
- Échappement des caractères spéciaux
- Standardisation des formats

### Timestamps
- Conversion en format ISO8601
- Gestion des fuseaux horaires
- Validation des dates

## Gestion des Erreurs
- Logging des erreurs de nettoyage
- Stratégies de fallback
- Validation des résultats

## Performance
- Traitement par lots
- Cache des règles
- Optimisation des regex

## Intégration
- Interface avec le Parser
- Flux vers le Vectorizer
- Validation des données 