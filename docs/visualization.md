# Guide de Visualisation

Ce guide explique comment utiliser et personnaliser les visualisations du système de détection d'anomalies. Il couvre les différents types de graphiques, leur configuration et leur utilisation pour l'analyse des résultats.

## Types de Visualisations

### 1. Courbes d'Entraînement

```python
from src.visualization.result_visualizer import ResultVisualizer

visualizer = ResultVisualizer(output_dir='plots')

# Visualisation des métriques d'entraînement
visualizer.plot_training_curves(
    history={
        'precision': [0.8, 0.85, 0.9],  # Évolution de la précision
        'recall': [0.75, 0.82, 0.88],   # Évolution du rappel
        'f1': [0.77, 0.83, 0.89]        # Évolution du score F1
    },
    model_name='ensemble',              # Nom du modèle
    timestamp='20240101_120000'         # Horodatage
)
```

**Objectif** : Suivre l'évolution des performances du modèle pendant l'entraînement
- **Précision** : Fiabilité des prédictions positives
- **Rappel** : Capacité à détecter les anomalies
- **Score F1** : Équilibre entre précision et rappel

### 2. Matrice de Confusion

```python
# Visualisation de la matrice de confusion
visualizer.plot_confusion_matrix(
    confusion_matrix=[[100, 10],  # Vrais négatifs, Faux positifs
                      [5, 85]],   # Faux négatifs, Vrais positifs
    model_name='ensemble',
    timestamp='20240101_120000'
)
```

**Objectif** : Visualiser la distribution des prédictions
- **Vrais négatifs** : Anomalies correctement ignorées
- **Faux positifs** : Fausses alertes
- **Faux négatifs** : Anomalies manquées
- **Vrais positifs** : Anomalies correctement détectées

### 3. Distribution des Scores

```python
# Visualisation de la distribution des scores
visualizer.plot_score_distribution(
    scores=[0.1, 0.3, 0.5, 0.7, 0.9],  # Scores d'anomalie
    model_name='ensemble',
    timestamp='20240101_120000'
)
```

**Objectif** : Analyser la distribution des scores d'anomalie
- **Scores faibles** : Comportements normaux
- **Scores moyens** : Zone d'incertitude
- **Scores élevés** : Anomalies probables

### 4. Courbe ROC

```python
# Visualisation de la courbe ROC
visualizer.plot_roc_curve(
    y_true=[0, 1, 0, 1],           # Valeurs réelles
    y_score=[0.1, 0.8, 0.3, 0.9],  # Scores prédits
    model_name='ensemble',
    timestamp='20240101_120000'
)
```

**Objectif** : Évaluer la capacité de discrimination du modèle
- **Axe X** : Taux de faux positifs
- **Axe Y** : Taux de vrais positifs
- **AUC** : Aire sous la courbe (performance globale)

## Comparaison des Modèles

### 1. Métriques de Performance

```python
# Comparaison des métriques entre modèles
visualizer.plot_model_comparison(
    metrics={
        'isolation_forest': {
            'precision': 0.85,  # Précision du modèle
            'recall': 0.82,     # Rappel du modèle
            'f1': 0.83          # Score F1 du modèle
        },
        'local_outlier_factor': {
            'precision': 0.88,
            'recall': 0.85,
            'f1': 0.86
        }
    },
    timestamp='20240101_120000'
)
```

**Objectif** : Comparer les performances des différents modèles
- **Précision** : Fiabilité des prédictions
- **Rappel** : Capacité de détection
- **Score F1** : Performance globale

### 2. Corrélation des Scores

```python
# Visualisation de la corrélation entre modèles
visualizer.plot_score_correlation(
    scores={
        'isolation_forest': [0.1, 0.3, 0.5],      # Scores du premier modèle
        'local_outlier_factor': [0.2, 0.4, 0.6]   # Scores du second modèle
    },
    timestamp='20240101_120000'
)
```

**Objectif** : Analyser l'accord entre les modèles
- **Corrélation positive** : Modèles d'accord
- **Corrélation négative** : Modèles en désaccord
- **Pas de corrélation** : Modèles indépendants

## Scores Combinés

### 1. Visualisation des Scores Individuels

```python
# Visualisation des scores de chaque modèle
visualizer.plot_individual_scores(
    scores={
        'isolation_forest': [0.1, 0.3, 0.5],        # Scores Isolation Forest
        'local_outlier_factor': [0.2, 0.4, 0.6],    # Scores LOF
        'elliptic_envelope': [0.15, 0.35, 0.55],    # Scores Elliptic Envelope
        'one_class_svm': [0.12, 0.32, 0.52]         # Scores One-Class SVM
    },
    timestamp='20240101_120000'
)
```

**Objectif** : Comparer les scores de chaque modèle
- **Scores par modèle** : Performance individuelle
- **Distribution** : Comportement de chaque modèle
- **Tendances** : Patterns de détection

### 2. Visualisation des Scores Combinés

```python
# Visualisation des scores combinés
visualizer.plot_combined_scores(
    individual_scores={
        'isolation_forest': [0.1, 0.3, 0.5],
        'local_outlier_factor': [0.2, 0.4, 0.6]
    },
    combined_scores=[0.15, 0.35, 0.55],  # Scores après combinaison
    operation='mean',                    # Opération de combinaison
    timestamp='20240101_120000'
)
```

**Objectif** : Analyser l'effet de la combinaison des scores
- **Scores individuels** : Contribution de chaque modèle
- **Score combiné** : Résultat final
- **Opération** : Méthode de combinaison

## Personnalisation des Graphiques

### 1. Style et Couleurs

```python
# Configuration du style
visualizer.set_style(
    style='seaborn',      # Style de graphique
    palette='viridis',    # Palette de couleurs
    context='paper'       # Contexte d'affichage
)

# Personnalisation des couleurs
visualizer.set_colors(
    normal='#2ecc71',     # Couleur pour les points normaux
    anomaly='#e74c3c',    # Couleur pour les anomalies
    threshold='#f1c40f'   # Couleur pour les seuils
)
```

**Options de style** :
- **Style** : seaborn, ggplot, bmh, etc.
- **Palette** : viridis, plasma, inferno, etc.
- **Contexte** : paper, notebook, talk, poster

### 2. Format et Taille

```python
# Configuration du format
visualizer.set_format(
    dpi=300,              # Résolution en points par pouce
    format='png',         # Format de fichier
    bbox_inches='tight'   # Gestion des marges
)

# Configuration de la taille
visualizer.set_size(
    width=12,             # Largeur en pouces
    height=8,             # Hauteur en pouces
    aspect_ratio='auto'   # Ratio d'aspect
)
```

**Options de format** :
- **DPI** : Résolution de l'image
- **Format** : png, pdf, svg, etc.
- **Taille** : Dimensions du graphique

## Export des Visualisations

### 1. Formats Supportés

- **PNG** (par défaut)
  * Format raster
  * Bonne qualité
  * Taille de fichier modérée

- **PDF**
  * Format vectoriel
  * Qualité maximale
  * Idéal pour l'impression

- **SVG**
  * Format vectoriel
  * Modifiable
  * Idéal pour le web

- **HTML** (interactif)
  * Visualisations dynamiques
  * Zoom et pan
  * Tooltips d'information

### 2. Export en Lot

```python
# Export de toutes les visualisations
visualizer.export_all(
    output_dir='reports',        # Répertoire de sortie
    format='pdf',                # Format d'export
    include_timestamp=True       # Inclure l'horodatage
)
```

**Options d'export** :
- **Répertoire** : Organisation des fichiers
- **Format** : Type de fichier
- **Horodatage** : Gestion des versions

## Intégration avec le Dashboard

### 1. Mise à Jour Automatique

```python
# Configuration de la mise à jour automatique
visualizer.configure_auto_update(
    interval=300,  # Intervalle de mise à jour (secondes)
    gui_data_dir='gui_data'  # Répertoire des données
)
```

**Fonctionnalités** :
- **Mise à jour périodique**
- **Rafraîchissement des données**
- **Gestion du cache**

### 2. Données en Temps Réel

```python
# Mise à jour des visualisations en temps réel
visualizer.update_realtime_plots(
    new_data={
        'scores': [0.1, 0.3, 0.5],      # Nouveaux scores
        'predictions': [0, 1, 0]         # Nouvelles prédictions
    },
    window_size=1000                     # Taille de la fenêtre
)
```

**Fonctionnalités** :
- **Mise à jour dynamique**
- **Fenêtre glissante**
- **Gestion de la mémoire**

## Bonnes Pratiques

1. **Organisation**
   - Utiliser des noms de fichiers cohérents
     * Format : `type_date_timestamp`
     * Exemple : `confusion_matrix_20240101_120000`
   - Structurer les répertoires logiquement
     * Par type de visualisation
     * Par date
     * Par modèle
   - Inclure des timestamps dans les noms
     * Faciliter le suivi
     * Éviter les conflits
     * Gérer les versions

2. **Performance**
   - Optimiser la taille des graphiques
     * Adapter la résolution
     * Compresser si nécessaire
     * Équilibrer qualité/taille
   - Utiliser le cache pour les données fréquentes
     * Réduire les calculs
     * Accélérer l'affichage
     * Gérer la mémoire
   - Limiter le nombre de points affichés
     * Échantillonner si nécessaire
     * Regrouper les données
     * Maintenir la lisibilité

3. **Lisibilité**
   - Choisir des couleurs contrastées
     * Différencier les catégories
     * Maintenir l'accessibilité
     * Respecter les standards
   - Ajouter des légendes claires
     * Expliquer les symboles
     * Détailler les unités
     * Contextualiser les données
   - Inclure des titres descriptifs
     * Résumer le contenu
     * Indiquer la période
     * Préciser le contexte

4. **Maintenance**
   - Nettoyer les anciennes visualisations
     * Archiver les données
     * Libérer l'espace
     * Maintenir l'organisation
   - Mettre à jour les styles régulièrement
     * Adapter aux standards
     * Améliorer la cohérence
     * Moderniser l'apparence
   - Sauvegarder les configurations
     * Réutiliser les paramètres
     * Maintenir la cohérence
     * Faciliter la reproduction 