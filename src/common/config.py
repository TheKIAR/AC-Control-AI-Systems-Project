# Configuration settings for the AI systems project

import os

# Project directories
# __file__ = <root>/src/common/config.py -> parents[2] = <root>
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parents[2])
import os
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
FUZZY_MODELS_DIR = os.path.join(MODELS_DIR, 'fuzzy')
RL_MODELS_DIR = os.path.join(MODELS_DIR, 'rl')
GENERATOR_MODELS_DIR = os.path.join(MODELS_DIR, 'generator')

# Experiment settings
EXPERIMENTS_DIR = os.path.join(BASE_DIR, 'experiments')

# Logging settings
LOGGING_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Hyperparameters for reinforcement learning
RL_HYPERPARAMS = {
    'learning_rate': 0.001,
    'discount_factor': 0.99,
    'exploration_rate': 1.0,
    'exploration_decay': 0.995,
    'min_exploration_rate': 0.01,
}

# Fuzzy logic settings
FUZZY_SETTINGS = {
    'temperature_range': (16, 30),  # Temperature range for the fuzzy system
    'default_temperature': 22,       # Default temperature setting
}

# Data generation settings
DATA_GENERATION_SETTINGS = {
    'num_samples': 1000,
    'features': ['feature1', 'feature2', 'feature3'],
}