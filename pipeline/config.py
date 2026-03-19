"""
Pipeline configuration
"""
import os
from pathlib import Path

# Root directory
ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPT_DIR = DATA_DIR / "transcripts"

# API Keys (from env)
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")

# Default settings
DEFAULT_BATCH_SIZE = 50
DEFAULT_LANGUAGE = "zh"

# Ensure directories exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
