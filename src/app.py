from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np

app = FastAPI(title="ModSec AI API")

class LogRequest(BaseModel):
    logs: List[str]

@app.get("/health")
async def health_check():
    """Vérifie l'état de l'API."""
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_logs(request: LogRequest):
    """
    Analyse une liste de logs.
    
    Args:
        request: Requête contenant les logs à analyser
        
    Returns:
        Résultat de l'analyse
    """
    try:
        # Simuler une analyse
        anomalies = []
        for log in request.logs:
            # Score aléatoire pour les tests
            score = np.random.random()
            anomalies.append({
                "log": log,
                "score": score,
                "is_anomaly": score > 0.8
            })
            
        return {
            "anomalies": anomalies,
            "score": np.mean([a["score"] for a in anomalies])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 