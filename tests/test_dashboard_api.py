"""
Tests unitaires pour l'API du tableau de bord.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.api.dashboard import (
    load_data,
    plot_anomalies_over_time,
    plot_ip_distribution,
    plot_uri_patterns
)

@pytest.fixture
def sample_data():
    """Crée des données de test pour les tests."""
    return pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-26', periods=100, freq='H'),
        'client_ip': ['192.168.1.' + str(i % 10) for i in range(100)],
        'request_uri': ['/api/test' + str(i % 5) for i in range(100)],
        'message': ['Test message ' + str(i) for i in range(100)],
        'is_anomaly': [i % 10 == 0 for i in range(100)],  # Every 10th log is an anomaly
        'anomaly_score': [0.1 + (i % 10) * 0.1 for i in range(100)]
    })

def test_load_data(sample_data):
    """Test le chargement et le prétraitement des données."""
    # Test avec la fenêtre de temps par défaut (24 heures)
    df = load_data(sample_data)
    
    # Vérifier que le DataFrame n'est pas vide
    assert not df.empty
    
    # Vérifier que les colonnes requises existent
    required_columns = ['timestamp', 'client_ip', 'request_uri', 'message', 'is_anomaly', 'anomaly_score']
    for col in required_columns:
        assert col in df.columns
    
    # Test avec une fenêtre de temps personnalisée
    time_window = 12  # heures
    df = load_data(sample_data, time_window=time_window)
    
    # Vérifier que les données sont filtrées par la fenêtre de temps
    max_time = df['timestamp'].max()
    min_time = df['timestamp'].min()
    assert (max_time - min_time).total_seconds() / 3600 <= time_window

def test_plot_anomalies_over_time(sample_data):
    """Test le tracé des anomalies dans le temps."""
    # Créer le graphique
    fig = plot_anomalies_over_time(sample_data)
    
    # Vérifier que la figure est créée
    assert fig is not None
    
    # Vérifier que le graphique a le bon nombre de traces
    assert len(fig.data) == 2  # Une pour les logs normaux, une pour les anomalies

def test_plot_ip_distribution(sample_data):
    """Test le tracé de la distribution des IP."""
    # Créer le graphique
    fig = plot_ip_distribution(sample_data)
    
    # Vérifier que la figure est créée
    assert fig is not None
    
    # Vérifier que le graphique a le bon nombre de traces
    assert len(fig.data) == 2  # Une pour les logs normaux, une pour les anomalies

def test_plot_uri_patterns(sample_data):
    """Test le tracé des patterns d'URI."""
    # Créer le graphique
    fig = plot_uri_patterns(sample_data)
    
    # Vérifier que la figure est créée
    assert fig is not None
    
    # Vérifier que le graphique a le bon nombre de traces
    assert len(fig.data) == 2  # Une pour les logs normaux, une pour les anomalies

def test_handle_empty_data():
    """Test la gestion d'un DataFrame vide."""
    empty_df = pd.DataFrame()
    
    # Test load_data avec un DataFrame vide
    df = load_data(empty_df)
    assert df.empty
    
    # Test des fonctions de tracé avec un DataFrame vide
    fig1 = plot_anomalies_over_time(empty_df)
    fig2 = plot_ip_distribution(empty_df)
    fig3 = plot_uri_patterns(empty_df)
    
    assert fig1 is not None
    assert fig2 is not None
    assert fig3 is not None

def test_handle_missing_columns(sample_data):
    """Test la gestion d'un DataFrame avec des colonnes manquantes."""
    incomplete_df = sample_data.drop(columns=['is_anomaly', 'anomaly_score'])
    
    # Test load_data avec un DataFrame incomplet
    with pytest.raises(KeyError):
        load_data(incomplete_df)
    
    # Test des fonctions de tracé avec un DataFrame incomplet
    with pytest.raises(KeyError):
        plot_anomalies_over_time(incomplete_df)
    
    with pytest.raises(KeyError):
        plot_ip_distribution(incomplete_df)
    
    with pytest.raises(KeyError):
        plot_uri_patterns(incomplete_df)

def test_handle_invalid_time_window(sample_data):
    """Test la gestion d'une fenêtre de temps invalide."""
    # Test avec une fenêtre de temps négative
    with pytest.raises(ValueError):
        load_data(sample_data, time_window=-1)
    
    # Test avec une fenêtre de temps nulle
    with pytest.raises(ValueError):
        load_data(sample_data, time_window=0) 