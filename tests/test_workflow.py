import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.modsec_ai.workflow import WorkflowManager
import subprocess

@pytest.fixture
def workflow_manager():
    """Fixture pour créer une instance de WorkflowManager."""
    return WorkflowManager()

@pytest.fixture
def mock_subprocess():
    """Fixture pour mocker subprocess.run."""
    with patch('subprocess.run') as mock:
        yield mock

def test_run_command_success(workflow_manager, mock_subprocess):
    """Test de run_command avec succès."""
    # Configuration du mock
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    # Test
    result = workflow_manager.run_command(['echo', 'test'])
    
    # Vérifications
    assert result is True
    mock_subprocess.assert_called_once()
    mock_subprocess.assert_called_with(
        ['echo', 'test'],
        cwd=workflow_manager.project_root,
        check=True,
        capture_output=True,
        text=True
    )

def test_run_command_failure(workflow_manager, mock_subprocess):
    """Test de run_command avec échec."""
    # Configuration du mock pour simuler une erreur
    mock_subprocess.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=['echo', 'test'],
        stderr='Error message'
    )
    
    # Test
    result = workflow_manager.run_command(['echo', 'test'])
    
    # Vérifications
    assert result is False
    mock_subprocess.assert_called_once()

def test_run_tests(workflow_manager, mock_subprocess):
    """Test de run_tests."""
    # Configuration du mock
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    # Test
    result = workflow_manager.run_tests()
    
    # Vérifications
    assert result is True
    mock_subprocess.assert_called_once()
    expected_command = [
        "pytest",
        "--cov=src",
        "--cov-report=html:docs/coverage_report",
        "--cov-report=term-missing",
        "tests/"
    ]
    mock_subprocess.assert_called_with(
        expected_command,
        cwd=workflow_manager.project_root,
        check=True,
        capture_output=True,
        text=True
    )

def test_generate_docs(workflow_manager, mock_subprocess):
    """Test de generate_docs."""
    # Configuration du mock
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    # Test
    result = workflow_manager.generate_docs()
    
    # Vérifications
    assert result is True
    mock_subprocess.assert_called_once()
    expected_command = [
        "sphinx-build",
        "-b", "html",
        "docs/source",
        "docs/build"
    ]
    mock_subprocess.assert_called_with(
        expected_command,
        cwd=workflow_manager.project_root,
        check=True,
        capture_output=True,
        text=True
    )

def test_check_code_quality(workflow_manager, mock_subprocess):
    """Test de check_code_quality."""
    # Configuration du mock
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    # Test
    result = workflow_manager.check_code_quality()
    
    # Vérifications
    assert result is True
    assert mock_subprocess.call_count == 2
    
    # Vérification de l'appel à pylint
    pylint_command = [
        "pylint",
        "--rcfile=.pylintrc",
        "src"
    ]
    mock_subprocess.assert_any_call(
        pylint_command,
        cwd=workflow_manager.project_root,
        check=True,
        capture_output=True,
        text=True
    )
    
    # Vérification de l'appel à mypy
    mypy_command = [
        "mypy",
        "--config-file=mypy.ini",
        "src"
    ]
    mock_subprocess.assert_any_call(
        mypy_command,
        cwd=workflow_manager.project_root,
        check=True,
        capture_output=True,
        text=True
    )

def test_run_workflow_success(workflow_manager, mock_subprocess):
    """Test de run_workflow avec succès."""
    # Configuration du mock pour toutes les étapes
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    # Mock des méthodes individuelles
    with patch.object(workflow_manager, 'check_environment', return_value=True), \
         patch.object(workflow_manager, 'setup_virtual_env', return_value=True), \
         patch.object(workflow_manager, 'run_tests', return_value=True), \
         patch.object(workflow_manager, 'generate_docs', return_value=True), \
         patch.object(workflow_manager, 'check_code_quality', return_value=True):
        
        # Test
        result = workflow_manager.run_workflow()
        
        # Vérifications
        assert result is True

def test_run_workflow_failure(workflow_manager, mock_subprocess):
    """Test de run_workflow avec échec."""
    # Configuration du mock pour simuler un échec à l'étape des tests
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    # Mock des méthodes individuelles avec un échec à run_tests
    with patch.object(workflow_manager, 'check_environment', return_value=True), \
         patch.object(workflow_manager, 'setup_virtual_env', return_value=True), \
         patch.object(workflow_manager, 'run_tests', return_value=False), \
         patch.object(workflow_manager, 'generate_docs', return_value=True), \
         patch.object(workflow_manager, 'check_code_quality', return_value=True):
        
        # Test
        result = workflow_manager.run_workflow()
        
        # Vérifications
        assert result is False

def test_workflow_with_custom_cwd(workflow_manager, mock_subprocess, tmp_path):
    """Test de run_command avec un répertoire de travail personnalisé."""
    # Configuration du mock
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    # Test
    result = workflow_manager.run_command(['echo', 'test'], cwd=tmp_path)
    
    # Vérifications
    assert result is True
    mock_subprocess.assert_called_once()
    mock_subprocess.assert_called_with(
        ['echo', 'test'],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True
    ) 