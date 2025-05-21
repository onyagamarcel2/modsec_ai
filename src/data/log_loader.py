import os
import logging
from typing import Optional, List
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ModSecLogLoader:
    """Chargeur de logs ModSecurity."""
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialise le chargeur.
        
        Args:
            log_path: Chemin vers le fichier de log (optionnel)
        """
        self.log_path = log_path
        if log_path:
            self._validate_log_file()
        
    def _validate_log_file(self) -> None:
        """Vérifie que le fichier de log existe."""
        if not os.path.exists(self.log_path):
            raise FileNotFoundError(f"Fichier de log non trouvé: {self.log_path}")
            
    def load_logs(self, logs: Optional[List[str]] = None, start_date: Optional[str] = None) -> pd.DataFrame:
        """
        Charge les logs depuis le fichier ou la liste fournie.
        
        Args:
            logs: Liste de logs à charger (optionnel)
            start_date: Date de début pour filtrer les logs (optionnel)
            
        Returns:
            DataFrame contenant les logs
        """
        try:
            if logs is not None:
                # Créer un DataFrame à partir de la liste de logs
                df = pd.DataFrame({'message': logs})
                df['timestamp'] = pd.Timestamp.now()
                return df
            elif self.log_path:
                # Charger depuis le fichier
                df = pd.read_csv(self.log_path, parse_dates=['timestamp'])
                if start_date:
                    df = df[df['timestamp'] >= pd.to_datetime(start_date)]
                return df
            else:
                raise ValueError("Aucune source de logs fournie")
        except Exception as e:
            logger.error(f"Erreur de chargement: {str(e)}")
            raise

class LogStreamer:
    """Streaming en temps réel des logs."""
    
    def __init__(self, log_path: str, callback):
        self.log_path = log_path
        self.callback = callback
        self.observer = Observer()
        self.handler = LogFileHandler(self._process_new_logs)
        
    def start(self):
        self.observer.schedule(self.handler, 
                             os.path.dirname(self.log_path),
                             recursive=False)
        self.observer.start()
        
    def stop(self):
        self.observer.stop()
        self.observer.join()
        
    def _process_new_logs(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        self.callback(line.strip())
        except Exception as e:
            logger.error(f"Erreur de streaming: {str(e)}")

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.log'):
            self.callback(event.src_path)
 