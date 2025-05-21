# 🛡️ ModSec AI - Détection d'Anomalies en Temps Réel pour ModSecurity

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen)](docs/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)

ModSec AI est une solution avancée de détection d'anomalies en temps réel pour les logs ModSecurity, combinant l'intelligence artificielle et l'analyse comportementale pour renforcer la sécurité de vos applications web.

## 🎯 Introduction


### Contexte
Les logs ModSecurity génèrent un volume important de données de sécurité qui nécessitent une analyse continue. Les approches traditionnelles basées sur des règles statiques ne suffisent plus face à l'évolution constante des menaces.

### Objectifs
- Détection en temps réel des comportements anormaux dans les logs ModSecurity
- Apprentissage continu pour s'adapter aux nouveaux patterns légitimes
- Réduction des faux positifs grâce à l'analyse comportementale
- Amélioration continue de la détection via le réentraînement du modèle

### Importance
ModSec AI s'inscrit dans une approche moderne de la sécurité (DevSecOps) en :
- Automatisant l'analyse des logs de sécurité
- Fournissant des insights en temps réel
- Permettant une réponse proactive aux menaces
- S'intégrant dans les pipelines CI/CD

## 🧠 Fonctionnalités Principales

### 🔍 Détection en Temps Réel
- Analyse continue des logs ModSecurity
- Détection immédiate des comportements anormaux
- Alertes configurables (email, Slack, webhook)

### 📊 Analyse Comportementale
- Apprentissage des patterns légitimes
- Détection des déviations comportementales
- Réduction des faux positifs

### 🔄 Apprentissage Continu
- Mise à jour automatique du modèle
- Adaptation aux nouveaux patterns
- Amélioration continue de la détection

### 📈 Visualisation & Reporting
- Dashboard interactif (Streamlit)
- Rapports détaillés des anomalies
- Métriques de performance

## 🏗️ Architecture Technique

```mermaid
flowchart TD
    subgraph "Data Sources"
        A[modsec_audit.log / .gz]
    end

    subgraph "1. Preprocessing"
        A --> B1[Log Parser<br/>Multi-section]
        B1 --> B2[Cleaning / Normalization]
    end

    subgraph "2. Feature Engineering"
        B2 --> C1[Vectorization<br/>TF-IDF + Word2Vec]
        C1 --> C2[Feature Extraction<br/>Statistical + Contextual]
    end

    subgraph "3. Model Management"
        C2 --> D1[Model Training & Evaluation<br/>Isolation Forest]
        D1 --> D2[Model Export .pkl]
        D2 --> D5[Anomaly Detection Engine Load Model]

        H2[Training Buffer] --> D3[Incremental Update<br/>Sliding Window]
        D3 --> D4[Model Retraining]
        D4 --> D2
    end

    subgraph "4. Real-Time Detection"
        F1[Watchdog Monitor<br/>modsec_audit.log]
        F1 --> F2[New Log Line Detected]
        F2 --> B1
        C2 --> D5[Anomaly Detection Engine Load Model]
        D5 --> F4[Is Anomaly?]

        F4 -->|Yes| G1[Alerting System<br/>Log + Email + Webhook]
        F4 -->|Yes| G4[Anomalies Buffer<br/>En attente de validation]
        F4 -->|No| G2[Update Knowledge Base]

        G4 --> G5[Validation humaine ou AI-Assisted]
        G5 -->|Validé comme normal| H2[Training Buffer]
    end

    subgraph "5. Visualization & Logs"
        G1 --> H1[JSON/CSV Logs]
        G2 --> H2[Training Buffer]
        H1 --> I1[Streamlit Dashboard<br/>or Grafana + InfluxDB]
        H2 --> D3
    end

    subgraph "6. ModSecurity Improvement"
        J1[Validation de la vulnérabilité] --> J2[Formulation de nouvelles règles]
        J2 --> J3[Configuration ModSecurity<br/>mise à jour des règles de sécurité]
        J3 --> I1
    end

    %% Nouveau flux de validation
    F4 -->|Yes| J1

    %% Styles communs
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B1 fill:#ffe,stroke:#333
    style B2 fill:#ffe,stroke:#333
    style C1 fill:#ddf,stroke:#333
    style C2 fill:#ddf,stroke:#333
    style D1 fill:#bfb,stroke:#333
    style D2 fill:#bfb,stroke:#333
    style D3 fill:#bfb,stroke:#333
    style D4 fill:#bfb,stroke:#333
    style D5 fill:#bfb,stroke:#333
    style F4 fill:#bff,stroke:#333
    style G1 fill:#fcc,stroke:#333
    style G2 fill:#fcc,stroke:#333
    style G4 fill:#fc9,stroke:#333
    style G5 fill:#fc9,stroke:#333
    style H1 fill:#bbf,stroke:#333
    style H2 fill:#ccf,stroke:#333
    style I1 fill:#bbf,stroke:#333
    style J1 fill:#cfc,stroke:#333
    style J2 fill:#cfc,stroke:#333
    style J3 fill:#cfc,stroke:#333
```

### Flux de Séquence Complet

```mermaid
sequenceDiagram
    participant WM as Watchdog Monitor
    participant LP as Log Parser
    participant CN as Cleaning/Normalization
    participant VE as Vectorization
    participant FE as Feature Extraction
    participant AD as Anomaly Detection
    participant AS as Alerting System
    participant AB as Anomalies Buffer
    participant KB as Knowledge Base
    participant TB as Training Buffer
    participant MU as Model Update
    participant VR as Validation Rules
    participant DB as Dashboard

    %% Phase d'initialisation
    Note over AD,MU: Phase d'Initialisation
    AD->>MU: Charger modèle initial
    MU-->>AD: Modèle chargé

    %% Boucle de détection
    loop Surveillance Continue
        WM->>LP: Nouveau log détecté
        LP->>CN: Log parsé
        CN->>VE: Données nettoyées
        VE->>FE: Vecteurs générés
        FE->>AD: Features extraites
        AD->>AD: Évaluation anomalie

        alt Anomalie détectée
            AD->>AS: Alerte générée
            AD->>AB: Stockage anomalie
            AD->>VR: Validation requise
            VR->>DB: Affichage pour validation
            
            alt Validation humaine
                DB->>VR: Confirmation utilisateur
                VR->>KB: Mise à jour base de connaissances
            else Validation automatique
                VR->>KB: Mise à jour automatique
            end
        else Comportement normal
            AD->>KB: Mise à jour base de connaissances
            KB->>TB: Ajout au buffer d'entraînement
        end

        %% Mise à jour du modèle
        alt Buffer plein ou période écoulée
            TB->>MU: Déclenchement mise à jour
            MU->>MU: Réentraînement modèle
            MU->>AD: Mise à jour modèle
        end
    end
```

### Description des Composants

#### 1. Preprocessing
- **Log Parser** : Analyse multi-section des logs ModSecurity
- **Cleaning/Normalization** : Nettoyage et standardisation des données

#### 2. Feature Engineering
- **Vectorization** : Transformation en vecteurs (TF-IDF + Word2Vec)
- **Feature Extraction** : Extraction de caractéristiques statistiques et contextuelles

#### 3. Model Management
- **Model Training** : Entraînement et évaluation du modèle Isolation Forest
- **Model Export** : Sauvegarde du modèle entraîné
- **Incremental Update** : Mise à jour incrémentale avec fenêtre glissante
- **Model Retraining** : Réentraînement périodique du modèle

#### 4. Real-Time Detection
- **Watchdog Monitor** : Surveillance en temps réel des logs
- **Anomaly Detection** : Détection des anomalies
- **Alerting System** : Système d'alertes multi-canal
- **Validation** : Processus de validation humaine ou assistée par IA

#### 5. Visualization & Logs
- **JSON/CSV Logs** : Stockage structuré des logs
- **Training Buffer** : Buffer d'apprentissage
- **Dashboard** : Interface de visualisation (Streamlit/Grafana)

#### 6. ModSecurity Improvement
- **Validation** : Validation des vulnérabilités détectées
- **Rule Formulation** : Création de nouvelles règles
- **Configuration** : Mise à jour des règles ModSecurity

## 🏗️ Architecture Technique Complète

```mermaid
graph TD
    subgraph "Ingestion & Prétraitement"
        A1[ModSecLogLoader] --> |Logs bruts| B1[ModSecPreprocessor]
        B1 --> |Logs nettoyés| C1[ModSecParser]
        C1 --> |Logs structurés| D1[FeatureExtractor]
    end

    subgraph "Vectorisation & Détection"
        D1 --> |Features| E1[LogVectorizer]
        E1 --> |Vecteurs| F1[AnomalyDetector]
        F1 --> |Scores| G1[ModelUpdater]
        G1 --> |Mise à jour| E1
    end

    subgraph "Interface & Monitoring"
        F1 --> |Alertes| H1[NotificationManager]
        F1 --> |Métriques| I1[PerformanceMonitor]
        F1 --> |Données| J1[Dashboard]
        F1 --> |API| K1[FastAPI]
    end

    subgraph "Stockage & Cache"
        L1[VectorCache] --> |Cache| E1
        M1[AlertManager] --> |Historique| H1
        N1[GUIDataManager] --> |État| J1
    end

    subgraph "Utilitaires"
        O1[RuleBasedDetector] --> |Règles| F1
        P1[RealTimeDetector] --> |Streaming| F1
    end

    subgraph "Cycle d'Amélioration"
        J1 --> |Confirmation| Q1[FeedbackManager]
        K1 --> |Validation| Q1
        Q1 --> |Feedback| G1
        Q1 --> |Nouvelles règles| R1[RuleGenerator]
        R1 --> |Règles ModSecurity| S1[ModSecRuleManager]
        S1 --> |Mise à jour| O1
    end

    subgraph "Entraînement & Réentraînement"
        T1[TrainingPipeline] --> |Données d'entraînement| U1[ModelTrainer]
        U1 --> |Modèle initial| F1
        V1[RetrainingScheduler] --> |Déclencheur| W1[IncrementalTrainer]
        W1 --> |Mise à jour| G1
    end

    style A1 fill:#f9f,stroke:#333,stroke-width:2px
    style F1 fill:#bbf,stroke:#333,stroke-width:2px
    style J1 fill:#bfb,stroke:#333,stroke-width:2px
    style K1 fill:#bfb,stroke:#333,stroke-width:2px
    style Q1 fill:#fbb,stroke:#333,stroke-width:2px
    style U1 fill:#fbb,stroke:#333,stroke-width:2px
```

### Composants Détaillés

#### Ingestion & Prétraitement
- **ModSecLogLoader** : Chargement et validation des logs ModSecurity
- **ModSecPreprocessor** : Nettoyage et normalisation des données
- **ModSecParser** : Extraction structurée des informations
- **FeatureExtractor** : Extraction des caractéristiques pertinentes

#### Vectorisation & Détection
- **LogVectorizer** : Transformation en vecteurs (Word2Vec/TF-IDF)
- **AnomalyDetector** : Détection des anomalies (Isolation Forest, LOF, etc.)
- **ModelUpdater** : Mise à jour incrémentale du modèle

#### Interface & Monitoring
- **NotificationManager** : Gestion des alertes (email, Slack, webhook)
- **PerformanceMonitor** : Suivi des métriques de performance
- **Dashboard** : Interface utilisateur Streamlit
- **FastAPI** : API REST pour l'intégration

#### Stockage & Cache
- **VectorCache** : Cache des vecteurs pour optimisation
- **AlertManager** : Gestion de l'historique des alertes
- **GUIDataManager** : Gestion de l'état de l'interface

#### Utilitaires
- **RuleBasedDetector** : Détection basée sur des règles
- **RealTimeDetector** : Détection en temps réel

#### Cycle d'Amélioration
- **FeedbackManager** : Gestion des retours utilisateur
- **RuleGenerator** : Génération de nouvelles règles
- **ModSecRuleManager** : Gestion des règles ModSecurity

#### Entraînement & Réentraînement
- **TrainingPipeline** : Pipeline d'entraînement initial
- **ModelTrainer** : Entraînement du modèle
- **RetrainingScheduler** : Planification du réentraînement
- **IncrementalTrainer** : Entraînement incrémental

## 📊 Flux de Données global

```mermaid
sequenceDiagram
    participant DL as DataLoader
    participant PP as Preprocessor
    participant P as Parser
    participant FE as FeatureExtractor
    participant AD as AnomalyDetector
    participant MU as ModelUpdater
    
    DL->>PP: Raw Logs
    PP->>P: Cleaned Data
    P->>FE: Parsed Entries
    FE->>AD: Feature Vectors
    AD->>MU: Anomaly Results
    MU->>FE: Updated Model
```

## 📁 Structure du Projet

```
modsec_ai/
├── config/             # Configuration files
├── docs/              # Documentation
├── scripts/           # Utility scripts
├── src/               # Source code
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   ├── models/       # ML models
│   └── utils/        # Utilities
├── tests/            # Test suite
├── .pylintrc         # Pylint configuration
├── mypy.ini          # Mypy configuration
├── requirements.txt  # Dependencies
└── setup.py         # Package setup
```

## 🧩 Modules & Composants

### 📦 DataLoader
- Rôle : Chargement et validation des logs ModSecurity
- Documentation : [docs/dataloader.md](docs/dataloader.md)

### 🔧 Preprocessor
- Rôle : Nettoyage et normalisation des données
- Documentation : [docs/preprocessor.md](docs/preprocessor.md)

### 📝 Parser
- Rôle : Extraction structurée des informations des logs
- Documentation : [docs/parser.md](docs/parser.md)

### 🎯 FeatureExtractor
- Rôle : Transformation des données en vecteurs exploitables
- Documentation : [docs/feature_extractor.md](docs/feature_extractor.md)

### 🧠 AnomalyDetector
- Rôle : Détection des comportements anormaux
- Documentation : [docs/anomaly_detector.md](docs/anomaly_detector.md)

### 🔄 ModelUpdater
- Rôle : Mise à jour continue du modèle
- Documentation : [docs/model_updater.md](docs/model_updater.md)

### 👀 WatchdogMonitor
- Rôle : Surveillance continue des fichiers de logs ModSecurity
- Documentation : [docs/watchdog_monitor.md](docs/watchdog_monitor.md)

### 🧹 CleaningNormalization
- Rôle : Nettoyage et standardisation des données
- Documentation : [docs/cleaning_normalization.md](docs/cleaning_normalization.md)

### 📊 Vectorization
- Rôle : Transformation des logs en vecteurs
- Documentation : [docs/vectorization.md](docs/vectorization.md)

### 🔔 AlertingSystem
- Rôle : Gestion des alertes et notifications
- Documentation : [docs/alerting_system.md](docs/alerting_system.md)

### 📥 AnomaliesBuffer
- Rôle : Stockage temporaire des anomalies
- Documentation : [docs/anomalies_buffer.md](docs/anomalies_buffer.md)

### 🧠 KnowledgeBase
- Rôle : Base de connaissances des patterns
- Documentation : [docs/knowledge_base.md](docs/knowledge_base.md)

### 📚 TrainingBuffer
- Rôle : Buffer d'entraînement du modèle
- Documentation : [docs/training_buffer.md](docs/training_buffer.md)

### ✅ ValidationRules
- Rôle : Gestion des règles de validation
- Documentation : [docs/validation_rules.md](docs/validation_rules.md)

### 📊 Dashboard
- Rôle : Interface utilisateur pour la visualisation et la validation
- Documentation : [docs/dashboard.md](docs/dashboard.md)

## ⚙️ Installation

### Prérequis
- Python 3.8+
- pip
- virtualenv (recommandé)

### Installation

1. Cloner le repository :
```bash
git clone https://github.com/yourusername/modsec_ai.git
cd modsec_ai
```

2. Créer et activer l'environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configuration :
```bash
cp config/config.example.yaml config/config.yaml
# Éditer config.yaml avec vos paramètres
```

## 🚀 Guide de Démarrage Rapide

1. Lancer le pipeline de détection :
```bash
python -m modsec_ai.src.core.pipeline
```

2. Démarrer le dashboard :
```bash
streamlit run modsec_ai/src/api/dashboard.py
```

3. Accéder à l'API :
```bash
uvicorn modsec_ai.src.api.main:app --reload
```

## 📚 Documentation

La documentation complète est disponible dans le dossier `docs/` :
- [Guide d'installation](docs/installation.md)
- [Guide d'utilisation](docs/usage.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Configuration](docs/configuration.md)

## 🙋 Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Contact
- Email : onyagamarcel2@gmail.com
- Issues : [GitHub Issues](https://github.com/onyagamarcel2/modsec_ai/issues)

## ⚖️ Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🏷️ Crédits


- [Drain3](https://github.com/IBM/Drain3) - Base du parser de logs
- [Scikit-learn](https://scikit-learn.org/) - Algorithmes de détection d'anomalies


---

<div align="center">
  <sub>Built with ❤️ by Marcel ONYAGA</sub>
</div> 