"""
Module pour la mise à jour incrémentale et le réentraînement des modèles de détection d'anomalies.
"""

import os
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Union
from collections import deque

from src.models.anomaly_detectors import (
    IsolationForestDetector,
    LocalOutlierFactorDetector,
    EllipticEnvelopeDetector,
    OneClassSVMDetector,
    EnsembleAnomalyDetector
)
from src.data.log_loader import ModSecLogLoader
from src.data.preprocessor import ModSecPreprocessor
from src.models.vectorizer import LogVectorizer

logger = logging.getLogger(__name__)

class ModelUpdater:
    """Classe pour gérer la mise à jour incrémentale et le réentraînement des modèles."""
    
    def __init__(
        self,
        model_dir: str,
        window_size: int = 1000,
        update_interval: int = 3600,
        min_samples: int = 100,
        max_samples: int = 10000,
        performance_threshold: float = 0.8
    ):
        """
        Initialise le gestionnaire de mise à jour des modèles.

        Args:
            model_dir: Répertoire contenant les modèles
            window_size: Taille de la fenêtre glissante pour l'analyse
            update_interval: Intervalle de mise à jour en secondes
            min_samples: Nombre minimum d'échantillons pour la mise à jour
            max_samples: Nombre maximum d'échantillons à conserver
            performance_threshold: Seuil de performance pour déclencher le réentraînement
        """
        self.model_dir = model_dir
        self.window_size = window_size
        self.update_interval = update_interval
        self.min_samples = min_samples
        self.max_samples = max_samples
        self.performance_threshold = performance_threshold
        
        # Buffer circulaire pour stocker les données récentes
        self.data_buffer = deque(maxlen=max_samples)
        
        # Horodatage de la dernière mise à jour
        self.last_update = datetime.now()
        
        # Charger les modèles existants
        self.models = self._load_models()
        
        # Initialiser le vectoriseur
        self.vectorizer = LogVectorizer()
        
        # Initialiser le prétraitement
        self.preprocessor = ModSecPreprocessor()
        
        # Métriques de performance
        self.performance_history = {
            'precision': [],
            'recall': [],
            'f1': [],
            'auc': []
        }

    def _load_models(self) -> Dict[str, object]:
        """Charge les modèles depuis le répertoire spécifié."""
        models = {}
        try:
            # Charger chaque type de modèle
            models['isolation_forest'] = IsolationForestDetector.load(
                os.path.join(self.model_dir, 'isolation_forest')
            )
            models['local_outlier_factor'] = LocalOutlierFactorDetector.load(
                os.path.join(self.model_dir, 'local_outlier_factor')
            )
            models['elliptic_envelope'] = EllipticEnvelopeDetector.load(
                os.path.join(self.model_dir, 'elliptic_envelope')
            )
            models['one_class_svm'] = OneClassSVMDetector.load(
                os.path.join(self.model_dir, 'one_class_svm')
            )
            models['ensemble'] = EnsembleAnomalyDetector.load(
                os.path.join(self.model_dir, 'ensemble')
            )
        except Exception as e:
            logger.error(f"Erreur lors du chargement des modèles: {str(e)}")
            raise
        return models

    def update(self, new_data: List[Dict]) -> None:
        """
        Met à jour les modèles avec de nouvelles données.

        Args:
            new_data: Liste de nouvelles données à ajouter
        """
        # Ajouter les nouvelles données au buffer
        self.data_buffer.extend(new_data)
        
        # Vérifier si une mise à jour est nécessaire
        current_time = datetime.now()
        time_since_update = (current_time - self.last_update).total_seconds()
        
        if (len(self.data_buffer) >= self.min_samples and 
            time_since_update >= self.update_interval):
            
            # Préparer les données pour la mise à jour
            processed_data = self._prepare_data()
            
            # Mettre à jour les modèles
            self._update_models(processed_data)
            
            # Évaluer les performances
            performance = self._evaluate_performance(processed_data)
            
            # Vérifier si un réentraînement complet est nécessaire
            if self._should_retrain(performance):
                self._retrain_models(processed_data)
            
            # Mettre à jour l'horodatage
            self.last_update = current_time
            
            # Sauvegarder les modèles
            self._save_models()

    def _prepare_data(self) -> np.ndarray:
        """Prépare les données pour la mise à jour des modèles."""
        # Convertir le buffer en liste
        data = list(self.data_buffer)
        
        # Prétraiter les données
        processed_data = self.preprocessor.preprocess(data)
        
        # Vectoriser les données
        vectors = self.vectorizer.transform(processed_data)
        
        return vectors

    def _update_models(self, vectors: np.ndarray) -> None:
        """
        Met à jour les modèles avec de nouvelles données.

        Args:
            vectors: Vecteurs des données prétraitées
        """
        try:
            # Mettre à jour chaque modèle
            for name, model in self.models.items():
                if hasattr(model, 'partial_fit'):
                    # Mise à jour incrémentale si supportée
                    model.partial_fit(vectors)
                else:
                    # Réentraînement complet sinon
                    model.fit(vectors)
                    
            logger.info("Mise à jour des modèles terminée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des modèles: {str(e)}")
            raise

    def _evaluate_performance(self, vectors: np.ndarray) -> Dict[str, float]:
        """
        Évalue les performances des modèles.

        Args:
            vectors: Vecteurs des données prétraitées

        Returns:
            Dictionnaire des métriques de performance
        """
        performance = {}
        
        try:
            # Évaluer chaque modèle
            for name, model in self.models.items():
                # Obtenir les prédictions
                predictions = model.predict(vectors)
                scores = model.predict_proba(vectors)
                
                # Calculer les métriques
                from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
                
                performance[name] = {
                    'precision': precision_score(vectors, predictions),
                    'recall': recall_score(vectors, predictions),
                    'f1': f1_score(vectors, predictions),
                    'auc': roc_auc_score(vectors, scores)
                }
                
            # Mettre à jour l'historique des performances
            for metric in ['precision', 'recall', 'f1', 'auc']:
                self.performance_history[metric].append(
                    np.mean([p[metric] for p in performance.values()])
                )
                
            return performance
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation des performances: {str(e)}")
            raise

    def _should_retrain(self, performance: Dict[str, Dict[str, float]]) -> bool:
        """
        Détermine si un réentraînement complet est nécessaire.

        Args:
            performance: Dictionnaire des performances actuelles

        Returns:
            True si un réentraînement est nécessaire, False sinon
        """
        # Calculer la moyenne des performances
        avg_performance = np.mean([
            np.mean([p[metric] for p in performance.values()])
            for metric in ['precision', 'recall', 'f1', 'auc']
        ])
        
        # Vérifier si la performance est en dessous du seuil
        if avg_performance < self.performance_threshold:
            logger.warning(
                f"Performance moyenne ({avg_performance:.3f}) en dessous du seuil "
                f"({self.performance_threshold}). Réentraînement nécessaire."
            )
            return True
            
        return False

    def _retrain_models(self, vectors: np.ndarray) -> None:
        """
        Réentraîne complètement les modèles.

        Args:
            vectors: Vecteurs des données prétraitées
        """
        try:
            # Réentraîner chaque modèle
            for name, model in self.models.items():
                model.fit(vectors)
                
            logger.info("Réentraînement des modèles terminé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du réentraînement des modèles: {str(e)}")
            raise

    def _save_models(self) -> None:
        """Sauvegarde les modèles mis à jour."""
        try:
            # Créer le répertoire s'il n'existe pas
            os.makedirs(self.model_dir, exist_ok=True)
            
            # Sauvegarder chaque modèle
            for name, model in self.models.items():
                model.save(os.path.join(self.model_dir, name))
                
            logger.info("Sauvegarde des modèles terminée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des modèles: {str(e)}")
            raise

    def get_performance_history(self) -> Dict[str, List[float]]:
        """
        Retourne l'historique des performances.

        Returns:
            Dictionnaire contenant l'historique des métriques
        """
        return self.performance_history 