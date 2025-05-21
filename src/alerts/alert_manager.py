"""
Module pour la gestion des alertes et notifications de détection d'anomalies.
"""

import os
import json
import logging
import smtplib
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    """Classe représentant une alerte."""
    timestamp: datetime
    severity: str
    source: str
    message: str
    details: Dict
    score: float
    model: str
    status: str = "new"

class AlertManager:
    """Classe pour gérer les alertes et les notifications."""
    
    SEVERITY_LEVELS = {
        'critical': 4,
        'high': 3,
        'medium': 2,
        'low': 1
    }
    
    def __init__(
        self,
        config_path: str,
        alert_history_size: int = 1000,
        min_severity: str = 'medium'
    ):
        """
        Initialise le gestionnaire d'alertes.

        Args:
            config_path: Chemin vers le fichier de configuration
            alert_history_size: Taille maximale de l'historique des alertes
            min_severity: Niveau de sévérité minimum pour les notifications
        """
        self.config_path = config_path
        self.alert_history_size = alert_history_size
        self.min_severity = min_severity
        
        # Charger la configuration
        self.config = self._load_config()
        
        # Historique des alertes
        self.alert_history: List[Alert] = []
        
        # Initialiser les connecteurs de notification
        self._init_notification_connectors()
        
    def _load_config(self) -> Dict:
        """Charge la configuration depuis le fichier."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
            raise
            
    def _init_notification_connectors(self) -> None:
        """Initialise les connecteurs de notification."""
        self.notification_connectors = {}
        
        # Email
        if 'email' in self.config['notifications']:
            self.notification_connectors['email'] = self._create_email_connector()
            
        # Slack
        if 'slack' in self.config['notifications']:
            self.notification_connectors['slack'] = self._create_slack_connector()
            
        # Webhook
        if 'webhook' in self.config['notifications']:
            self.notification_connectors['webhook'] = self._create_webhook_connector()
            
    def _create_email_connector(self) -> Dict:
        """Crée un connecteur pour les notifications par email."""
        email_config = self.config['notifications']['email']
        return {
            'smtp_server': email_config['smtp_server'],
            'smtp_port': email_config['smtp_port'],
            'username': email_config['username'],
            'password': email_config['password'],
            'from_addr': email_config['from_addr'],
            'to_addrs': email_config['to_addrs']
        }
        
    def _create_slack_connector(self) -> Dict:
        """Crée un connecteur pour les notifications Slack."""
        slack_config = self.config['notifications']['slack']
        return {
            'webhook_url': slack_config['webhook_url'],
            'channel': slack_config['channel']
        }
        
    def _create_webhook_connector(self) -> Dict:
        """Crée un connecteur pour les notifications webhook."""
        webhook_config = self.config['notifications']['webhook']
        return {
            'url': webhook_config['url'],
            'headers': webhook_config.get('headers', {}),
            'method': webhook_config.get('method', 'POST')
        }
        
    def create_alert(
        self,
        severity: str,
        source: str,
        message: str,
        details: Dict,
        score: float,
        model: str
    ) -> Alert:
        """
        Crée une nouvelle alerte.

        Args:
            severity: Niveau de sévérité (critical, high, medium, low)
            source: Source de l'alerte
            message: Message de l'alerte
            details: Détails supplémentaires
            score: Score d'anomalie
            model: Nom du modèle ayant détecté l'anomalie

        Returns:
            L'alerte créée
        """
        alert = Alert(
            timestamp=datetime.now(),
            severity=severity,
            source=source,
            message=message,
            details=details,
            score=score,
            model=model
        )
        
        # Ajouter à l'historique
        self.alert_history.append(alert)
        if len(self.alert_history) > self.alert_history_size:
            self.alert_history.pop(0)
            
        # Envoyer les notifications si nécessaire
        if self.SEVERITY_LEVELS[severity] >= self.SEVERITY_LEVELS[self.min_severity]:
            self._send_notifications(alert)
            
        return alert
        
    def _send_notifications(self, alert: Alert) -> None:
        """
        Envoie les notifications pour une alerte.

        Args:
            alert: L'alerte à notifier
        """
        # Email
        if 'email' in self.notification_connectors:
            self._send_email_notification(alert)
            
        # Slack
        if 'slack' in self.notification_connectors:
            self._send_slack_notification(alert)
            
        # Webhook
        if 'webhook' in self.notification_connectors:
            self._send_webhook_notification(alert)
            
    def _send_email_notification(self, alert: Alert) -> None:
        """
        Envoie une notification par email.

        Args:
            alert: L'alerte à notifier
        """
        try:
            connector = self.notification_connectors['email']
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = connector['from_addr']
            msg['To'] = ', '.join(connector['to_addrs'])
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.message}"
            
            # Corps du message
            body = f"""
            Alerte de détection d'anomalie
            
            Sévérité: {alert.severity}
            Source: {alert.source}
            Message: {alert.message}
            Score: {alert.score:.3f}
            Modèle: {alert.model}
            Horodatage: {alert.timestamp}
            
            Détails:
            {json.dumps(alert.details, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Envoyer l'email
            with smtplib.SMTP(connector['smtp_server'], connector['smtp_port']) as server:
                server.starttls()
                server.login(connector['username'], connector['password'])
                server.send_message(msg)
                
            logger.info(f"Notification email envoyée pour l'alerte: {alert.message}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification email: {str(e)}")
            
    def _send_slack_notification(self, alert: Alert) -> None:
        """
        Envoie une notification Slack.

        Args:
            alert: L'alerte à notifier
        """
        try:
            connector = self.notification_connectors['slack']
            
            # Préparer le message
            message = {
                "channel": connector['channel'],
                "text": f"*[{alert.severity.upper()}] {alert.message}*",
                "attachments": [{
                    "color": self._get_severity_color(alert.severity),
                    "fields": [
                        {"title": "Source", "value": alert.source, "short": True},
                        {"title": "Score", "value": f"{alert.score:.3f}", "short": True},
                        {"title": "Modèle", "value": alert.model, "short": True},
                        {"title": "Horodatage", "value": str(alert.timestamp), "short": True},
                        {"title": "Détails", "value": json.dumps(alert.details, indent=2), "short": False}
                    ]
                }]
            }
            
            # Envoyer le message
            response = requests.post(
                connector['webhook_url'],
                json=message
            )
            response.raise_for_status()
            
            logger.info(f"Notification Slack envoyée pour l'alerte: {alert.message}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification Slack: {str(e)}")
            
    def _send_webhook_notification(self, alert: Alert) -> None:
        """
        Envoie une notification webhook.

        Args:
            alert: L'alerte à notifier
        """
        try:
            connector = self.notification_connectors['webhook']
            
            # Préparer les données
            data = asdict(alert)
            data['timestamp'] = data['timestamp'].isoformat()
            
            # Envoyer la requête
            response = requests.request(
                method=connector['method'],
                url=connector['url'],
                headers=connector['headers'],
                json=data
            )
            response.raise_for_status()
            
            logger.info(f"Notification webhook envoyée pour l'alerte: {alert.message}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification webhook: {str(e)}")
            
    def _get_severity_color(self, severity: str) -> str:
        """
        Retourne la couleur correspondant au niveau de sévérité.

        Args:
            severity: Niveau de sévérité

        Returns:
            Code couleur hexadécimal
        """
        colors = {
            'critical': '#FF0000',  # Rouge
            'high': '#FFA500',      # Orange
            'medium': '#FFFF00',    # Jaune
            'low': '#00FF00'        # Vert
        }
        return colors.get(severity, '#808080')  # Gris par défaut
        
    def get_alert_history(
        self,
        severity: Optional[str] = None,
        source: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Alert]:
        """
        Récupère l'historique des alertes avec filtres optionnels.

        Args:
            severity: Filtrer par niveau de sévérité
            source: Filtrer par source
            start_time: Filtrer par date de début
            end_time: Filtrer par date de fin

        Returns:
            Liste des alertes filtrées
        """
        filtered_alerts = self.alert_history
        
        if severity:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.severity == severity
            ]
            
        if source:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.source == source
            ]
            
        if start_time:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.timestamp >= start_time
            ]
            
        if end_time:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.timestamp <= end_time
            ]
            
        return filtered_alerts
        
    def update_alert_status(self, alert: Alert, new_status: str) -> None:
        """
        Met à jour le statut d'une alerte.

        Args:
            alert: L'alerte à mettre à jour
            new_status: Nouveau statut
        """
        alert.status = new_status
        logger.info(f"Statut de l'alerte mis à jour: {alert.message} -> {new_status}") 