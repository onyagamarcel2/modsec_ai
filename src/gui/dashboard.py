"""
Interface graphique principale du dashboard.
"""

import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer

from .modsec_rules_gui import ModSecRulesGUI
from src.modsec.rule_manager import ModSecRuleManager

logger = logging.getLogger(__name__)

class Dashboard(QMainWindow):
    """Interface graphique principale."""
    
    def __init__(self, rule_manager: ModSecRuleManager):
        """Initialise le dashboard."""
        super().__init__()
        
        self.rule_manager = rule_manager
        
        # Configuration de la fenêtre
        self.setWindowTitle("ModSec AI Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Créer l'interface
        self._create_ui()
        
    def _create_ui(self):
        """Crée l'interface utilisateur."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet règles
        rules_tab = ModSecRulesGUI(self.rule_manager)
        tabs.addTab(rules_tab, "Règles")
        
        # Onglet statistiques
        stats_tab = QWidget()
        tabs.addTab(stats_tab, "Statistiques")
        
        # Onglet alertes
        alerts_tab = QWidget()
        tabs.addTab(alerts_tab, "Alertes")
        
        main_layout.addWidget(tabs)
        
def main():
    """Point d'entrée de l'application."""
    app = QApplication(sys.argv)
    
    # Créer le gestionnaire de règles
    rule_manager = ModSecRuleManager()
    
    # Créer et afficher le dashboard
    dashboard = Dashboard(rule_manager)
    dashboard.show()
    
    sys.exit(app.exec_()) 