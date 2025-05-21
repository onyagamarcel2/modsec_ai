"""
Tests unitaires pour GUIDataManager (gestionnaire de données pour l'interface graphique).
"""
import pytest
import pandas as pd
import os
import json
import shutil
from datetime import datetime, timedelta
from src.utils.gui_data_manager import GUIDataManager

@pytest.fixture
def temp_output_dir(tmp_path):
    """Crée un répertoire temporaire pour les données."""
    output_dir = tmp_path / "test_gui_data"
    output_dir.mkdir()
    yield str(output_dir)
    # Nettoyage après les tests
    shutil.rmtree(output_dir)

@pytest.fixture
def gui_manager(temp_output_dir):
    """Crée une instance de GUIDataManager pour les tests."""
    return GUIDataManager(output_dir=temp_output_dir)

@pytest.fixture
def sample_anomalies_df():
    """Crée un DataFrame d'exemple avec des anomalies."""
    data = {
        'timestamp': [datetime.now()],
        'client_ip': ['192.168.1.1'],
        'request_uri': ['/login'],
        'anomaly_score': [0.95],
        'message': ['Possible SQL injection'],
        'is_anomaly': [True]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_stats():
    """Crée des statistiques d'exemple."""
    return {
        'total_requests': 100,
        'anomaly_count': 5,
        'avg_score': 0.75
    }

def test_initialization(temp_output_dir):
    """Teste l'initialisation du gestionnaire de données."""
    manager = GUIDataManager(output_dir=temp_output_dir)
    assert manager.output_dir == temp_output_dir
    assert os.path.exists(temp_output_dir)
    assert len(manager.anomalies_data) == 0
    assert len(manager.stats_data) == 0

def test_add_anomalies(gui_manager, sample_anomalies_df):
    """Teste l'ajout d'anomalies."""
    # Ajouter des anomalies
    gui_manager.add_anomalies(sample_anomalies_df)
    
    # Vérifier que les données ont été ajoutées
    assert len(gui_manager.anomalies_data) == 1
    anomaly = gui_manager.anomalies_data[0]
    assert anomaly['client_ip'] == '192.168.1.1'
    assert anomaly['request_uri'] == '/login'
    assert anomaly['anomaly_score'] == 0.95
    assert anomaly['is_anomaly'] is True

def test_update_stats(gui_manager, sample_stats):
    """Teste la mise à jour des statistiques."""
    # Mettre à jour les statistiques
    gui_manager.update_stats(sample_stats)
    
    # Après update_stats, stats_data doit être vide (car sauvegardé)
    assert len(gui_manager.stats_data) == 0
    # Vérifier qu'un fichier de stats a été créé
    files = os.listdir(gui_manager.output_dir)
    assert any(f.startswith('stats_') for f in files)

def test_save_and_load_data(gui_manager, sample_anomalies_df, sample_stats):
    """Teste la sauvegarde et le chargement des données."""
    # Ajouter des données
    gui_manager.add_anomalies(sample_anomalies_df)
    gui_manager.update_stats(sample_stats)
    
    # Forcer la sauvegarde
    gui_manager._save_anomalies()
    gui_manager._save_stats()
    
    # Vérifier que les fichiers ont été créés
    files = os.listdir(gui_manager.output_dir)
    assert any(f.startswith('anomalies_') for f in files)
    assert any(f.startswith('stats_') for f in files)
    
    # Récupérer les dernières données
    latest_data = gui_manager.get_latest_data()
    assert len(latest_data['anomalies']) == 1
    assert len(latest_data['stats']) == 1

def test_cleanup_old_data(gui_manager, sample_anomalies_df, sample_stats):
    """Teste le nettoyage des anciennes données."""
    # Ajouter et sauvegarder des données
    gui_manager.add_anomalies(sample_anomalies_df)
    gui_manager.update_stats(sample_stats)
    gui_manager._save_anomalies()
    gui_manager._save_stats()
    
    # Créer un fichier ancien
    old_file = os.path.join(gui_manager.output_dir, 'old_file.json')
    with open(old_file, 'w') as f:
        json.dump({'test': 'data'}, f)
    
    # Modifier la date de création du fichier
    old_time = datetime.now() - timedelta(days=8)
    os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
    
    # Nettoyer les anciennes données
    gui_manager.cleanup_old_data(max_age_days=7)
    
    # Vérifier que le fichier ancien a été supprimé
    assert not os.path.exists(old_file)
    # Vérifier que les fichiers récents sont toujours présents
    files = os.listdir(gui_manager.output_dir)
    assert any(f.startswith('anomalies_') for f in files)
    assert any(f.startswith('stats_') for f in files)

def test_handle_invalid_data(gui_manager):
    """Teste la gestion des données invalides."""
    # Tester avec un DataFrame vide
    empty_df = pd.DataFrame()
    gui_manager.add_anomalies(empty_df)
    assert len(gui_manager.anomalies_data) == 0
    
    # Tester avec des statistiques invalides
    invalid_stats = None
    gui_manager.update_stats(invalid_stats)
    assert len(gui_manager.stats_data) == 0

def test_auto_save_anomalies(gui_manager, sample_anomalies_df):
    """Teste la sauvegarde automatique des anomalies après 100 points."""
    # Ajouter 101 anomalies
    for _ in range(101):
        gui_manager.add_anomalies(sample_anomalies_df)
    
    # Vérifier que les données ont été sauvegardées
    files = os.listdir(gui_manager.output_dir)
    assert any(f.startswith('anomalies_') for f in files)
    assert len(gui_manager.anomalies_data) < 100  # Les données ont été sauvegardées 