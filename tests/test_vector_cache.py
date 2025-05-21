"""
Tests unitaires pour VectorCache (système de mise en cache des vecteurs).
"""
import pytest
import numpy as np
import os
import json
import shutil
from datetime import datetime, timedelta
from src.utils.vector_cache import VectorCache

@pytest.fixture
def temp_cache_dir(tmp_path):
    """Crée un répertoire temporaire pour le cache."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    yield str(cache_dir)
    # Nettoyage après les tests
    shutil.rmtree(cache_dir)

@pytest.fixture
def vector_cache(temp_cache_dir):
    """Crée une instance de VectorCache pour les tests."""
    return VectorCache(cache_dir=temp_cache_dir, max_size=5, ttl_hours=1)

def test_initialization(temp_cache_dir):
    """Teste l'initialisation du cache."""
    cache = VectorCache(cache_dir=temp_cache_dir)
    assert cache.cache_dir == temp_cache_dir
    assert cache.max_size == 10000  # Valeur par défaut
    assert cache.ttl == timedelta(hours=24)  # Valeur par défaut
    assert len(cache.cache) == 0
    assert len(cache.access_times) == 0
    assert os.path.exists(temp_cache_dir)

def test_put_and_get(vector_cache):
    """Teste l'ajout et la récupération de vecteurs."""
    tokens = ["test", "tokens"]
    vector = np.array([1.0, 2.0, 3.0])
    
    # Test put
    vector_cache.put(tokens, vector)
    assert len(vector_cache.cache) == 1
    assert len(vector_cache.access_times) == 1
    
    # Test get
    retrieved = vector_cache.get(tokens)
    assert retrieved is not None
    np.testing.assert_array_equal(retrieved, vector)
    
    # Test get avec tokens différents
    assert vector_cache.get(["different", "tokens"]) is None

def test_cache_persistence(temp_cache_dir):
    """Teste la persistance du cache sur le disque."""
    # Créer et remplir un cache
    cache1 = VectorCache(cache_dir=temp_cache_dir)
    tokens = ["test", "tokens"]
    vector = np.array([1.0, 2.0, 3.0])
    cache1.put(tokens, vector)
    
    # Forcer la sauvegarde du cache
    cache1._save_cache()
    
    # Vérifier que le fichier de cache existe
    cache_file = os.path.join(temp_cache_dir, 'vector_cache.json')
    assert os.path.exists(cache_file)
    
    # Créer une nouvelle instance qui devrait charger le cache
    cache2 = VectorCache(cache_dir=temp_cache_dir)
    retrieved = cache2.get(tokens)
    assert retrieved is not None
    np.testing.assert_array_equal(retrieved, vector)

def test_cache_cleanup(vector_cache):
    """Teste le nettoyage automatique du cache."""
    # Remplir le cache jusqu'à la limite
    for i in range(6):  # max_size = 5
        tokens = [f"token{i}"]
        vector = np.array([i])
        vector_cache.put(tokens, vector)
    
    # Vérifier que le cache a été nettoyé
    assert len(vector_cache.cache) <= 5
    assert len(vector_cache.access_times) <= 5

def test_cache_expiration(vector_cache):
    """Teste l'expiration des entrées du cache."""
    # Ajouter une entrée
    tokens = ["test", "tokens"]
    vector = np.array([1.0, 2.0, 3.0])
    vector_cache.put(tokens, vector)
    
    # Forcer l'expiration en modifiant le temps d'accès
    old_time = datetime.now() - timedelta(hours=2)  # TTL = 1 heure
    vector_cache.access_times[vector_cache._get_hash(tokens)] = old_time
    
    # Déclencher le nettoyage
    vector_cache._cleanup()
    
    # Vérifier que l'entrée a expiré
    assert vector_cache.get(tokens) is None

def test_clear_cache(vector_cache):
    """Teste la suppression du cache."""
    # Ajouter des entrées
    tokens = ["test", "tokens"]
    vector = np.array([1.0, 2.0, 3.0])
    vector_cache.put(tokens, vector)
    
    # Vider le cache
    vector_cache.clear()
    
    # Vérifier que le cache est vide
    assert len(vector_cache.cache) == 0
    assert len(vector_cache.access_times) == 0
    assert vector_cache.get(tokens) is None

def test_invalid_cache_file(temp_cache_dir):
    """Teste la gestion d'un fichier de cache invalide."""
    # Créer un fichier de cache invalide
    cache_file = os.path.join(temp_cache_dir, 'vector_cache.json')
    with open(cache_file, 'w') as f:
        f.write('invalid json')
    
    # Vérifier que le cache s'initialise correctement malgré le fichier invalide
    cache = VectorCache(cache_dir=temp_cache_dir)
    assert len(cache.cache) == 0
    assert len(cache.access_times) == 0 