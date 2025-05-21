"""
Module pour visualiser les résultats d'entraînement et de classification.
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Union, Optional
from sklearn.metrics import roc_curve, auc
from src.config.model_config import VISUALIZATIONS

logger = logging.getLogger(__name__)

class ResultVisualizer:
    """Classe pour visualiser les résultats d'entraînement et de classification."""
    
    def __init__(self, output_dir: str):
        """Initialise le visualiseur de résultats.
        
        Args:
            output_dir (str): Répertoire de sortie pour les graphiques
        """
        self.output_dir = output_dir
    
    def plot_training_curves(self, history: Dict[str, List[float]], 
                           model_name: str, timestamp: str):
        """Trace les courbes d'entraînement.
        
        Args:
            history (Dict[str, List[float]]): Historique des métriques
            model_name (str): Nom du modèle
            timestamp (str): Horodatage pour le nom du fichier
        """
        try:
            plots_dir = f"{self.output_dir}/plots/training"
            os.makedirs(plots_dir, exist_ok=True)
            
            for metric, values in history.items():
                plt.figure(figsize=(10, 6))
                plt.plot(values, label=metric)
                plt.title(f'{metric} - {model_name}')
                plt.xlabel('Époque')
                plt.ylabel(metric)
                plt.legend()
                plt.grid(True)
                
                # Sauvegarder le graphique
                plt.savefig(f"{plots_dir}/{model_name}_{metric}_{timestamp}.png")
                plt.close()
                
        except Exception as e:
            logger.error("Erreur lors de la création des courbes d'entraînement: %s", str(e))
            raise
    
    def plot_confusion_matrix(self, cm: np.ndarray, model_name: str, timestamp: str):
        """Trace la matrice de confusion.
        
        Args:
            cm (np.ndarray): Matrice de confusion
            model_name (str): Nom du modèle
            timestamp (str): Horodatage pour le nom du fichier
        """
        try:
            plots_dir = f"{self.output_dir}/plots/classification"
            os.makedirs(plots_dir, exist_ok=True)
            
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title(f'Matrice de confusion - {model_name}')
            plt.ylabel('Vraie valeur')
            plt.xlabel('Prédiction')
            
            # Sauvegarder le graphique
            plt.savefig(f"{plots_dir}/{model_name}_confusion_matrix_{timestamp}.png")
            plt.close()
            
        except Exception as e:
            logger.error("Erreur lors de la création de la matrice de confusion: %s", str(e))
            raise
    
    def plot_score_distribution(self, scores: np.ndarray, model_name: str, timestamp: str):
        """Trace la distribution des scores d'anomalie.
        
        Args:
            scores (np.ndarray): Scores d'anomalie
            model_name (str): Nom du modèle
            timestamp (str): Horodatage pour le nom du fichier
        """
        try:
            plots_dir = f"{self.output_dir}/plots/classification"
            os.makedirs(plots_dir, exist_ok=True)
            
            plt.figure(figsize=(10, 6))
            sns.histplot(scores, bins=50)
            plt.title(f'Distribution des scores - {model_name}')
            plt.xlabel('Score d\'anomalie')
            plt.ylabel('Fréquence')
            
            # Sauvegarder le graphique
            plt.savefig(f"{plots_dir}/{model_name}_score_distribution_{timestamp}.png")
            plt.close()
            
        except Exception as e:
            logger.error("Erreur lors de la création de la distribution des scores: %s", str(e))
            raise
    
    def plot_roc_curve(self, y_true: np.ndarray, scores: np.ndarray, 
                      model_name: str, timestamp: str):
        """Trace la courbe ROC.
        
        Args:
            y_true (np.ndarray): Vraies valeurs
            scores (np.ndarray): Scores d'anomalie
            model_name (str): Nom du modèle
            timestamp (str): Horodatage pour le nom du fichier
        """
        try:
            plots_dir = f"{self.output_dir}/plots/classification"
            os.makedirs(plots_dir, exist_ok=True)
            
            fpr, tpr, _ = roc_curve(y_true, scores)
            roc_auc = auc(fpr, tpr)
            
            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, label=f'ROC (AUC = {roc_auc:.2f})')
            plt.plot([0, 1], [0, 1], 'k--')
            plt.title(f'Courbe ROC - {model_name}')
            plt.xlabel('Taux de faux positifs')
            plt.ylabel('Taux de vrais positifs')
            plt.legend()
            
            # Sauvegarder le graphique
            plt.savefig(f"{plots_dir}/{model_name}_roc_curve_{timestamp}.png")
            plt.close()
            
        except Exception as e:
            logger.error("Erreur lors de la création de la courbe ROC: %s", str(e))
            raise
    
    def plot_model_comparison(self, metrics: Dict[str, Dict[str, float]], 
                            timestamp: str):
        """Trace la comparaison des performances des modèles.
        
        Args:
            metrics (Dict[str, Dict[str, float]]): Métriques par modèle
            timestamp (str): Horodatage pour le nom du fichier
        """
        try:
            plots_dir = f"{self.output_dir}/plots/comparison"
            os.makedirs(plots_dir, exist_ok=True)
            
            # Créer un DataFrame pour les métriques
            df = pd.DataFrame(metrics).T
            
            # Tracer les métriques par modèle
            plt.figure(figsize=(12, 6))
            df.plot(kind='bar')
            plt.title('Comparaison des performances des modèles')
            plt.xlabel('Modèle')
            plt.ylabel('Score')
            plt.legend(title='Métrique')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Sauvegarder le graphique
            plt.savefig(f"{plots_dir}/model_comparison_{timestamp}.png")
            plt.close()
            
            # Tracer la matrice de corrélation des scores
            plt.figure(figsize=(10, 8))
            sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
            plt.title('Corrélation des métriques entre les modèles')
            
            # Sauvegarder le graphique
            plt.savefig(f"{plots_dir}/metric_correlation_{timestamp}.png")
            plt.close()
            
        except Exception as e:
            logger.error("Erreur lors de la création de la comparaison des modèles: %s", str(e))
            raise
    
    def plot_combined_scores(self, scores: Dict[str, np.ndarray], 
                           combined_scores: np.ndarray,
                           operation: str, timestamp: str):
        """Trace les scores individuels et combinés.
        
        Args:
            scores (Dict[str, np.ndarray]): Scores par modèle
            combined_scores (np.ndarray): Scores combinés
            operation (str): Opération de combinaison utilisée
            timestamp (str): Horodatage pour le nom du fichier
        """
        try:
            plots_dir = f"{self.output_dir}/plots/combined"
            os.makedirs(plots_dir, exist_ok=True)
            
            # Tracer les distributions des scores
            plt.figure(figsize=(15, 8))
            
            # Tracer les scores individuels
            for model_name, model_scores in scores.items():
                sns.kdeplot(model_scores, label=model_name)
            
            # Tracer les scores combinés
            sns.kdeplot(combined_scores, label=f'Score combiné ({operation})', 
                       linestyle='--', linewidth=2)
            
            plt.title('Distribution des scores d\'anomalie')
            plt.xlabel('Score')
            plt.ylabel('Densité')
            plt.legend()
            
            # Sauvegarder le graphique
            plt.savefig(f"{plots_dir}/combined_scores_{timestamp}.png")
            plt.close()
            
        except Exception as e:
            logger.error("Erreur lors de la création des scores combinés: %s", str(e))
            raise 