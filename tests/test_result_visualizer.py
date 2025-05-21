"""
Tests pour le visualiseur de résultats.
"""

import os
import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from src.visualization.result_visualizer import ResultVisualizer

@pytest.fixture
def temp_output_dir(tmp_path):
    """Crée un répertoire temporaire pour les sorties."""
    output_dir = tmp_path / "visualization_output"
    os.makedirs(output_dir, exist_ok=True)
    return str(output_dir)

@pytest.fixture
def visualizer(temp_output_dir):
    """Crée une instance de ResultVisualizer pour les tests."""
    return ResultVisualizer(output_dir=temp_output_dir)

@pytest.fixture
def timestamp():
    """Retourne un horodatage pour les tests."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def test_initialization(visualizer, temp_output_dir):
    """Test l'initialisation du visualiseur."""
    assert visualizer.output_dir == temp_output_dir

def test_plot_training_curves(visualizer, timestamp):
    """Test la création des courbes d'entraînement."""
    history = {
        'loss': [0.5, 0.4, 0.3, 0.2],
        'accuracy': [0.7, 0.8, 0.85, 0.9]
    }
    model_name = "test_model"
    
    visualizer.plot_training_curves(history, model_name, timestamp)
    
    # Vérifier que les fichiers ont été créés
    plots_dir = os.path.join(visualizer.output_dir, "plots", "training")
    assert os.path.exists(os.path.join(plots_dir, f"{model_name}_loss_{timestamp}.png"))
    assert os.path.exists(os.path.join(plots_dir, f"{model_name}_accuracy_{timestamp}.png"))

def test_plot_confusion_matrix(visualizer, timestamp):
    """Test la création de la matrice de confusion."""
    cm = np.array([[10, 2], [3, 15]])
    model_name = "test_model"
    
    visualizer.plot_confusion_matrix(cm, model_name, timestamp)
    
    # Vérifier que le fichier a été créé
    plots_dir = os.path.join(visualizer.output_dir, "plots", "classification")
    assert os.path.exists(os.path.join(plots_dir, f"{model_name}_confusion_matrix_{timestamp}.png"))

def test_plot_score_distribution(visualizer, timestamp):
    """Test la création de la distribution des scores."""
    scores = np.random.normal(0.5, 0.1, 1000)
    model_name = "test_model"
    
    visualizer.plot_score_distribution(scores, model_name, timestamp)
    
    # Vérifier que le fichier a été créé
    plots_dir = os.path.join(visualizer.output_dir, "plots", "classification")
    assert os.path.exists(os.path.join(plots_dir, f"{model_name}_score_distribution_{timestamp}.png"))

def test_plot_roc_curve(visualizer, timestamp):
    """Test la création de la courbe ROC."""
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    scores = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.7, 0.4, 0.6])
    model_name = "test_model"
    
    visualizer.plot_roc_curve(y_true, scores, model_name, timestamp)
    
    # Vérifier que le fichier a été créé
    plots_dir = os.path.join(visualizer.output_dir, "plots", "classification")
    assert os.path.exists(os.path.join(plots_dir, f"{model_name}_roc_curve_{timestamp}.png"))

def test_plot_model_comparison(visualizer, timestamp):
    """Test la création de la comparaison des modèles."""
    metrics = {
        'model1': {'accuracy': 0.85, 'precision': 0.82, 'recall': 0.88},
        'model2': {'accuracy': 0.83, 'precision': 0.80, 'recall': 0.86},
        'model3': {'accuracy': 0.87, 'precision': 0.84, 'recall': 0.90}
    }
    
    visualizer.plot_model_comparison(metrics, timestamp)
    
    # Vérifier que les fichiers ont été créés
    plots_dir = os.path.join(visualizer.output_dir, "plots", "comparison")
    assert os.path.exists(os.path.join(plots_dir, f"model_comparison_{timestamp}.png"))
    assert os.path.exists(os.path.join(plots_dir, f"metric_correlation_{timestamp}.png"))

def test_plot_combined_scores(visualizer, timestamp):
    """Test la création des scores combinés."""
    scores = {
        'model1': np.random.normal(0.5, 0.1, 1000),
        'model2': np.random.normal(0.6, 0.1, 1000),
        'model3': np.random.normal(0.55, 0.1, 1000)
    }
    combined_scores = np.mean([scores['model1'], scores['model2'], scores['model3']], axis=0)
    operation = "mean"
    
    visualizer.plot_combined_scores(scores, combined_scores, operation, timestamp)
    
    # Vérifier que le fichier a été créé
    plots_dir = os.path.join(visualizer.output_dir, "plots", "combined")
    assert os.path.exists(os.path.join(plots_dir, f"combined_scores_{timestamp}.png"))

def test_invalid_inputs(visualizer, timestamp):
    """Test la gestion des entrées invalides."""
    # Test avec une matrice de confusion invalide
    with pytest.raises(Exception):
        visualizer.plot_confusion_matrix(np.array([1, 2, 3]), "test_model", timestamp)
    
    # Test avec des scores invalides
    with pytest.raises(Exception):
        visualizer.plot_score_distribution(np.array([]), "test_model", timestamp)
    
    # Test avec des métriques invalides
    with pytest.raises(Exception):
        visualizer.plot_model_comparison({}, timestamp) 