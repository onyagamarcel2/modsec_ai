"""
Configuration de pytest pour les tests.
"""

import os
import sys

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 