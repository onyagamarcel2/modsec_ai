"""
Tests unitaires pour l'interface graphique du tableau de bord.
"""

import pytest
from PyQt5.QtWidgets import QApplication
from src.gui.dashboard import Dashboard

@pytest.fixture
def app():
    """Crée une instance de QApplication pour les tests."""
    return QApplication([])

@pytest.fixture
def dashboard(app):
    """Crée une instance de Dashboard pour les tests."""
    return Dashboard()

def test_dashboard_initialization(dashboard):
    """Test l'initialisation du tableau de bord."""
    assert dashboard is not None
    assert dashboard.windowTitle() == "ModSec AI Dashboard"

def test_dashboard_components(dashboard):
    """Test la présence des composants du tableau de bord."""
    assert dashboard.centralWidget() is not None
    assert dashboard.statusBar() is not None
    assert dashboard.rules_gui is not None
    assert dashboard.validation_gui is not None
    assert dashboard.anomaly_gui is not None 