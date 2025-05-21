# Vectorization

## Vue d'Ensemble
Le composant Vectorization transforme les logs ModSecurity nettoyés en vecteurs numériques utilisables par les algorithmes de détection d'anomalies.

## Fonctionnalités

### Méthodes de Vectorisation
- TF-IDF (Term Frequency-Inverse Document Frequency)
- Word2Vec embeddings
- Feature scaling
- Normalisation des vecteurs

### Configuration
```yaml
vectorization:
  method: "tfidf"  # tfidf, word2vec
  tfidf:
    max_features: 1000
    min_df: 2
    max_df: 0.95
  word2vec:
    vector_size: 100
    window: 5
    min_count: 2
  scaling:
    method: "standard"  # standard, minmax
    with_mean: true
    with_std: true
```

## Utilisation

```python
from modsec_ai.src.core.vectorization import Vectorizer

vectorizer = Vectorizer(
    method="tfidf",
    config_path="config/vectorization.yaml"
)

vectors = vectorizer.transform(log_entries)
```

## Caractéristiques

### TF-IDF
- Extraction des tokens
- Calcul des fréquences
- Normalisation des scores

### Word2Vec
- Entraînement du modèle
- Génération des embeddings
- Mise à jour incrémentale

### Feature Scaling
- Standardisation
- Normalisation Min-Max
- Gestion des outliers

## Gestion des Erreurs
- Validation des entrées
- Gestion des dimensions
- Reprise après erreur

## Performance
- Vectorisation par lots
- Cache des modèles
- Optimisation mémoire

## Intégration
- Interface avec FeatureExtractor
- Flux vers AnomalyDetector
- Mise à jour du vocabulaire 