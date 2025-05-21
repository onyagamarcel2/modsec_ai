"""
Interface graphique pour la gestion des règles ModSecurity.
"""

import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QTextEdit,
    QComboBox, QMessageBox, QSplitter, QTabWidget, QLineEdit,
    QDialog, QFormLayout, QDialogButtonBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

from src.modsec.rule_manager import ModSecRuleManager, ModSecRule, RuleStatus

logger = logging.getLogger(__name__)

class RuleDialog(QDialog):
    """Dialogue pour créer/modifier une règle."""
    
    def __init__(
        self,
        parent: QWidget,
        rule: Optional[ModSecRule] = None,
        title: str = "Nouvelle règle"
    ):
        """
        Initialise le dialogue.

        Args:
            parent: Widget parent
            rule: Règle existante à modifier
            title: Titre du dialogue
        """
        super().__init__(parent)
        
        self.rule = rule
        self.setWindowTitle(title)
        self.setModal(True)
        
        # Créer l'interface
        self._create_ui()
        
        # Remplir les champs si modification
        if rule:
            self._fill_fields()
            
    def _create_ui(self):
        """Crée l'interface utilisateur."""
        layout = QFormLayout(self)
        
        # Nom
        self.name_edit = QLineEdit()
        layout.addRow("Nom:", self.name_edit)
        
        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        layout.addRow("Description:", self.desc_edit)
        
        # Contenu
        self.content_edit = QTextEdit()
        layout.addRow("Contenu:", self.content_edit)
        
        # Statut
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            status.value for status in RuleStatus
        ])
        layout.addRow("Statut:", self.status_combo)
        
        # Tags
        self.tags_list = QListWidget()
        self.tags_list.setMaximumHeight(100)
        layout.addRow("Tags:", self.tags_list)
        
        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
    def _fill_fields(self):
        """Remplit les champs avec les données de la règle."""
        self.name_edit.setText(self.rule.name)
        self.desc_edit.setText(self.rule.description)
        self.content_edit.setText(self.rule.content)
        self.status_combo.setCurrentText(self.rule.status.value)
        
        # Ajouter les tags
        for tag in self.rule.tags:
            self.tags_list.addItem(tag)
            
    def get_rule_data(self) -> Dict:
        """
        Récupère les données du formulaire.

        Returns:
            Dictionnaire des données
        """
        return {
            'name': self.name_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'content': self.content_edit.toPlainText(),
            'status': RuleStatus(self.status_combo.currentText()),
            'tags': [
                self.tags_list.item(i).text()
                for i in range(self.tags_list.count())
            ]
        }

class ModSecRulesGUI(QMainWindow):
    """Interface graphique pour la gestion des règles ModSecurity."""
    
    def __init__(
        self,
        rule_manager: ModSecRuleManager,
        refresh_interval: int = 5000
    ):
        """
        Initialise l'interface graphique.

        Args:
            rule_manager: Gestionnaire de règles
            refresh_interval: Intervalle de rafraîchissement en ms
        """
        super().__init__()
        
        self.rule_manager = rule_manager
        self.refresh_interval = refresh_interval
        
        # Configuration de la fenêtre
        self.setWindowTitle("Gestion des Règles ModSecurity")
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
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        
        # Bouton nouvelle règle
        new_rule_btn = QPushButton("Nouvelle règle")
        new_rule_btn.clicked.connect(self.create_rule)
        toolbar.addWidget(new_rule_btn)
        
        # Bouton sauvegarde
        backup_btn = QPushButton("Sauvegarder")
        backup_btn.clicked.connect(self.backup_rules)
        toolbar.addWidget(backup_btn)
        
        # Bouton restauration
        restore_btn = QPushButton("Restaurer")
        restore_btn.clicked.connect(self.restore_backup)
        toolbar.addWidget(restore_btn)
        
        # Recherche
        toolbar.addWidget(QLabel("Rechercher:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.refresh_data)
        toolbar.addWidget(self.search_edit)
        
        # Filtre par statut
        toolbar.addWidget(QLabel("Statut:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Tous"] + [
            status.value for status in RuleStatus
        ])
        self.status_combo.currentTextChanged.connect(self.refresh_data)
        toolbar.addWidget(self.status_combo)
        
        toolbar.addStretch()
        main_layout.addLayout(toolbar)
        
        # Table des règles
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(7)
        self.rules_table.setHorizontalHeaderLabels([
            "ID", "Nom", "Description", "Statut", "Créé par",
            "Date création", "Actions"
        ])
        main_layout.addWidget(self.rules_table)
        
        # Zone de détails
        details_group = QWidget()
        details_layout = QVBoxLayout(details_group)
        
        # Contenu de la règle
        details_layout.addWidget(QLabel("Contenu de la règle:"))
        self.rule_content = QTextEdit()
        self.rule_content.setReadOnly(True)
        details_layout.addWidget(self.rule_content)
        
        # Tags
        details_layout.addWidget(QLabel("Tags:"))
        self.tags_list = QListWidget()
        details_layout.addWidget(self.tags_list)
        
        main_layout.addWidget(details_group)
        
    def refresh_data(self):
        """Rafraîchit les données affichées."""
        try:
            # Récupérer les filtres
            status = self.status_combo.currentText()
            if status == "Tous":
                status = None
            else:
                status = RuleStatus(status)
                
            search = self.search_edit.text()
            
            # Récupérer les règles
            rules = self.rule_manager.get_rules(
                status=status,
                search=search
            )
            
            # Mettre à jour la table
            self.rules_table.setRowCount(len(rules))
            for i, rule in enumerate(rules):
                self.rules_table.setItem(i, 0, QTableWidgetItem(rule.rule_id))
                self.rules_table.setItem(i, 1, QTableWidgetItem(rule.name))
                self.rules_table.setItem(i, 2, QTableWidgetItem(rule.description))
                self.rules_table.setItem(i, 3, QTableWidgetItem(rule.status.value))
                self.rules_table.setItem(i, 4, QTableWidgetItem(rule.created_by))
                self.rules_table.setItem(i, 5, QTableWidgetItem(
                    rule.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                # Boutons d'action
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("Modifier")
                edit_btn.clicked.connect(
                    lambda checked, r=rule: self.edit_rule(r)
                )
                actions_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("Supprimer")
                delete_btn.clicked.connect(
                    lambda checked, r=rule: self.delete_rule(r)
                )
                actions_layout.addWidget(delete_btn)
                
                self.rules_table.setCellWidget(i, 6, actions_widget)
                
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement des règles: {str(e)}")
            QMessageBox.critical(self, "Erreur", str(e))
            
    def create_rule(self):
        """Crée une nouvelle règle."""
        dialog = RuleDialog(self, title="Nouvelle règle")
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_rule_data()
                self.rule_manager.create_rule(
                    name=data['name'],
                    description=data['description'],
                    content=data['content'],
                    created_by="user",  # TODO: Récupérer l'utilisateur actuel
                    tags=data['tags'],
                    status=data['status']
                )
                self.refresh_data()
                
            except Exception as e:
                logger.error(f"Erreur lors de la création de la règle: {str(e)}")
                QMessageBox.critical(self, "Erreur", str(e))
                
    def edit_rule(self, rule: ModSecRule):
        """
        Modifie une règle existante.

        Args:
            rule: Règle à modifier
        """
        dialog = RuleDialog(self, rule=rule, title="Modifier la règle")
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_rule_data()
                self.rule_manager.update_rule(
                    rule_id=rule.rule_id,
                    name=data['name'],
                    description=data['description'],
                    content=data['content'],
                    status=data['status'],
                    updated_by="user",  # TODO: Récupérer l'utilisateur actuel
                    tags=data['tags']
                )
                self.refresh_data()
                
            except Exception as e:
                logger.error(f"Erreur lors de la modification de la règle: {str(e)}")
                QMessageBox.critical(self, "Erreur", str(e))
                
    def delete_rule(self, rule: ModSecRule):
        """
        Supprime une règle.

        Args:
            rule: Règle à supprimer
        """
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer la règle {rule.name} ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.rule_manager.delete_rule(rule.rule_id)
                self.refresh_data()
                
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de la règle: {str(e)}")
                QMessageBox.critical(self, "Erreur", str(e))
                
    def backup_rules(self):
        """Crée une sauvegarde des règles."""
        try:
            backup_file = self.rule_manager.backup_rules()
            QMessageBox.information(
                self,
                "Succès",
                f"Sauvegarde créée: {backup_file}"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {str(e)}")
            QMessageBox.critical(self, "Erreur", str(e))
            
    def restore_backup(self):
        """Restaure une sauvegarde."""
        # TODO: Ajouter un dialogue pour sélectionner le fichier de sauvegarde
        pass

def main():
    """Fonction principale."""
    # Créer l'application
    app = QApplication(sys.argv)
    
    # Créer le gestionnaire de règles
    rule_manager = ModSecRuleManager(
        rules_dir="config/modsec/rules",
        custom_rules_file="custom_rules.conf"
    )
    
    # Créer et afficher la fenêtre
    window = ModSecRulesGUI(rule_manager)
    window.show()
    
    # Lancer l'application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 