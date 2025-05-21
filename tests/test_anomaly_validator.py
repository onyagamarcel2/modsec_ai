"""
Tests unitaires pour le module de validation des anomalies (AnomalyValidator).
"""

import pytest
from unittest.mock import MagicMock, patch
import os
import tempfile
from datetime import datetime
from src.validation.anomaly_validator import AnomalyValidator, ValidationStatus, AnomalyValidation

@pytest.fixture
def temp_dirs(tmp_path):
    validation_dir = tmp_path / "validations"
    rules_dir = tmp_path / "rules"
    validation_dir.mkdir()
    rules_dir.mkdir()
    return str(validation_dir), str(rules_dir)

@pytest.fixture
def validator(temp_dirs):
    validation_dir, rules_dir = temp_dirs
    return AnomalyValidator(validation_dir, rules_dir, auto_create_rules=True)

def test_create_validation(validator):
    val = validator.create_validation(
        anomaly_id="A1",
        log_sequence=[{"uri": "/test"}],
        anomaly_score=0.9,
        detection_model="IForest"
    )
    assert val.anomaly_id == "A1"
    assert val.validation_status == ValidationStatus.PENDING
    assert val.modsec_rule_id is not None
    # Vérifie que le fichier de validation existe
    path = os.path.join(validator.validation_dir, "A1.json")
    assert os.path.exists(path)

def test_validate_anomaly(validator):
    val = validator.create_validation(
        anomaly_id="A2",
        log_sequence=[{"uri": "/test2"}],
        anomaly_score=0.8,
        detection_model="LOF"
    )
    validated = validator.validate_anomaly(
        anomaly_id="A2",
        status=ValidationStatus.VALIDATED,
        validated_by="admin",
        notes="Vraie anomalie"
    )
    assert validated.validation_status == ValidationStatus.VALIDATED
    assert validated.validated_by == "admin"
    assert validated.validation_notes == "Vraie anomalie"
    assert validated.validation_timestamp is not None

def test_mark_normal_removes_rule(validator):
    val = validator.create_validation(
        anomaly_id="A3",
        log_sequence=[{"uri": "/test3"}],
        anomaly_score=0.7,
        detection_model="SVM"
    )
    rule_path = os.path.join(validator.modsec_rules_dir, f"{val.modsec_rule_id}.conf")
    assert os.path.exists(rule_path)
    # Marquer comme normal doit supprimer la règle
    validator.validate_anomaly(
        anomaly_id="A3",
        status=ValidationStatus.NORMAL,
        validated_by="user"
    )
    assert not os.path.exists(rule_path)

def test_get_pending_validations(validator):
    validator.create_validation("A4", [{"uri": "/a4"}], 0.5, "IForest")
    validator.create_validation("A5", [{"uri": "/a5"}], 0.6, "LOF")
    # Valider l'une d'elles
    validator.validate_anomaly("A4", ValidationStatus.VALIDATED, "admin")
    pending = validator.get_pending_validations()
    assert len(pending) == 1
    assert pending[0].anomaly_id == "A5"

def test_get_validation_history(validator):
    validator.create_validation("A6", [{"uri": "/a6"}], 0.5, "IForest")
    validator.create_validation("A7", [{"uri": "/a7"}], 0.6, "LOF")
    validator.validate_anomaly("A6", ValidationStatus.VALIDATED, "admin")
    validator.validate_anomaly("A7", ValidationStatus.NORMAL, "user")
    hist = validator.get_validation_history(status=ValidationStatus.VALIDATED)
    assert len(hist) == 1
    assert hist[0].anomaly_id == "A6"
    hist_all = validator.get_validation_history()
    assert len(hist_all) == 2

def test_duplicate_validation_raises(validator):
    validator.create_validation("A8", [{"uri": "/a8"}], 0.5, "IForest")
    with pytest.raises(Exception):
        validator.create_validation("A8", [{"uri": "/a8"}], 0.5, "IForest") 