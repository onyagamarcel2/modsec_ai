"""
Tests unitaires pour NotificationManager (gestionnaire de notifications).
"""
import pytest
import json
import os
from unittest.mock import Mock, patch
from src.utils.notifications import NotificationManager

@pytest.fixture
def temp_config_file(tmp_path):
    """Crée un fichier de configuration temporaire."""
    config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "test@example.com",
        "smtp_password": "password",
        "recipient": "admin@example.com",
        "webhook_url": "https://hooks.slack.com/services/test"
    }
    config_file = tmp_path / "notification_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    return str(config_file)

@pytest.fixture
def notification_manager(temp_config_file):
    """Crée une instance de NotificationManager pour les tests."""
    return NotificationManager(
        notification_type='email',
        config_file=temp_config_file
    )

def test_initialization():
    """Teste l'initialisation du gestionnaire de notifications."""
    # Test avec valeurs par défaut
    manager = NotificationManager()
    assert manager.notification_type == 'email'
    assert manager.config == {}
    
    # Test avec type personnalisé
    manager = NotificationManager(notification_type='slack')
    assert manager.notification_type == 'slack'

def test_load_config(temp_config_file):
    """Teste le chargement de la configuration."""
    # Test avec fichier valide
    manager = NotificationManager(config_file=temp_config_file)
    assert manager.config['smtp_server'] == 'smtp.example.com'
    assert manager.config['smtp_port'] == 587
    
    # Test avec fichier inexistant
    manager = NotificationManager(config_file='nonexistent.json')
    assert manager.config == {}

def test_send_email(notification_manager):
    """Teste l'envoi de notification par email."""
    with patch('smtplib.SMTP') as mock_smtp:
        # Configurer le mock
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Envoyer une notification
        notification_manager.send_notification(
            subject="Test Subject",
            message="Test Message"
        )
        
        # Vérifier que le serveur SMTP a été appelé correctement
        mock_smtp.assert_called_once_with('smtp.example.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'password')
        mock_server.send_message.assert_called_once()

def test_send_slack(temp_config_file):
    """Teste l'envoi de notification Slack."""
    manager = NotificationManager(
        notification_type='slack',
        config_file=temp_config_file
    )
    
    with patch('requests.post') as mock_post:
        # Configurer le mock
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Envoyer une notification
        manager.send_notification(
            subject="Test Subject",
            message="Test Message"
        )
        
        # Vérifier que la requête a été envoyée correctement
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['text'] == "*Test Subject*\nTest Message"

def test_send_webhook(temp_config_file):
    """Teste l'envoi de notification webhook."""
    manager = NotificationManager(
        notification_type='webhook',
        config_file=temp_config_file
    )
    
    with patch('requests.post') as mock_post:
        # Configurer le mock
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Envoyer une notification
        manager.send_notification(
            subject="Test Subject",
            message="Test Message",
            extra_data="test"
        )
        
        # Vérifier que la requête a été envoyée correctement
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['subject'] == "Test Subject"
        assert kwargs['json']['message'] == "Test Message"
        assert kwargs['json']['extra_data'] == "test"

def test_invalid_notification_type():
    """Teste la gestion d'un type de notification invalide."""
    manager = NotificationManager(notification_type='invalid')
    
    with pytest.raises(Exception):
        manager.send_notification(
            subject="Test Subject",
            message="Test Message"
        )

def test_missing_config():
    """Teste la gestion d'une configuration manquante."""
    manager = NotificationManager()
    
    with pytest.raises(ValueError):
        manager.send_notification(
            subject="Test Subject",
            message="Test Message"
        )

def test_invalid_config_file(tmp_path):
    """Teste la gestion d'un fichier de configuration invalide."""
    invalid_config = tmp_path / "invalid_config.json"
    with open(invalid_config, 'w') as f:
        f.write("invalid json")
    
    manager = NotificationManager(config_file=str(invalid_config))
    assert manager.config == {} 