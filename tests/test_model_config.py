"""
Tests unitaires pour src/config/model_config.py
"""
import pytest
from src.config import model_config

def test_available_models_structure():
    models = model_config.AVAILABLE_MODELS
    assert isinstance(models, dict)
    for key, model in models.items():
        assert 'name' in model
        assert 'description' in model
        assert 'parameters' in model
        assert isinstance(model['parameters'], dict)
        for param, param_info in model['parameters'].items():
            assert 'type' in param_info
            assert 'default' in param_info
            assert 'description' in param_info

def test_score_operations_structure():
    ops = model_config.SCORE_OPERATIONS
    assert isinstance(ops, dict)
    for key, op in ops.items():
        assert 'name' in op
        assert 'description' in op
        assert 'function' in op

def test_visualizations_structure():
    vis = model_config.VISUALIZATIONS
    assert isinstance(vis, dict)
    for key, v in vis.items():
        assert 'name' in v
        assert 'description' in v
        assert 'plots' in v
        assert isinstance(v['plots'], list)
        for plot in v['plots']:
            assert 'name' in plot
            assert 'type' in plot
            assert 'x_label' in plot
            assert 'y_label' in plot

def test_evaluation_metrics_structure():
    metrics = model_config.EVALUATION_METRICS
    assert isinstance(metrics, dict)
    for key, metric in metrics.items():
        assert 'name' in metric
        assert 'description' in metric

def test_model_parameters_ranges():
    # Vérifie que les bornes min/max sont cohérentes pour les paramètres numériques
    for model in model_config.AVAILABLE_MODELS.values():
        for param, param_info in model['parameters'].items():
            if param_info['type'] in ('float', 'int'):
                assert param_info['min'] < param_info['max']
                assert param_info['min'] <= param_info['default'] <= param_info['max']
            if param_info['type'] == 'choice':
                assert 'choices' in param_info
                assert param_info['default'] in param_info['choices'] 