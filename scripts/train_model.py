#!/usr/bin/env python3
import argparse
import logging
import os
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from src.data.log_loader import ModSecLogLoader
from src.data.preprocessor import ModSecPreprocessor
from src.models.vectorizer import LogVectorizer
from src.models.anomaly_detectors import (
    IsolationForestDetector,
    LocalOutlierFactorDetector,
    EllipticEnvelopeDetector,
    OneClassSVMDetector,
    EnsembleAnomalyDetector
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Train anomaly detection model on ModSecurity logs')
    parser.add_argument('--log-file', type=str, required=True,
                      help='Path to the ModSecurity log file')
    parser.add_argument('--output-dir', type=str, default='models',
                      help='Directory to save trained models')
    parser.add_argument('--vectorizer-type', type=str, default='word2vec',
                      choices=['word2vec', 'tfidf'],
                      help='Type of vectorizer to use')
    parser.add_argument('--detector-type', type=str, default='ensemble',
                      choices=['isolation_forest', 'local_outlier_factor', 
                              'elliptic_envelope', 'one_class_svm', 'ensemble'],
                      help='Type of anomaly detector to use')
    parser.add_argument('--start-date', type=str,
                      help='Start date for training data (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                      help='End date for training data (YYYY-MM-DD)')
    
    # Vectorizer parameters
    parser.add_argument('--vector-size', type=int, default=100,
                      help='Size of word vectors for Word2Vec')
    parser.add_argument('--window-size', type=int, default=5,
                      help='Context window size for Word2Vec')
    parser.add_argument('--min-count', type=int, default=1,
                      help='Minimum word count for Word2Vec')
    
    # Detector parameters
    parser.add_argument('--contamination', type=float, default=0.1,
                      help='Expected proportion of anomalies in the data')
    parser.add_argument('--n-estimators', type=int, default=100,
                      help='Number of trees in Isolation Forest')
    parser.add_argument('--n-neighbors', type=int, default=20,
                      help='Number of neighbors for Local Outlier Factor')
    parser.add_argument('--nu', type=float, default=0.1,
                      help='Nu parameter for One-Class SVM')
    parser.add_argument('--kernel', type=str, default='rbf',
                      choices=['linear', 'poly', 'rbf', 'sigmoid'],
                      help='Kernel type for One-Class SVM')
    
    # Cross-validation parameters
    parser.add_argument('--cross-validate', action='store_true',
                      help='Perform cross-validation during training')
    parser.add_argument('--n-folds', type=int, default=5,
                      help='Number of folds for cross-validation')
    
    # Evaluation parameters
    parser.add_argument('--test-split', type=float, default=0.2,
                      help='Proportion of data to use for testing')
    
    return parser.parse_args()

def evaluate_model(detector, X_test, y_test):
    """Evaluate model performance on test data."""
    predictions, scores = detector.predict(X_test)
    predictions = predictions == -1  # Convert to binary (True for anomalies)
    
    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, average='binary'
    )
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_test, predictions)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'confusion_matrix': cm
    }

def plot_training_results(metrics, output_dir, timestamp):
    """Plot and save training results."""
    # Create plots directory
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Plot confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(metrics['confusion_matrix'], annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(os.path.join(plots_dir, f'confusion_matrix_{timestamp}.png'))
    plt.close()
    
    # Plot metrics
    metrics_df = pd.DataFrame({
        'Metric': ['Precision', 'Recall', 'F1 Score'],
        'Value': [metrics['precision'], metrics['recall'], metrics['f1_score']]
    })
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x='Metric', y='Value', data=metrics_df)
    plt.title('Model Performance Metrics')
    plt.ylim(0, 1)
    plt.savefig(os.path.join(plots_dir, f'metrics_{timestamp}.png'))
    plt.close()

def train_model(log_file, output_dir, vectorizer_type, detector_type, 
                start_date=None, end_date=None, vector_size=100, window_size=5,
                min_count=1, contamination=0.1, n_estimators=100,
                n_neighbors=20, nu=0.1, kernel='rbf',
                cross_validate=False, n_folds=5, test_split=0.2):
    """Train the anomaly detection model."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load logs
        logger.info("Loading logs from %s", log_file)
        loader = ModSecLogLoader(log_file)
        df = loader.load_logs(start_date=start_date, end_date=end_date)
        
        if df.empty:
            raise ValueError("No logs found in the specified date range")
        
        # Preprocess logs
        logger.info("Preprocessing logs")
        preprocessor = ModSecPreprocessor()
        processed_df = preprocessor.preprocess(df)
        
        # Split data into train and test sets
        train_df, test_df = train_test_split(
            processed_df, test_size=test_split, random_state=42
        )
        
        # Train vectorizer
        logger.info("Training %s vectorizer", vectorizer_type)
        vectorizer = LogVectorizer(
            vectorizer_type=vectorizer_type,
            vector_size=vector_size,
            window_size=window_size,
            min_count=min_count
        )
        vectorizer.fit(train_df['tokens'])
        
        # Transform logs to vectors
        logger.info("Transforming logs to vectors")
        train_vectors = vectorizer.transform(train_df['tokens'])
        test_vectors = vectorizer.transform(test_df['tokens'])
        
        # Create and train detector
        logger.info("Training %s anomaly detector", detector_type)
        if detector_type == 'ensemble':
            detector = EnsembleAnomalyDetector()
        else:
            detectors = {
                'isolation_forest': IsolationForestDetector(
                    contamination=contamination,
                    n_estimators=n_estimators
                ),
                'local_outlier_factor': LocalOutlierFactorDetector(
                    n_neighbors=n_neighbors,
                    contamination=contamination
                ),
                'elliptic_envelope': EllipticEnvelopeDetector(
                    contamination=contamination
                ),
                'one_class_svm': OneClassSVMDetector(
                    nu=nu,
                    kernel=kernel
                )
            }
            detector = detectors[detector_type]
        
        if cross_validate:
            logger.info("Performing cross-validation")
            cv_scores = cross_val_score(
                detector.model, train_vectors, cv=n_folds, scoring='f1'
            )
            logger.info("Cross-validation scores: %s", cv_scores)
            logger.info("Mean CV score: %.3f (+/- %.3f)", 
                       cv_scores.mean(), cv_scores.std() * 2)
        
        detector.fit(train_vectors)
        
        # Evaluate model
        logger.info("Evaluating model on test set")
        predictions = detector.predict(test_vectors)
        scores = detector.predict_proba(test_vectors)
        predictions = predictions == -1  # Convert to binary (True for anomalies)
        
        # Calculate metrics
        precision, recall, f1, _ = precision_recall_fscore_support(
            test_df['is_anomaly'], predictions, average='binary'
        )
        cm = confusion_matrix(test_df['is_anomaly'], predictions)
        
        metrics = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm
        }
        
        logger.info("Test metrics: %s", metrics)
        
        # Save models
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vectorizer_path = os.path.join(output_dir, f'vectorizer_{timestamp}')
        detector_path = os.path.join(output_dir, f'detector_{timestamp}')
        
        logger.info("Saving vectorizer to %s", vectorizer_path)
        vectorizer.save(vectorizer_path)
        
        logger.info("Saving detector to %s", detector_path)
        detector.save(detector_path)
        
        # Plot and save results
        plot_training_results(metrics, output_dir, timestamp)
        
        # Save model metadata
        metadata = {
            'timestamp': timestamp,
            'vectorizer_type': vectorizer_type,
            'detector_type': detector_type,
            'start_date': start_date,
            'end_date': end_date,
            'num_samples': len(df),
            'vectorizer_path': vectorizer_path,
            'detector_path': detector_path,
            'vector_size': vector_size,
            'window_size': window_size,
            'min_count': min_count,
            'contamination': contamination,
            'n_estimators': n_estimators,
            'n_neighbors': n_neighbors,
            'nu': nu,
            'kernel': kernel,
            'test_split': test_split,
            'metrics': metrics
        }
        
        metadata_path = os.path.join(output_dir, f'metadata_{timestamp}.json')
        pd.Series(metadata).to_json(metadata_path)
        
        logger.info("Training completed successfully")
        return metadata
        
    except Exception as e:
        logger.error("Error during model training: %s", str(e))
        raise

def main():
    """Main function."""
    args = parse_args()
    
    try:
        metadata = train_model(
            log_file=args.log_file,
            output_dir=args.output_dir,
            vectorizer_type=args.vectorizer_type,
            detector_type=args.detector_type,
            start_date=args.start_date,
            end_date=args.end_date,
            vector_size=args.vector_size,
            window_size=args.window_size,
            min_count=args.min_count,
            contamination=args.contamination,
            n_estimators=args.n_estimators,
            n_neighbors=args.n_neighbors,
            nu=args.nu,
            kernel=args.kernel,
            cross_validate=args.cross_validate,
            n_folds=args.n_folds,
            test_split=args.test_split
        )
        
        logger.info("Model metadata: %s", metadata)
        
    except Exception as e:
        logger.error("Failed to train model: %s", str(e))
        raise

if __name__ == '__main__':
    main() 