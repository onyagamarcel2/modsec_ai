"""
Tests unitaires pour l'interface graphique.
"""

import os
import pytest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from src.gui.modsec_rules_gui import ModSecRulesGUI
from src.gui.validation_gui import ValidationGUI
from src.modsec.rule_manager import ModSecRuleManager, RuleStatus
from src.validation.anomaly_validator import AnomalyValidator, ValidationStatus

@pytest.fixture
def app():
    """Crée une instance de QApplication pour les tests."""
    return QApplication([])

@pytest.fixture
def temp_dirs(tmp_path):
    """Crée des répertoires temporaires pour les tests."""
    validations_dir = tmp_path / "validations"
    rules_dir = tmp_path / "rules"
    validations_dir.mkdir()
    rules_dir.mkdir()
    return validations_dir, rules_dir

@pytest.fixture
def components(temp_dirs):
    """Initialise les composants pour les tests."""
    validations_dir, rules_dir = temp_dirs
    rule_manager = ModSecRuleManager(
        rules_dir=str(rules_dir),
        custom_rules_file="custom_rules.conf"
    )
    validator = AnomalyValidator(
        validations_dir=str(validations_dir),
        rule_manager=rule_manager
    )
    return rule_manager, validator

def test_rules_gui_initialization(app, components):
    """Test l'initialisation de l'interface de règles."""
    rule_manager, _ = components
    gui = ModSecRulesGUI(rule_manager)
    
    # Vérifier que l'interface est créée
    assert gui is not None
    assert gui.rule_manager == rule_manager
    
    # Vérifier les composants de base
    assert gui.table is not None
    assert gui.detail_area is not None
    assert gui.toolbar is not None

def test_rules_gui_create_rule(app, components):
    """Test la création d'une règle via l'interface."""
    rule_manager, _ = components
    gui = ModSecRulesGUI(rule_manager)
    
    # Simuler le clic sur le bouton de création
    QTest.mouseClick(gui.toolbar.actions()[0].trigger(), Qt.LeftButton)
    
    # Vérifier que la boîte de dialogue est ouverte
    dialog = gui.findChild(QDialog)
    assert dialog is not None
    
    # Remplir le formulaire
    dialog.name_edit.setText("Test Rule")
    dialog.description_edit.setText("Test Description")
    dialog.content_edit.setText("REQUEST_HEADERS:User-Agent")
    dialog.status_combo.setCurrentText("ACTIVE")
    
    # Accepter le dialogue
    dialog.accept()
    
    # Vérifier que la règle a été créée
    rules = rule_manager.get_rules()
    assert len(rules) == 1
    assert rules[0].name == "Test Rule"

def test_rules_gui_filter_rules(app, components):
    """Test le filtrage des règles dans l'interface."""
    rule_manager, _ = components
    
    # Créer quelques règles
    rule_manager.create_rule(
        name="Active Rule",
        description="Test active rule",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user",
        status=RuleStatus.ACTIVE
    )
    
    rule_manager.create_rule(
        name="Inactive Rule",
        description="Test inactive rule",
        content="REQUEST_HEADERS:Referer",
        created_by="test_user",
        status=RuleStatus.INACTIVE
    )
    
    gui = ModSecRulesGUI(rule_manager)
    
    # Tester le filtrage par statut
    gui.status_filter.setCurrentText("ACTIVE")
    assert gui.table.rowCount() == 1
    assert gui.table.item(0, 0).text() == "Active Rule"
    
    # Tester la recherche
    gui.search_edit.setText("Inactive")
    assert gui.table.rowCount() == 1
    assert gui.table.item(0, 0).text() == "Inactive Rule"

def test_validation_gui_initialization(app, components):
    """Test l'initialisation de l'interface de validation."""
    _, validator = components
    gui = ValidationGUI(validator)
    
    # Vérifier que l'interface est créée
    assert gui is not None
    assert gui.validator == validator
    
    # Vérifier les composants de base
    assert gui.pending_table is not None
    assert gui.history_table is not None
    assert gui.detail_area is not None

def test_validation_gui_create_validation(app, components):
    """Test la création d'une validation via l'interface."""
    _, validator = components
    gui = ValidationGUI(validator)
    
    # Créer une validation
    validation = validator.create_validation(
        anomaly_id="test_anomaly_1",
        log_sequence=["log1", "log2"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    # Vérifier que la validation apparaît dans la table
    assert gui.pending_table.rowCount() == 1
    assert gui.pending_table.item(0, 0).text() == validation.anomaly_id

def test_validation_gui_validate_anomaly(app, components):
    """Test la validation d'une anomalie via l'interface."""
    _, validator = components
    gui = ValidationGUI(validator)
    
    # Créer une validation
    validation = validator.create_validation(
        anomaly_id="test_anomaly_2",
        log_sequence=["log1", "log2"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    # Sélectionner la validation
    gui.pending_table.selectRow(0)
    
    # Changer le statut
    gui.status_combo.setCurrentText("VALIDATED")
    gui.notes_edit.setText("Test validation")
    
    # Valider
    QTest.mouseClick(gui.validate_button, Qt.LeftButton)
    
    # Vérifier que la validation a été mise à jour
    updated_validation = validator.get_validation(validation.anomaly_id)
    assert updated_validation.validation_status == ValidationStatus.VALIDATED
    assert updated_validation.validation_notes == "Test validation"

def test_validation_gui_filter_history(app, components):
    """Test le filtrage de l'historique dans l'interface."""
    _, validator = components
    gui = ValidationGUI(validator)
    
    # Créer et valider des anomalies
    validator.create_validation(
        anomaly_id="test_anomaly_3",
        log_sequence=["log1"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    validator.create_validation(
        anomaly_id="test_anomaly_4",
        log_sequence=["log2"],
        anomaly_score=0.85,
        detection_model="test_model"
    )
    
    validator.validate_anomaly(
        anomaly_id="test_anomaly_3",
        status=ValidationStatus.VALIDATED,
        validated_by="user1"
    )
    
    validator.validate_anomaly(
        anomaly_id="test_anomaly_4",
        status=ValidationStatus.NORMAL,
        validated_by="user2"
    )
    
    # Tester le filtrage par statut
    gui.history_status_filter.setCurrentText("VALIDATED")
    assert gui.history_table.rowCount() == 1
    assert gui.history_table.item(0, 0).text() == "test_anomaly_3"
    
    # Tester le filtrage par utilisateur
    gui.history_user_filter.setCurrentText("user2")
    assert gui.history_table.rowCount() == 1
    assert gui.history_table.item(0, 0).text() == "test_anomaly_4"

def test_gui_error_handling(app, components):
    """Test la gestion des erreurs dans l'interface."""
    rule_manager, validator = components
    rules_gui = ModSecRulesGUI(rule_manager)
    validation_gui = ValidationGUI(validator)
    
    # Tester la création d'une règle invalide
    QTest.mouseClick(rules_gui.toolbar.actions()[0].trigger(), Qt.LeftButton)
    dialog = rules_gui.findChild(QDialog)
    dialog.name_edit.setText("")  # Nom vide
    dialog.accept()
    
    # Vérifier que le message d'erreur est affiché
    assert rules_gui.statusBar().currentMessage() != ""
    
    # Tester la validation d'une anomalie inexistante
    validation_gui.pending_table.selectRow(0)
    QTest.mouseClick(validation_gui.validate_button, Qt.LeftButton)
    
    # Vérifier que le message d'erreur est affiché
    assert validation_gui.statusBar().currentMessage() != "" 