"""
Tests unitaires pour le validateur d'anomalies.
"""

import os
import pytest
from datetime import datetime
from src.validation.anomaly_validator import (
    AnomalyValidator,
    AnomalyValidation,
    ValidationStatus
)
from src.modsec.rule_manager import ModSecRuleManager, RuleStatus

@pytest.fixture
def temp_dirs(tmp_path):
    """Crée des répertoires temporaires pour les tests."""
    validations_dir = tmp_path / "validations"
    rules_dir = tmp_path / "rules"
    validations_dir.mkdir()
    rules_dir.mkdir()
    return validations_dir, rules_dir

@pytest.fixture
def validator(temp_dirs):
    """Crée une instance de AnomalyValidator pour les tests."""
    validations_dir, rules_dir = temp_dirs
    rule_manager = ModSecRuleManager(
        rules_dir=str(rules_dir),
        custom_rules_file="custom_rules.conf"
    )
    return AnomalyValidator(
        validations_dir=str(validations_dir),
        rule_manager=rule_manager
    )

def test_create_validation(validator):
    """Test la création d'une validation."""
    # Créer une validation
    validation = validator.create_validation(
        anomaly_id="test_anomaly_1",
        log_sequence=["log1", "log2"],
        anomaly_score=0.95,
        detection_model="test_model",
        create_rule=True
    )
    
    assert validation.anomaly_id == "test_anomaly_1"
    assert validation.log_sequence == ["log1", "log2"]
    assert validation.anomaly_score == 0.95
    assert validation.detection_model == "test_model"
    assert validation.validation_status == ValidationStatus.PENDING
    assert validation.modsec_rule_id is not None

def test_create_validation_with_invalid_data(validator):
    """Test la création d'une validation avec des données invalides."""
    # Test avec un score invalide
    with pytest.raises(ValueError):
        validator.create_validation(
            anomaly_id="test_anomaly_invalid",
            log_sequence=["log1"],
            anomaly_score=1.5,  # Score > 1
            detection_model="test_model"
        )
    
    # Test avec une séquence de logs vide
    with pytest.raises(ValueError):
        validator.create_validation(
            anomaly_id="test_anomaly_empty",
            log_sequence=[],  # Séquence vide
            anomaly_score=0.95,
            detection_model="test_model"
        )

def test_create_duplicate_validation(validator):
    """Test la création d'une validation avec un ID déjà existant."""
    # Créer une première validation
    validator.create_validation(
        anomaly_id="test_anomaly_dup",
        log_sequence=["log1"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    # Tenter de créer une validation avec le même ID
    with pytest.raises(ValueError):
        validator.create_validation(
            anomaly_id="test_anomaly_dup",
            log_sequence=["log2"],
            anomaly_score=0.85,
            detection_model="test_model"
        )

def test_validate_anomaly(validator):
    """Test la validation d'une anomalie."""
    # Créer une validation
    validation = validator.create_validation(
        anomaly_id="test_anomaly_2",
        log_sequence=["log1", "log2"],
        anomaly_score=0.95,
        detection_model="test_model",
        create_rule=True
    )
    
    # Valider l'anomalie
    validator.validate_anomaly(
        anomaly_id=validation.anomaly_id,
        status=ValidationStatus.VALIDATED,
        validated_by="test_user",
        notes="Test validation"
    )
    
    # Récupérer la validation mise à jour
    updated_validation = validator.get_validation(validation.anomaly_id)
    
    assert updated_validation.validation_status == ValidationStatus.VALIDATED
    assert updated_validation.validated_by == "test_user"
    assert updated_validation.validation_notes == "Test validation"
    assert updated_validation.validation_timestamp is not None

def test_validate_nonexistent_anomaly(validator):
    """Test la validation d'une anomalie inexistante."""
    with pytest.raises(ValueError):
        validator.validate_anomaly(
            anomaly_id="nonexistent",
            status=ValidationStatus.VALIDATED,
            validated_by="test_user"
        )

def test_validate_with_invalid_status(validator):
    """Test la validation avec un statut invalide."""
    # Créer une validation
    validation = validator.create_validation(
        anomaly_id="test_anomaly_invalid_status",
        log_sequence=["log1"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    # Tenter de valider avec un statut invalide
    with pytest.raises(ValueError):
        validator.validate_anomaly(
            anomaly_id=validation.anomaly_id,
            status="INVALID_STATUS",  # Statut invalide
            validated_by="test_user"
        )

def test_mark_normal(validator):
    """Test le marquage d'une anomalie comme normale."""
    # Créer une validation avec une règle
    validation = validator.create_validation(
        anomaly_id="test_anomaly_3",
        log_sequence=["log1", "log2"],
        anomaly_score=0.95,
        detection_model="test_model",
        create_rule=True
    )
    
    # Marquer comme normale
    validator.validate_anomaly(
        anomaly_id=validation.anomaly_id,
        status=ValidationStatus.NORMAL,
        validated_by="test_user"
    )
    
    # Vérifier que la règle a été supprimée
    with pytest.raises(ValueError):
        validator.rule_manager.get_rule(validation.modsec_rule_id)

def test_get_pending_validations(validator):
    """Test la récupération des validations en attente."""
    # Créer plusieurs validations
    validator.create_validation(
        anomaly_id="test_anomaly_4",
        log_sequence=["log1"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    validator.create_validation(
        anomaly_id="test_anomaly_5",
        log_sequence=["log2"],
        anomaly_score=0.85,
        detection_model="test_model"
    )
    
    # Valider une des anomalies
    validator.validate_anomaly(
        anomaly_id="test_anomaly_4",
        status=ValidationStatus.VALIDATED,
        validated_by="test_user"
    )
    
    # Récupérer les validations en attente
    pending = validator.get_pending_validations()
    
    assert len(pending) == 1
    assert pending[0].anomaly_id == "test_anomaly_5"

def test_get_validation_history(validator):
    """Test la récupération de l'historique des validations."""
    # Créer et valider plusieurs anomalies
    validator.create_validation(
        anomaly_id="test_anomaly_6",
        log_sequence=["log1"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    validator.create_validation(
        anomaly_id="test_anomaly_7",
        log_sequence=["log2"],
        anomaly_score=0.85,
        detection_model="test_model"
    )
    
    validator.validate_anomaly(
        anomaly_id="test_anomaly_6",
        status=ValidationStatus.VALIDATED,
        validated_by="test_user"
    )
    
    validator.validate_anomaly(
        anomaly_id="test_anomaly_7",
        status=ValidationStatus.NORMAL,
        validated_by="test_user"
    )
    
    # Récupérer l'historique
    history = validator.get_validation_history()
    
    assert len(history) == 2
    assert any(v.anomaly_id == "test_anomaly_6" and 
              v.validation_status == ValidationStatus.VALIDATED 
              for v in history)
    assert any(v.anomaly_id == "test_anomaly_7" and 
              v.validation_status == ValidationStatus.NORMAL 
              for v in history)

def test_get_validation_history_with_filters(validator):
    """Test la récupération de l'historique avec des filtres."""
    # Créer et valider des anomalies avec différents statuts
    validator.create_validation(
        anomaly_id="test_anomaly_8",
        log_sequence=["log1"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    validator.create_validation(
        anomaly_id="test_anomaly_9",
        log_sequence=["log2"],
        anomaly_score=0.85,
        detection_model="test_model"
    )
    
    validator.validate_anomaly(
        anomaly_id="test_anomaly_8",
        status=ValidationStatus.VALIDATED,
        validated_by="user1"
    )
    
    validator.validate_anomaly(
        anomaly_id="test_anomaly_9",
        status=ValidationStatus.NORMAL,
        validated_by="user2"
    )
    
    # Tester le filtrage par statut
    validated = validator.get_validation_history(status=ValidationStatus.VALIDATED)
    assert len(validated) == 1
    assert validated[0].anomaly_id == "test_anomaly_8"
    
    # Tester le filtrage par utilisateur
    user1_validations = validator.get_validation_history(validated_by="user1")
    assert len(user1_validations) == 1
    assert user1_validations[0].anomaly_id == "test_anomaly_8"

def test_rule_creation_from_anomaly(validator):
    """Test la création d'une règle à partir d'une anomalie."""
    # Créer une validation avec une règle
    validation = validator.create_validation(
        anomaly_id="test_anomaly_10",
        log_sequence=["log1", "log2"],
        anomaly_score=0.95,
        detection_model="test_model",
        create_rule=True
    )
    
    # Vérifier que la règle a été créée
    rule = validator.rule_manager.get_rule(validation.modsec_rule_id)
    
    assert rule is not None
    assert rule.status == RuleStatus.ACTIVE
    assert "anomaly_generated" in rule.tags

def test_validation_file_operations(validator):
    """Test les opérations sur les fichiers de validation."""
    # Créer une validation
    validation = validator.create_validation(
        anomaly_id="test_anomaly_11",
        log_sequence=["log1"],
        anomaly_score=0.95,
        detection_model="test_model"
    )
    
    # Vérifier que le fichier existe
    validation_file = os.path.join(validator.validations_dir, f"{validation.anomaly_id}.json")
    assert os.path.exists(validation_file)
    
    # Vérifier le contenu du fichier
    with open(validation_file, 'r') as f:
        content = f.read()
        assert validation.anomaly_id in content
        assert str(validation.anomaly_score) in content
        assert validation.detection_model in content 