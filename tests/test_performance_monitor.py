import os
import shutil
import tempfile
import pandas as pd
from src.utils.performance_monitor import PerformanceMonitor

def test_initialization_creates_output_dir():
    temp_dir = tempfile.mkdtemp()
    monitor = PerformanceMonitor(output_dir=temp_dir)
    assert os.path.exists(temp_dir)
    assert isinstance(monitor.metrics, dict)
    assert set(monitor.metrics.keys()) == {'timestamp','num_logs','num_anomalies','processing_time','memory_usage','cpu_usage'}
    shutil.rmtree(temp_dir)

def test_update_metrics_adds_data():
    temp_dir = tempfile.mkdtemp()
    monitor = PerformanceMonitor(output_dir=temp_dir)
    monitor.update_metrics(num_logs=10, num_anomalies=2, processing_time=0.5)
    assert len(monitor.metrics['timestamp']) == 1
    assert monitor.metrics['num_logs'][0] == 10
    assert monitor.metrics['num_anomalies'][0] == 2
    assert monitor.metrics['processing_time'][0] == 0.5
    shutil.rmtree(temp_dir)

def test_save_metrics_creates_files():
    temp_dir = tempfile.mkdtemp()
    monitor = PerformanceMonitor(output_dir=temp_dir)
    # Ajouter 100 points pour forcer la sauvegarde
    for _ in range(100):
        monitor.update_metrics(num_logs=1, num_anomalies=0, processing_time=0.1)
    # Vérifier la présence de fichiers CSV et JSON
    files = os.listdir(temp_dir)
    csv_files = [f for f in files if f.startswith('performance_metrics_') and f.endswith('.csv')]
    json_files = [f for f in files if f.startswith('performance_stats_') and f.endswith('.json')]
    assert len(csv_files) >= 1
    assert len(json_files) >= 1
    shutil.rmtree(temp_dir)

def test_reset_metrics():
    temp_dir = tempfile.mkdtemp()
    monitor = PerformanceMonitor(output_dir=temp_dir)
    monitor.update_metrics(num_logs=5, num_anomalies=1, processing_time=0.2)
    monitor._reset_metrics()
    for key in monitor.metrics:
        assert monitor.metrics[key] == []
    shutil.rmtree(temp_dir)

def test_start_and_stop_monitoring():
    temp_dir = tempfile.mkdtemp()
    monitor = PerformanceMonitor(output_dir=temp_dir, interval=1)
    monitor.start()
    assert monitor.running
    monitor.stop()
    assert not monitor.running
    shutil.rmtree(temp_dir)

def test_update_metrics_handles_exceptions():
    temp_dir = tempfile.mkdtemp()
    monitor = PerformanceMonitor(output_dir=temp_dir)
    # Simuler une erreur en supprimant une clé
    del monitor.metrics['num_logs']
    try:
        monitor.update_metrics(num_logs=1, num_anomalies=1, processing_time=0.1)
    except Exception:
        assert False, "update_metrics ne doit pas lever d'exception même en cas d'erreur interne"
    shutil.rmtree(temp_dir) 