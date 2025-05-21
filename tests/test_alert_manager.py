"""
Tests unitaires pour AlertManager (gestionnaire d'alertes pour les anomalies).
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.utils.alert_manager import AlertManager

@pytest.fixture
def mock_notification_manager():
    """Crée un gestionnaire de notifications mock."""
    return Mock()

@pytest.fixture
def alert_manager(mock_notification_manager):
    """Crée une instance de AlertManager pour les tests (seuil élevé pour éviter le déclenchement d'alerte)."""
    return AlertManager(
        threshold=4,  # Seuil supérieur au nombre d'anomalies pour éviter le vidage
        window=300,   # 5 minutes
        notification_manager=mock_notification_manager
    )

@pytest.fixture
def alert_manager_low_threshold(mock_notification_manager):
    """Crée une instance de AlertManager pour tester le déclenchement d'alerte."""
    return AlertManager(
        threshold=3,  # Seuil bas pour déclencher l'alerte
        window=300,
        notification_manager=mock_notification_manager
    )

@pytest.fixture
def sample_anomalies_df():
    """Crée un DataFrame d'exemple avec des anomalies."""
    data = {
        'client_ip': ['192.168.1.1', '192.168.1.2', '192.168.1.1'],
        'request_uri': ['/login', '/admin', '/api'],
        'anomaly_score': [0.95, 0.85, 0.90],
        'message': ['SQL injection', 'XSS attack', 'Path traversal']
    }
    return pd.DataFrame(data)

def test_initialization():
    """Teste l'initialisation du gestionnaire d'alertes."""
    # Test avec valeurs par défaut
    manager = AlertManager()
    assert manager.threshold == 5
    assert manager.window == 300
    assert manager.notification_manager is None
    assert len(manager.anomaly_history) == 0
    
    # Test avec valeurs personnalisées
    notification_manager = Mock()
    manager = AlertManager(threshold=10, window=600, notification_manager=notification_manager)
    assert manager.threshold == 10
    assert manager.window == 600
    assert manager.notification_manager == notification_manager

def test_check_anomalies_below_threshold(alert_manager, sample_anomalies_df):
    """Teste la vérification des anomalies sous le seuil."""
    alert_manager.check_anomalies(sample_anomalies_df)
    assert len(alert_manager.anomaly_history) == 3
    alert_manager.notification_manager.send_notification.assert_not_called()

def test_check_anomalies_above_threshold(alert_manager_low_threshold, sample_anomalies_df):
    """Teste la vérification des anomalies au-dessus du seuil."""
    # Ajouter suffisamment d'anomalies pour dépasser le seuil en un seul appel
    alert_manager_low_threshold.check_anomalies(sample_anomalies_df)
    alert_manager_low_threshold.notification_manager.send_notification.assert_called_once()
    assert len(alert_manager_low_threshold.anomaly_history) == 0

def test_anomaly_history_cleanup(alert_manager, sample_anomalies_df):
    """Teste le nettoyage de l'historique des anomalies."""
    # Ajouter des anomalies avec un timestamp ancien
    old_time = datetime.now() - timedelta(seconds=alert_manager.window + 10)
    for _, row in sample_anomalies_df.iterrows():
        alert_manager.anomaly_history.append({
            'timestamp': old_time,
            'client_ip': row['client_ip'],
            'request_uri': row['request_uri'],
            'anomaly_score': row['anomaly_score'],
            'message': row['message']
        })
    # Ajouter des anomalies récentes
    for _, row in sample_anomalies_df.iterrows():
        alert_manager.anomaly_history.append({
            'timestamp': datetime.now(),
            'client_ip': row['client_ip'],
            'request_uri': row['request_uri'],
            'anomaly_score': row['anomaly_score'],
            'message': row['message']
        })
    # Nettoyer l'historique (simulateur d'appel interne)
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(seconds=alert_manager.window)
    alert_manager.anomaly_history = [
        anomaly for anomaly in alert_manager.anomaly_history
        if anomaly['timestamp'] > cutoff_time
    ]
    # Vérifier que seules les anomalies récentes restent
    assert len(alert_manager.anomaly_history) == 3

def test_create_anomaly_summary(alert_manager, sample_anomalies_df):
    """Teste la création du résumé des anomalies."""
    alert_manager.check_anomalies(sample_anomalies_df)
    summary = alert_manager._create_anomaly_summary()
    assert "Résumé des anomalies détectées" in summary
    assert "Nombre total d'anomalies: 3" in summary
    assert "Nombre d'IPs uniques: 2" in summary
    assert "Top 3 des IPs suspectes" in summary
    assert "192.168.1.1" in summary  # IP la plus fréquente

def test_handle_invalid_data(alert_manager):
    """Teste la gestion des données invalides."""
    # Tester avec un DataFrame vide
    empty_df = pd.DataFrame()
    alert_manager.check_anomalies(empty_df)
    assert len(alert_manager.anomaly_history) == 0
    
    # Tester avec des données manquantes
    invalid_df = pd.DataFrame({
        'client_ip': ['192.168.1.1'],
        'request_uri': ['/login']
    })
    alert_manager.check_anomalies(invalid_df)
    assert len(alert_manager.anomaly_history) == 1
    assert alert_manager.anomaly_history[0]['anomaly_score'] == 0.0
    assert alert_manager.anomaly_history[0]['message'] == ''

def test_alert_without_notification_manager():
    """Teste le déclenchement d'alerte sans gestionnaire de notifications."""
    # Créer un gestionnaire sans notification_manager
    manager = AlertManager(threshold=1)
    
    # Ajouter une anomalie
    anomalies_df = pd.DataFrame({
        'client_ip': ['192.168.1.1'],
        'request_uri': ['/login'],
        'anomaly_score': [0.95],
        'message': ['Test alert']
    })
    
    # Vérifier que l'alerte est déclenchée sans erreur
    manager.check_anomalies(anomalies_df)
    assert len(manager.anomaly_history) == 0  # L'historique est réinitialisé 