"""
Module pour combiner les scores de différents modèles de détection d'anomalies.
"""

import numpy as np
import logging
from typing import Dict, List, Union, Callable
from src.config.model_config import SCORE_OPERATIONS

logger = logging.getLogger(__name__)

class ScoreCombiner:
    """Classe pour combiner les scores de différents modèles."""
    
    def __init__(self, operation: str = 'mean', weights: Dict[str, float] = None):
        """Initialise le combinateur de scores.
        
        Args:
            operation (str): Type d'opération à utiliser pour combiner les scores
            weights (Dict[str, float]): Poids à utiliser pour chaque modèle (pour la moyenne pondérée)
        """
        self.operation = operation
        self.weights = weights or {}
        self._validate_operation()
    
    def _validate_operation(self):
        """Vérifie que l'opération est valide."""
        if self.operation not in SCORE_OPERATIONS:
            raise ValueError(f"Opération invalide: {self.operation}. "
                           f"Opérations valides: {list(SCORE_OPERATIONS.keys())}")
    
    def combine_scores(self, scores: Dict[str, np.ndarray]) -> np.ndarray:
        """Combine les scores de différents modèles.
        
        Args:
            scores (Dict[str, np.ndarray]): Dictionnaire des scores par modèle
            
        Returns:
            np.ndarray: Scores combinés
        """
        try:
            if not scores:
                raise ValueError("Aucun score fourni")
            
            # Convertir les scores en tableau numpy
            score_arrays = np.array([scores[model] for model in scores])
            
            if self.operation == 'mean':
                return np.mean(score_arrays, axis=0)
            
            elif self.operation == 'max':
                return np.max(score_arrays, axis=0)
            
            elif self.operation == 'min':
                return np.min(score_arrays, axis=0)
            
            elif self.operation == 'weighted_mean':
                if not self.weights:
                    # Utiliser des poids égaux si non spécifiés
                    weights = np.ones(len(scores)) / len(scores)
                else:
                    # Vérifier que tous les modèles ont un poids
                    missing_weights = set(scores.keys()) - set(self.weights.keys())
                    if missing_weights:
                        raise ValueError(f"Poids manquants pour les modèles: {missing_weights}")
                    weights = np.array([self.weights[model] for model in scores])
                
                return np.average(score_arrays, axis=0, weights=weights)
            
            else:
                raise ValueError(f"Opération non implémentée: {self.operation}")
                
        except Exception as e:
            logger.error("Erreur lors de la combinaison des scores: %s", str(e))
            raise
    
    def get_operation_info(self) -> Dict:
        """Retourne les informations sur l'opération actuelle.
        
        Returns:
            Dict: Informations sur l'opération
        """
        return SCORE_OPERATIONS[self.operation]
    
    def set_operation(self, operation: str):
        """Change l'opération de combinaison.
        
        Args:
            operation (str): Nouvelle opération
        """
        self.operation = operation
        self._validate_operation()
    
    def set_weights(self, weights: Dict[str, float]):
        """Change les poids pour la moyenne pondérée.
        
        Args:
            weights (Dict[str, float]): Nouveaux poids
        """
        self.weights = weights 