#!/usr/bin/env python3
"""
Script pour tester le système d'alerte.
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.alerts.alert_manager import AlertManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description='Test du système d\'alerte'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/notifications.json',
        help='Chemin vers le fichier de configuration des notifications'
    )
    
    parser.add_argument(
        '--severity',
        type=str,
        choices=['critical', 'high', 'medium', 'low'],
        default='medium',
        help='Niveau de sévérité pour les alertes de test'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Nombre d\'alertes à générer'
    )
    
    return parser.parse_args()

def generate_test_alert(severity: str) -> dict:
    """
    Génère une alerte de test.

    Args:
        severity: Niveau de sévérité

    Returns:
        Dictionnaire contenant les détails de l'alerte
    """
    return {
        'severity': severity,
        'source': 'test_script',
        'message': f'Test alert - {severity} severity',
        'details': {
            'test_id': 'test_123',
            'timestamp': datetime.now().isoformat(),
            'additional_info': 'This is a test alert'
        },
        'score': 0.85 if severity == 'high' else 0.95,
        'model': 'test_model'
    }

def main():
    """Fonction principale."""
    # Parser les arguments
    args = parse_args()
    
    try:
        # Initialiser le gestionnaire d'alertes
        alert_manager = AlertManager(
            config_path=args.config,
            min_severity=args.severity
        )
        
        logger.info(f"Génération de {args.count} alertes de niveau {args.severity}")
        
        # Générer les alertes de test
        for i in range(args.count):
            alert_data = generate_test_alert(args.severity)
            
            # Créer l'alerte
            alert = alert_manager.create_alert(
                severity=alert_data['severity'],
                source=alert_data['source'],
                message=alert_data['message'],
                details=alert_data['details'],
                score=alert_data['score'],
                model=alert_data['model']
            )
            
            logger.info(f"Alerte créée: {alert.message}")
            
        # Afficher l'historique des alertes
        alerts = alert_manager.get_alert_history(severity=args.severity)
        logger.info(f"\nHistorique des alertes ({len(alerts)}):")
        for alert in alerts:
            logger.info(
                f"[{alert.timestamp}] {alert.severity.upper()}: "
                f"{alert.message} (score: {alert.score:.3f})"
            )
            
    except Exception as e:
        logger.error(f"Erreur lors du test: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 