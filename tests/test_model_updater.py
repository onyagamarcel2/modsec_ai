"""
Tests unitaires pour le module de mise à jour des modèles (ModelUpdater).
"""

import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from src.models.model_updater import ModelUpdater

@pytest.fixture
def mock_dependencies(monkeypatch, tmp_path):
    # Mock des modèles
    mock_model = MagicMock()
    mock_model.predict.return_value = np.ones(10)
    mock_model.predict_proba.return_value = np.linspace(0, 1, 10)
    mock_model.fit.return_value = None
    mock_model.partial_fit.return_value = None
    
    # Patch les load de chaque détecteur pour retourner le mock
    for name in [
        'IsolationForestDetector',
        'LocalOutlierFactorDetector',
        'EllipticEnvelopeDetector',
        'OneClassSVMDetector',
        'EnsembleAnomalyDetector']:
        monkeypatch.setattr(f"src.models.anomaly_detectors.{name}.load", staticmethod(lambda path: mock_model))
    
    # Mock du vectorizer et du preprocessor
    monkeypatch.setattr("src.models.vectorizer.LogVectorizer", lambda: MagicMock(transform=MagicMock(return_value=np.ones((10, 5)))))
    monkeypatch.setattr("src.data.preprocessor.ModSecPreprocessor", lambda: MagicMock(preprocess=MagicMock(return_value=['log']*10)))
    
    # Créer un répertoire temporaire pour les modèles
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    return str(model_dir)

def test_initialization(mock_dependencies):
    updater = ModelUpdater(model_dir=mock_dependencies)
    assert updater.model_dir == mock_dependencies
    assert isinstance(updater.models, dict)
    assert 'isolation_forest' in updater.models
    assert updater.data_buffer.maxlen == updater.max_samples

def test_update_logic(monkeypatch, mock_dependencies):
    # Patch AVANT l'instanciation de ModelUpdater, sur le chemin utilisé dans le module
    monkeypatch.setattr("src.models.model_updater.ModSecPreprocessor", lambda: MagicMock(preprocess=MagicMock(return_value=['log']*2)))
    monkeypatch.setattr("src.models.model_updater.LogVectorizer", lambda: MagicMock(transform=MagicMock(return_value=np.ones((2, 5)))))
    
    # Mock du modèle qui retourne des prédictions de la même taille que les données
    mock_model = MagicMock()
    mock_model.predict.return_value = np.ones((2, 5))  # Matrice 2x5 comme les données d'entrée
    mock_model.predict_proba.return_value = np.ones((2, 5))  # Matrice 2x5 pour les probabilités
    mock_model.fit.return_value = None
    mock_model.partial_fit.return_value = None
    
    # Patch les load de chaque détecteur pour retourner le mock
    for name in [
        'IsolationForestDetector',
        'LocalOutlierFactorDetector',
        'EllipticEnvelopeDetector',
        'OneClassSVMDetector',
        'EnsembleAnomalyDetector']:
        monkeypatch.setattr(f"src.models.anomaly_detectors.{name}.load", staticmethod(lambda path: mock_model))
    
    updater = ModelUpdater(model_dir=mock_dependencies, min_samples=2, update_interval=0)
    new_data = [{'log': 'entry1'}, {'log': 'entry2'}]
    updater.update(new_data)
    assert len(updater.data_buffer) == 2

def test_prepare_data(monkeypatch, mock_dependencies):
    # Patch AVANT l'instanciation de ModelUpdater, sur le chemin utilisé dans le module
    monkeypatch.setattr("src.models.model_updater.ModSecPreprocessor", lambda: MagicMock(preprocess=MagicMock(return_value=['log']*10)))
    monkeypatch.setattr("src.models.model_updater.LogVectorizer", lambda: MagicMock(transform=MagicMock(return_value=np.ones((10, 5)))))
    updater = ModelUpdater(model_dir=mock_dependencies)
    updater.data_buffer.extend([{'log': 'entry'}]*10)
    vectors = updater._prepare_data()
    assert isinstance(vectors, np.ndarray)
    assert vectors.shape == (10, 5)

def test_update_models(monkeypatch, mock_dependencies):
    updater = ModelUpdater(model_dir=mock_dependencies)
    vectors = np.ones((10, 5))
    # Doit appeler fit ou partial_fit sur chaque modèle
    updater._update_models(vectors)
    for model in updater.models.values():
        assert model.fit.called or model.partial_fit.called

def test_evaluate_performance(monkeypatch, mock_dependencies):
    updater = ModelUpdater(model_dir=mock_dependencies)
    vectors = np.ones((10, 5))
    # Patch les métriques sklearn.metrics (et non le module local)
    with patch("sklearn.metrics.precision_score", return_value=1.0), \
         patch("sklearn.metrics.recall_score", return_value=1.0), \
         patch("sklearn.metrics.f1_score", return_value=1.0), \
         patch("sklearn.metrics.roc_auc_score", return_value=1.0):
        perf = updater._evaluate_performance(vectors)
        assert isinstance(perf, dict)
        for v in perf.values():
            assert v['precision'] == 1.0
            assert v['recall'] == 1.0
            assert v['f1'] == 1.0
            assert v['auc'] == 1.0

def test_should_retrain(mock_dependencies):
    updater = ModelUpdater(model_dir=mock_dependencies)
    perf = {
        'isolation_forest': {'precision': 0.7, 'recall': 0.7, 'f1': 0.5, 'auc': 0.7},
        'local_outlier_factor': {'precision': 0.9, 'recall': 0.9, 'f1': 0.9, 'auc': 0.9},
        'elliptic_envelope': {'precision': 0.7, 'recall': 0.7, 'f1': 0.7, 'auc': 0.7},
        'one_class_svm': {'precision': 0.6, 'recall': 0.6, 'f1': 0.6, 'auc': 0.6},
        'ensemble': {'precision': 0.8, 'recall': 0.8, 'f1': 0.8, 'auc': 0.8}
    }
    # Seuil par défaut = 0.8
    assert updater._should_retrain(perf) is True
    perf = {k: {'precision': 0.9, 'recall': 0.9, 'f1': 0.9, 'auc': 0.9} for k in perf}
    assert updater._should_retrain(perf) is False

def test_save_models(monkeypatch, mock_dependencies):
    updater = ModelUpdater(model_dir=mock_dependencies)
    # Patch la méthode save de chaque modèle
    for model in updater.models.values():
        model.save = MagicMock()
    updater._save_models()
    for model in updater.models.values():
        assert model.save.called

def test_get_performance_history(mock_dependencies):
    updater = ModelUpdater(model_dir=mock_dependencies)
    hist = updater.get_performance_history()
    assert isinstance(hist, dict)
    for k in ['precision', 'recall', 'f1', 'auc']:
        assert k in hist
        assert isinstance(hist[k], list) 