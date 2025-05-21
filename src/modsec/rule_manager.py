"""
Gestionnaire de règles ModSecurity.
"""

import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RuleStatus(Enum):
    """Statuts possibles pour une règle ModSecurity."""
    ACTIVE = "active"      # Règle active
    INACTIVE = "inactive"  # Règle inactive
    TESTING = "testing"    # Règle en phase de test

@dataclass
class ModSecRule:
    """Classe représentant une règle ModSecurity."""
    rule_id: str
    name: str
    description: str
    content: str
    status: RuleStatus
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    tags: List[str] = None
    test_results: Dict = None
    related_rules: List[str] = None

class ModSecRuleManager:
    """Gestionnaire de règles ModSecurity."""
    
    def __init__(
        self,
        rules_dir: str,
        custom_rules_file: str = "custom_rules.conf",
        backup_dir: str = "backups"
    ):
        """
        Initialise le gestionnaire de règles.

        Args:
            rules_dir: Répertoire des règles ModSecurity
            custom_rules_file: Nom du fichier de règles personnalisées
            backup_dir: Répertoire des sauvegardes
        """
        self.rules_dir = rules_dir
        self.custom_rules_file = os.path.join(rules_dir, custom_rules_file)
        self.backup_dir = os.path.join(rules_dir, backup_dir)
        
        # Créer les répertoires si nécessaire
        os.makedirs(rules_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Charger les règles existantes
        self.rules: Dict[str, ModSecRule] = {}
        self._load_rules()
        
    def _load_rules(self) -> None:
        """Charge les règles depuis le répertoire."""
        try:
            # Charger les règles personnalisées
            if os.path.exists(self.custom_rules_file):
                with open(self.custom_rules_file, 'r') as f:
                    content = f.read()
                    self._parse_rules(content)
                    
            # Charger les règles individuelles
            for filename in os.listdir(self.rules_dir):
                if filename.endswith('.conf') and filename != os.path.basename(self.custom_rules_file):
                    with open(os.path.join(self.rules_dir, filename), 'r') as f:
                        content = f.read()
                        self._parse_rules(content)
                        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des règles: {str(e)}")
            raise
            
    def _parse_rules(self, content: str) -> None:
        """
        Parse le contenu d'un fichier de règles.

        Args:
            content: Contenu du fichier de règles
        """
        # Pattern pour extraire les règles
        rule_pattern = r'# Rule: (.*?)\nSecRule (.*?) "id:(\d+),'
        
        for match in re.finditer(rule_pattern, content, re.DOTALL):
            name = match.group(1)
            rule_content = match.group(2)
            rule_id = match.group(3)
            
            # Extraire la description
            desc_match = re.search(r'msg:\'(.*?)\'', rule_content)
            description = desc_match.group(1) if desc_match else ""
            
            # Créer la règle
            rule = ModSecRule(
                rule_id=rule_id,
                name=name,
                description=description,
                content=rule_content,
                status=RuleStatus.ACTIVE,
                created_at=datetime.now(),
                created_by="system",
                tags=[],
                test_results={},
                related_rules=[]
            )
            
            self.rules[rule_id] = rule
            
    def create_rule(
        self,
        name: str,
        description: str,
        content: str,
        created_by: str,
        tags: List[str] = None,
        status: RuleStatus = RuleStatus.ACTIVE
    ) -> ModSecRule:
        """
        Crée une nouvelle règle ModSecurity.

        Args:
            name: Nom de la règle
            description: Description de la règle
            content: Contenu de la règle
            created_by: Créateur de la règle
            tags: Tags associés à la règle
            status: Statut de la règle

        Returns:
            La règle créée
        """
        # Générer un ID unique
        rule_id = self._generate_rule_id()
        
        # Créer la règle
        rule = ModSecRule(
            rule_id=rule_id,
            name=name,
            description=description,
            content=content,
            status=status,
            created_at=datetime.now(),
            created_by=created_by,
            tags=tags or [],
            test_results={},
            related_rules=[]
        )
        
        # Sauvegarder la règle
        self._save_rule(rule)
        
        return rule
        
    def _generate_rule_id(self) -> str:
        """
        Génère un ID unique pour une règle.

        Returns:
            ID unique
        """
        # Récupérer tous les IDs existants
        existing_ids = set(self.rules.keys())
        
        # Générer un nouvel ID
        base_id = 1000000  # Commencer à partir de 1000000
        while str(base_id) in existing_ids:
            base_id += 1
            
        return str(base_id)
        
    def _save_rule(self, rule: ModSecRule) -> None:
        """
        Sauvegarde une règle dans le fichier de règles personnalisées.

        Args:
            rule: Règle à sauvegarder
        """
        try:
            # Créer le contenu de la règle
            rule_content = f"""# Rule: {rule.name}
# Description: {rule.description}
# Created: {rule.created_at}
# Created by: {rule.created_by}
# Status: {rule.status.value}
# Tags: {', '.join(rule.tags)}
SecRule {rule.content} "id:{rule.rule_id},
    phase:1,
    log,
    msg:'{rule.description}',
    severity:CRITICAL,
    tag:'custom_rule'"

"""
            # Ajouter la règle au fichier
            with open(self.custom_rules_file, 'a') as f:
                f.write(rule_content)
                
            # Mettre à jour le dictionnaire des règles
            self.rules[rule.rule_id] = rule
            
            logger.info(f"Règle créée: {rule.rule_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la règle: {str(e)}")
            raise
            
    def update_rule(
        self,
        rule_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[RuleStatus] = None,
        updated_by: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ModSecRule:
        """
        Met à jour une règle existante.

        Args:
            rule_id: ID de la règle à mettre à jour
            name: Nouveau nom
            description: Nouvelle description
            content: Nouveau contenu
            status: Nouveau statut
            updated_by: Utilisateur mettant à jour
            tags: Nouveaux tags

        Returns:
            La règle mise à jour
        """
        if rule_id not in self.rules:
            raise ValueError(f"Règle non trouvée: {rule_id}")
            
        rule = self.rules[rule_id]
        
        # Mettre à jour les champs
        if name is not None:
            rule.name = name
        if description is not None:
            rule.description = description
        if content is not None:
            rule.content = content
        if status is not None:
            rule.status = status
        if tags is not None:
            rule.tags = tags
            
        rule.updated_at = datetime.now()
        rule.updated_by = updated_by
        
        # Sauvegarder les modifications
        self._update_rule_file(rule)
        
        return rule
        
    def _update_rule_file(self, rule: ModSecRule) -> None:
        """
        Met à jour le fichier de règles avec une règle modifiée.

        Args:
            rule: Règle mise à jour
        """
        try:
            # Lire le fichier
            with open(self.custom_rules_file, 'r') as f:
                content = f.read()
                
            # Remplacer la règle
            pattern = f"# Rule: .*?id:{rule.rule_id},.*?\n\n"
            new_content = f"""# Rule: {rule.name}
# Description: {rule.description}
# Created: {rule.created_at}
# Created by: {rule.created_by}
# Updated: {rule.updated_at}
# Updated by: {rule.updated_by}
# Status: {rule.status.value}
# Tags: {', '.join(rule.tags)}
SecRule {rule.content} "id:{rule.rule_id},
    phase:1,
    log,
    msg:'{rule.description}',
    severity:CRITICAL,
    tag:'custom_rule'"

"""
            content = re.sub(pattern, new_content, content, flags=re.DOTALL)
            
            # Sauvegarder le fichier
            with open(self.custom_rules_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du fichier de règles: {str(e)}")
            raise
            
    def delete_rule(self, rule_id: str) -> None:
        """
        Supprime une règle.

        Args:
            rule_id: ID de la règle à supprimer
        """
        if rule_id not in self.rules:
            raise ValueError(f"Règle non trouvée: {rule_id}")
            
        try:
            # Lire le fichier
            with open(self.custom_rules_file, 'r') as f:
                content = f.read()
                
            # Supprimer la règle
            pattern = f"# Rule: .*?id:{rule_id},.*?\n\n"
            content = re.sub(pattern, "", content, flags=re.DOTALL)
            
            # Sauvegarder le fichier
            with open(self.custom_rules_file, 'w') as f:
                f.write(content)
                
            # Supprimer la règle du dictionnaire
            del self.rules[rule_id]
            
            logger.info(f"Règle supprimée: {rule_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la règle: {str(e)}")
            raise
            
    def get_rule(self, rule_id: str) -> ModSecRule:
        """
        Récupère une règle par son ID.

        Args:
            rule_id: ID de la règle

        Returns:
            La règle trouvée
        """
        if rule_id not in self.rules:
            raise ValueError(f"Règle non trouvée: {rule_id}")
            
        return self.rules[rule_id]
        
    def get_rules(
        self,
        status: Optional[RuleStatus] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> List[ModSecRule]:
        """
        Récupère les règles avec filtres.

        Args:
            status: Filtrer par statut
            tags: Filtrer par tags
            search: Rechercher dans le nom/description

        Returns:
            Liste des règles filtrées
        """
        filtered_rules = list(self.rules.values())
        
        if status:
            filtered_rules = [
                r for r in filtered_rules
                if r.status == status
            ]
            
        if tags:
            filtered_rules = [
                r for r in filtered_rules
                if all(tag in r.tags for tag in tags)
            ]
            
        if search:
            search = search.lower()
            filtered_rules = [
                r for r in filtered_rules
                if search in r.name.lower() or search in r.description.lower()
            ]
            
        return filtered_rules
        
    def backup_rules(self) -> str:
        """
        Crée une sauvegarde des règles.

        Returns:
            Chemin du fichier de sauvegarde
        """
        try:
            # Générer le nom du fichier de sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"rules_backup_{timestamp}.conf")
            
            # Copier le fichier de règles
            with open(self.custom_rules_file, 'r') as src:
                with open(backup_file, 'w') as dst:
                    dst.write(src.read())
                    
            logger.info(f"Sauvegarde créée: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {str(e)}")
            raise
            
    def restore_backup(self, backup_file: str) -> None:
        """
        Restaure une sauvegarde de règles.

        Args:
            backup_file: Chemin du fichier de sauvegarde
        """
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(backup_file):
                raise ValueError(f"Fichier de sauvegarde non trouvé: {backup_file}")
                
            # Créer une sauvegarde avant restauration
            self.backup_rules()
            
            # Restaurer la sauvegarde
            with open(backup_file, 'r') as src:
                with open(self.custom_rules_file, 'w') as dst:
                    dst.write(src.read())
                    
            # Recharger les règles
            self._load_rules()
            
            logger.info(f"Sauvegarde restaurée: {backup_file}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la restauration de la sauvegarde: {str(e)}")
            raise 