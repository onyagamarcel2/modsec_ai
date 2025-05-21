import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import yaml

from ..data.log_loader import ModSecLogLoader
from ..data.preprocessor import ModSecPreprocessor
from ..models.vectorizer import LogVectorizer
from ..models.anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)

app = FastAPI(title="ModSec AI API",
             description="API de détection d'anomalies pour les logs ModSecurity")

class LogEntry(BaseModel):
    """Modèle pour une entrée de log."""
    timestamp: str
    client_ip: str
    request_uri: str
    message: str

class DetectionResponse(BaseModel):
    """Modèle pour la réponse de détection."""
    is_anomaly: bool
    score: float
    details: Dict[str, Any]

class ModSecAI:
    """Classe principale pour la détection d'anomalies."""
    
    def __init__(self, config_path: str):
        """Initialise le système avec la configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Initialisation des composants
        self.log_loader = ModSecLogLoader(self.config['modsecurity']['log_path'])
        self.preprocessor = ModSecPreprocessor()
        self.vectorizer = LogVectorizer(**self.config['model']['vectorizer'])
        self.detector = AnomalyDetector(**self.config['model']['detector'])
        
    def detect_anomaly(self, log_entry: LogEntry) -> DetectionResponse:
        """Détecte les anomalies dans une entrée de log."""
        try:
            # Prétraitement
            df = self.preprocessor.preprocess(pd.DataFrame([log_entry.dict()]))
            
            # Vectorisation
            vectors = self.vectorizer.transform(df['tokens'].tolist())
            
            # Détection
            predictions, scores = self.detector.predict(vectors)
            
            return DetectionResponse(
                is_anomaly=bool(predictions[0]),
                score=float(scores[0]),
                details={
                    'ip_pattern': df['ip_pattern'].iloc[0],
                    'uri_pattern': df['uri_pattern'].iloc[0]
                }
            )
        except Exception as e:
            logger.error(f"Erreur de détection: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Instance globale
modsec_ai = None

@app.on_event("startup")
async def startup_event():
    """Initialise le système au démarrage."""
    global modsec_ai
    try:
        modsec_ai = ModSecAI("config/config.yaml")
    except Exception as e:
        logger.error(f"Erreur d'initialisation: {str(e)}")
        raise

@app.post("/detect", response_model=DetectionResponse)
async def detect_anomaly(log_entry: LogEntry):
    """Endpoint de détection d'anomalies."""
    return modsec_ai.detect_anomaly(log_entry)

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, 
                host=modsec_ai.config['api']['host'],
                port=modsec_ai.config['api']['port']) 