"""
Interface graphique pour la validation des anomalies.
"""

import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QTextEdit,
    QComboBox, QMessageBox, QSplitter, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

from src.validation.anomaly_validator import AnomalyValidator, ValidationStatus, AnomalyValidation

logger = logging.getLogger(__name__)

class ValidationGUI(QMainWindow):
    """Interface graphique pour la validation des anomalies."""
    
    def __init__(
        self,
        validator: AnomalyValidator,
        refresh_interval: int = 5000
    ):
        """
        Initialise l'interface graphique.

        Args:
            validator: Instance du validateur d'anomalies
            refresh_interval: Intervalle de rafraîchissement en ms
        """
        super().__init__()
        
        self.validator = validator
        self.refresh_interval = refresh_interval
        
        # Configuration de la fenêtre
        self.setWindowTitle("Validation des Anomalies")
        self.setGeometry(100, 100, 1200, 800)
        
        # Créer l'interface
        self._create_ui()
        
        # Timer pour le rafraîchissement automatique
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(refresh_interval)
        
        # Charger les données initiales
        self.refresh_data()
        
    def _create_ui(self):
        """Crée l'interface utilisateur."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Créer les onglets
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Onglet des validations en attente
        pending_tab = QWidget()
        tabs.addTab(pending_tab, "Validations en Attente")
        
        # Onglet de l'historique
        history_tab = QWidget()
        tabs.addTab(history_tab, "Historique")
        
        # Configuration de l'onglet des validations en attente
        self._setup_pending_tab(pending_tab)
        
        # Configuration de l'onglet de l'historique
        self._setup_history_tab(history_tab)
        
    def _setup_pending_tab(self, tab: QWidget):
        """
        Configure l'onglet des validations en attente.

        Args:
            tab: Widget de l'onglet
        """
        layout = QVBoxLayout(tab)
        
        # Table des validations en attente
        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(7)
        self.pending_table.setHorizontalHeaderLabels([
            "ID", "Horodatage", "Score", "Modèle", "Statut",
            "Actions", "Détails"
        ])
        layout.addWidget(self.pending_table)
        
        # Zone de détails
        details_layout = QHBoxLayout()
        
        # Logs
        logs_group = QWidget()
        logs_layout = QVBoxLayout(logs_group)
        logs_layout.addWidget(QLabel("Logs"))
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        logs_layout.addWidget(self.logs_text)
        
        # Actions
        actions_group = QWidget()
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.addWidget(QLabel("Actions"))
        
        # Statut
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Nouveau statut:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            status.value for status in ValidationStatus
        ])
        status_layout.addWidget(self.status_combo)
        actions_layout.addLayout(status_layout)
        
        # Notes
        actions_layout.addWidget(QLabel("Notes:"))
        self.notes_text = QTextEdit()
        actions_layout.addWidget(self.notes_text)
        
        # Bouton de validation
        self.validate_button = QPushButton("Valider")
        self.validate_button.clicked.connect(self.validate_selected)
        actions_layout.addWidget(self.validate_button)
        
        # Ajouter les groupes au layout
        details_layout.addWidget(logs_group, 2)
        details_layout.addWidget(actions_group, 1)
        layout.addLayout(details_layout)
        
    def _setup_history_tab(self, tab: QWidget):
        """
        Configure l'onglet de l'historique.

        Args:
            tab: Widget de l'onglet
        """
        layout = QVBoxLayout(tab)
        
        # Filtres
        filters_layout = QHBoxLayout()
        
        # Filtre par statut
        filters_layout.addWidget(QLabel("Statut:"))
        self.history_status_combo = QComboBox()
        self.history_status_combo.addItems(["Tous"] + [
            status.value for status in ValidationStatus
        ])
        self.history_status_combo.currentTextChanged.connect(self.refresh_history)
        filters_layout.addWidget(self.history_status_combo)
        
        # Bouton de rafraîchissement
        refresh_button = QPushButton("Rafraîchir")
        refresh_button.clicked.connect(self.refresh_history)
        filters_layout.addWidget(refresh_button)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        # Table de l'historique
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Horodatage", "Score", "Modèle", "Statut",
            "Validé par", "Date validation", "Notes"
        ])
        layout.addWidget(self.history_table)
        
    def refresh_data(self):
        """Rafraîchit les données affichées."""
        self.refresh_pending()
        self.refresh_history()
        
    def refresh_pending(self):
        """Rafraîchit la liste des validations en attente."""
        try:
            # Récupérer les validations en attente
            pending = self.validator.get_pending_validations()
            
            # Mettre à jour la table
            self.pending_table.setRowCount(len(pending))
            for i, validation in enumerate(pending):
                self.pending_table.setItem(i, 0, QTableWidgetItem(validation.anomaly_id))
                self.pending_table.setItem(i, 1, QTableWidgetItem(
                    validation.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                ))
                self.pending_table.setItem(i, 2, QTableWidgetItem(
                    f"{validation.anomaly_score:.3f}"
                ))
                self.pending_table.setItem(i, 3, QTableWidgetItem(validation.detection_model))
                self.pending_table.setItem(i, 4, QTableWidgetItem(
                    validation.validation_status.value
                ))
                
                # Boutons d'action
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                view_button = QPushButton("Voir")
                view_button.clicked.connect(
                    lambda checked, v=validation: self.view_validation(v)
                )
                actions_layout.addWidget(view_button)
                
                self.pending_table.setCellWidget(i, 5, actions_widget)
                
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement des validations en attente: {str(e)}")
            QMessageBox.critical(self, "Erreur", str(e))
            
    def refresh_history(self):
        """Rafraîchit l'historique des validations."""
        try:
            # Récupérer le statut sélectionné
            status = self.history_status_combo.currentText()
            if status == "Tous":
                status = None
            else:
                status = ValidationStatus(status)
                
            # Récupérer l'historique
            history = self.validator.get_validation_history(status=status)
            
            # Mettre à jour la table
            self.history_table.setRowCount(len(history))
            for i, validation in enumerate(history):
                self.history_table.setItem(i, 0, QTableWidgetItem(validation.anomaly_id))
                self.history_table.setItem(i, 1, QTableWidgetItem(
                    validation.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                ))
                self.history_table.setItem(i, 2, QTableWidgetItem(
                    f"{validation.anomaly_score:.3f}"
                ))
                self.history_table.setItem(i, 3, QTableWidgetItem(validation.detection_model))
                self.history_table.setItem(i, 4, QTableWidgetItem(
                    validation.validation_status.value
                ))
                self.history_table.setItem(i, 5, QTableWidgetItem(
                    validation.validated_by or ""
                ))
                self.history_table.setItem(i, 6, QTableWidgetItem(
                    validation.validation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    if validation.validation_timestamp else ""
                ))
                self.history_table.setItem(i, 7, QTableWidgetItem(
                    validation.validation_notes or ""
                ))
                
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement de l'historique: {str(e)}")
            QMessageBox.critical(self, "Erreur", str(e))
            
    def view_validation(self, validation: AnomalyValidation):
        """
        Affiche les détails d'une validation.

        Args:
            validation: La validation à afficher
        """
        # Afficher les logs
        self.logs_text.clear()
        for log in validation.log_sequence:
            self.logs_text.append(json.dumps(log, indent=2))
            
        # Sélectionner la ligne dans la table
        for i in range(self.pending_table.rowCount()):
            if self.pending_table.item(i, 0).text() == validation.anomaly_id:
                self.pending_table.selectRow(i)
                break
                
    def validate_selected(self):
        """Valide la validation sélectionnée."""
        try:
            # Récupérer la ligne sélectionnée
            selected_rows = self.pending_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Attention", "Aucune validation sélectionnée")
                return
                
            # Récupérer l'ID de la validation
            row = selected_rows[0].row()
            anomaly_id = self.pending_table.item(row, 0).text()
            
            # Récupérer le nouveau statut et les notes
            new_status = ValidationStatus(self.status_combo.currentText())
            notes = self.notes_text.toPlainText()
            
            # Valider l'anomalie
            self.validator.validate_anomaly(
                anomaly_id=anomaly_id,
                status=new_status,
                validated_by="user",  # TODO: Récupérer l'utilisateur actuel
                notes=notes
            )
            
            # Rafraîchir les données
            self.refresh_data()
            
            # Réinitialiser les champs
            self.notes_text.clear()
            
            QMessageBox.information(
                self,
                "Succès",
                f"Validation mise à jour avec le statut: {new_status.value}"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation: {str(e)}")
            QMessageBox.critical(self, "Erreur", str(e))

def main():
    """Fonction principale."""
    # Créer l'application
    app = QApplication(sys.argv)
    
    # Créer le validateur
    validator = AnomalyValidator(
        validation_dir="data/validations",
        modsec_rules_dir="config/modsec/rules"
    )
    
    # Créer et afficher la fenêtre
    window = ValidationGUI(validator)
    window.show()
    
    # Lancer l'application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 