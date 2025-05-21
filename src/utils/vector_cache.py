import logging
import numpy as np
from datetime import datetime, timedelta
import hashlib
import json
import os

logger = logging.getLogger(__name__)

class VectorCache:
    """Système de mise en cache pour les vecteurs de logs."""
    
    def __init__(self, cache_dir='vector_cache', max_size=10000, ttl_hours=24):
        """Initialise le cache de vecteurs.
        
        Args:
            cache_dir (str): Répertoire de stockage du cache
            max_size (int): Nombre maximum d'entrées dans le cache
            ttl_hours (int): Durée de vie des entrées en heures
        """
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.cache = {}
        self.access_times = {}
        
        # Créer le répertoire de cache
        os.makedirs(cache_dir, exist_ok=True)
        
        # Charger le cache existant
        self._load_cache()
    
    def _load_cache(self):
        """Charge le cache depuis le disque."""
        try:
            cache_file = os.path.join(self.cache_dir, 'vector_cache.json')
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.cache = {k: np.array(v) for k, v in data['cache'].items()}
                    self.access_times = {k: datetime.fromisoformat(v) 
                                      for k, v in data['access_times'].items()}
                logger.info("Cache loaded with %d entries", len(self.cache))
        except Exception as e:
            logger.error("Error loading cache: %s", str(e))
    
    def _save_cache(self):
        """Sauvegarde le cache sur le disque."""
        try:
            cache_file = os.path.join(self.cache_dir, 'vector_cache.json')
            data = {
                'cache': {k: v.tolist() for k, v in self.cache.items()},
                'access_times': {k: v.isoformat() for k, v in self.access_times.items()}
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            logger.info("Cache saved with %d entries", len(self.cache))
        except Exception as e:
            logger.error("Error saving cache: %s", str(e))
    
    def _get_hash(self, tokens):
        """Génère un hash pour une liste de tokens."""
        return hashlib.md5(' '.join(tokens).encode()).hexdigest()
    
    def _cleanup(self):
        """Nettoie le cache en supprimant les entrées expirées et en limitant la taille."""
        try:
            current_time = datetime.now()
            
            # Supprimer les entrées expirées
            expired_keys = [
                k for k, t in self.access_times.items()
                if current_time - t > self.ttl
            ]
            for k in expired_keys:
                del self.cache[k]
                del self.access_times[k]
            
            # Limiter la taille du cache
            if len(self.cache) > self.max_size:
                # Trier par temps d'accès
                sorted_keys = sorted(
                    self.access_times.keys(),
                    key=lambda k: self.access_times[k]
                )
                # Supprimer les entrées les plus anciennes
                for k in sorted_keys[:len(self.cache) - self.max_size]:
                    del self.cache[k]
                    del self.access_times[k]
            
            # Sauvegarder le cache nettoyé
            self._save_cache()
            
        except Exception as e:
            logger.error("Error cleaning up cache: %s", str(e))
    
    def get(self, tokens):
        """Récupère un vecteur du cache.
        
        Args:
            tokens (list): Liste de tokens
            
        Returns:
            numpy.ndarray or None: Vecteur en cache ou None si non trouvé
        """
        try:
            key = self._get_hash(tokens)
            if key in self.cache:
                # Mettre à jour le temps d'accès
                self.access_times[key] = datetime.now()
                return self.cache[key]
            return None
            
        except Exception as e:
            logger.error("Error getting from cache: %s", str(e))
            return None
    
    def put(self, tokens, vector):
        """Ajoute un vecteur au cache.
        
        Args:
            tokens (list): Liste de tokens
            vector (numpy.ndarray): Vecteur à mettre en cache
        """
        try:
            key = self._get_hash(tokens)
            self.cache[key] = vector
            self.access_times[key] = datetime.now()
            
            # Nettoyer le cache si nécessaire
            if len(self.cache) >= self.max_size:
                self._cleanup()
                
        except Exception as e:
            logger.error("Error putting in cache: %s", str(e))
    
    def clear(self):
        """Vide le cache."""
        try:
            self.cache.clear()
            self.access_times.clear()
            self._save_cache()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error("Error clearing cache: %s", str(e)) 