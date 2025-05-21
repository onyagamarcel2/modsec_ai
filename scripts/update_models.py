#!/usr/bin/env python3
"""
Script pour la mise à jour incrémentale des modèles de détection d'anomalies.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import List, Dict

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.model_updater import ModelUpdater
from src.data.log_loader import ModSecLogLoader

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description='Mise à jour incrémentale des modèles de détection d\'anomalies'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        required=True,
        help='Chemin vers le fichier de logs ModSecurity'
    )
    
    parser.add_argument(
        '--model-dir',
        type=str,
        required=True,
        help='Répertoire contenant les modèles'
    )
    
    parser.add_argument(
        '--window-size',
        type=int,
        default=1000,
        help='Taille de la fenêtre glissante (défaut: 1000)'
    )
    
    parser.add_argument(
        '--update-interval',
        type=int,
        default=3600,
        help='Intervalle de mise à jour en secondes (défaut: 3600)'
    )
    
    parser.add_argument(
        '--min-samples',
        type=int,
        default=100,
        help='Nombre minimum d\'échantillons pour la mise à jour (défaut: 100)'
    )
    
    parser.add_argument(
        '--max-samples',
        type=int,
        default=10000,
        help='Nombre maximum d\'échantillons à conserver (défaut: 10000)'
    )
    
    parser.add_argument(
        '--performance-threshold',
        type=float,
        default=0.8,
        help='Seuil de performance pour le réentraînement (défaut: 0.8)'
    )
    
    return parser.parse_args()

def main():
    """Fonction principale."""
    # Parser les arguments
    args = parse_args()
    
    try:
        # Initialiser le chargeur de logs
        log_loader = ModSecLogLoader(args.log_file)
        
        # Initialiser le gestionnaire de mise à jour
        updater = ModelUpdater(
            model_dir=args.model_dir,
            window_size=args.window_size,
            update_interval=args.update_interval,
            min_samples=args.min_samples,
            max_samples=args.max_samples,
            performance_threshold=args.performance_threshold
        )
        
        logger.info("Démarrage de la mise à jour des modèles...")
        
        # Boucle principale
        while True:
            try:
                # Charger les nouveaux logs
                new_logs = log_loader.load_new_logs()
                
                if new_logs:
                    logger.info(f"Chargement de {len(new_logs)} nouveaux logs")
                    
                    # Mettre à jour les modèles
                    updater.update(new_logs)
                    
                    # Afficher les performances
                    performance = updater.get_performance_history()
                    logger.info("Performances actuelles:")
                    for metric, values in performance.items():
                        if values:
                            logger.info(f"  {metric}: {values[-1]:.3f}")
                
            except KeyboardInterrupt:
                logger.info("Arrêt demandé par l'utilisateur")
                break
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour: {str(e)}")
                continue
            
    except Exception as e:
        logger.error(f"Erreur fatale: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 