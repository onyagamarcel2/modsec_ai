"""
Tests unitaires pour le gestionnaire de règles ModSecurity.
"""

import os
import pytest
from datetime import datetime
from modsec.rule_manager import (
    ModSecRuleManager,
    ModSecRule,
    RuleStatus
)

@pytest.fixture
def temp_rules_dir(tmp_path):
    """Crée un répertoire temporaire pour les tests."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    return rules_dir

@pytest.fixture
def rule_manager(temp_rules_dir):
    """Crée une instance de ModSecRuleManager pour les tests."""
    return ModSecRuleManager(
        rules_dir=str(temp_rules_dir),
        custom_rules_file="custom_rules.conf"
    )

def test_create_rule(rule_manager):
    """Test la création d'une règle."""
    rule = rule_manager.create_rule(
        name="Test Rule",
        description="Test Description",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user",
        tags=["test", "unit"]
    )
    
    assert rule.name == "Test Rule"
    assert rule.description == "Test Description"
    assert rule.content == "REQUEST_HEADERS:User-Agent"
    assert rule.status == RuleStatus.ACTIVE
    assert rule.created_by == "test_user"
    assert rule.tags == ["test", "unit"]
    assert rule.rule_id.isdigit()

def test_create_rule_with_invalid_content(rule_manager):
    """Test la création d'une règle avec un contenu invalide."""
    with pytest.raises(ValueError):
        rule_manager.create_rule(
            name="Invalid Rule",
            description="Invalid rule content",
            content="",  # Contenu vide
            created_by="test_user"
        )

def test_create_rule_with_invalid_name(rule_manager):
    """Test la création d'une règle avec un nom invalide."""
    with pytest.raises(ValueError):
        rule_manager.create_rule(
            name="",  # Nom vide
            description="Test Description",
            content="REQUEST_HEADERS:User-Agent",
            created_by="test_user"
        )

def test_duplicate_rule_id(rule_manager):
    """Test la gestion des IDs de règles uniques."""
    # Créer une première règle
    rule1 = rule_manager.create_rule(
        name="Rule 1",
        description="First rule",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user"
    )
    
    # Créer une deuxième règle
    rule2 = rule_manager.create_rule(
        name="Rule 2",
        description="Second rule",
        content="REQUEST_HEADERS:Referer",
        created_by="test_user"
    )
    
    # Vérifier que les IDs sont différents
    assert rule1.rule_id != rule2.rule_id

def test_update_rule(rule_manager):
    """Test la mise à jour d'une règle."""
    # Créer une règle
    rule = rule_manager.create_rule(
        name="Original Rule",
        description="Original Description",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user"
    )
    
    # Mettre à jour la règle
    updated_rule = rule_manager.update_rule(
        rule_id=rule.rule_id,
        name="Updated Rule",
        description="Updated Description",
        status=RuleStatus.INACTIVE,
        updated_by="test_user"
    )
    
    assert updated_rule.name == "Updated Rule"
    assert updated_rule.description == "Updated Description"
    assert updated_rule.status == RuleStatus.INACTIVE
    assert updated_rule.updated_by == "test_user"

def test_update_nonexistent_rule(rule_manager):
    """Test la mise à jour d'une règle inexistante."""
    with pytest.raises(ValueError):
        rule_manager.update_rule(
            rule_id="nonexistent",
            name="Updated Rule",
            updated_by="test_user"
        )

def test_delete_rule(rule_manager):
    """Test la suppression d'une règle."""
    # Créer une règle
    rule = rule_manager.create_rule(
        name="Rule to Delete",
        description="Will be deleted",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user"
    )
    
    # Supprimer la règle
    rule_manager.delete_rule(rule.rule_id)
    
    # Vérifier que la règle n'existe plus
    with pytest.raises(ValueError):
        rule_manager.get_rule(rule.rule_id)

def test_delete_nonexistent_rule(rule_manager):
    """Test la suppression d'une règle inexistante."""
    with pytest.raises(ValueError):
        rule_manager.delete_rule("nonexistent")

def test_get_rules_with_filters(rule_manager):
    """Test le filtrage des règles."""
    # Créer plusieurs règles avec différents statuts et tags
    rule1 = rule_manager.create_rule(
        name="Active Rule",
        description="Active rule",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user",
        status=RuleStatus.ACTIVE,
        tags=["active"]
    )
    
    rule2 = rule_manager.create_rule(
        name="Inactive Rule",
        description="Inactive rule",
        content="REQUEST_HEADERS:Referer",
        created_by="test_user",
        status=RuleStatus.INACTIVE,
        tags=["inactive"]
    )
    
    # Tester le filtrage par statut
    active_rules = rule_manager.get_rules(status=RuleStatus.ACTIVE)
    assert len(active_rules) == 1
    assert active_rules[0].rule_id == rule1.rule_id
    
    # Tester le filtrage par tags
    tagged_rules = rule_manager.get_rules(tags=["active"])
    assert len(tagged_rules) == 1
    assert tagged_rules[0].rule_id == rule1.rule_id
    
    # Tester la recherche
    search_rules = rule_manager.get_rules(search="Active")
    assert len(search_rules) == 1
    assert search_rules[0].rule_id == rule1.rule_id

def test_get_rules_with_multiple_filters(rule_manager):
    """Test le filtrage avec plusieurs critères."""
    # Créer des règles avec différentes combinaisons
    rule1 = rule_manager.create_rule(
        name="Rule A",
        description="Test rule A",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user",
        status=RuleStatus.ACTIVE,
        tags=["test", "active"]
    )
    
    rule2 = rule_manager.create_rule(
        name="Rule B",
        description="Test rule B",
        content="REQUEST_HEADERS:Referer",
        created_by="test_user",
        status=RuleStatus.ACTIVE,
        tags=["test", "inactive"]
    )
    
    # Tester la combinaison de filtres
    filtered_rules = rule_manager.get_rules(
        status=RuleStatus.ACTIVE,
        tags=["test", "active"],
        search="Rule A"
    )
    
    assert len(filtered_rules) == 1
    assert filtered_rules[0].rule_id == rule1.rule_id

def test_backup_and_restore(rule_manager):
    """Test la sauvegarde et la restauration des règles."""
    # Créer quelques règles
    rule1 = rule_manager.create_rule(
        name="Rule 1",
        description="First rule",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user"
    )
    
    rule2 = rule_manager.create_rule(
        name="Rule 2",
        description="Second rule",
        content="REQUEST_HEADERS:Referer",
        created_by="test_user"
    )
    
    # Créer une sauvegarde
    backup_file = rule_manager.backup_rules()
    assert os.path.exists(backup_file)
    
    # Supprimer les règles
    rule_manager.delete_rule(rule1.rule_id)
    rule_manager.delete_rule(rule2.rule_id)
    
    # Restaurer la sauvegarde
    rule_manager.restore_backup(backup_file)
    
    # Vérifier que les règles sont restaurées
    restored_rule1 = rule_manager.get_rule(rule1.rule_id)
    restored_rule2 = rule_manager.get_rule(rule2.rule_id)
    
    assert restored_rule1.name == rule1.name
    assert restored_rule2.name == rule2.name

def test_restore_invalid_backup(rule_manager):
    """Test la restauration d'une sauvegarde invalide."""
    with pytest.raises(ValueError):
        rule_manager.restore_backup("nonexistent_backup.conf")

def test_rule_file_operations(rule_manager):
    """Test les opérations sur le fichier de règles."""
    # Créer une règle
    rule = rule_manager.create_rule(
        name="File Test Rule",
        description="Testing file operations",
        content="REQUEST_HEADERS:User-Agent",
        created_by="test_user"
    )
    
    # Vérifier que le fichier existe
    assert os.path.exists(rule_manager.custom_rules_file)
    
    # Vérifier le contenu du fichier
    with open(rule_manager.custom_rules_file, 'r') as f:
        content = f.read()
        assert rule.name in content
        assert rule.content in content
        assert rule.rule_id in content 