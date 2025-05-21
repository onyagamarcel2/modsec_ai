"""
API du dashboard pour Streamlit.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yaml
import logging
import os
from pathlib import Path

from ..data.log_loader import ModSecLogLoader
from ..data.preprocessor import ModSecPreprocessor
from ..models.vectorizer import LogVectorizer
from ..models.anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)

def load_config():
    """Charge la configuration depuis le fichier YAML."""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Charger la configuration
config = load_config()

# Configuration de la page
st.set_page_config(
    page_title=config['dashboard']['title'],
    layout="wide"
)

# Titre
st.title(config['dashboard']['title'])

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Sélection du modèle
    model = st.selectbox(
        "Modèle",
        options=["isolation_forest", "local_outlier_factor", "elliptic_envelope", "one_class_svm"],
        index=0
    )
    
    # Seuil d'anomalie
    threshold = st.slider(
        "Seuil d'anomalie",
        min_value=0.0,
        max_value=1.0,
        value=config['alerts']['threshold'],
        step=0.1
    )
    
    # Intervalle de rafraîchissement
    refresh = st.number_input(
        "Intervalle de rafraîchissement (secondes)",
        min_value=10,
        max_value=3600,
        value=config['dashboard']['refresh_interval']
    )

# Onglets
tab1, tab2, tab3 = st.tabs(["Règles", "Statistiques", "Alertes"])

with tab1:
    st.header("Règles ModSecurity")
    # TODO: Implémenter l'affichage des règles

with tab2:
    st.header("Statistiques")
    # TODO: Implémenter l'affichage des statistiques

with tab3:
    st.header("Alertes")
    # TODO: Implémenter l'affichage des alertes

# Initialisation
log_loader = ModSecLogLoader(config['modsecurity']['log_path'])
preprocessor = ModSecPreprocessor()
vectorizer = LogVectorizer(**config['model']['vectorizer'])
detector = AnomalyDetector(**config['model']['detector'])

# Interface Streamlit
st.title("ModSec AI Dashboard")
st.markdown("Dashboard de surveillance des anomalies ModSecurity")

# Sidebar
st.sidebar.title("Paramètres")
time_window = st.sidebar.selectbox(
    "Fenêtre temporelle",
    ["1 heure", "6 heures", "12 heures", "24 heures", "7 jours"]
)

# Fonctions de visualisation
def plot_anomalies_over_time(df):
    fig = px.scatter(df, 
                    x='timestamp',
                    y='score',
                    color='is_anomaly',
                    title="Anomalies détectées",
                    labels={'score': 'Score d\'anomalie',
                           'timestamp': 'Heure'})
    return fig

def plot_ip_distribution(df):
    fig = px.histogram(df[df['is_anomaly']],
                      x='client_ip',
                      title="Distribution des IPs suspectes")
    return fig

def plot_uri_patterns(df):
    fig = px.treemap(df[df['is_anomaly']],
                     path=['uri_pattern'],
                     title="Patterns d'URI suspects")
    return fig

# Chargement et traitement des données
@st.cache_data(ttl=300)  # Cache pour 5 minutes
def load_data():
    # Calcul de la date de début
    now = datetime.now()
    if time_window == "1 heure":
        start_date = now - timedelta(hours=1)
    elif time_window == "6 heures":
        start_date = now - timedelta(hours=6)
    elif time_window == "12 heures":
        start_date = now - timedelta(hours=12)
    elif time_window == "24 heures":
        start_date = now - timedelta(hours=24)
    else:  # 7 jours
        start_date = now - timedelta(days=7)
        
    # Chargement des logs
    df = log_loader.load_logs(start_date.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Prétraitement
    df = preprocessor.preprocess(df)
    
    # Vectorisation et détection
    vectors = vectorizer.transform(df['tokens'].tolist())
    predictions, scores = detector.predict(vectors)
    
    df['is_anomaly'] = predictions
    df['score'] = scores
    
    return df

# Affichage des données
try:
    df = load_data()
    
    # Métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total des logs", len(df))
    with col2:
        st.metric("Anomalies détectées", df['is_anomaly'].sum())
    with col3:
        st.metric("Taux d'anomalies", 
                 f"{(df['is_anomaly'].sum() / len(df) * 100):.2f}%")
    
    # Graphiques
    st.plotly_chart(plot_anomalies_over_time(df), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_ip_distribution(df), use_container_width=True)
    with col2:
        st.plotly_chart(plot_uri_patterns(df), use_container_width=True)
    
    # Table des anomalies
    st.subheader("Dernières anomalies détectées")
    st.dataframe(
        df[df['is_anomaly']].sort_values('timestamp', ascending=False)
        .head(10)[['timestamp', 'client_ip', 'request_uri', 'score']]
    )
    
except Exception as e:
    st.error(f"Erreur lors du chargement des données: {str(e)}")
    logger.error(f"Erreur dashboard: {str(e)}") 