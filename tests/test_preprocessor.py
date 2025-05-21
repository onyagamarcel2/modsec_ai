"""
Tests unitaires pour le prétraitement des logs.
"""

import pytest
import pandas as pd
from src.data.preprocessor import ModSecPreprocessor

@pytest.fixture
def sample_text():
    """Crée un texte de test."""
    return "GET /api/test/123 HTTP/1.1 User-Agent: Mozilla/5.0"

@pytest.fixture
def sample_dataframe():
    """Crée un DataFrame de test."""
    return pd.DataFrame({
        'client_ip': ['192.168.1.1', '10.0.0.1', '172.16.0.1'],
        'request_uri': ['/api/users/123', '/api/products/456', '/api/orders/789'],
        'message': [
            'GET /api/users/123 HTTP/1.1',
            'POST /api/products/456 HTTP/1.1',
            'PUT /api/orders/789 HTTP/1.1'
        ]
    })

def test_preprocessor_initialization():
    """Test l'initialisation du prétraitement."""
    preprocessor = ModSecPreprocessor()
    assert preprocessor is not None

def test_preprocess_string(sample_text):
    """Test le prétraitement d'une chaîne de caractères."""
    preprocessor = ModSecPreprocessor()
    processed = preprocessor.preprocess(sample_text)
    
    assert isinstance(processed, str)
    assert processed == "get /api/test/123 http/1.1 user-agent : mozilla/5.0"

def test_preprocess_dataframe(sample_dataframe):
    """Test le prétraitement d'un DataFrame."""
    preprocessor = ModSecPreprocessor()
    processed = preprocessor.preprocess(sample_dataframe)
    
    assert isinstance(processed, pd.DataFrame)
    assert 'ip_pattern' in processed.columns
    assert 'uri_pattern' in processed.columns
    assert 'tokens' in processed.columns
    assert len(processed) == len(sample_dataframe)

def test_clean_columns(sample_dataframe):
    """Test le nettoyage des colonnes."""
    preprocessor = ModSecPreprocessor()
    cleaned = preprocessor._clean_columns(sample_dataframe)
    
    assert isinstance(cleaned, pd.DataFrame)
    assert all(col.islower() for col in cleaned.columns)
    assert all(' ' not in col for col in cleaned.columns)

def test_extract_features(sample_dataframe):
    """Test l'extraction des caractéristiques."""
    preprocessor = ModSecPreprocessor()
    features = preprocessor._extract_features(sample_dataframe)
    
    assert 'ip_pattern' in features.columns
    assert 'uri_pattern' in features.columns
    assert features['ip_pattern'].iloc[0] == '192.168.*.*'
    assert features['uri_pattern'].iloc[0] == '/api/users/*'

def test_tokenize_logs(sample_dataframe):
    """Test la tokenization des logs."""
    preprocessor = ModSecPreprocessor()
    tokenized = preprocessor._tokenize_logs(sample_dataframe)
    
    assert 'tokens' in tokenized.columns
    assert isinstance(tokenized['tokens'].iloc[0], list)
    assert all(isinstance(token, str) for token in tokenized['tokens'].iloc[0])

def test_extract_ip_pattern():
    """Test l'extraction des patterns d'IP."""
    preprocessor = ModSecPreprocessor()
    
    # Test IP valide
    assert preprocessor._extract_ip_pattern('192.168.1.1') == '192.168.*.*'
    
    # Test IP invalide
    assert preprocessor._extract_ip_pattern('invalid') == 'invalid'
    
    # Test IP vide
    assert preprocessor._extract_ip_pattern('') == ''

def test_extract_uri_pattern():
    """Test l'extraction des patterns d'URI."""
    preprocessor = ModSecPreprocessor()
    
    # Test URI avec segments numériques
    assert preprocessor._extract_uri_pattern('/api/users/123') == '/api/users/*'
    
    # Test URI sans segments numériques
    assert preprocessor._extract_uri_pattern('/api/users') == '/api/users'
    
    # Test URI vide
    assert preprocessor._extract_uri_pattern('') == ''

def test_preprocess_invalid_type():
    """Test le prétraitement avec un type invalide."""
    preprocessor = ModSecPreprocessor()
    with pytest.raises(ValueError):
        preprocessor.preprocess(123)  # Type int non supporté

import unittest
import pandas as pd
import numpy as np

class TestModSecPreprocessor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sample DataFrame for testing
        self.sample_data = pd.DataFrame({
            'timestamp': ['2024-01-26 10:00:00', '2024-01-26 10:01:00'],
            'client_ip': ['192.168.1.1', '192.168.1.2'],
            'request_uri': ['/api/test1', '/api/test2'],
            'message': [
                'Message: Test message 1 [file "/etc/modsecurity/rules/test.conf"] [line "1"] [id "1000"] [severity "CRITICAL"]',
                'Message: Test message 2 [file "/etc/modsecurity/rules/test.conf"] [line "2"] [id "1001"] [severity "WARNING"]'
            ]
        })
        
        # Initialize preprocessor
        self.preprocessor = ModSecPreprocessor()

    def test_clean_columns(self):
        """Test cleaning of DataFrame columns."""
        # Add some empty columns
        self.sample_data['empty_col'] = np.nan
        self.sample_data['duplicate_col'] = self.sample_data['client_ip']
        
        cleaned_df = self.preprocessor._clean_columns(self.sample_data)
        
        # Check if empty columns are removed
        self.assertNotIn('empty_col', cleaned_df.columns)
        
        # Check if column names are standardized
        self.assertTrue(all(col.islower() for col in cleaned_df.columns))

    def test_extract_features(self):
        """Test feature extraction from logs."""
        df = self.preprocessor._extract_features(self.sample_data)
        
        # Check if new features are added
        self.assertIn('ip_pattern', df.columns)
        self.assertIn('uri_pattern', df.columns)
        
        # Check if patterns are correctly extracted
        self.assertEqual(df['ip_pattern'].iloc[0], '192.168.*.*')
        self.assertTrue(df['uri_pattern'].iloc[0].startswith('/api/'))

    def test_tokenize_logs(self):
        """Test log message tokenization."""
        df = self.preprocessor._tokenize_logs(self.sample_data)
        
        # Check if tokens column is added
        self.assertIn('tokens', df.columns)
        
        # Check if tokens are correctly extracted
        self.assertIsInstance(df['tokens'].iloc[0], list)
        self.assertTrue(all(isinstance(token, str) for token in df['tokens'].iloc[0]))

    def test_preprocess(self):
        """Test complete preprocessing pipeline."""
        processed_df = self.preprocessor.preprocess(self.sample_data)
        
        # Check if all preprocessing steps are applied
        self.assertIn('tokens', processed_df.columns)
        self.assertIn('ip_pattern', processed_df.columns)
        self.assertIn('uri_pattern', processed_df.columns)
        
        # Check if original data is preserved
        self.assertIn('timestamp', processed_df.columns)
        self.assertIn('client_ip', processed_df.columns)
        self.assertIn('request_uri', processed_df.columns)
        self.assertIn('message', processed_df.columns)

    def test_extract_ip_pattern(self):
        """Test IP pattern extraction."""
        ip = '192.168.1.100'
        pattern = self.preprocessor._extract_ip_pattern(ip)
        
        # Check if pattern is correctly generated
        self.assertEqual(pattern, '192.168.*.*')

    def test_extract_uri_pattern(self):
        """Test URI pattern extraction."""
        uri = '/api/users/123/profile'
        pattern = self.preprocessor._extract_uri_pattern(uri)
        
        # Check if pattern is correctly generated
        self.assertTrue(pattern.startswith('/api/'))
        self.assertIn('*', pattern)

if __name__ == '__main__':
    unittest.main() 