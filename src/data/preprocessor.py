import re
import logging
from typing import List, Dict, Any, Union
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

class ModSecPreprocessor:
    """Prétraitement des logs ModSecurity."""
    
    def __init__(self):
        """Initialise le prétraitement et télécharge les ressources NLTK nécessaires."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
    def preprocess(self, data: Union[str, pd.DataFrame]) -> Union[str, pd.DataFrame]:
        """
        Prétraite les logs ModSecurity.
        
        Args:
            data: Log ou DataFrame à prétraiter
            
        Returns:
            Log ou DataFrame prétraité
        """
        try:
            if isinstance(data, str):
                # Prétraitement d'une chaîne
                return self._preprocess_string(data)
            elif isinstance(data, pd.DataFrame):
                # Prétraitement d'un DataFrame
                return self._preprocess_dataframe(data)
            else:
                raise ValueError("Type de données non supporté")
        except Exception as e:
            logger.error(f"Erreur de prétraitement: {str(e)}")
            raise
            
    def _preprocess_string(self, text: str) -> str:
        """
        Prétraite une chaîne de caractères.
        
        Args:
            text: Texte à prétraiter
            
        Returns:
            Texte prétraité
        """
        # Nettoyage basique
        text = text.lower().strip()
        
        # Tokenization
        tokens = word_tokenize(text)
        
        # Reconstruction
        return ' '.join(tokens)
            
    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prétraite un DataFrame.
        
        Args:
            df: DataFrame à prétraiter
            
        Returns:
            DataFrame prétraité
        """
        # Nettoyage des colonnes
        df = self._clean_columns(df)
        
        # Extraction des caractéristiques
        df = self._extract_features(df)
        
        # Tokenization
        df = self._tokenize_logs(df)
        
        return df
        
    def _clean_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie et standardise les colonnes."""
        # Suppression des colonnes vides
        df = df.dropna(axis=1, how='all')
        
        # Standardisation des noms de colonnes
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        return df
        
    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrait des caractéristiques des logs."""
        # Extraction des patterns communs
        df['ip_pattern'] = df['client_ip'].apply(self._extract_ip_pattern)
        df['uri_pattern'] = df['request_uri'].apply(self._extract_uri_pattern)
        
        return df
        
    def _tokenize_logs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tokenize les messages de log."""
        df['tokens'] = df['message'].apply(lambda x: word_tokenize(str(x).lower()))
        return df
        
    def _extract_ip_pattern(self, ip: str) -> str:
        """Extrait un pattern d'IP."""
        if not ip:
            return ''
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return ip
        
    def _extract_uri_pattern(self, uri: str) -> str:
        """Extrait un pattern d'URI."""
        if not uri:
            return ''
        # Remplace les segments numériques par *
        pattern = re.sub(r'/\d+', '/*', uri)
        return pattern 