import logging
from typing import List, Dict, Any
import numpy as np
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

class LogVectorizer:
    """Vectorisation des logs ModSecurity."""
    
    def __init__(self, vectorizer_type: str = "word2vec", **kwargs):
        """
        Initialise le vectoriseur.
        
        Args:
            vectorizer_type: Type de vectorisation ("word2vec" ou "tfidf")
            **kwargs: Paramètres additionnels pour le vectoriseur
        """
        self.vectorizer_type = vectorizer_type
        self.params = kwargs
        self.model = None
        
    def fit(self, logs: List[List[str]]) -> None:
        """
        Entraîne le modèle de vectorisation.
        
        Args:
            logs: Liste de logs tokenizés
        """
        try:
            if self.vectorizer_type == "word2vec":
                self.model = Word2Vec(sentences=logs,
                                   vector_size=self.params.get('size', 100),
                                   window=self.params.get('window', 5),
                                   min_count=self.params.get('min_count', 1),
                                   workers=self.params.get('workers', 4))
            elif self.vectorizer_type == "tfidf":
                self.model = TfidfVectorizer(**self.params)
                self.model.fit([' '.join(log) for log in logs])
            else:
                raise ValueError(f"Type de vectoriseur non supporté: {self.vectorizer_type}")
        except Exception as e:
            logger.error(f"Erreur d'entraînement: {str(e)}")
            raise
            
    def transform(self, logs: List[List[str]]) -> np.ndarray:
        """
        Transforme les logs en vecteurs.
        
        Args:
            logs: Liste de logs tokenizés
            
        Returns:
            Matrice de vecteurs
        """
        try:
            if self.vectorizer_type == "word2vec":
                return self._word2vec_transform(logs)
            elif self.vectorizer_type == "tfidf":
                return self.model.transform([' '.join(log) for log in logs]).toarray()
            else:
                raise ValueError(f"Type de vectoriseur non supporté: {self.vectorizer_type}")
        except Exception as e:
            logger.error(f"Erreur de transformation: {str(e)}")
            raise
            
    def _word2vec_transform(self, logs: List[List[str]]) -> np.ndarray:
        """Transforme les logs avec Word2Vec."""
        vectors = []
        for log in logs:
            # Moyenne des vecteurs des mots présents dans le modèle
            word_vectors = [self.model.wv[word] for word in log 
                          if word in self.model.wv]
            if word_vectors:
                vectors.append(np.mean(word_vectors, axis=0))
            else:
                vectors.append(np.zeros(self.model.vector_size))
        return np.array(vectors)
        
    def save(self, path: str) -> None:
        """Sauvegarde le modèle."""
        try:
            if self.vectorizer_type == "word2vec":
                self.model.save(path)
            elif self.vectorizer_type == "tfidf":
                import joblib
                joblib.dump(self.model, path)
        except Exception as e:
            logger.error(f"Erreur de sauvegarde: {str(e)}")
            raise
            
    def load(self, path: str) -> None:
        """Charge le modèle."""
        try:
            if self.vectorizer_type == "word2vec":
                self.model = Word2Vec.load(path)
            elif self.vectorizer_type == "tfidf":
                import joblib
                self.model = joblib.load(path)
        except Exception as e:
            logger.error(f"Erreur de chargement: {str(e)}")
            raise 