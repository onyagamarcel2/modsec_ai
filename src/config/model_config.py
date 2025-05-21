"""
Configuration des modèles et options de visualisation pour l'interface graphique.
"""

# Configuration des modèles disponibles
AVAILABLE_MODELS = {
    'isolation_forest': {
        'name': 'Isolation Forest',
        'description': 'Algorithme basé sur les arbres de décision, efficace pour les données de grande dimension',
        'parameters': {
            'contamination': {
                'type': 'float',
                'default': 0.1,
                'min': 0.01,
                'max': 0.5,
                'step': 0.01,
                'description': 'Proportion attendue d\'anomalies'
            },
            'n_estimators': {
                'type': 'int',
                'default': 100,
                'min': 10,
                'max': 1000,
                'step': 10,
                'description': 'Nombre d\'arbres'
            }
        }
    },
    'local_outlier_factor': {
        'name': 'Local Outlier Factor',
        'description': 'Algorithme basé sur la densité locale, efficace pour les anomalies contextuelles',
        'parameters': {
            'n_neighbors': {
                'type': 'int',
                'default': 20,
                'min': 5,
                'max': 100,
                'step': 1,
                'description': 'Nombre de voisins'
            },
            'contamination': {
                'type': 'float',
                'default': 0.1,
                'min': 0.01,
                'max': 0.5,
                'step': 0.01,
                'description': 'Proportion attendue d\'anomalies'
            }
        }
    },
    'elliptic_envelope': {
        'name': 'Elliptic Envelope',
        'description': 'Algorithme basé sur la distribution gaussienne, efficace pour les données approximativement gaussiennes',
        'parameters': {
            'contamination': {
                'type': 'float',
                'default': 0.1,
                'min': 0.01,
                'max': 0.5,
                'step': 0.01,
                'description': 'Proportion attendue d\'anomalies'
            }
        }
    },
    'one_class_svm': {
        'name': 'One-Class SVM',
        'description': 'Algorithme basé sur les machines à vecteurs de support, efficace pour les données non linéaires',
        'parameters': {
            'nu': {
                'type': 'float',
                'default': 0.1,
                'min': 0.01,
                'max': 0.5,
                'step': 0.01,
                'description': 'Paramètre de régularisation'
            },
            'kernel': {
                'type': 'choice',
                'default': 'rbf',
                'choices': ['linear', 'poly', 'rbf', 'sigmoid'],
                'description': 'Type de noyau'
            }
        }
    }
}

# Configuration des opérations de combinaison des scores
SCORE_OPERATIONS = {
    'mean': {
        'name': 'Moyenne',
        'description': 'Calcule la moyenne des scores de tous les modèles',
        'function': 'np.mean'
    },
    'max': {
        'name': 'Maximum',
        'description': 'Prend le score maximum parmi tous les modèles',
        'function': 'np.max'
    },
    'min': {
        'name': 'Minimum',
        'description': 'Prend le score minimum parmi tous les modèles',
        'function': 'np.min'
    },
    'weighted_mean': {
        'name': 'Moyenne pondérée',
        'description': 'Calcule une moyenne pondérée des scores',
        'function': 'np.average'
    }
}

# Configuration des visualisations disponibles
VISUALIZATIONS = {
    'training': {
        'name': 'Courbes d\'entraînement',
        'description': 'Affiche les métriques d\'entraînement au fil du temps',
        'plots': [
            {
                'name': 'Loss',
                'type': 'line',
                'x_label': 'Époque',
                'y_label': 'Loss'
            },
            {
                'name': 'Précision',
                'type': 'line',
                'x_label': 'Époque',
                'y_label': 'Précision'
            }
        ]
    },
    'classification': {
        'name': 'Résultats de classification',
        'description': 'Affiche les résultats de la classification',
        'plots': [
            {
                'name': 'Matrice de confusion',
                'type': 'heatmap',
                'x_label': 'Prédiction',
                'y_label': 'Vraie valeur'
            },
            {
                'name': 'Distribution des scores',
                'type': 'histogram',
                'x_label': 'Score d\'anomalie',
                'y_label': 'Fréquence'
            },
            {
                'name': 'ROC Curve',
                'type': 'line',
                'x_label': 'Taux de faux positifs',
                'y_label': 'Taux de vrais positifs'
            }
        ]
    },
    'model_comparison': {
        'name': 'Comparaison des modèles',
        'description': 'Compare les performances des différents modèles',
        'plots': [
            {
                'name': 'Métriques par modèle',
                'type': 'bar',
                'x_label': 'Modèle',
                'y_label': 'Score'
            },
            {
                'name': 'Matrice de corrélation des scores',
                'type': 'heatmap',
                'x_label': 'Modèle',
                'y_label': 'Modèle'
            }
        ]
    }
}

# Configuration des métriques d'évaluation
EVALUATION_METRICS = {
    'precision': {
        'name': 'Précision',
        'description': 'Proportion de prédictions positives correctes'
    },
    'recall': {
        'name': 'Rappel',
        'description': 'Proportion de vrais positifs correctement identifiés'
    },
    'f1_score': {
        'name': 'Score F1',
        'description': 'Moyenne harmonique de la précision et du rappel'
    },
    'auc_roc': {
        'name': 'AUC-ROC',
        'description': 'Aire sous la courbe ROC'
    },
    'confusion_matrix': {
        'name': 'Matrice de confusion',
        'description': 'Tableau des prédictions correctes et incorrectes'
    }
} 