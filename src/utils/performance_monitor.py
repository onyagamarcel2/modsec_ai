import logging
import threading
import time
from datetime import datetime
import pandas as pd
import os
import json

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Moniteur de performance pour le système de détection d'anomalies."""
    
    def __init__(self, interval=60, output_dir='metrics'):
        """Initialise le moniteur de performance.
        
        Args:
            interval (int): Intervalle en secondes entre les mesures
            output_dir (str): Répertoire de sortie pour les métriques
        """
        self.interval = interval
        self.output_dir = output_dir
        self.metrics = {
            'timestamp': [],
            'num_logs': [],
            'num_anomalies': [],
            'processing_time': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        self.running = False
        self.thread = None
        
        # Créer le répertoire de sortie
        os.makedirs(output_dir, exist_ok=True)
    
    def start(self):
        """Démarre le monitoring des performances."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Performance monitoring started")
    
    def stop(self):
        """Arrête le monitoring des performances."""
        self.running = False
        if self.thread:
            self.thread.join()
        self._save_metrics()
        logger.info("Performance monitoring stopped")
    
    def update_metrics(self, num_logs=0, num_anomalies=0, processing_time=0):
        """Met à jour les métriques de performance.
        
        Args:
            num_logs (int): Nombre de logs traités
            num_anomalies (int): Nombre d'anomalies détectées
            processing_time (float): Temps de traitement en secondes
        """
        try:
            current_time = datetime.now()
            
            # Ajouter les métriques
            self.metrics['timestamp'].append(current_time)
            self.metrics['num_logs'].append(num_logs)
            self.metrics['num_anomalies'].append(num_anomalies)
            self.metrics['processing_time'].append(processing_time)
            
            # Ajouter les métriques système
            self.metrics['memory_usage'].append(self._get_memory_usage())
            self.metrics['cpu_usage'].append(self._get_cpu_usage())
            
            # Sauvegarder les métriques si nécessaire
            if len(self.metrics['timestamp']) >= 100:  # Sauvegarder tous les 100 points
                self._save_metrics()
                self._reset_metrics()
                
        except Exception as e:
            logger.error("Error updating metrics: %s", str(e))
    
    def _monitor_loop(self):
        """Boucle principale de monitoring."""
        while self.running:
            try:
                # Mettre à jour les métriques système
                self.update_metrics()
                
                # Attendre l'intervalle
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error("Error in monitoring loop: %s", str(e))
                time.sleep(self.interval)
    
    def _get_memory_usage(self):
        """Obtient l'utilisation de la mémoire."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0
    
    def _get_cpu_usage(self):
        """Obtient l'utilisation du CPU."""
        try:
            import psutil
            return psutil.cpu_percent()
        except:
            return 0
    
    def _save_metrics(self):
        """Sauvegarde les métriques dans un fichier."""
        try:
            if not self.metrics['timestamp']:
                return
                
            # Convertir en DataFrame
            df = pd.DataFrame(self.metrics)
            
            # Générer le nom du fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f'performance_metrics_{timestamp}.csv')
            
            # Sauvegarder les métriques
            df.to_csv(output_file, index=False)
            
            # Sauvegarder les statistiques
            stats = {
                'timestamp': timestamp,
                'total_logs': df['num_logs'].sum(),
                'total_anomalies': df['num_anomalies'].sum(),
                'avg_processing_time': df['processing_time'].mean(),
                'max_processing_time': df['processing_time'].max(),
                'avg_memory_usage': df['memory_usage'].mean(),
                'max_memory_usage': df['memory_usage'].max(),
                'avg_cpu_usage': df['cpu_usage'].mean(),
                'max_cpu_usage': df['cpu_usage'].max()
            }
            
            stats_file = os.path.join(self.output_dir, f'performance_stats_{timestamp}.json')
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
            logger.info("Performance metrics saved to %s", output_file)
            
        except Exception as e:
            logger.error("Error saving metrics: %s", str(e))
    
    def _reset_metrics(self):
        """Réinitialise les métriques."""
        self.metrics = {
            'timestamp': [],
            'num_logs': [],
            'num_anomalies': [],
            'processing_time': [],
            'memory_usage': [],
            'cpu_usage': []
        } 