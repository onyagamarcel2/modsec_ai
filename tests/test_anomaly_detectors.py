"""
Tests unitaires pour les implémentations spécifiques des détecteurs d'anomalies.
"""

import pytest
import numpy as np
import os
import tempfile
from src.models.anomaly_detectors import (
    IsolationForestDetector,
    LocalOutlierFactorDetector,
    EllipticEnvelopeDetector,
    OneClassSVMDetector,
    EnsembleAnomalyDetector
)

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
def high_dim_data():
    """Crée des données de haute dimensionnalité pour tester PCA."""
    np.random.seed(42)
    return np.random.normal(0, 1, (100, 150))

def test_isolation_forest_detector(sample_data):
    """Test le détecteur Isolation Forest."""
    detector = IsolationForestDetector(contamination=0.1)
    
    # Test de l'entraînement
    detector.fit(sample_data)
    assert detector.model is not None
    assert detector.scaler is not None
    
    # Test des prédictions
    predictions = detector.predict(sample_data)
    scores = detector.predict_proba(sample_data)
    
    assert isinstance(predictions, np.ndarray)
    assert isinstance(scores, np.ndarray)
    assert predictions.shape[0] == sample_data.shape[0]
    assert scores.shape[0] == sample_data.shape[0]
    assert all(pred in [-1, 1] for pred in predictions)

def test_local_outlier_factor_detector(sample_data):
    """Test le détecteur Local Outlier Factor."""
    detector = LocalOutlierFactorDetector(n_neighbors=20, contamination=0.1)
    
    # Test de l'entraînement
    detector.fit(sample_data)
    assert detector.model is not None
    assert detector.scaler is not None
    
    # Test des prédictions
    predictions = detector.predict(sample_data)
    scores = detector.predict_proba(sample_data)
    
    assert isinstance(predictions, np.ndarray)
    assert isinstance(scores, np.ndarray)
    assert predictions.shape[0] == sample_data.shape[0]
    assert scores.shape[0] == sample_data.shape[0]
    assert all(pred in [-1, 1] for pred in predictions)

def test_elliptic_envelope_detector(sample_data):
    """Test le détecteur Elliptic Envelope."""
    detector = EllipticEnvelopeDetector(contamination=0.1)
    
    # Test de l'entraînement
    detector.fit(sample_data)
    assert detector.model is not None
    assert detector.scaler is not None
    
    # Test des prédictions
    predictions = detector.predict(sample_data)
    scores = detector.predict_proba(sample_data)
    
    assert isinstance(predictions, np.ndarray)
    assert isinstance(scores, np.ndarray)
    assert predictions.shape[0] == sample_data.shape[0]
    assert scores.shape[0] == sample_data.shape[0]
    assert all(pred in [-1, 1] for pred in predictions)

def test_one_class_svm_detector(sample_data):
    """Test le détecteur One-Class SVM."""
    detector = OneClassSVMDetector(nu=0.1)
    
    # Test de l'entraînement
    detector.fit(sample_data)
    assert detector.model is not None
    assert detector.scaler is not None
    
    # Test des prédictions
    predictions = detector.predict(sample_data)
    scores = detector.predict_proba(sample_data)
    
    assert isinstance(predictions, np.ndarray)
    assert isinstance(scores, np.ndarray)
    assert predictions.shape[0] == sample_data.shape[0]
    assert scores.shape[0] == sample_data.shape[0]
    assert all(pred in [-1, 1] for pred in predictions)

def test_ensemble_detector(sample_data):
    """Test le détecteur d'ensemble."""
    # Créer un ensemble de détecteurs
    detectors = [
        IsolationForestDetector(),
        LocalOutlierFactorDetector(),
        EllipticEnvelopeDetector()
    ]
    ensemble = EnsembleAnomalyDetector(detectors=detectors)
    
    # Test de l'entraînement
    ensemble.fit(sample_data)
    assert all(detector.model is not None for detector in ensemble.detectors)
    
    # Test des prédictions
    predictions = ensemble.predict(sample_data)
    scores = ensemble.predict_proba(sample_data)
    
    assert isinstance(predictions, np.ndarray)
    assert isinstance(scores, np.ndarray)
    assert predictions.shape[0] == sample_data.shape[0]
    assert scores.shape[0] == sample_data.shape[0]
    assert all(pred in [-1, 1] for pred in predictions)

def test_pca_reduction(high_dim_data):
    """Test la réduction de dimensionnalité avec PCA."""
    detector = IsolationForestDetector()
    
    # Test de l'entraînement avec données de haute dimension
    detector.fit(high_dim_data)
    assert detector.pca is not None
    assert detector.model is not None
    
    # Test des prédictions
    predictions = detector.predict(high_dim_data)
    scores = detector.predict_proba(high_dim_data)
    
    assert isinstance(predictions, np.ndarray)
    assert isinstance(scores, np.ndarray)
    assert predictions.shape[0] == high_dim_data.shape[0]
    assert scores.shape[0] == high_dim_data.shape[0]

def test_save_and_load(sample_data):
    """Test la sauvegarde et le chargement des modèles."""
    # Test avec Isolation Forest
    detector = IsolationForestDetector()
    detector.fit(sample_data)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = os.path.join(temp_dir, 'model.joblib')
        
        # Sauvegarder le modèle
        detector.save(model_path)
        
        # Charger le modèle
        loaded_detector = IsolationForestDetector.load(model_path)
        
        # Vérifier que les prédictions sont identiques
        predictions1 = detector.predict(sample_data)
        predictions2 = loaded_detector.predict(sample_data)
        
        np.testing.assert_array_equal(predictions1, predictions2)

def test_detection_of_known_anomalies(sample_data):
    """Test la détection d'anomalies connues avec différents détecteurs."""
    detectors = [
        IsolationForestDetector(contamination=0.1),
        LocalOutlierFactorDetector(n_neighbors=20, contamination=0.1),
        EllipticEnvelopeDetector(contamination=0.1),
        OneClassSVMDetector(nu=0.1)
    ]
    
    for detector in detectors:
        detector.fit(sample_data)
        predictions = detector.predict(sample_data)
        scores = detector.predict_proba(sample_data)
        
        # Vérifier que les scores d'anomalie sont plus élevés pour les anomalies connues
        anomaly_scores = scores[-5:]  # Scores des 5 dernières lignes (anomalies)
        normal_scores = scores[:-5]   # Scores des lignes normales
        
        # Les scores d'anomalie devraient être plus élevés pour les anomalies
        assert np.mean(anomaly_scores) > np.mean(normal_scores)
        
        # Au moins une anomalie devrait être détectée
        assert np.any(predictions[-5:] == -1) 