import logging
import json
import os
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class GUIDataManager:
    """Gestionnaire de données pour l'interface graphique."""
    
    def __init__(self, output_dir='gui_data'):
        """Initialise le gestionnaire de données.
        
        Args:
            output_dir (str): Répertoire de sortie pour les données
        """
        self.output_dir = output_dir
        self.anomalies_data = []
        self.stats_data = []
        
        # Créer le répertoire de sortie
        os.makedirs(output_dir, exist_ok=True)
    
    def add_anomalies(self, anomalies_df):
        """Ajoute des anomalies aux données pour l'interface graphique.
        
        Args:
            anomalies_df (pd.DataFrame): DataFrame contenant les anomalies détectées
        """
        try:
            # Convertir les anomalies en format adapté pour l'interface
            for _, anomaly in anomalies_df.iterrows():
                anomaly_data = {
                    'timestamp': anomaly.get('timestamp', datetime.now()).isoformat(),
                    'client_ip': anomaly.get('client_ip', 'unknown'),
                    'request_uri': anomaly.get('request_uri', 'unknown'),
                    'anomaly_score': float(anomaly.get('anomaly_score', 0.0)),
                    'message': anomaly.get('message', ''),
                    'is_anomaly': bool(anomaly.get('is_anomaly', False))
                }
                self.anomalies_data.append(anomaly_data)
            
            # Sauvegarder les données si nécessaire
            if len(self.anomalies_data) >= 100:  # Sauvegarder tous les 100 points
                self._save_anomalies()
                
        except Exception as e:
            logger.error("Error adding anomalies: %s", str(e))
    
    def update_stats(self, stats):
        """Met à jour les statistiques pour l'interface graphique.
        
        Args:
            stats (dict): Dictionnaire contenant les statistiques
        """
        try:
            # Ajouter timestamp aux statistiques
            stats['timestamp'] = datetime.now().isoformat()
            self.stats_data.append(stats)
            
            # Sauvegarder les statistiques
            self._save_stats()
            
        except Exception as e:
            logger.error("Error updating stats: %s", str(e))
    
    def _save_anomalies(self):
        """Sauvegarde les anomalies dans un fichier."""
        try:
            if not self.anomalies_data:
                return
                
            # Générer le nom du fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f'anomalies_{timestamp}.json')
            
            # Sauvegarder les anomalies
            with open(output_file, 'w') as f:
                json.dump(self.anomalies_data, f, indent=2)
                
            # Réinitialiser les données
            self.anomalies_data = []
            
            logger.info("Anomalies data saved to %s", output_file)
            
        except Exception as e:
            logger.error("Error saving anomalies: %s", str(e))
    
    def _save_stats(self):
        """Sauvegarde les statistiques dans un fichier."""
        try:
            if not self.stats_data:
                return
                
            # Générer le nom du fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f'stats_{timestamp}.json')
            
            # Sauvegarder les statistiques
            with open(output_file, 'w') as f:
                json.dump(self.stats_data, f, indent=2)
                
            # Réinitialiser les données
            self.stats_data = []
            
            logger.info("Stats data saved to %s", output_file)
            
        except Exception as e:
            logger.error("Error saving stats: %s", str(e))
    
    def get_latest_data(self):
        """Récupère les dernières données pour l'interface graphique."""
        try:
            # Trouver les derniers fichiers
            anomaly_files = sorted([f for f in os.listdir(self.output_dir) if f.startswith('anomalies_')])
            stats_files = sorted([f for f in os.listdir(self.output_dir) if f.startswith('stats_')])
            
            latest_data = {
                'anomalies': [],
                'stats': []
            }
            
            # Charger les dernières anomalies
            if anomaly_files:
                latest_anomalies = os.path.join(self.output_dir, anomaly_files[-1])
                with open(latest_anomalies, 'r') as f:
                    latest_data['anomalies'] = json.load(f)
            
            # Charger les dernières statistiques
            if stats_files:
                latest_stats = os.path.join(self.output_dir, stats_files[-1])
                with open(latest_stats, 'r') as f:
                    latest_data['stats'] = json.load(f)
            
            return latest_data
            
        except Exception as e:
            logger.error("Error getting latest data: %s", str(e))
            return {'anomalies': [], 'stats': []}
    
    def cleanup_old_data(self, max_age_days=7):
        """Nettoie les anciennes données.
        
        Args:
            max_age_days (int): Âge maximum des fichiers en jours
        """
        try:
            current_time = datetime.now()
            max_age = timedelta(days=max_age_days)
            
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if current_time - file_time > max_age:
                    os.remove(file_path)
                    logger.info("Removed old file: %s", file_path)
                    
        except Exception as e:
            logger.error("Error cleaning up old data: %s", str(e)) 