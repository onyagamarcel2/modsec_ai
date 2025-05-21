import logging
import re
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class RuleBasedDetector:
    """Détecteur d'anomalies basé sur des règles."""
    
    def __init__(self, rules_file=None):
        """Initialise le détecteur basé sur des règles.
        
        Args:
            rules_file (str, optional): Chemin vers le fichier de règles
        """
        self.rules = []
        if rules_file:
            self.load_rules(rules_file)
    
    def load_rules(self, rules_file):
        """Charge les règles depuis un fichier.
        
        Args:
            rules_file (str): Chemin vers le fichier de règles
        """
        try:
            if not os.path.exists(rules_file):
                logger.warning("Rules file not found: %s", rules_file)
                return
                
            with open(rules_file, 'r') as f:
                rules_data = json.load(f)
                self.rules = rules_data.get('rules', [])
                
            logger.info("Loaded %d rules from %s", len(self.rules), rules_file)
            
        except Exception as e:
            logger.error("Error loading rules: %s", str(e))
    
    def add_rule(self, rule):
        """Ajoute une règle au détecteur.
        
        Args:
            rule (dict): Règle à ajouter
        """
        try:
            # Valider la règle
            if not self._validate_rule(rule):
                logger.error("Invalid rule: %s", rule)
                return
                
            self.rules.append(rule)
            logger.info("Added rule: %s", rule.get('name', 'Unnamed rule'))
            
        except Exception as e:
            logger.error("Error adding rule: %s", str(e))
    
    def _validate_rule(self, rule):
        """Valide une règle.
        
        Args:
            rule (dict): Règle à valider
            
        Returns:
            bool: True si la règle est valide
        """
        required_fields = ['name', 'pattern', 'severity']
        if not all(field in rule for field in required_fields):
            return False
            
        try:
            # Compiler le pattern regex
            re.compile(rule['pattern'])
            return True
        except re.error:
            return False
    
    def detect(self, log_entry):
        """Détecte les anomalies dans une entrée de log.
        
        Args:
            log_entry (dict): Entrée de log à analyser
            
        Returns:
            list: Liste des règles déclenchées
        """
        try:
            triggered_rules = []
            
            for rule in self.rules:
                if self._check_rule(rule, log_entry):
                    triggered_rules.append({
                        'rule_name': rule['name'],
                        'severity': rule['severity'],
                        'description': rule.get('description', ''),
                        'timestamp': datetime.now().isoformat()
                    })
            
            return triggered_rules
            
        except Exception as e:
            logger.error("Error detecting anomalies: %s", str(e))
            return []
    
    def _check_rule(self, rule, log_entry):
        """Vérifie si une règle est déclenchée par une entrée de log.
        
        Args:
            rule (dict): Règle à vérifier
            log_entry (dict): Entrée de log
            
        Returns:
            bool: True si la règle est déclenchée
        """
        try:
            # Vérifier les conditions de la règle
            conditions = rule.get('conditions', {})
            for field, pattern in conditions.items():
                if field not in log_entry:
                    return False
                    
                if not re.search(pattern, str(log_entry[field])):
                    return False
            
            # Vérifier le pattern principal
            log_text = ' '.join(str(v) for v in log_entry.values())
            return bool(re.search(rule['pattern'], log_text))
            
        except Exception as e:
            logger.error("Error checking rule: %s", str(e))
            return False
    
    def save_rules(self, rules_file):
        """Sauvegarde les règles dans un fichier.
        
        Args:
            rules_file (str): Chemin vers le fichier de règles
        """
        try:
            rules_data = {'rules': self.rules}
            with open(rules_file, 'w') as f:
                json.dump(rules_data, f, indent=2)
            logger.info("Saved %d rules to %s", len(self.rules), rules_file)
            
        except Exception as e:
            logger.error("Error saving rules: %s", str(e))
    
    def get_rules(self):
        """Récupère la liste des règles."""
        return self.rules.copy()
    
    def clear_rules(self):
        """Vide la liste des règles."""
        self.rules = []
        logger.info("Cleared all rules") 