"""
Tests d'intégration pour vérifier les interactions entre les composants.
"""

import os
import pytest
from datetime import datetime
from src.modsec.rule_manager import ModSecRuleManager, RuleStatus
from src.validation.anomaly_validator import AnomalyValidator, ValidationStatus
from src.models.anomaly_detector import AnomalyDetector
from src.gui.modsec_rules_gui import ModSecRulesGUI
from PyQt5.QtWidgets import QApplication
import sys

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
    detector = AnomalyDetector()
    return rule_manager, validator, detector

def test_anomaly_to_rule_workflow(components):
    """
    Test le workflow complet de création d'une règle à partir d'une anomalie.
    """
    rule_manager, validator, _ = components
    
    # 1. Créer une validation d'anomalie
    validation = validator.create_validation(
        anomaly_id="test_anomaly_1",
        log_sequence=[
            "GET /admin HTTP/1.1",
            "User-Agent: sqlmap/1.4.12"
        ],
        anomaly_score=0.95,
        detection_model="test_model",
        create_rule=True
    )
    
    # 2. Vérifier que la règle a été créée
    rule = rule_manager.get_rule(validation.modsec_rule_id)
    assert rule is not None
    assert rule.status == RuleStatus.ACTIVE
    
    # 3. Valider l'anomalie
    validator.validate_anomaly(
        anomaly_id=validation.anomaly_id,
        status=ValidationStatus.VALIDATED,
        validated_by="test_user",
        notes="Confirmed SQL injection attempt"
    )
    
    # 4. Vérifier que la règle est toujours active
    rule = rule_manager.get_rule(validation.modsec_rule_id)
    assert rule.status == RuleStatus.ACTIVE
    
    # 5. Marquer l'anomalie comme normale
    validator.validate_anomaly(
        anomaly_id=validation.anomaly_id,
        status=ValidationStatus.NORMAL,
        validated_by="test_user",
        notes="False positive"
    )
    
    # 6. Vérifier que la règle a été supprimée
    with pytest.raises(ValueError):
        rule_manager.get_rule(validation.modsec_rule_id)

def test_rule_management_workflow(components):
    """
    Test le workflow de gestion des règles.
    """
    rule_manager, validator, _ = components
    
    # 1. Créer plusieurs règles
    rule1 = rule_manager.create_rule(
        name="Test Rule 1",
        description="First test rule",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user",
        tags=["test"]
    )
    
    rule2 = rule_manager.create_rule(
        name="Test Rule 2",
        description="Second test rule",
        content="REQUEST_HEADERS:Referer",
        created_by="test_user",
        tags=["test"]
    )
    
    # 2. Vérifier que les règles sont actives
    assert rule1.status == RuleStatus.ACTIVE
    assert rule2.status == RuleStatus.ACTIVE
    
    # 3. Désactiver une règle
    rule_manager.update_rule(
        rule_id=rule1.rule_id,
        status=RuleStatus.INACTIVE,
        updated_by="test_user"
    )
    
    # 4. Vérifier le statut
    updated_rule = rule_manager.get_rule(rule1.rule_id)
    assert updated_rule.status == RuleStatus.INACTIVE
    
    # 5. Vérifier le filtrage
    active_rules = rule_manager.get_rules(status=RuleStatus.ACTIVE)
    assert len(active_rules) == 1
    assert active_rules[0].rule_id == rule2.rule_id

def test_backup_and_restore_workflow(components):
    """
    Test le workflow de sauvegarde et restauration.
    """
    rule_manager, validator, _ = components
    
    # 1. Créer des règles
    rule1 = rule_manager.create_rule(
        name="Backup Rule 1",
        description="First backup rule",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user"
    )
    
    rule2 = rule_manager.create_rule(
        name="Backup Rule 2",
        description="Second backup rule",
        content="REQUEST_HEADERS:Referer",
        created_by="test_user"
    )
    
    # 2. Créer une sauvegarde
    backup_file = rule_manager.backup_rules()
    assert os.path.exists(backup_file)
    
    # 3. Supprimer les règles
    rule_manager.delete_rule(rule1.rule_id)
    rule_manager.delete_rule(rule2.rule_id)
    
    # 4. Restaurer la sauvegarde
    rule_manager.restore_backup(backup_file)
    
    # 5. Vérifier que les règles sont restaurées
    restored_rule1 = rule_manager.get_rule(rule1.rule_id)
    restored_rule2 = rule_manager.get_rule(rule2.rule_id)
    
    assert restored_rule1.name == rule1.name
    assert restored_rule2.name == rule2.name

@pytest.mark.gui
def test_gui_integration(components):
    """
    Test l'intégration avec l'interface graphique.
    """
    # Créer l'application Qt
    app = QApplication(sys.argv)
    
    rule_manager, validator, _ = components
    
    # Créer l'interface
    gui = ModSecRulesGUI(rule_manager)
    
    # Vérifier que l'interface est créée
    assert gui is not None
    assert gui.rule_manager == rule_manager
    
    # Nettoyer
    app.quit()

def test_validation_workflow(components):
    """
    Test le workflow complet de validation.
    """
    rule_manager, validator, _ = components
    
    # 1. Créer une validation
    validation = validator.create_validation(
        anomaly_id="test_anomaly_2",
        log_sequence=[
            "POST /login HTTP/1.1",
            "Content-Type: application/x-www-form-urlencoded",
            "username=admin&password=admin"
        ],
        anomaly_score=0.85,
        detection_model="test_model",
        create_rule=True
    )
    
    # 2. Vérifier les validations en attente
    pending = validator.get_pending_validations()
    assert len(pending) == 1
    assert pending[0].anomaly_id == validation.anomaly_id
    
    # 3. Valider l'anomalie
    validator.validate_anomaly(
        anomaly_id=validation.anomaly_id,
        status=ValidationStatus.VALIDATED,
        validated_by="test_user",
        notes="Confirmed brute force attempt"
    )
    
    # 4. Vérifier l'historique
    history = validator.get_validation_history()
    assert len(history) == 1
    assert history[0].validation_status == ValidationStatus.VALIDATED
    
    # 5. Vérifier que la règle est active
    rule = rule_manager.get_rule(validation.modsec_rule_id)
    assert rule.status == RuleStatus.ACTIVE
    assert "anomaly_generated" in rule.tags 