import logging
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class AlertManager:
    """Gestionnaire d'alertes pour les anomalies détectées."""
    
    def __init__(self, threshold=5, window=300, notification_manager=None):
        """Initialise le gestionnaire d'alertes.
        
        Args:
            threshold (int): Nombre d'anomalies pour déclencher une alerte
            window (int): Fenêtre de temps en secondes pour le seuil
            notification_manager (NotificationManager): Gestionnaire de notifications
        """
        self.threshold = threshold
        self.window = window
        self.notification_manager = notification_manager
        self.anomaly_history = []
    
    def check_anomalies(self, anomalies_df):
        """Vérifie les anomalies et déclenche des alertes si nécessaire.
        
        Args:
            anomalies_df (pd.DataFrame): DataFrame contenant les anomalies détectées
        """
        try:
            # Ajouter les nouvelles anomalies à l'historique
            current_time = datetime.now()
            for _, anomaly in anomalies_df.iterrows():
                self.anomaly_history.append({
                    'timestamp': current_time,
                    'client_ip': anomaly.get('client_ip', 'unknown'),
                    'request_uri': anomaly.get('request_uri', 'unknown'),
                    'anomaly_score': anomaly.get('anomaly_score', 0.0),
                    'message': anomaly.get('message', '')
                })
            
            # Nettoyer l'historique des anomalies plus anciennes que la fenêtre
            cutoff_time = current_time - timedelta(seconds=self.window)
            self.anomaly_history = [
                anomaly for anomaly in self.anomaly_history
                if anomaly['timestamp'] > cutoff_time
            ]
            
            # Vérifier si le seuil est dépassé
            if len(self.anomaly_history) >= self.threshold:
                self._trigger_alert()
                
        except Exception as e:
            logger.error("Error checking anomalies: %s", str(e))
    
    def _trigger_alert(self):
        """Déclenche une alerte."""
        try:
            # Créer un résumé des anomalies
            summary = self._create_anomaly_summary()
            
            # Envoyer une notification si un gestionnaire est configuré
            if self.notification_manager:
                self.notification_manager.send_notification(
                    subject="ALERTE: Anomalies détectées",
                    message=summary
                )
            
            # Réinitialiser l'historique après l'alerte
            self.anomaly_history = []
            
            logger.info("Alert triggered: %s", summary)
            
        except Exception as e:
            logger.error("Error triggering alert: %s", str(e))
    
    def _create_anomaly_summary(self):
        """Crée un résumé des anomalies détectées."""
        try:
            # Convertir l'historique en DataFrame
            df = pd.DataFrame(self.anomaly_history)
            
            # Calculer les statistiques
            total_anomalies = len(df)
            unique_ips = df['client_ip'].nunique()
            avg_score = df['anomaly_score'].mean()
            
            # Identifier les IPs les plus suspectes
            top_ips = df.groupby('client_ip').size().nlargest(3)
            
            # Créer le résumé
            summary = f"""
            Résumé des anomalies détectées:
            - Nombre total d'anomalies: {total_anomalies}
            - Nombre d'IPs uniques: {unique_ips}
            - Score d'anomalie moyen: {avg_score:.2f}
            
            Top 3 des IPs suspectes:
            {top_ips.to_string()}
            
            Détails des dernières anomalies:
            {df.tail(3).to_string()}
            """
            
            return summary
            
        except Exception as e:
            logger.error("Error creating anomaly summary: %s", str(e))
            return "Erreur lors de la création du résumé des anomalies" 