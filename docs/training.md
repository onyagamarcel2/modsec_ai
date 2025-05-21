# Guide d'Entraînement

Ce guide détaille le processus d'entraînement des modèles de détection d'anomalies pour ModSecurity. Il explique comment préparer, entraîner et évaluer les différents modèles de détection d'anomalies.

## Modèles Disponibles

Le système propose plusieurs algorithmes de détection d'anomalies, chacun ayant ses propres caractéristiques et cas d'utilisation :

### 1. Isolation Forest
```python
from src.models.anomaly_detectors import IsolationForestDetector

detector = IsolationForestDetector(
    contamination=0.1,  # Proportion attendue d'anomalies dans les données
    n_estimators=100    # Nombre d'arbres dans la forêt
)
```
**Caractéristiques** :
- Algorithme basé sur l'isolation des points anormaux
- Particulièrement efficace pour les données à haute dimension
- Temps d'entraînement rapide
- Idéal pour les grands ensembles de données

### 2. Local Outlier Factor
```python
from src.models.anomaly_detectors import LocalOutlierFactorDetector

detector = LocalOutlierFactorDetector(
    n_neighbors=20,     # Nombre de voisins pour calculer la densité locale
    contamination=0.1   # Proportion attendue d'anomalies
)
```
**Caractéristiques** :
- Basé sur la densité locale des points
- Détecte les anomalies en comparant la densité locale d'un point avec celle de ses voisins
- Particulièrement efficace pour les clusters de données
- Sensible au choix du nombre de voisins

### 3. Elliptic Envelope
```python
from src.models.anomaly_detectors import EllipticEnvelopeDetector

detector = EllipticEnvelopeDetector(
    contamination=0.1   # Proportion attendue d'anomalies
)
```
**Caractéristiques** :
- Modèle basé sur l'hypothèse de distribution gaussienne
- Crée une enveloppe elliptique autour des données normales
- Particulièrement efficace pour les données distribuées normalement
- Sensible aux données non gaussiennes

### 4. One-Class SVM
```python
from src.models.anomaly_detectors import OneClassSVMDetector

detector = OneClassSVMDetector(
    nu=0.1,            # Paramètre de régularisation (proportion d'anomalies attendues)
    kernel='rbf'       # Type de noyau pour la transformation non-linéaire
)
```
**Caractéristiques** :
- Algorithme basé sur les machines à vecteurs de support
- Crée une frontière de décision autour des données normales
- Particulièrement efficace pour les données non-linéaires
- Peut être coûteux en calcul pour les grands ensembles de données

### 5. Ensemble de Modèles
```python
from src.models.anomaly_detectors import EnsembleAnomalyDetector

detector = EnsembleAnomalyDetector()  # Combine tous les modèles pour une détection plus robuste
```
**Caractéristiques** :
- Combine les prédictions de tous les modèles
- Améliore la robustesse de la détection
- Réduit les faux positifs
- Permet une détection plus précise

## Processus d'Entraînement

### 1. Préparation des Données

```python
from src.data.log_loader import ModSecLogLoader
from src.data.preprocessor import ModSecPreprocessor

# Chargement des logs avec filtrage par date
loader = ModSecLogLoader('logs/modsec.log')
df = loader.load_logs(
    start_date='2024-01-01',  # Date de début de la période d'entraînement
    end_date='2024-01-31'     # Date de fin de la période d'entraînement
)

# Prétraitement des données (nettoyage, normalisation, etc.)
preprocessor = ModSecPreprocessor()
processed_df = preprocessor.preprocess(df)
```

### 2. Vectorisation

```python
from src.models.vectorizer import LogVectorizer

# Création du vectoriseur pour transformer les logs en vecteurs
vectorizer = LogVectorizer(
    vectorizer_type='word2vec',  # Type de vectorisation (word2vec, tf-idf, etc.)
    vector_size=100,             # Dimension des vecteurs
    window_size=5,               # Taille de la fenêtre de contexte
    min_count=1                  # Fréquence minimale des tokens
)

# Entraînement du vectoriseur et transformation des données
vectorizer.fit(processed_df['tokens'])
vectors = vectorizer.transform(processed_df['tokens'])
```

### 3. Entraînement du Modèle

```python
# Entraînement simple du modèle
detector.fit(vectors)

# Entraînement avec validation croisée pour évaluer la robustesse
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(
    detector.model, 
    vectors, 
    cv=5,              # Nombre de plis pour la validation croisée
    scoring='f1'       # Métrique d'évaluation
)
```

### 4. Évaluation

```python
# Génération des prédictions et des scores
predictions = detector.predict(test_vectors)  # Prédictions binaires (0: normal, 1: anomalie)
scores = detector.predict_proba(test_vectors) # Scores de probabilité

# Calcul des métriques d'évaluation
from sklearn.metrics import precision_recall_fscore_support

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true,           # Valeurs réelles
    predictions,      # Prédictions du modèle
    average='binary'  # Type de moyenne pour les métriques
)
```

## Utilisation du Script d'Entraînement

### Options de Base

```bash
python scripts/train_model.py \
    --log-file logs/modsec.log \      # Fichier de logs à analyser
    --output-dir models \             # Répertoire de sortie pour les modèles
    --detector-type ensemble \        # Type de détecteur à utiliser
    --vectorizer-type word2vec        # Type de vectorisation
```

### Options Avancées

```bash
python scripts/train_model.py \
    --log-file logs/modsec.log \
    --output-dir models \
    --detector-type ensemble \
    --vectorizer-type word2vec \
    --vector-size 200 \              # Taille des vecteurs
    --window-size 10 \               # Taille de la fenêtre de contexte
    --min-count 2 \                  # Fréquence minimale des tokens
    --contamination 0.05 \           # Proportion attendue d'anomalies
    --n-estimators 200 \             # Nombre d'arbres (Isolation Forest)
    --n-neighbors 30 \               # Nombre de voisins (LOF)
    --nu 0.05 \                      # Paramètre de régularisation (SVM)
    --kernel rbf \                   # Type de noyau (SVM)
    --cross-validate \               # Activer la validation croisée
    --n-folds 5 \                    # Nombre de plis
    --test-split 0.2                 # Proportion des données de test
```

## Interprétation des Résultats

### 1. Métriques d'Évaluation

- **Précision** : Proportion de prédictions positives correctes
  - Indique la fiabilité des alertes générées
  - Valeur élevée = peu de faux positifs

- **Rappel** : Proportion de vrais positifs correctement identifiés
  - Indique la capacité à détecter toutes les anomalies
  - Valeur élevée = peu de faux négatifs

- **Score F1** : Moyenne harmonique de la précision et du rappel
  - Équilibre entre précision et rappel
  - Métrique globale de performance

- **AUC-ROC** : Aire sous la courbe ROC
  - Mesure la capacité à distinguer les classes
  - Valeur proche de 1 = excellente discrimination

### 2. Visualisations

Les graphiques suivants sont générés automatiquement pour faciliter l'analyse :

- **Courbes d'entraînement** : Évolution des métriques pendant l'entraînement
  - Permet de détecter le surapprentissage
  - Aide à choisir le nombre d'itérations optimal

- **Matrice de confusion** : Distribution des prédictions correctes/incorrectes
  - Visualise les vrais/faux positifs/négatifs
  - Aide à comprendre les erreurs du modèle

- **Distribution des scores** : Histogramme des scores d'anomalie
  - Montre la séparation entre normal et anormal
  - Aide à choisir le seuil de décision

- **Courbe ROC** : Taux de vrais/faux positifs
  - Évalue la performance à différents seuils
  - Aide à choisir le compromis optimal

- **Comparaison des modèles** : Métriques par modèle
  - Permet de comparer les performances
  - Aide à choisir le meilleur modèle

### 3. Fichiers de Sortie

```
models/
├── vectorizer_20240101_120000/    # Modèle de vectorisation
├── detector_20240101_120000/      # Modèle de détection
├── metadata_20240101_120000.json  # Métadonnées (paramètres, performances)
└── plots/                         # Graphiques
    ├── training/                  # Courbes d'entraînement
    ├── classification/           # Résultats de classification
    └── comparison/              # Comparaison des modèles
```

## Bonnes Pratiques

1. **Préparation des Données**
   - Utiliser une période suffisante pour l'entraînement
     * Minimum recommandé : 1 mois de données
     * Idéal : 3-6 mois pour capturer les variations saisonnières
   - Équilibrer les données normales/anormales
     * Éviter le déséquilibre extrême
     * Utiliser des techniques de rééchantillonnage si nécessaire
   - Nettoyer les logs avant l'entraînement
     * Supprimer les doublons
     * Corriger les erreurs de format
     * Normaliser les valeurs

2. **Sélection du Modèle**
   - Commencer avec l'ensemble de modèles
     * Meilleure robustesse
     * Moins sensible aux particularités des données
   - Ajuster les paramètres selon les résultats
     * Utiliser la validation croisée
     * Tester différentes combinaisons
   - Utiliser la validation croisée
     * Évaluer la stabilité du modèle
     * Détecter le surapprentissage

3. **Évaluation**
   - Tester sur des données récentes
     * Évaluer la capacité de généralisation
     * Détecter la dérive des performances
   - Vérifier les faux positifs/négatifs
     * Analyser les cas d'erreur
     * Ajuster les seuils si nécessaire
   - Analyser les cas d'erreur
     * Comprendre les patterns problématiques
     * Améliorer le prétraitement

4. **Maintenance**
   - Réentraîner régulièrement
     * Mettre à jour avec les nouvelles données
     * Adapter aux changements de patterns
   - Surveiller la dérive des performances
     * Détecter la dégradation
     * Déclencher le réentraînement si nécessaire
   - Mettre à jour les paramètres
     * Adapter aux changements de l'environnement
     * Optimiser les performances 