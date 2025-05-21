"""
Tests unitaires pour RealTimeDetector (détection temps réel).
"""
import pytest
import numpy as np
from src.utils.real_time_detector import RealTimeDetector

def test_initialization():
    detector = RealTimeDetector()
    stats = detector.get_stats()
    assert stats['total_logs'] == 0
    assert stats['total_anomalies'] == 0
    assert stats['mean_score'] == 0.0
    assert stats['std_score'] == 0.0
    assert stats['current_threshold'] == 0.0
    assert stats['current_anomaly_ratio'] == 0.0

def test_update_and_anomaly_detection(monkeypatch):
    detector = RealTimeDetector(window_size=5, min_anomaly_ratio=0.2, adaptive_threshold=True)
    # Patch le seuil pour qu'il soit toujours 0.5
    monkeypatch.setattr(detector, '_calculate_adaptive_threshold', lambda: 0.5)
    # Remplir la fenêtre avec des scores normaux
    detector.update(0.1)
    detector.update(0.2)
    # Ajouter un score anormal (supérieur au seuil patché)
    res = detector.update(1.0)
    assert res['is_anomaly']
    # Vérifier le ratio d'anomalies
    stats = detector.get_stats()
    assert stats['total_anomalies'] == 1
    assert stats['total_logs'] == 3
    assert stats['current_anomaly_ratio'] == pytest.approx(1/3)

def test_adaptive_threshold():
    detector = RealTimeDetector(window_size=3, adaptive_threshold=True)
    # Remplir la fenêtre
    for _ in range(3):
        res = detector.update(0.2)
        assert not res['is_anomaly']
        assert res['threshold'] > 0.0
    # Ajouter un score anormal (beaucoup plus élevé)
    res = detector.update(10.0)
    assert res['is_anomaly']

def test_alert_triggered(monkeypatch):
    detector = RealTimeDetector(window_size=6, min_anomaly_ratio=0.5, adaptive_threshold=True)
    # Patch le seuil pour qu'il soit toujours 0.5
    monkeypatch.setattr(detector, '_calculate_adaptive_threshold', lambda: 0.5)
    
    # Ajouter des scores normaux jusqu'à ce que la fenêtre soit pleine
    for _ in range(6):
        res = detector.update(0.1)
        assert not res['alert_triggered']  # Pas d'alerte car pas d'anomalies
    
    # Ajouter des scores anormaux jusqu'à atteindre le ratio de 0.5
    # Pour atteindre un ratio de 0.5, il faut autant d'anomalies que de logs normaux
    for _ in range(6):
        res = detector.update(1.0)
        if res['stats']['total_logs'] >= 12:  # 6 normaux + 6 anormaux
            assert res['alert_triggered']  # Alerte déclenchée car ratio = 0.5
            break
        assert not res['alert_triggered']  # Pas d'alerte avant d'atteindre le ratio

def test_reset():
    detector = RealTimeDetector()
    for s in [0.1, 0.2, 0.9]:
        detector.update(s)
    detector.reset()
    stats = detector.get_stats()
    assert stats['total_logs'] == 0
    assert stats['total_anomalies'] == 0
    assert stats['mean_score'] == 0.0
    assert stats['std_score'] == 0.0
    assert stats['current_threshold'] == 0.0
    assert stats['current_anomaly_ratio'] == 0.0

def test_update_with_exception(monkeypatch):
    detector = RealTimeDetector()
    # Provoquer une exception dans np.mean
    monkeypatch.setattr(np, 'mean', lambda x: 1/0)
    res = detector.update(0.5)
    assert res is None 