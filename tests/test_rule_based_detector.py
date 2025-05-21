"""
Tests unitaires pour RuleBasedDetector (détection basée sur des règles).
"""
import os
import json
import pytest
from src.utils.rule_based_detector import RuleBasedDetector

@pytest.fixture
def simple_rule():
    return {
        'name': 'Detect SQLi',
        'pattern': r"select.+from|union.+select|drop table",
        'severity': 'high',
        'description': 'SQL injection pattern',
        'conditions': {'uri': r'/login'}
    }

@pytest.fixture
def log_entry():
    return {
        'uri': '/login',
        'body': 'username=admin&password=1234 union select password from users',
        'method': 'POST'
    }

@pytest.fixture
def tmp_rules_file(tmp_path, simple_rule):
    rules_file = tmp_path / "rules.json"
    with open(rules_file, 'w') as f:
        json.dump({'rules': [simple_rule]}, f)
    return str(rules_file)

def test_add_and_validate_rule(simple_rule):
    detector = RuleBasedDetector()
    detector.add_rule(simple_rule)
    assert len(detector.get_rules()) == 1
    # Test règle invalide (pattern manquant)
    invalid_rule = {'name': 'NoPattern', 'severity': 'low'}
    detector.add_rule(invalid_rule)
    assert len(detector.get_rules()) == 1  # Pas ajoutée

def test_detect_anomaly(simple_rule, log_entry):
    detector = RuleBasedDetector()
    detector.add_rule(simple_rule)
    results = detector.detect(log_entry)
    assert len(results) == 1
    assert results[0]['rule_name'] == 'Detect SQLi'
    # Cas négatif
    log_entry2 = {'uri': '/home', 'body': 'normal', 'method': 'GET'}
    assert detector.detect(log_entry2) == []

def test_load_and_save_rules(tmp_rules_file, simple_rule):
    detector = RuleBasedDetector()
    detector.load_rules(tmp_rules_file)
    assert len(detector.get_rules()) == 1
    # Sauvegarde
    save_path = tmp_rules_file + '_out.json'
    detector.save_rules(save_path)
    assert os.path.exists(save_path)
    with open(save_path) as f:
        data = json.load(f)
        assert 'rules' in data and len(data['rules']) == 1

def test_clear_rules(simple_rule):
    detector = RuleBasedDetector()
    detector.add_rule(simple_rule)
    assert len(detector.get_rules()) == 1
    detector.clear_rules()
    assert detector.get_rules() == []

def test_invalid_rule_pattern():
    detector = RuleBasedDetector()
    bad_rule = {'name': 'bad', 'pattern': '[unclosed', 'severity': 'low'}
    detector.add_rule(bad_rule)
    assert detector.get_rules() == []

def test_missing_rules_file(tmp_path):
    detector = RuleBasedDetector()
    missing_file = str(tmp_path / "doesnotexist.json")
    detector.load_rules(missing_file)  # Doit juste logger un warning, pas d'exception
    assert detector.get_rules() == []

def test_check_rule_conditions():
    detector = RuleBasedDetector()
    rule = {
        'name': 'Cond',
        'pattern': r"admin",
        'severity': 'medium',
        'conditions': {'method': r'POST', 'uri': r'/login'}
    }
    detector.add_rule(rule)
    # Respecte toutes les conditions
    log = {'uri': '/login', 'body': 'admin', 'method': 'POST'}
    assert detector.detect(log)
    # Ne respecte pas une condition
    log2 = {'uri': '/login', 'body': 'admin', 'method': 'GET'}
    assert detector.detect(log2) == []

def test_detect_with_empty_rules(log_entry):
    detector = RuleBasedDetector()
    assert detector.detect(log_entry) == [] 