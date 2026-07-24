"""
Configuration settings for the Election Campaign Analysis project.
Defines base paths and project directory hierarchy.
"""

from pathlib import Path

# Base workspace directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory references
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Logs & output folders
LOG_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "outputs" / "figures"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
