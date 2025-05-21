#!/usr/bin/env python3
import argparse
import logging
import os
import json
import time
from datetime import datetime
import pandas as pd
import numpy as np
from src.data.log_loader import LogStreamer
from src.preprocessing.modsec_preprocessor import ModSecPreprocessor
from src.features.log_vectorizer import LogVectorizer
from src.models.anomaly_detector import AnomalyDetector
from src.utils.vector_cache import VectorCache
from src.utils.real_time_detector import RealTimeDetector
from src.utils.rule_based_detector import RuleBasedDetector
from src.utils.gui_data_manager import GUIDataManager
from src.utils.notifications import NotificationManager
from src.utils.alert_manager import AlertManager
from src.utils.performance_monitor import PerformanceMonitor

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description='Détection d\'anomalies en temps réel')
    
    # Arguments existants
    parser.add_argument('--log-file', type=str, required=True,
                      help='Chemin vers le fichier de logs ModSecurity')
    parser.add_argument('--model-dir', type=str, required=True,
                      help='Répertoire contenant les modèles entraînés')
    parser.add_argument('--output-dir', type=str, default='anomalies',
                      help='Répertoire de sortie pour les anomalies détectées')
    parser.add_argument('--threshold', type=float, default=0.5,
                      help='Seuil de détection d\'anomalies')
    parser.add_argument('--batch-size', type=int, default=10,
                      help='Taille du lot de logs à traiter')
    parser.add_argument('--check-interval', type=int, default=5,
                      help='Intervalle de vérification des nouveaux logs (secondes)')
    
    # Nouveaux arguments pour les optimisations
    parser.add_argument('--enable-cache', action='store_true',
                      help='Activer la mise en cache des vecteurs')
    parser.add_argument('--cache-dir', type=str, default='vector_cache',
                      help='Répertoire de stockage du cache')
    parser.add_argument('--cache-size', type=int, default=10000,
                      help='Taille maximale du cache')
    parser.add_argument('--cache-ttl', type=int, default=24,
                      help='Durée de vie du cache en heures')
    
    parser.add_argument('--window-size', type=int, default=1000,
                      help='Taille de la fenêtre glissante')
    parser.add_argument('--min-anomaly-ratio', type=float, default=0.1,
                      help='Ratio minimum d\'anomalies pour déclencher une alerte')
    parser.add_argument('--adaptive-threshold', action='store_true',
                      help='Utiliser un seuil adaptatif')
    
    parser.add_argument('--rules-file', type=str,
                      help='Chemin vers le fichier de règles')
    
    parser.add_argument('--gui-data-dir', type=str, default='gui_data',
                      help='Répertoire pour les données de l\'interface graphique')
    parser.add_argument('--max-data-age', type=int, default=7,
                      help='Âge maximum des données en jours')
    
    # Notification settings
    parser.add_argument('--enable-notifications', action='store_true',
                      help='Enable anomaly notifications')
    parser.add_argument('--notification-type', type=str, default='email',
                      choices=['email', 'slack', 'webhook'],
                      help='Type of notification to send')
    parser.add_argument('--notification-config', type=str,
                      help='Path to notification configuration file')
    
    # Alert settings
    parser.add_argument('--alert-threshold', type=int, default=5,
                      help='Number of anomalies to trigger an alert')
    parser.add_argument('--alert-window', type=int, default=300,
                      help='Time window in seconds for alert threshold')
    
    # Performance monitoring
    parser.add_argument('--enable-monitoring', action='store_true',
                      help='Enable performance monitoring')
    parser.add_argument('--monitoring-interval', type=int, default=60,
                      help='Interval in seconds for performance monitoring')
    
    return parser.parse_args()

def load_models(model_dir):
    """Charge les modèles entraînés."""
    try:
        # Charger les métadonnées
        metadata_file = os.path.join(model_dir, 'metadata.json')
        if not os.path.exists(metadata_file):
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Charger les modèles
        vectorizer = LogVectorizer.load(os.path.join(model_dir, 'vectorizer.pkl'))
        detector = AnomalyDetector.load(os.path.join(model_dir, 'detector.pkl'))
        
        return vectorizer, detector, metadata
        
    except Exception as e:
        logger.error("Error loading models: %s", str(e))
        raise

def process_logs(logs_df, vectorizer, detector, vector_cache=None, 
                real_time_detector=None, rule_detector=None):
    """Traite les logs et détecte les anomalies."""
    try:
        # Prétraiter les logs
        preprocessor = ModSecPreprocessor()
        processed_logs = preprocessor.transform(logs_df)
        
        # Vectoriser les logs
        if vector_cache:
            vectors = []
            for _, log in processed_logs.iterrows():
                # Vérifier le cache
                cache_key = ' '.join(log['tokens'])
                vector = vector_cache.get(cache_key)
                
                if vector is None:
                    # Vectoriser et mettre en cache
                    vector = vectorizer.transform([log['tokens']])[0]
                    vector_cache.put(cache_key, vector)
                
                vectors.append(vector)
            vectors = np.array(vectors)
        else:
            vectors = vectorizer.transform(processed_logs['tokens'])
        
        # Détecter les anomalies
        if real_time_detector:
            # Utiliser le détecteur en temps réel
            results = []
            for i, vector in enumerate(vectors):
                score = detector.predict_proba([vector])[0]
                result = real_time_detector.update(score)
                if result:
                    results.append(result)
            
            # Convertir les résultats en DataFrame
            anomalies_df = pd.DataFrame(results)
        else:
            # Utiliser le détecteur standard
            scores = detector.predict_proba(vectors)
            anomalies_df = pd.DataFrame({
                'timestamp': processed_logs['timestamp'],
                'client_ip': processed_logs['client_ip'],
                'request_uri': processed_logs['request_uri'],
                'anomaly_score': scores,
                'is_anomaly': scores > args.threshold
            })
        
        # Appliquer les règles si activées
        if rule_detector:
            rule_results = []
            for _, log in processed_logs.iterrows():
                triggered_rules = rule_detector.detect(log)
                if triggered_rules:
                    rule_results.extend(triggered_rules)
            
            if rule_results:
                # Ajouter les résultats des règles aux anomalies
                rule_df = pd.DataFrame(rule_results)
                anomalies_df = pd.concat([anomalies_df, rule_df], axis=1)
        
        return anomalies_df
        
    except Exception as e:
        logger.error("Error processing logs: %s", str(e))
        return pd.DataFrame()

def save_anomalies(anomalies_df, output_dir, timestamp=None):
    """Sauvegarde les anomalies détectées."""
    try:
        if anomalies_df.empty:
            return
            
        # Créer le répertoire de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer le nom du fichier
        if timestamp is None:
            timestamp = datetime.now()
        filename = f'anomalies_{timestamp.strftime("%Y%m%d_%H%M%S")}.csv'
        output_file = os.path.join(output_dir, filename)
        
        # Sauvegarder les anomalies
        anomalies_df.to_csv(output_file, index=False)
        logger.info("Anomalies saved to %s", output_file)
        
    except Exception as e:
        logger.error("Error saving anomalies: %s", str(e))

def monitor_logs(args):
    """Surveille les logs en temps réel."""
    try:
        # Charger les modèles
        vectorizer, detector, metadata = load_models(args.model_dir)
        
        # Initialiser les composants d'optimisation
        vector_cache = None
        if args.enable_cache:
            vector_cache = VectorCache(
                cache_dir=args.cache_dir,
                max_size=args.cache_size,
                ttl_hours=args.cache_ttl
            )
        
        real_time_detector = RealTimeDetector(
            window_size=args.window_size,
            min_anomaly_ratio=args.min_anomaly_ratio,
            adaptive_threshold=args.adaptive_threshold
        )
        
        rule_detector = None
        if args.rules_file:
            rule_detector = RuleBasedDetector(args.rules_file)
        
        # Initialiser le gestionnaire de données GUI
        gui_manager = GUIDataManager(args.gui_data_dir)
        
        # Initialiser le streamer de logs
        streamer = LogStreamer(args.log_file)
        
        # Initialiser les composants de notification
        notification_manager = None
        if args.enable_notifications:
            notification_manager = NotificationManager(
                notification_type=args.notification_type,
                config_file=args.notification_config
            )
        
        # Initialiser le gestionnaire d'alerte
        alert_manager = AlertManager(
            threshold=args.alert_threshold,
            window=args.alert_window,
            notification_manager=notification_manager
        )
        
        # Initialiser le moniteur de performance
        performance_monitor = None
        if args.enable_monitoring:
            performance_monitor = PerformanceMonitor(
                interval=args.monitoring_interval,
                output_dir=args.output_dir
            )
            performance_monitor.start()
        
        # Boucle principale de surveillance
        while True:
            try:
                # Lire les nouveaux logs
                new_logs = streamer.read_new_logs(batch_size=args.batch_size)
                if new_logs.empty:
                    time.sleep(args.check_interval)
                    continue
                
                # Traiter les logs
                anomalies_df = process_logs(
                    new_logs, vectorizer, detector,
                    vector_cache=vector_cache,
                    real_time_detector=real_time_detector,
                    rule_detector=rule_detector
                )
                
                if not anomalies_df.empty:
                    # Sauvegarder les anomalies
                    save_anomalies(anomalies_df, args.output_dir)
                    
                    # Ajouter les anomalies aux données GUI
                    gui_manager.add_anomalies(anomalies_df)
                    
                    # Mettre à jour les statistiques
                    stats = {
                        'total_logs': len(new_logs),
                        'total_anomalies': len(anomalies_df),
                        'anomaly_ratio': len(anomalies_df) / len(new_logs),
                        'timestamp': datetime.now().isoformat()
                    }
                    gui_manager.update_stats(stats)
                    
                    # Vérifier les alertes
                    alert_manager.check_anomalies(anomalies_df)
                    
                    # Mettre à jour les métriques de performance
                    if performance_monitor:
                        performance_monitor.update_metrics(
                            num_logs=len(new_logs),
                            num_anomalies=len(anomalies_df),
                            processing_time=time.time() - streamer.last_check_time
                        )
                
                # Nettoyer les anciennes données
                gui_manager.cleanup_old_data(args.max_data_age)
                
            except Exception as e:
                logger.error("Error in monitoring loop: %s", str(e))
                time.sleep(args.check_interval)
                
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error("Error in monitoring: %s", str(e))
    finally:
        # Nettoyage
        if vector_cache:
            vector_cache.clear()
        if performance_monitor:
            performance_monitor.stop()
        if notification_manager:
            notification_manager.close()

def main():
    """Fonction principale."""
    try:
        args = parse_args()
        monitor_logs(args)
    except Exception as e:
        logger.error("Error in main: %s", str(e))
        raise

if __name__ == '__main__':
    main() 