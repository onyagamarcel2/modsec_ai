"""
Module pour la validation des anomalies détectées.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    """Statuts possibles pour la validation d'une anomalie."""
    PENDING = "pending"      # En attente de validation
    VALIDATED = "validated"  # Validée comme anomalie
    NORMAL = "normal"       # Marquée comme normale
    IGNORED = "ignored"     # Ignorée

@dataclass
class AnomalyValidation:
    """Classe représentant la validation d'une anomalie."""
    anomaly_id: str
    timestamp: datetime
    log_sequence: List[Dict]  # Séquence de logs associée
    anomaly_score: float
    detection_model: str
    validation_status: ValidationStatus
    validated_by: Optional[str] = None
    validation_timestamp: Optional[datetime] = None
    validation_notes: Optional[str] = None
    modsec_rule_id: Optional[str] = None

class AnomalyValidator:
    """Classe pour gérer la validation des anomalies."""
    
    def __init__(
        self,
        validation_dir: str,
        modsec_rules_dir: str,
        auto_create_rules: bool = True
    ):
        """
        Initialise le validateur d'anomalies.

        Args:
            validation_dir: Répertoire pour stocker les validations
            modsec_rules_dir: Répertoire des règles ModSecurity
            auto_create_rules: Créer automatiquement des règles pour les anomalies
        """
        self.validation_dir = validation_dir
        self.modsec_rules_dir = modsec_rules_dir
        self.auto_create_rules = auto_create_rules
        
        # Créer les répertoires si nécessaire
        os.makedirs(validation_dir, exist_ok=True)
        os.makedirs(modsec_rules_dir, exist_ok=True)
        
        # Charger les validations existantes
        self.validations: Dict[str, AnomalyValidation] = {}
        self._load_validations()
        
    def _load_validations(self) -> None:
        """Charge les validations depuis le répertoire."""
        try:
            for filename in os.listdir(self.validation_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(self.validation_dir, filename), 'r') as f:
                        data = json.load(f)
                        validation = AnomalyValidation(
                            anomaly_id=data['anomaly_id'],
                            timestamp=datetime.fromisoformat(data['timestamp']),
                            log_sequence=data['log_sequence'],
                            anomaly_score=data['anomaly_score'],
                            detection_model=data['detection_model'],
                            validation_status=ValidationStatus(data['validation_status']),
                            validated_by=data.get('validated_by'),
                            validation_timestamp=datetime.fromisoformat(data['validation_timestamp']) if data.get('validation_timestamp') else None,
                            validation_notes=data.get('validation_notes'),
                            modsec_rule_id=data.get('modsec_rule_id')
                        )
                        self.validations[validation.anomaly_id] = validation
                        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des validations: {str(e)}")
            raise
            
    def _save_validation(self, validation: AnomalyValidation) -> None:
        """
        Sauvegarde une validation dans le répertoire.

        Args:
            validation: La validation à sauvegarder
        """
        try:
            data = asdict(validation)
            data['timestamp'] = data['timestamp'].isoformat()
            if data['validation_timestamp']:
                data['validation_timestamp'] = data['validation_timestamp'].isoformat()
            data['validation_status'] = data['validation_status'].value
            
            filename = f"{validation.anomaly_id}.json"
            with open(os.path.join(self.validation_dir, filename), 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la validation: {str(e)}")
            raise
            
    def create_validation(
        self,
        anomaly_id: str,
        log_sequence: List[Dict],
        anomaly_score: float,
        detection_model: str
    ) -> AnomalyValidation:
        """
        Crée une nouvelle validation pour une anomalie.

        Args:
            anomaly_id: Identifiant unique de l'anomalie
            log_sequence: Séquence de logs associée
            anomaly_score: Score d'anomalie
            detection_model: Modèle ayant détecté l'anomalie

        Returns:
            La validation créée

        Raises:
            ValueError: Si une validation avec le même ID existe déjà
        """
        if anomaly_id in self.validations:
            raise ValueError(f"Une validation avec l'ID {anomaly_id} existe déjà")

        validation = AnomalyValidation(
            anomaly_id=anomaly_id,
            timestamp=datetime.now(),
            log_sequence=log_sequence,
            anomaly_score=anomaly_score,
            detection_model=detection_model,
            validation_status=ValidationStatus.PENDING
        )
        
        # Créer une règle ModSecurity si activé
        if self.auto_create_rules:
            rule_id = self._create_modsec_rule(validation)
            validation.modsec_rule_id = rule_id
            
        # Sauvegarder la validation
        self.validations[anomaly_id] = validation
        self._save_validation(validation)
        
        return validation
        
    def _create_modsec_rule(self, validation: AnomalyValidation) -> str:
        """
        Crée une règle ModSecurity pour une anomalie.

        Args:
            validation: La validation pour laquelle créer la règle

        Returns:
            Identifiant de la règle créée
        """
        try:
            # Générer un ID unique pour la règle
            rule_id = f"ANOMALY_{validation.anomaly_id}"
            
            # Créer la règle
            rule_content = self._generate_modsec_rule(validation)
            
            # Sauvegarder la règle
            rule_path = os.path.join(self.modsec_rules_dir, f"{rule_id}.conf")
            with open(rule_path, 'w') as f:
                f.write(rule_content)
                
            logger.info(f"Règle ModSecurity créée: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la règle ModSecurity: {str(e)}")
            raise
            
    def _generate_modsec_rule(self, validation: AnomalyValidation) -> str:
        """
        Génère le contenu d'une règle ModSecurity.

        Args:
            validation: La validation pour laquelle générer la règle

        Returns:
            Contenu de la règle
        """
        # Extraire les patterns des logs
        patterns = self._extract_patterns(validation.log_sequence)
        
        # Générer la règle
        rule = f"""# Règle générée automatiquement pour l'anomalie {validation.anomaly_id}
SecRule REQUEST_URI "@rx {patterns['uri']}" \\
    "id:{validation.anomaly_id}, \\
    phase:1, \\
    log, \\
    msg:'Anomalie détectée: {validation.detection_model}', \\
    severity:CRITICAL, \\
    tag:'anomaly_detection'"
"""
        return rule
        
    def _extract_patterns(self, log_sequence: List[Dict]) -> Dict[str, str]:
        """
        Extrait les patterns des logs pour la règle.

        Args:
            log_sequence: Séquence de logs

        Returns:
            Dictionnaire des patterns extraits
        """
        # TODO: Implémenter l'extraction des patterns
        # Pour l'instant, retourner des patterns simples
        return {
            'uri': '.*',
            'method': '.*',
            'headers': '.*'
        }
        
    def validate_anomaly(
        self,
        anomaly_id: str,
        status: ValidationStatus,
        validated_by: str,
        notes: Optional[str] = None
    ) -> AnomalyValidation:
        """
        Valide une anomalie.

        Args:
            anomaly_id: Identifiant de l'anomalie
            status: Nouveau statut de validation
            validated_by: Utilisateur ayant validé
            notes: Notes optionnelles

        Returns:
            La validation mise à jour
        """
        if anomaly_id not in self.validations:
            raise ValueError(f"Anomalie non trouvée: {anomaly_id}")
            
        validation = self.validations[anomaly_id]
        
        # Mettre à jour la validation
        validation.validation_status = status
        validation.validated_by = validated_by
        validation.validation_timestamp = datetime.now()
        validation.validation_notes = notes
        
        # Gérer la règle ModSecurity
        if status == ValidationStatus.NORMAL and validation.modsec_rule_id:
            self._remove_modsec_rule(validation.modsec_rule_id)
            validation.modsec_rule_id = None
            
        # Sauvegarder les modifications
        self._save_validation(validation)
        
        return validation
        
    def _remove_modsec_rule(self, rule_id: str) -> None:
        """
        Supprime une règle ModSecurity.

        Args:
            rule_id: Identifiant de la règle à supprimer
        """
        try:
            rule_path = os.path.join(self.modsec_rules_dir, f"{rule_id}.conf")
            if os.path.exists(rule_path):
                os.remove(rule_path)
                logger.info(f"Règle ModSecurity supprimée: {rule_id}")
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la règle ModSecurity: {str(e)}")
            raise
            
    def get_pending_validations(self) -> List[AnomalyValidation]:
        """
        Récupère les validations en attente.

        Returns:
            Liste des validations en attente
        """
        return [
            validation for validation in self.validations.values()
            if validation.validation_status == ValidationStatus.PENDING
        ]
        
    def get_validation_history(
        self,
        status: Optional[ValidationStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AnomalyValidation]:
        """
        Récupère l'historique des validations avec filtres.

        Args:
            status: Filtrer par statut
            start_time: Filtrer par date de début
            end_time: Filtrer par date de fin

        Returns:
            Liste des validations filtrées
        """
        filtered_validations = list(self.validations.values())
        
        if status:
            filtered_validations = [
                v for v in filtered_validations
                if v.validation_status == status
            ]
            
        if start_time:
            filtered_validations = [
                v for v in filtered_validations
                if v.timestamp >= start_time
            ]
            
        if end_time:
            filtered_validations = [
                v for v in filtered_validations
                if v.timestamp <= end_time
            ]
            
        return filtered_validations 