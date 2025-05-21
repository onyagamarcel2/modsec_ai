"""
Tests unitaires pour le détecteur d'anomalies.
"""

import pytest
import numpy as np
import os
import tempfile
from src.models.anomaly_detector import AnomalyDetector

@pytest.fixture
def sample_data():
    """Crée des données de test."""
    # Générer des données normales (cluster gaussien)
    np.random.seed(42)
    normal_data = np.random.normal(0, 1, (100, 10))
    
    # Générer quelques anomalies (points éloignés)
    anomalies = np.random.normal(5, 1, (5, 10))
    
    return np.vstack([normal_data, anomalies])

@pytest.fixture
def detector():
    """Crée une instance de AnomalyDetector pour les tests."""
    return AnomalyDetector(
        detector_type="isolation_forest",
        n_estimators=100,
        contamination=0.1
    )

def test_detector_initialization():
    """Test l'initialisation du détecteur."""
    detector = AnomalyDetector()
    assert detector is not None
    assert detector.detector_type == "isolation_forest"
    assert detector.model is None
    assert detector.scaler is not None

def test_detector_initialization_with_params():
    """Test l'initialisation avec des paramètres personnalisés."""
    detector = AnomalyDetector(
        detector_type="isolation_forest",
        n_estimators=200,
        contamination=0.2
    )
    assert detector.params['n_estimators'] == 200
    assert detector.params['contamination'] == 0.2

def test_fit(detector, sample_data):
    """Test l'entraînement du modèle."""
    detector.fit(sample_data)
    assert detector.model is not None
    assert detector.scaler is not None

def test_predict(detector, sample_data):
    """Test la prédiction d'anomalies."""
    # D'abord entraîner le modèle
    detector.fit(sample_data)
    
    # Puis faire des prédictions
    predictions, scores = detector.predict(sample_data)
    
    assert isinstance(predictions, np.ndarray)
    assert isinstance(scores, np.ndarray)
    assert predictions.shape[0] == sample_data.shape[0]
    assert scores.shape[0] == sample_data.shape[0]
    assert all(pred in [0, 1] for pred in predictions)  # 0: normal, 1: anomalie

def test_predict_without_fit(detector, sample_data):
    """Test la prédiction sans avoir entraîné le modèle."""
    with pytest.raises(Exception):
        detector.predict(sample_data)

def test_save_and_load(detector, sample_data):
    """Test la sauvegarde et le chargement du modèle."""
    # Entraîner le modèle
    detector.fit(sample_data)
    
    # Créer un répertoire temporaire
    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = os.path.join(temp_dir, 'model.joblib')
        
        # Sauvegarder le modèle
        detector.save(model_path)
        
        # Charger le modèle
        new_detector = AnomalyDetector()
        new_detector.load(model_path)
        
        # Vérifier que les prédictions sont identiques
        predictions1, scores1 = detector.predict(sample_data)
        predictions2, scores2 = new_detector.predict(sample_data)
        
        np.testing.assert_array_equal(predictions1, predictions2)
        np.testing.assert_array_almost_equal(scores1, scores2)

def test_invalid_detector_type():
    """Test l'initialisation avec un type de détecteur invalide."""
    detector = AnomalyDetector(detector_type="invalid_type")
    with pytest.raises(ValueError):
        detector.fit(np.random.normal(0, 1, (10, 10)))

def test_detection_of_known_anomalies(detector, sample_data):
    """Test la détection d'anomalies connues."""
    # Entraîner le modèle
    detector.fit(sample_data)
    
    # Les 5 dernières lignes sont des anomalies
    predictions, scores = detector.predict(sample_data)
    
    # Vérifier que les anomalies sont détectées
    assert np.mean(predictions[-5:]) > 0.5  # La majorité des anomalies sont détectées
    assert np.mean(scores[-5:]) > np.mean(scores[:-5])  # Les scores d'anomalie sont plus élevés

def test_consistency_of_predictions(detector, sample_data):
    """Test la cohérence des prédictions sur les mêmes données."""
    # Entraîner le modèle
    detector.fit(sample_data)
    
    # Faire deux prédictions sur les mêmes données
    predictions1, scores1 = detector.predict(sample_data)
    predictions2, scores2 = detector.predict(sample_data)
    
    # Vérifier que les résultats sont identiques
    np.testing.assert_array_equal(predictions1, predictions2)
    np.testing.assert_array_almost_equal(scores1, scores2) 