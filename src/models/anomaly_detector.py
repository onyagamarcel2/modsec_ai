import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Détecteur d'anomalies pour les logs ModSecurity."""
    
    def __init__(self, detector_type: str = "isolation_forest", **kwargs):
        """
        Initialise le détecteur d'anomalies.
        
        Args:
            detector_type: Type de détecteur ("isolation_forest")
            **kwargs: Paramètres additionnels pour le détecteur
        """
        self.detector_type = detector_type
        self.params = kwargs
        self.model = None
        self.scaler = StandardScaler()
        
    def fit(self, X: np.ndarray) -> None:
        """
        Entraîne le modèle de détection.
        
        Args:
            X: Matrice de caractéristiques
        """
        try:
            # Normalisation des données
            X_scaled = self.scaler.fit_transform(X)
            
            if self.detector_type == "isolation_forest":
                self.model = IsolationForest(
                    n_estimators=self.params.get('n_estimators', 100),
                    max_samples=self.params.get('max_samples', 'auto'),
                    contamination=self.params.get('contamination', 0.1),
                    random_state=42
                )
                self.model.fit(X_scaled)
            else:
                raise ValueError(f"Type de détecteur non supporté: {self.detector_type}")
        except Exception as e:
            logger.error(f"Erreur d'entraînement: {str(e)}")
            raise
            
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prédit les anomalies.
        
        Args:
            X: Matrice de caractéristiques
            
        Returns:
            Tuple (prédictions, scores)
        """
        try:
            # Normalisation des données
            X_scaled = self.scaler.transform(X)
            
            if self.detector_type == "isolation_forest":
                predictions = self.model.predict(X_scaled)
                scores = -self.model.score_samples(X_scaled)
                
                # Conversion: -1 -> 1 (anomalie), 1 -> 0 (normal)
                predictions = (predictions == -1).astype(int)
                
                return predictions, scores
            else:
                raise ValueError(f"Type de détecteur non supporté: {self.detector_type}")
        except Exception as e:
            logger.error(f"Erreur de prédiction: {str(e)}")
            raise
            
    def save(self, path: str) -> None:
        """Sauvegarde le modèle."""
        try:
            import joblib
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'params': self.params
            }
            joblib.dump(model_data, path)
        except Exception as e:
            logger.error(f"Erreur de sauvegarde: {str(e)}")
            raise
            
    def load(self, path: str) -> None:
        """Charge le modèle."""
        try:
            import joblib
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.params = model_data['params']
        except Exception as e:
            logger.error(f"Erreur de chargement: {str(e)}")
            raise 