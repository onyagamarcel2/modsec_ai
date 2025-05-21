import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)

class ModSecVectorizer:
    """Vectoriseur de logs ModSecurity."""
    
    def __init__(self):
        """Initialise le vectoriseur avec TF-IDF."""
        self.model = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def vectorize(self, log: str) -> list:
        """
        Vectorise un log.
        
        Args:
            log: Log à vectoriser
            
        Returns:
            Vecteur TF-IDF du log
        """
        try:
            # Transformer le log en vecteur
            vector = self.model.fit_transform([log])
            return vector.toarray()[0].tolist()
        except Exception as e:
            logger.error(f"Erreur de vectorisation: {str(e)}")
            raise
            
    def fit_transform(self, logs: list) -> np.ndarray:
        """
        Apprend le modèle et transforme les logs.
        
        Args:
            logs: Liste de logs à vectoriser
            
        Returns:
            Matrice de vecteurs TF-IDF
        """
        try:
            return self.model.fit_transform(logs).toarray()
        except Exception as e:
            logger.error(f"Erreur de fit_transform: {str(e)}")
            raise
            
    def transform(self, logs: list) -> np.ndarray:
        """
        Transforme les logs avec le modèle appris.
        
        Args:
            logs: Liste de logs à vectoriser
            
        Returns:
            Matrice de vecteurs TF-IDF
        """
        try:
            return self.model.transform(logs).toarray()
        except Exception as e:
            logger.error(f"Erreur de transform: {str(e)}")
            raise 