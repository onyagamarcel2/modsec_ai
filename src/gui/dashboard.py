from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QStatusBar
)
from PyQt5.QtCore import Qt
from .modsec_rules_gui import RulesGUI
from .validation_gui import ValidationGUI

class Dashboard(QMainWindow):
    """Tableau de bord principal de l'application."""
    
    def __init__(self):
        """Initialise le tableau de bord."""
        super().__init__()
        self.setWindowTitle("ModSec AI Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Créer le widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Créer le layout principal
        layout = QVBoxLayout(central_widget)
        
        # Créer l'en-tête
        header = QHBoxLayout()
        title = QLabel("ModSec AI Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        
        # Ajouter l'en-tête au layout principal
        layout.addLayout(header)
        
        # Créer les onglets
        tabs = QTabWidget()
        
        # Onglet des règles
        self.rules_gui = RulesGUI()
        tabs.addTab(self.rules_gui, "Règles")
        
        # Onglet de validation
        self.validation_gui = ValidationGUI()
        tabs.addTab(self.validation_gui, "Validation")
        
        # Onglet des anomalies
        self.anomaly_gui = QWidget()
        anomaly_layout = QVBoxLayout(self.anomaly_gui)
        anomaly_layout.addWidget(QLabel("Interface des anomalies à venir..."))
        tabs.addTab(self.anomaly_gui, "Anomalies")
        
        # Ajouter les onglets au layout principal
        layout.addWidget(tabs)
        
        # Créer la barre de statut
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt")
        
    def show_status(self, message: str, timeout: int = 0):
        """
        Affiche un message dans la barre de statut.
        
        Args:
            message: Message à afficher
            timeout: Durée d'affichage en millisecondes (0 = permanent)
        """
        self.statusBar.showMessage(message, timeout) 