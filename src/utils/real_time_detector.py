import logging
import numpy as np
from collections import deque
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class RealTimeDetector:
    """Détecteur d'anomalies en temps réel avec fenêtre glissante."""
    
    def __init__(self, window_size=1000, min_anomaly_ratio=0.1, 
                 adaptive_threshold=True, threshold_window=100):
        """Initialise le détecteur en temps réel.
        
        Args:
            window_size (int): Taille de la fenêtre glissante
            min_anomaly_ratio (float): Ratio minimum d'anomalies pour déclencher une alerte
            adaptive_threshold (bool): Utiliser un seuil adaptatif
            threshold_window (int): Taille de la fenêtre pour le calcul du seuil adaptatif
        """
        self.window_size = window_size
        self.min_anomaly_ratio = min_anomaly_ratio
        self.adaptive_threshold = adaptive_threshold
        self.threshold_window = threshold_window
        
        # Fenêtre glissante pour les scores
        self.score_window = deque(maxlen=window_size)
        # Fenêtre glissante pour les seuils
        self.threshold_window = deque(maxlen=threshold_window)
        # Statistiques en temps réel
        self.stats = {
            'total_logs': 0,
            'total_anomalies': 0,
            'current_anomaly_ratio': 0.0,
            'mean_score': 0.0,
            'std_score': 0.0,
            'current_threshold': 0.0
        }
    
    def update(self, score, timestamp=None):
        """Met à jour le détecteur avec un nouveau score.
        
        Args:
            score (float): Score d'anomalie
            timestamp (datetime, optional): Horodatage du score
            
        Returns:
            dict: Résultat de la détection
        """
        try:
            # Ajouter le score à la fenêtre
            self.score_window.append(score)
            
            # Mettre à jour les statistiques
            self.stats['total_logs'] += 1
            self.stats['mean_score'] = np.mean(self.score_window)
            self.stats['std_score'] = np.std(self.score_window)
            
            # Calculer le seuil adaptatif si activé
            if self.adaptive_threshold:
                threshold = self._calculate_adaptive_threshold()
            else:
                threshold = self.stats['mean_score'] + 2 * self.stats['std_score']
            
            self.stats['current_threshold'] = threshold
            
            # Détecter l'anomalie
            is_anomaly = score > threshold
            if is_anomaly:
                self.stats['total_anomalies'] += 1
            
            # Calculer le ratio d'anomalies actuel
            self.stats['current_anomaly_ratio'] = (
                self.stats['total_anomalies'] / self.stats['total_logs']
            )
            
            # Vérifier si une alerte doit être déclenchée
            alert_triggered = (
                len(self.score_window) >= self.window_size and
                self.stats['current_anomaly_ratio'] >= self.min_anomaly_ratio
            )
            
            return {
                'timestamp': timestamp or datetime.now(),
                'score': score,
                'threshold': threshold,
                'is_anomaly': is_anomaly,
                'alert_triggered': alert_triggered,
                'stats': self.stats.copy()
            }
            
        except Exception as e:
            logger.error("Error updating detector: %s", str(e))
            return None
    
    def _calculate_adaptive_threshold(self):
        """Calcule un seuil adaptatif basé sur les scores récents."""
        try:
            if len(self.score_window) < 2:
                return float('inf')
            
            # Calculer la moyenne et l'écart-type sur la fenêtre
            mean = np.mean(self.score_window)
            std = np.std(self.score_window)
            
            # Ajuster le seuil en fonction de la distribution
            if std == 0:
                return mean + 1.0
            
            # Utiliser un multiple de l'écart-type qui s'adapte à la distribution
            z_scores = np.abs((np.array(self.score_window) - mean) / std)
            threshold_multiplier = np.percentile(z_scores, 95)
            
            return mean + threshold_multiplier * std
            
        except Exception as e:
            logger.error("Error calculating adaptive threshold: %s", str(e))
            return float('inf')
    
    def get_stats(self):
        """Récupère les statistiques actuelles."""
        return self.stats.copy()
    
    def reset(self):
        """Réinitialise le détecteur."""
        self.score_window.clear()
        self.threshold_window.clear()
        self.stats = {
            'total_logs': 0,
            'total_anomalies': 0,
            'current_anomaly_ratio': 0.0,
            'mean_score': 0.0,
            'std_score': 0.0,
            'current_threshold': 0.0
        } 