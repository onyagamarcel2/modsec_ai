#!/usr/bin/env python3
"""
Script de workflow pour automatiser les tâches de développement.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowManager:
    """Gestionnaire de workflow pour le projet."""
    
    def __init__(self):
        """Initialise le gestionnaire de workflow."""
        self.project_root = Path(__file__).parent
        self.venv_dir = self.project_root / "venv"
        
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> bool:
        """
        Exécute une commande shell.
        
        Args:
            command: Liste des arguments de la commande
            cwd: Répertoire de travail (optionnel)
            
        Returns:
            bool: True si la commande a réussi, False sinon
        """
        try:
            subprocess.run(
                command,
                cwd=cwd or self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de l'exécution de la commande: {e}")
            logger.error(f"Sortie d'erreur: {e.stderr}")
            return False
            
    def check_environment(self) -> bool:
        """
        Vérifie l'environnement de développement.
        
        Returns:
            bool: True si l'environnement est correct, False sinon
        """
        logger.info("Vérification de l'environnement...")
        
        # Vérifier Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.error("Python 3.8 ou supérieur est requis")
            return False
            
        # Vérifier les dépendances système
        required_commands = ["git", "pip"]
        for cmd in required_commands:
            if not self.run_command([cmd, "--version"]):
                logger.error(f"La commande {cmd} n'est pas disponible")
                return False
                
        logger.info("Environnement vérifié avec succès")
        return True
        
    def setup_virtual_env(self) -> bool:
        """
        Configure l'environnement virtuel.
        
        Returns:
            bool: True si la configuration a réussi, False sinon
        """
        logger.info("Configuration de l'environnement virtuel...")
        
        # Créer le venv s'il n'existe pas
        if not self.venv_dir.exists():
            if not self.run_command([sys.executable, "-m", "venv", "venv"]):
                return False
                
        # Activer le venv et installer les dépendances
        pip_cmd = str(self.venv_dir / "Scripts" / "pip") if os.name == "nt" else str(self.venv_dir / "bin" / "pip")
        
        if not self.run_command([pip_cmd, "install", "--upgrade", "pip"]):
            return False
            
        if not self.run_command([pip_cmd, "install", "-r", "requirements.txt"]):
            return False
            
        logger.info("Environnement virtuel configuré avec succès")
        return True
        
    def run_tests(self) -> bool:
        """
        Exécute les tests unitaires.
        
        Returns:
            bool: True si les tests ont réussi, False sinon
        """
        logger.info("Exécution des tests...")
        
        # Exécuter les tests avec pytest
        if not self.run_command([
            "pytest",
            "--cov=src",
            "--cov-report=html:docs/coverage_report",
            "--cov-report=term-missing",
            "tests/"
        ]):
            return False
            
        logger.info("Tests exécutés avec succès")
        return True
        
    def generate_docs(self) -> bool:
        """
        Génère la documentation.
        
        Returns:
            bool: True si la génération a réussi, False sinon
        """
        logger.info("Génération de la documentation...")
        
        # Générer la documentation avec Sphinx
        if not self.run_command([
            "sphinx-build",
            "-b", "html",
            "docs/source",
            "docs/build"
        ]):
            return False
            
        logger.info("Documentation générée avec succès")
        return True
        
    def check_code_quality(self) -> bool:
        """
        Vérifie la qualité du code.
        
        Returns:
            bool: True si les vérifications ont réussi, False sinon
        """
        logger.info("Vérification de la qualité du code...")
        
        # Exécuter pylint
        if not self.run_command([
            "pylint",
            "--rcfile=.pylintrc",
            "src"
        ]):
            return False
            
        # Exécuter mypy
        if not self.run_command([
            "mypy",
            "--config-file=mypy.ini",
            "src"
        ]):
            return False
            
        logger.info("Qualité du code vérifiée avec succès")
        return True
        
    def run_workflow(self) -> bool:
        """
        Exécute le workflow complet.
        
        Returns:
            bool: True si le workflow a réussi, False sinon
        """
        steps = [
            (self.check_environment, "Vérification de l'environnement"),
            (self.setup_virtual_env, "Configuration de l'environnement virtuel"),
            (self.run_tests, "Exécution des tests"),
            (self.generate_docs, "Génération de la documentation"),
            (self.check_code_quality, "Vérification de la qualité du code")
        ]
        
        for step_func, step_name in steps:
            logger.info(f"Démarrage: {step_name}")
            if not step_func():
                logger.error(f"Échec: {step_name}")
                return False
            logger.info(f"Succès: {step_name}")
            
        logger.info("Workflow terminé avec succès")
        return True

def main():
    """Point d'entrée du script."""
    workflow = WorkflowManager()
    success = workflow.run_workflow()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 