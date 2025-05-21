import logging
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope
from sklearn.svm import OneClassSVM
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class BaseAnomalyDetector:
    """Classe de base pour les détecteurs d'anomalies."""
    
    def __init__(self, name):
        """Initialise le détecteur.
        
        Args:
            name (str): Nom du détecteur
        """
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        self.pca = None
    
    def fit(self, X):
        """Entraîne le modèle.
        
        Args:
            X (numpy.ndarray): Données d'entraînement
        """
        raise NotImplementedError
    
    def predict(self, X):
        """Prédit les anomalies.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Prédictions (-1 pour anomalies, 1 pour normal)
        """
        raise NotImplementedError
    
    def predict_proba(self, X):
        """Calcule les scores d'anomalie.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Scores d'anomalie (plus élevé = plus anormal)
        """
        raise NotImplementedError
    
    def save(self, path):
        """Sauvegarde le modèle.
        
        Args:
            path (str): Chemin de sauvegarde
        """
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'pca': self.pca
            }
            joblib.dump(model_data, path)
            logger.info("Model saved to %s", path)
        except Exception as e:
            logger.error("Error saving model: %s", str(e))
            raise
    
    @classmethod
    def load(cls, path):
        """Charge le modèle.
        
        Args:
            path (str): Chemin du modèle
            
        Returns:
            BaseAnomalyDetector: Instance du détecteur
        """
        try:
            model_data = joblib.load(path)
            detector = cls(model_data['model'])
            detector.scaler = model_data['scaler']
            detector.pca = model_data['pca']
            return detector
        except Exception as e:
            logger.error("Error loading model: %s", str(e))
            raise

class IsolationForestDetector(BaseAnomalyDetector):
    """Détecteur d'anomalies basé sur Isolation Forest."""
    
    def __init__(self, contamination=0.1, n_estimators=100, max_samples='auto'):
        """Initialise le détecteur.
        
        Args:
            contamination (float): Proportion attendue d'anomalies
            n_estimators (int): Nombre d'arbres
            max_samples (int or str): Nombre d'échantillons par arbre
        """
        super().__init__('isolation_forest')
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples=max_samples,
            random_state=42
        )
    
    def fit(self, X):
        """Entraîne le modèle.
        
        Args:
            X (numpy.ndarray): Données d'entraînement
        """
        try:
            # Normaliser les données
            X_scaled = self.scaler.fit_transform(X)
            
            # Réduire la dimensionnalité si nécessaire
            if X.shape[1] > 100:
                self.pca = PCA(n_components=100)
                X_scaled = self.pca.fit_transform(X_scaled)
            
            # Entraîner le modèle
            self.model.fit(X_scaled)
            
        except Exception as e:
            logger.error("Error fitting model: %s", str(e))
            raise
    
    def predict(self, X):
        """Prédit les anomalies.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Prédictions (-1 pour anomalies, 1 pour normal)
        """
        try:
            X_scaled = self.scaler.transform(X)
            if self.pca:
                X_scaled = self.pca.transform(X_scaled)
            return self.model.predict(X_scaled)
        except Exception as e:
            logger.error("Error predicting: %s", str(e))
            raise
    
    def predict_proba(self, X):
        """Calcule les scores d'anomalie.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Scores d'anomalie (plus élevé = plus anormal)
        """
        try:
            X_scaled = self.scaler.transform(X)
            if self.pca:
                X_scaled = self.pca.transform(X_scaled)
            return -self.model.score_samples(X_scaled)
        except Exception as e:
            logger.error("Error computing anomaly scores: %s", str(e))
            raise

class LocalOutlierFactorDetector(BaseAnomalyDetector):
    """Détecteur d'anomalies basé sur Local Outlier Factor."""
    
    def __init__(self, n_neighbors=20, contamination=0.1):
        """Initialise le détecteur.
        
        Args:
            n_neighbors (int): Nombre de voisins
            contamination (float): Proportion attendue d'anomalies
        """
        super().__init__('local_outlier_factor')
        self.model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=contamination,
            novelty=True
        )
    
    def fit(self, X):
        """Entraîne le modèle.
        
        Args:
            X (numpy.ndarray): Données d'entraînement
        """
        try:
            X_scaled = self.scaler.fit_transform(X)
            if self.pca:
                X_scaled = self.pca.fit_transform(X_scaled)
            self.model.fit(X_scaled)
        except Exception as e:
            logger.error("Error fitting model: %s", str(e))
            raise
    
    def predict(self, X):
        """Prédit les anomalies.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Prédictions (-1 pour anomalies, 1 pour normal)
        """
        try:
            X_scaled = self.scaler.transform(X)
            if self.pca:
                X_scaled = self.pca.transform(X_scaled)
            return self.model.predict(X_scaled)
        except Exception as e:
            logger.error("Error predicting: %s", str(e))
            raise
    
    def predict_proba(self, X):
        """Calcule les scores d'anomalie.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Scores d'anomalie (plus élevé = plus anormal)
        """
        try:
            X_scaled = self.scaler.transform(X)
            if self.pca:
                X_scaled = self.pca.transform(X_scaled)
            return -self.model.score_samples(X_scaled)
        except Exception as e:
            logger.error("Error computing anomaly scores: %s", str(e))
            raise

class EllipticEnvelopeDetector(BaseAnomalyDetector):
    """Détecteur d'anomalies basé sur Elliptic Envelope."""
    
    def __init__(self, contamination=0.1):
        """Initialise le détecteur.
        
        Args:
            contamination (float): Proportion attendue d'anomalies
        """
        super().__init__('elliptic_envelope')
        self.model = EllipticEnvelope(
            contamination=contamination,
            random_state=42
        )
    
    def fit(self, X):
        """Entraîne le modèle.
        
        Args:
            X (numpy.ndarray): Données d'entraînement
        """
        try:
            X_scaled = self.scaler.fit_transform(X)
            if self.pca:
                X_scaled = self.pca.fit_transform(X_scaled)
            self.model.fit(X_scaled)
        except Exception as e:
            logger.error("Error fitting model: %s", str(e))
            raise
    
    def predict(self, X):
        """Prédit les anomalies.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Prédictions (-1 pour anomalies, 1 pour normal)
        """
        try:
            X_scaled = self.scaler.transform(X)
            if self.pca:
                X_scaled = self.pca.transform(X_scaled)
            return self.model.predict(X_scaled)
        except Exception as e:
            logger.error("Error predicting: %s", str(e))
            raise
    
    def predict_proba(self, X):
        """Calcule les scores d'anomalie.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Scores d'anomalie (plus élevé = plus anormal)
        """
        try:
            X_scaled = self.scaler.transform(X)
            if self.pca:
                X_scaled = self.pca.transform(X_scaled)
            return -self.model.score_samples(X_scaled)
        except Exception as e:
            logger.error("Error computing anomaly scores: %s", str(e))
            raise

class OneClassSVMDetector(BaseAnomalyDetector):
    """Détecteur d'anomalies basé sur One-Class SVM."""
    
    def __init__(self, nu=0.1, kernel='rbf'):
        """Initialise le détecteur.
        
        Args:
            nu (float): Paramètre de régularisation
            kernel (str): Type de noyau
        """
        super().__init__('one_class_svm')
        self.model = OneClassSVM(
            nu=nu,
            kernel=kernel
        )
    
    def fit(self, X):
        """Entraîne le modèle.
        
        Args:
            X (numpy.ndarray): Données d'entraînement
        """
        try:
            X_scaled = self.scaler.fit_transform(X)
            if self.pca:
                X_scaled = self.pca.fit_transform(X_scaled)
            self.model.fit(X_scaled)
        except Exception as e:
            logger.error("Error fitting model: %s", str(e))
            raise
    
    def predict(self, X):
        """Prédit les anomalies.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Prédictions (-1 pour anomalies, 1 pour normal)
        """
        try:
            X_scaled = self.scaler.transform(X)
            if self.pca:
                X_scaled = self.pca.transform(X_scaled)
            return self.model.predict(X_scaled)
        except Exception as e:
            logger.error("Error predicting: %s", str(e))
            raise
    
    def predict_proba(self, X):
        """Calcule les scores d'anomalie.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Scores d'anomalie (plus élevé = plus anormal)
        """
        try:
            X_scaled = self.scaler.transform(X)
            if self.pca:
                X_scaled = self.pca.transform(X_scaled)
            return -self.model.score_samples(X_scaled)
        except Exception as e:
            logger.error("Error computing anomaly scores: %s", str(e))
            raise

class EnsembleAnomalyDetector:
    """Ensemble de détecteurs d'anomalies."""
    
    def __init__(self, detectors=None):
        """Initialise l'ensemble.
        
        Args:
            detectors (list): Liste de détecteurs
        """
        self.detectors = detectors or [
            IsolationForestDetector(),
            LocalOutlierFactorDetector(),
            EllipticEnvelopeDetector(),
            OneClassSVMDetector()
        ]
    
    def fit(self, X):
        """Entraîne tous les détecteurs.
        
        Args:
            X (numpy.ndarray): Données d'entraînement
        """
        for detector in self.detectors:
            detector.fit(X)
    
    def predict(self, X):
        """Prédit les anomalies en utilisant le vote majoritaire.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Prédictions (-1 pour anomalies, 1 pour normal)
        """
        predictions = np.array([detector.predict(X) for detector in self.detectors])
        return np.sign(np.sum(predictions, axis=0))
    
    def predict_proba(self, X):
        """Calcule les scores d'anomalie en moyenne.
        
        Args:
            X (numpy.ndarray): Données à prédire
            
        Returns:
            numpy.ndarray: Scores d'anomalie (plus élevé = plus anormal)
        """
        scores = np.array([detector.predict_proba(X) for detector in self.detectors])
        return np.mean(scores, axis=0)
    
    def save(self, path):
        """Sauvegarde tous les détecteurs.
        
        Args:
            path (str): Chemin de sauvegarde
        """
        try:
            os.makedirs(path, exist_ok=True)
            for i, detector in enumerate(self.detectors):
                detector_path = os.path.join(path, f'detector_{i}.pkl')
                detector.save(detector_path)
        except Exception as e:
            logger.error("Error saving ensemble: %s", str(e))
            raise
    
    @classmethod
    def load(cls, path):
        """Charge tous les détecteurs.
        
        Args:
            path (str): Chemin des modèles
            
        Returns:
            EnsembleAnomalyDetector: Instance de l'ensemble
        """
        try:
            detectors = []
            for i in range(len(os.listdir(path))):
                detector_path = os.path.join(path, f'detector_{i}.pkl')
                detector = BaseAnomalyDetector.load(detector_path)
                detectors.append(detector)
            return cls(detectors)
        except Exception as e:
            logger.error("Error loading ensemble: %s", str(e))
            raise 