import re
import pandas as pd
from datetime import datetime
from pathlib import Path

# Expression régulière pour détecter les en-têtes de section
SECTION_HEADER_RE = re.compile(r'^--([a-zA-Z0-9]+)-([A-Z])--$')

# Fonction pour reconstituer les lignes coupées (headers sur plusieurs lignes)
def join_multiline_headers(lines):
    result = []
    buffer = ''
    for line in lines:
        if line.strip() == '':
            continue
        if line.startswith(' ') or line.startswith('\t'):
            buffer += line.strip()
        else:
            if buffer:
                result.append(buffer)
            buffer = line.strip()
    if buffer:
        result.append(buffer)
    return result

def parse_modsec_audit_log(file_path):
    entries = []
    current_entry = {}
    current_section = None
    current_transaction_id = None

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            match = SECTION_HEADER_RE.match(line.strip())
            if match:
                tx_id, section = match.groups()
                if section == 'A' and current_entry:
                    # Nouvelle transaction, sauvegarder l'ancienne
                    entries.append(current_entry)
                    current_entry = {}
                current_transaction_id = tx_id
                current_section = section
                # Sauvegarder l'id de transaction
                current_entry['transaction_id'] = current_transaction_id
                continue

            # Stocker le contenu de chaque section
            key = f'section_{current_section}'
            if current_section:
                if key not in current_entry:
                    current_entry[key] = []
                current_entry[key].append(line)

        # Dernière transaction
        if current_entry:
            entries.append(current_entry)
    return entries

def parse_headers(header_lines):
    headers = {}
    lines = join_multiline_headers(header_lines)
    for line in lines:
        if ':' in line:
            k, v = line.split(':', 1)
            headers[k.strip()] = v.strip()
    return headers

def extract_features(entries):
    parsed_entries = []
    for entry in entries:
        data = {
            "transaction_id": entry.get("transaction_id"),
            "timestamp": None,
            "client_ip": None,
            "client_port": None,
            "server_ip": None,
            "server_port": None,
            "request_line": None,
            "host": None,
            "msg": None,
            "rule_id": None,
            "severity": None,
            "uri": None,
            "user_agent": None,
            "request_headers": None,
            "response_status": None,
            "response_headers": None,
            "apache_error": None
        }
        # Section A : métadonnées
        if 'section_A' in entry:
            lines = [l for l in entry['section_A'] if l.strip()]
            if lines:
                # Première ligne : timestamp, transaction id, IPs, ports
                meta = lines[0].split()
                if len(meta) >= 6:
                    data["timestamp"] = meta[0] + ' ' + meta[1]
                    data["client_ip"] = meta[2]
                    data["client_port"] = meta[3]
                    data["server_ip"] = meta[4]
                    data["server_port"] = meta[5]
        # Section B : requête HTTP
        if 'section_B' in entry:
            lines = [l for l in entry['section_B'] if l.strip()]
            if lines:
                data["request_line"] = lines[0]
                headers = parse_headers(lines[1:])
                data["request_headers"] = headers
                data["host"] = headers.get("Host")
                data["user_agent"] = headers.get("User-Agent")
                data["uri"] = data["request_line"].split()[1] if data["request_line"] else None
        # Section F : réponse HTTP
        if 'section_F' in entry:
            lines = [l for l in entry['section_F'] if l.strip()]
            if lines:
                data["response_status"] = lines[0] if lines else None
                data["response_headers"] = parse_headers(lines[1:]) if len(lines) > 1 else None
        # Section H : alertes, erreurs
        if 'section_H' in entry:
            lines = [l for l in entry['section_H'] if l.strip()]
            for line in lines:
                if 'Message:' in line:
                    msg_match = re.search(r'Message: (.*?) \[file', line)
                    id_match = re.search(r'\[id "(.*?)"\]', line)
                    sev_match = re.search(r'\[severity "(.*?)"\]', line)
                    uri_match = re.search(r'\[uri "(.*?)"\]', line)
                    if msg_match:
                        data['msg'] = msg_match.group(1)
                    if id_match:
                        data['rule_id'] = id_match.group(1)
                    if sev_match:
                        data['severity'] = sev_match.group(1)
                    if uri_match:
                        data['uri'] = uri_match.group(1)
                if 'Apache-Error:' in line:
                    data['apache_error'] = line
        parsed_entries.append(data)
    return pd.DataFrame(parsed_entries)

def parse_modsec_log_to_csv(log_path, output_csv):
    """
    Parse un fichier de log ModSecurity brut et exporte le résultat en CSV.
    
    Args:
        log_path: Chemin vers le fichier de log ModSecurity brut
        output_csv: Chemin de sortie pour le CSV parsé
    """
    print(f"⏳ Lecture de {log_path} ...")
    entries = parse_modsec_audit_log(log_path)
    print(f"🔍 {len(entries)} transactions détectées.")
    df = extract_features(entries)
    # Nettoyage : supprimer les entrées vides
    df = df.dropna(subset=["timestamp", "request_line"])
    # Format datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df.to_csv(output_csv, index=False)
    print(f"✅ CSV exporté vers {output_csv}")
    print("📊 Analyse terminée.")
    return df

class ModSecParser:
    """Parseur de logs ModSecurity."""
    
    def __init__(self):
        """Initialise le parseur."""
        pass
        
    def parse(self, log_line: str) -> dict:
        """
        Parse une ligne de log.
        
        Args:
            log_line: Ligne de log à parser
            
        Returns:
            Dictionnaire contenant les informations parsées
        """
        parts = log_line.split()
        if len(parts) >= 3:
            return {
                "method": parts[0],
                "path": parts[1],
                "version": parts[2]
            }
        return {}
        
    def parse_log_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse un fichier de log complet.
        
        Args:
            file_path: Chemin vers le fichier de log
            
        Returns:
            DataFrame contenant les logs parsés
        """
        entries = parse_modsec_audit_log(file_path)
        return extract_features(entries)
        
    def _parse_transaction(self, transaction: str) -> dict:
        """
        Parse une transaction complète.
        
        Args:
            transaction: Transaction à parser
            
        Returns:
            Dictionnaire contenant les sections parsées
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in transaction.split('\n'):
            match = SECTION_HEADER_RE.match(line.strip())
            if match:
                if current_section:
                    sections[current_section] = current_content
                current_section = match.group(2)
                current_content = []
            elif current_section:
                current_content.append(line)
                
        if current_section:
            sections[current_section] = current_content
            
        return sections
        
    def _extract_message_fields(self, message: str) -> dict:
        """
        Extrait les champs d'un message.
        
        Args:
            message: Message à parser
            
        Returns:
            Dictionnaire contenant les champs extraits
        """
        fields = {}
        for field in ['file', 'line', 'id', 'severity', 'uri']:
            match = re.search(rf'\[{field} "(.*?)"\]', message)
            if match:
                fields[field] = match.group(1)
        return fields
        
    def export_to_csv(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Exporte les données parsées en CSV.
        
        Args:
            df: DataFrame à exporter
            output_path: Chemin de sortie
        """
        df.to_csv(output_path, index=False) 