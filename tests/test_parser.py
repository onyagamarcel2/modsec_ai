"""
Tests unitaires pour le parseur de logs.
"""

import os
import pytest
import pandas as pd
from src.data.parser import ModSecParser, parse_modsec_audit_log, extract_features

@pytest.fixture
def parser():
    """Crée une instance de ModSecParser pour les tests."""
    return ModSecParser()

@pytest.fixture
def sample_log_content():
    """Crée un contenu de log de test."""
    return """--a1b2c3d4-A--
[26/Jan/2024:10:00:00 +0000] 192.168.1.1 8080 10.0.0.1 80
--a1b2c3d4-B--
GET /api/test HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
--a1b2c3d4-F--
HTTP/1.1 200 OK
--a1b2c3d4-H--
Message: Test message 1 [file "/etc/modsecurity/rules/test.conf"] [line "1"] [id "1000"] [severity "CRITICAL"] [uri "/api/test"]

--b2c3d4e5-A--
[26/Jan/2024:10:01:00 +0000] 192.168.1.2 8080 10.0.0.1 80
--b2c3d4e5-B--
POST /api/user HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
--b2c3d4e5-F--
HTTP/1.1 403 Forbidden
--b2c3d4e5-H--
Message: Test message 2 [file "/etc/modsecurity/rules/test.conf"] [line "2"] [id "1001"] [severity "WARNING"] [uri "/api/user"]
"""

@pytest.fixture
def temp_log_file(tmp_path, sample_log_content):
    """Crée un fichier de log temporaire pour les tests."""
    log_file = tmp_path / "test_modsec.log"
    log_file.write_text(sample_log_content)
    return str(log_file)

def test_parser_initialization(parser):
    """Test l'initialisation du parseur."""
    assert parser is not None

def test_parse_log(parser):
    """Test le parsing d'un log."""
    test_log = "GET /admin HTTP/1.1"
    
    # Parser le log
    parsed = parser.parse(test_log)
    
    assert parsed is not None
    assert "method" in parsed
    assert "path" in parsed
    assert "version" in parsed
    assert parsed["method"] == "GET"
    assert parsed["path"] == "/admin"
    assert parsed["version"] == "HTTP/1.1"

def test_parse_log_file(parser, temp_log_file):
    """Test le parsing d'un fichier de log."""
    # Parser le fichier de log
    df = parser.parse_log_file(temp_log_file)
    
    assert not df.empty
    assert "timestamp" in df.columns
    assert "client_ip" in df.columns
    assert "request_line" in df.columns
    assert "msg" in df.columns
    assert len(df) == 2

def test_parse_modsec_audit_log(temp_log_file):
    """Test le parsing des entrées de log ModSecurity."""
    entries = parse_modsec_audit_log(temp_log_file)
    
    assert len(entries) == 2
    assert all("transaction_id" in entry for entry in entries)
    assert all("section_A" in entry for entry in entries)
    assert all("section_B" in entry for entry in entries)
    assert all("section_F" in entry for entry in entries)
    assert all("section_H" in entry for entry in entries)

def test_extract_features(temp_log_file):
    """Test l'extraction des caractéristiques des entrées."""
    entries = parse_modsec_audit_log(temp_log_file)
    df = extract_features(entries)
    
    assert not df.empty
    assert "timestamp" in df.columns
    assert "client_ip" in df.columns
    assert "request_line" in df.columns
    assert "msg" in df.columns
    assert "rule_id" in df.columns
    assert "severity" in df.columns
    assert len(df) == 2

def test_export_to_csv(parser, temp_log_file, tmp_path):
    """Test l'export des données parsées en CSV."""
    # Parser le fichier de log
    df = parser.parse_log_file(temp_log_file)
    
    # Exporter en CSV
    output_path = str(tmp_path / "output.csv")
    parser.export_to_csv(df, output_path)
    
    assert os.path.exists(output_path)
    
    # Vérifier le contenu du CSV
    loaded_df = pd.read_csv(output_path)
    assert len(loaded_df) == len(df)
    assert all(col in loaded_df.columns for col in df.columns) 