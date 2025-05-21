"""
Tests unitaires pour l'interface graphique de gestion des règles ModSecurity (ModSecRulesGUI).
"""
import pytest
from PyQt5.QtWidgets import QApplication, QPushButton, QDialogButtonBox
from src.gui.modsec_rules_gui import ModSecRulesGUI
from src.modsec.rule_manager import ModSecRuleManager
import sys
import os

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def rule_manager(tmp_path):
    # Utiliser un dossier temporaire pour les règles
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    return ModSecRuleManager(str(rules_dir))

@pytest.fixture
def gui(rule_manager, app):
    return ModSecRulesGUI(rule_manager)

def test_gui_initialization(gui):
    assert gui is not None
    assert gui.windowTitle() == "Gestion des Règles ModSecurity"
    assert gui.rules_table.rowCount() == 0

def test_create_rule_via_dialog(gui, qtbot):
    # Simuler l'ouverture du dialogue de création
    qtbot.mouseClick(gui.findChild(QPushButton, "Nouvelle règle"), 1)
    dialog = gui.findChild(RuleDialog)
    assert dialog is not None
    # Remplir les champs du dialogue
    dialog.name_edit.setText("Test Rule")
    dialog.desc_edit.setText("Description test")
    dialog.content_edit.setPlainText("SecRule REQUEST_URI '@rx /test' 'id:1001,phase:1,deny'\n")
    dialog.status_combo.setCurrentIndex(0)  # ACTIVE
    # Valider
    qtbot.mouseClick(dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok), 1)
    # Vérifier que la règle a été ajoutée
    assert gui.rules_table.rowCount() == 1
    assert "Test Rule" in gui.rules_table.item(0, 1).text()

def test_invalid_rule_creation(gui, qtbot):
    qtbot.mouseClick(gui.findChild(QPushButton, "Nouvelle règle"), 1)
    dialog = gui.findChild(RuleDialog)
    assert dialog is not None
    # Laisser le nom vide
    dialog.name_edit.setText("")
    dialog.content_edit.setPlainText("")
    qtbot.mouseClick(dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok), 1)
    # La règle ne doit pas être ajoutée
    assert gui.rules_table.rowCount() == 0

def test_delete_rule(gui, qtbot):
    # Créer une règle valide
    qtbot.mouseClick(gui.findChild(QPushButton, "Nouvelle règle"), 1)
    dialog = gui.findChild(RuleDialog)
    dialog.name_edit.setText("ToDelete")
    dialog.content_edit.setPlainText("SecRule REQUEST_URI '@rx /del' 'id:1002,phase:1,deny'\n")
    qtbot.mouseClick(dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok), 1)
    assert gui.rules_table.rowCount() == 1
    # Sélectionner la règle et supprimer
    gui.rules_table.selectRow(0)
    qtbot.mouseClick(gui.findChild(QPushButton, "Supprimer"), 1)
    assert gui.rules_table.rowCount() == 0 