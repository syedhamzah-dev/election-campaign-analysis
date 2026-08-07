"""
Data Loader Module for Election Campaign Analysis (2004-2024).

Provides modular, type-hinted functions to load raw datasets safely using pathlib
and perform basic structural validation checks.
"""

import logging
from pathlib import Path
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


def load_dataset(file_path: Path) -> pd.DataFrame:
    """
    Load a single CSV dataset from disk with error checking.

    Args:
        file_path (Path): Absolute or relative path to the CSV file.

    Returns:
        pd.DataFrame: Loaded DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the loaded DataFrame is empty.
    """
    if not file_path.exists():
        logger.error(f"Dataset file not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"Loading dataset from: {file_path}")
    df = pd.read_csv(file_path)

    if df.empty:
        logger.warning(f"Loaded DataFrame from {file_path.name} is empty.")
        raise ValueError(f"File {file_path.name} is empty.")

    logger.info(f"Successfully loaded {file_path.name}: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df


def load_all_raw_datasets(raw_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Load all four raw datasets required for the project.

    Args:
        raw_dir (Path): Directory containing raw CSV files.

    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping dataset keys to DataFrames.
    """
    expected_files = {
        "constituency": raw_dir / "constituency.csv",
        "party_summary": raw_dir / "result_by_party_cleaned.csv",
        "state_summary": raw_dir / "result_by_state_cleaned.csv",
        "election_2024": raw_dir / "election_results_2024.csv",
    }

    datasets: Dict[str, pd.DataFrame] = {}
    for key, file_path in expected_files.items():
        datasets[key] = load_dataset(file_path)

    return datasets
