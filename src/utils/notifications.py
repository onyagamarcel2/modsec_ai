import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

logger = logging.getLogger(__name__)

class NotificationManager:
    """Gestionnaire de notifications pour les anomalies détectées."""
    
    def __init__(self, notification_type='email', config_file=None):
        """Initialise le gestionnaire de notifications.
        
        Args:
            notification_type (str): Type de notification ('email', 'slack', 'webhook')
            config_file (str): Chemin vers le fichier de configuration
        """
        self.notification_type = notification_type
        self.config = self._load_config(config_file)
        
    def _load_config(self, config_file):
        """Charge la configuration depuis un fichier."""
        if not config_file or not os.path.exists(config_file):
            return {}
            
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error loading notification config: %s", str(e))
            return {}
    
    def send_notification(self, subject, message, **kwargs):
        """Envoie une notification.
        
        Args:
            subject (str): Sujet de la notification
            message (str): Contenu de la notification
            **kwargs: Arguments supplémentaires spécifiques au type de notification
        """
        try:
            if self.notification_type == 'email':
                self._send_email(subject, message)
            elif self.notification_type == 'slack':
                self._send_slack(subject, message)
            elif self.notification_type == 'webhook':
                self._send_webhook(subject, message, **kwargs)
            else:
                logger.error("Unsupported notification type: %s", self.notification_type)
                
        except Exception as e:
            logger.error("Error sending notification: %s", str(e))
    
    def _send_email(self, subject, message):
        """Envoie une notification par email."""
        try:
            # Configuration SMTP
            smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.config.get('smtp_port', 587)
            smtp_user = self.config.get('smtp_user')
            smtp_password = self.config.get('smtp_password')
            recipient = self.config.get('recipient')
            
            if not all([smtp_user, smtp_password, recipient]):
                raise ValueError("Missing email configuration")
            
            # Création du message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Envoi du message
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                
            logger.info("Email notification sent successfully")
            
        except Exception as e:
            logger.error("Error sending email notification: %s", str(e))
            raise
    
    def _send_slack(self, subject, message):
        """Envoie une notification sur Slack."""
        try:
            webhook_url = self.config.get('webhook_url')
            if not webhook_url:
                raise ValueError("Missing Slack webhook URL")
            
            # Formatage du message Slack
            slack_message = {
                "text": f"*{subject}*\n{message}"
            }
            
            # Envoi du message
            response = requests.post(webhook_url, json=slack_message)
            response.raise_for_status()
            
            logger.info("Slack notification sent successfully")
            
        except Exception as e:
            logger.error("Error sending Slack notification: %s", str(e))
            raise
    
    def _send_webhook(self, subject, message, **kwargs):
        """Envoie une notification via webhook."""
        try:
            webhook_url = self.config.get('webhook_url')
            if not webhook_url:
                raise ValueError("Missing webhook URL")
            
            # Formatage du message
            payload = {
                "subject": subject,
                "message": message,
                **kwargs
            }
            
            # Envoi du message
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Webhook notification sent successfully")
            
        except Exception as e:
            logger.error("Error sending webhook notification: %s", str(e))
            raise
    
    def close(self):
        """Ferme les connexions si nécessaire."""
        pass  # À implémenter si nécessaire 