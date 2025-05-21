"""
Tests unitaires pour le chargeur de logs.
"""

import os
import pytest
import pandas as pd
from datetime import datetime
from src.data.log_loader import ModSecLogLoader, LogStreamer

@pytest.fixture
def sample_logs():
    """Crée une liste de logs de test."""
    return [
        "GET /api/test HTTP/1.1",
        "POST /api/user HTTP/1.1",
        "PUT /api/data HTTP/1.1"
    ]

@pytest.fixture
def temp_log_file(tmp_path):
    """Crée un fichier de log temporaire pour les tests."""
    log_file = tmp_path / "test.log"
    df = pd.DataFrame({
        'timestamp': [
            pd.Timestamp('2024-01-26 10:00:00'),
            pd.Timestamp('2024-01-26 10:01:00'),
            pd.Timestamp('2024-01-26 10:02:00')
        ],
        'message': [
            "GET /api/test HTTP/1.1",
            "POST /api/user HTTP/1.1",
            "PUT /api/data HTTP/1.1"
        ]
    })
    df.to_csv(log_file, index=False)
    return str(log_file)

def test_log_loader_initialization():
    """Test l'initialisation du chargeur de logs."""
    loader = ModSecLogLoader()
    assert loader is not None
    assert loader.log_path is None

def test_log_loader_with_path(temp_log_file):
    """Test l'initialisation avec un chemin de fichier."""
    loader = ModSecLogLoader(temp_log_file)
    assert loader.log_path == temp_log_file

def test_log_loader_invalid_path():
    """Test l'initialisation avec un chemin invalide."""
    with pytest.raises(FileNotFoundError):
        ModSecLogLoader("invalid/path/to/log.log")

def test_load_logs_from_list(sample_logs):
    """Test le chargement de logs depuis une liste."""
    loader = ModSecLogLoader()
    df = loader.load_logs(logs=sample_logs)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(sample_logs)
    assert 'message' in df.columns
    assert 'timestamp' in df.columns
    assert all(msg in df['message'].values for msg in sample_logs)

def test_load_logs_from_file(temp_log_file):
    """Test le chargement de logs depuis un fichier."""
    loader = ModSecLogLoader(temp_log_file)
    df = loader.load_logs()
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert 'timestamp' in df.columns
    assert 'message' in df.columns

def test_load_logs_with_date_filter(temp_log_file):
    """Test le chargement de logs avec un filtre de date."""
    loader = ModSecLogLoader(temp_log_file)
    df = loader.load_logs(start_date='2024-01-26 10:01:00')
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2  # Seulement les logs après 10:01:00
    assert all(df['timestamp'] >= pd.Timestamp('2024-01-26 10:01:00'))

def test_load_logs_no_source():
    """Test le chargement sans source de logs."""
    loader = ModSecLogLoader()
    with pytest.raises(ValueError):
        loader.load_logs()

def test_log_streamer_initialization(temp_log_file):
    """Test l'initialisation du streamer de logs."""
    def callback(line):
        pass
    
    streamer = LogStreamer(temp_log_file, callback)
    assert streamer.log_path == temp_log_file
    assert streamer.callback == callback
    assert streamer.observer is not None
    assert streamer.handler is not None

def test_log_streamer_start_stop(temp_log_file):
    """Test le démarrage et l'arrêt du streamer."""
    def callback(line):
        pass
    
    streamer = LogStreamer(temp_log_file, callback)
    streamer.start()
    assert streamer.observer.is_alive()
    streamer.stop()
    assert not streamer.observer.is_alive() 