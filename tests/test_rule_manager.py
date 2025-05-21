"""
Tests unitaires pour le gestionnaire de règles ModSecurity.
"""

import pytest
import os
import tempfile
from datetime import datetime
from src.modsec.rule_manager import ModSecRuleManager, ModSecRule, RuleStatus

@pytest.fixture
def temp_rules_dir():
    """Crée un répertoire temporaire pour les règles."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def rule_manager(temp_rules_dir):
    """Crée une instance de ModSecRuleManager avec un répertoire temporaire."""
    manager = ModSecRuleManager(temp_rules_dir)
    # Créer le fichier custom_rules.conf s'il n'existe pas
    if not os.path.exists(os.path.join(temp_rules_dir, "custom_rules.conf")):
        with open(os.path.join(temp_rules_dir, "custom_rules.conf"), 'w') as f:
            f.write("# Custom ModSecurity Rules\n")
    return manager

def test_initialization(rule_manager, temp_rules_dir):
    """Test l'initialisation du gestionnaire de règles."""
    assert rule_manager.rules_dir == temp_rules_dir
    assert os.path.exists(os.path.join(temp_rules_dir, "custom_rules.conf"))
    assert os.path.exists(os.path.join(temp_rules_dir, "backups"))
    assert isinstance(rule_manager.rules, dict)
    assert len(rule_manager.rules) == 0

def test_create_rule(rule_manager):
    """Test la création d'une règle."""
    rule = rule_manager.create_rule(
        name="Test Rule",
        description="Test Description",
        content="REQUEST_URI '@rx /test'",
        created_by="test_user",
        tags=["test", "security"],
        status=RuleStatus.ACTIVE
    )
    
    assert rule.rule_id in rule_manager.rules
    assert rule.name == "Test Rule"
    assert rule.description == "Test Description"
    assert rule.content == "REQUEST_URI '@rx /test'"
    assert rule.status == RuleStatus.ACTIVE
    assert rule.created_by == "test_user"
    assert set(rule.tags) == {"test", "security"}
    assert isinstance(rule.created_at, datetime)

def test_update_rule(rule_manager):
    """Test la mise à jour d'une règle."""
    # Créer une règle
    rule = rule_manager.create_rule(
        name="Original Name",
        description="Original Description",
        content="REQUEST_URI '@rx /test'",
        created_by="test_user"
    )
    
    # Mettre à jour la règle
    updated_rule = rule_manager.update_rule(
        rule_id=rule.rule_id,
        name="Updated Name",
        description="Updated Description",
        status=RuleStatus.INACTIVE,
        updated_by="test_user2",
        tags=["updated"]
    )
    
    assert updated_rule.name == "Updated Name"
    assert updated_rule.description == "Updated Description"
    assert updated_rule.status == RuleStatus.INACTIVE
    assert updated_rule.updated_by == "test_user2"
    assert updated_rule.tags == ["updated"]
    assert isinstance(updated_rule.updated_at, datetime)

def test_delete_rule(rule_manager):
    """Test la suppression d'une règle."""
    # Créer une règle
    rule = rule_manager.create_rule(
        name="To Delete",
        description="Will be deleted",
        content="REQUEST_URI '@rx /test'",
        created_by="test_user"
    )
    
    # Vérifier que la règle existe
    assert rule.rule_id in rule_manager.rules
    
    # Supprimer la règle
    rule_manager.delete_rule(rule.rule_id)
    
    # Vérifier que la règle n'existe plus
    assert rule.rule_id not in rule_manager.rules

def test_get_rule(rule_manager):
    """Test la récupération d'une règle."""
    # Créer une règle
    created_rule = rule_manager.create_rule(
        name="Test Rule",
        description="Test Description",
        content="REQUEST_URI '@rx /test'",
        created_by="test_user"
    )
    
    # Récupérer la règle
    retrieved_rule = rule_manager.get_rule(created_rule.rule_id)
    
    assert retrieved_rule == created_rule
    assert retrieved_rule.name == "Test Rule"
    assert retrieved_rule.description == "Test Description"

def test_get_rules_with_filters(rule_manager):
    """Test la récupération de règles avec filtres."""
    # Créer plusieurs règles avec différents statuts et tags
    rule1 = rule_manager.create_rule(
        name="Active Rule",
        description="Active rule description",
        content="REQUEST_URI '@rx /active'",
        created_by="test_user",
        status=RuleStatus.ACTIVE,
        tags=["active", "security"]
    )
    
    rule2 = rule_manager.create_rule(
        name="Inactive Rule",
        description="Inactive rule description",
        content="REQUEST_URI '@rx /inactive'",
        created_by="test_user",
        status=RuleStatus.INACTIVE,
        tags=["inactive"]
    )
    
    # Tester le filtre par statut
    active_rules = rule_manager.get_rules(status=RuleStatus.ACTIVE)
    assert len(active_rules) == 1
    assert active_rules[0].rule_id == rule1.rule_id
    
    # Tester le filtre par tags
    security_rules = rule_manager.get_rules(tags=["security"])
    assert len(security_rules) == 1
    assert security_rules[0].rule_id == rule1.rule_id
    
    # Tester la recherche par texte
    search_results = rule_manager.get_rules(search="active")
    assert len(search_results) == 2  # Devrait trouver les deux règles car "active" est dans les deux

def test_backup_and_restore(rule_manager):
    """Test la sauvegarde et la restauration des règles."""
    # Créer quelques règles
    rule1 = rule_manager.create_rule(
        name="Rule 1",
        description="First rule",
        content="REQUEST_URI '@rx /test1'",
        created_by="test_user"
    )
    
    rule2 = rule_manager.create_rule(
        name="Rule 2",
        description="Second rule",
        content="REQUEST_URI '@rx /test2'",
        created_by="test_user"
    )
    
    # Sauvegarder les règles
    backup_file = rule_manager.backup_rules()
    assert os.path.exists(backup_file)
    
    # Supprimer toutes les règles
    for rule_id in list(rule_manager.rules.keys()):
        rule_manager.delete_rule(rule_id)
    assert len(rule_manager.rules) == 0
    
    # Restaurer les règles
    rule_manager.restore_backup(backup_file)
    
    # Vérifier que les règles ont été restaurées
    assert len(rule_manager.rules) > 0
    
    # Vérifier que les règles originales sont présentes
    found_rule1 = False
    found_rule2 = False
    
    for rule in rule_manager.rules.values():
        if rule.name == "Rule 1" and rule.content == "REQUEST_URI '@rx /test1'":
            found_rule1 = True
        elif rule.name == "Rule 2" and rule.content == "REQUEST_URI '@rx /test2'":
            found_rule2 = True
            
    assert found_rule1, "Rule 1 n'a pas été restaurée correctement"
    assert found_rule2, "Rule 2 n'a pas été restaurée correctement" 