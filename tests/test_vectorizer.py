"""
Tests unitaires pour le vectoriseur de logs.
"""

import pytest
import numpy as np
from src.data.vectorizer import ModSecVectorizer

@pytest.fixture
def sample_logs():
    """Crée une liste de logs de test."""
    return [
        "GET /api/test HTTP/1.1 User-Agent: Mozilla/5.0",
        "POST /api/user HTTP/1.1 User-Agent: Chrome/91.0",
        "PUT /api/data HTTP/1.1 User-Agent: Firefox/89.0"
    ]

@pytest.fixture
def vectorizer():
    """Crée une instance de ModSecVectorizer pour les tests."""
    return ModSecVectorizer()

def test_vectorizer_initialization(vectorizer):
    """Test l'initialisation du vectoriseur."""
    assert vectorizer is not None
    assert vectorizer.model is not None

def test_vectorize_single_log(vectorizer):
    """Test la vectorisation d'un log unique."""
    log = "GET /api/test HTTP/1.1 User-Agent: Mozilla/5.0"
    vector = vectorizer.vectorize(log)
    
    assert isinstance(vector, list)
    assert len(vector) > 0
    assert all(isinstance(x, (int, float)) for x in vector)

def test_fit_transform(vectorizer, sample_logs):
    """Test l'apprentissage et la transformation des logs."""
    vectors = vectorizer.fit_transform(sample_logs)
    
    assert isinstance(vectors, np.ndarray)
    assert vectors.shape[0] == len(sample_logs)
    assert vectors.shape[1] > 0
    assert all(isinstance(x, (int, float)) for x in vectors.flatten())

def test_transform(vectorizer, sample_logs):
    """Test la transformation des logs avec un modèle appris."""
    # D'abord apprendre le modèle
    vectorizer.fit_transform(sample_logs)
    
    # Puis transformer de nouveaux logs
    new_logs = [
        "GET /api/new HTTP/1.1 User-Agent: Safari/14.0",
        "POST /api/other HTTP/1.1 User-Agent: Edge/91.0"
    ]
    vectors = vectorizer.transform(new_logs)
    
    assert isinstance(vectors, np.ndarray)
    assert vectors.shape[0] == len(new_logs)
    assert vectors.shape[1] > 0
    assert all(isinstance(x, (int, float)) for x in vectors.flatten())

def test_vectorize_empty_log(vectorizer):
    """Test la vectorisation d'un log vide."""
    with pytest.raises(Exception):
        vectorizer.vectorize("")

def test_fit_transform_empty_list(vectorizer):
    """Test l'apprentissage avec une liste vide."""
    with pytest.raises(Exception):
        vectorizer.fit_transform([])

def test_transform_without_fit(vectorizer):
    """Test la transformation sans avoir appris le modèle."""
    with pytest.raises(Exception):
        vectorizer.transform(["GET /api/test HTTP/1.1"])

def test_vectorize_special_characters(vectorizer):
    """Test la vectorisation de logs avec des caractères spéciaux."""
    log = "GET /api/test?param=value&id=123 HTTP/1.1"
    vector = vectorizer.vectorize(log)
    
    assert isinstance(vector, list)
    assert len(vector) > 0
    assert all(isinstance(x, (int, float)) for x in vector)

def test_consistency_between_fit_transform_and_transform(vectorizer, sample_logs):
    """Test la cohérence entre fit_transform et transform."""
    # Apprendre le modèle et transformer les logs
    vectors1 = vectorizer.fit_transform(sample_logs)
    
    # Réinitialiser le vectoriseur
    vectorizer = ModSecVectorizer()
    
    # Apprendre le modèle
    vectorizer.fit_transform(sample_logs)
    
    # Transformer les mêmes logs
    vectors2 = vectorizer.transform(sample_logs)
    
    # Vérifier que les résultats sont identiques
    np.testing.assert_array_almost_equal(vectors1, vectors2) 