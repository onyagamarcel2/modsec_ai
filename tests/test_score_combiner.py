"""
Tests unitaires pour le module de combinaison de scores.
"""

import pytest
import numpy as np
from src.models.score_combiner import ScoreCombiner

@pytest.fixture
def sample_scores():
    """Crée des scores de test pour différents modèles."""
    return {
        'model1': np.array([0.1, 0.5, 0.9]),
        'model2': np.array([0.2, 0.6, 0.8]),
        'model3': np.array([0.3, 0.4, 0.7])
    }

@pytest.fixture
def sample_weights():
    """Crée des poids de test pour les modèles."""
    return {
        'model1': 0.5,
        'model2': 0.3,
        'model3': 0.2
    }

def test_initialization():
    """Test l'initialisation du combinateur de scores."""
    # Test avec opération par défaut
    combiner = ScoreCombiner()
    assert combiner.operation == 'mean'
    assert combiner.weights == {}
    
    # Test avec opération personnalisée
    combiner = ScoreCombiner(operation='max')
    assert combiner.operation == 'max'
    
    # Test avec poids
    weights = {'model1': 0.5, 'model2': 0.5}
    combiner = ScoreCombiner(operation='weighted_mean', weights=weights)
    assert combiner.weights == weights

def test_invalid_operation():
    """Test la validation des opérations invalides."""
    with pytest.raises(ValueError):
        ScoreCombiner(operation='invalid_operation')

def test_mean_combination(sample_scores):
    """Test la combinaison par moyenne."""
    combiner = ScoreCombiner(operation='mean')
    combined = combiner.combine_scores(sample_scores)
    
    expected = np.mean([sample_scores['model1'], 
                       sample_scores['model2'], 
                       sample_scores['model3']], axis=0)
    
    np.testing.assert_array_almost_equal(combined, expected)

def test_max_combination(sample_scores):
    """Test la combinaison par maximum."""
    combiner = ScoreCombiner(operation='max')
    combined = combiner.combine_scores(sample_scores)
    
    expected = np.max([sample_scores['model1'], 
                      sample_scores['model2'], 
                      sample_scores['model3']], axis=0)
    
    np.testing.assert_array_almost_equal(combined, expected)

def test_min_combination(sample_scores):
    """Test la combinaison par minimum."""
    combiner = ScoreCombiner(operation='min')
    combined = combiner.combine_scores(sample_scores)
    
    expected = np.min([sample_scores['model1'], 
                      sample_scores['model2'], 
                      sample_scores['model3']], axis=0)
    
    np.testing.assert_array_almost_equal(combined, expected)

def test_weighted_mean_combination(sample_scores, sample_weights):
    """Test la combinaison par moyenne pondérée."""
    combiner = ScoreCombiner(operation='weighted_mean', weights=sample_weights)
    combined = combiner.combine_scores(sample_scores)
    
    expected = np.average([sample_scores['model1'], 
                         sample_scores['model2'], 
                         sample_scores['model3']], 
                         axis=0,
                         weights=[sample_weights['model1'],
                                sample_weights['model2'],
                                sample_weights['model3']])
    
    np.testing.assert_array_almost_equal(combined, expected)

def test_weighted_mean_missing_weights(sample_scores):
    """Test la gestion des poids manquants pour la moyenne pondérée."""
    weights = {'model1': 0.5, 'model2': 0.5}  # model3 manquant
    combiner = ScoreCombiner(operation='weighted_mean', weights=weights)
    
    with pytest.raises(ValueError):
        combiner.combine_scores(sample_scores)

def test_empty_scores():
    """Test la gestion des scores vides."""
    combiner = ScoreCombiner()
    
    with pytest.raises(ValueError):
        combiner.combine_scores({})

def test_set_operation():
    """Test le changement d'opération."""
    combiner = ScoreCombiner(operation='mean')
    assert combiner.operation == 'mean'
    
    combiner.set_operation('max')
    assert combiner.operation == 'max'
    
    with pytest.raises(ValueError):
        combiner.set_operation('invalid_operation')

def test_set_weights():
    """Test le changement des poids."""
    combiner = ScoreCombiner(operation='weighted_mean')
    assert combiner.weights == {}
    
    new_weights = {'model1': 0.6, 'model2': 0.4}
    combiner.set_weights(new_weights)
    assert combiner.weights == new_weights

def test_get_operation_info():
    """Test la récupération des informations sur l'opération."""
    combiner = ScoreCombiner(operation='mean')
    info = combiner.get_operation_info()
    
    assert isinstance(info, dict)
    assert 'description' in info
    assert 'function' in info
    assert 'name' in info 