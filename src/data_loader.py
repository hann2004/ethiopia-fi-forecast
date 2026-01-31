"""
Data loading and validation utilities for Ethiopia Financial Inclusion Forecasting
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_DATA_PATH = "data/raw/ethiopia_fi_unified_data.csv"
DEFAULT_REF_PATH = "data/raw/reference_codes .csv"


def load_unified_data(filepath: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Load the unified dataset from CSV
    
    Args:
        filepath: Path to the CSV file (defaults to DEFAULT_DATA_PATH)
        
    Returns:
        pandas.DataFrame: The loaded dataset
    """
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Successfully loaded data from {filepath}")
        logger.info(f"Dataset shape: {df.shape}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise


def validate_unified_schema(df: pd.DataFrame) -> Tuple[bool, Dict]:
    """
    Validate that the dataset follows the unified schema
    
    Args:
        df: The dataset to validate
        
    Returns:
        tuple: (is_valid, validation_report)
    """
    report = {
        'missing_columns': [],
        'required_columns_present': True,
        'record_type_distribution': None,
        'null_counts': None,
        'date_range': None
    }
    
    # Required columns based on the schema description
    required_columns = [
        'record_id', 'record_type', 'pillar', 'indicator', 
        'indicator_code', 'value_numeric', 'observation_date'
    ]
    
    # Check for missing columns
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        report['missing_columns'] = missing
        report['required_columns_present'] = False
        logger.warning(f"Missing required columns: {missing}")
    
    # Check record_type distribution
    if 'record_type' in df.columns:
        report['record_type_distribution'] = df['record_type'].value_counts().to_dict()
        expected_types = ['observation', 'event', 'impact_link', 'target']
        unexpected = [rt for rt in df['record_type'].unique() if rt not in expected_types]
        if unexpected:
            logger.warning(f"Unexpected record types: {unexpected}")
    
    # Check null values
    report['null_counts'] = df.isnull().sum().to_dict()
    
    # Check date range
    if 'observation_date' in df.columns:
        try:
            dates = pd.to_datetime(df['observation_date'], errors='coerce')
            valid_dates = dates.dropna()
            if not valid_dates.empty:
                report['date_range'] = {
                    'min': valid_dates.min().strftime('%Y-%m-%d'),
                    'max': valid_dates.max().strftime('%Y-%m-%d')
                }
        except:
            pass
    
    is_valid = report['required_columns_present']
    return is_valid, report


def separate_by_record_type(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Separate the unified dataset by record_type
    """
    separated = {}
    
    # Your data has these record_types
    record_types = {
        'observation': 'observations',
        'event': 'events', 
        'target': 'targets'
        # Note: No impact_links in the data yet!
    }
    
    for record_type, key_name in record_types.items():
        mask = df['record_type'] == record_type
        separated[key_name] = df[mask].copy()
        logger.info(f"Separated {len(separated[key_name])} {key_name}")
    
    # Impact links will be created separately
    separated['impact_links'] = pd.DataFrame()
    
    return separated


def load_reference_codes(filepath: str = DEFAULT_REF_PATH) -> pd.DataFrame:
    """
    Load the reference codes for categorical fields
    
    Args:
        filepath: Path to reference_codes.csv (defaults to DEFAULT_REF_PATH)
        
    Returns:
        pandas.DataFrame: Reference codes
    """
    try:
        ref_codes = pd.read_csv(filepath)
        logger.info(f"Loaded reference codes from {filepath}")
        return ref_codes
    except FileNotFoundError:
        logger.warning(f"Reference codes file not found: {filepath}")
        return pd.DataFrame()


def get_data_summary(df: pd.DataFrame, separated_data: Dict) -> Dict:
    """
    Generate a comprehensive summary of the dataset
    
    Args:
        df: Full unified dataset
        separated_data: Dictionary from separate_by_record_type
        
    Returns:
        dict: Summary statistics
    """
    summary = {}
    
    # Basic info
    summary['total_records'] = len(df)
    summary['columns'] = df.columns.tolist()
    
    # Record type distribution
    summary['record_type_counts'] = df['record_type'].value_counts().to_dict()
    
    # Pillar distribution (for observations and impact links)
    for key in ['observations', 'impact_links']:
        if key in separated_data and 'pillar' in separated_data[key].columns:
            summary[f'{key}_pillar_dist'] = separated_data[key]['pillar'].value_counts().to_dict()
    
    # Indicator coverage
    if 'observations' in separated_data:
        obs = separated_data['observations']
        summary['unique_indicators'] = obs['indicator'].nunique()
        summary['indicator_coverage'] = obs.groupby('indicator')['observation_date'].agg(['min', 'max', 'count']).to_dict()
    
    # Event categories
    if 'events' in separated_data and 'category' in separated_data['events'].columns:
        summary['event_categories'] = separated_data['events']['category'].value_counts().to_dict()
    
    # Temporal coverage
    if 'observation_date' in df.columns:
        try:
            dates = pd.to_datetime(df['observation_date'], errors='coerce')
            valid_dates = dates.dropna()
            if not valid_dates.empty:
                summary['date_range'] = {
                    'start': valid_dates.min(),
                    'end': valid_dates.max(),
                    'years_covered': (valid_dates.max() - valid_dates.min()).days / 365.25
                }
        except:
            pass
    
    return summary


def load_and_prepare_data(main_filepath: str = DEFAULT_DATA_PATH, 
                           ref_filepath: Optional[str] = DEFAULT_REF_PATH) -> Dict:
    """
    Main function to load and prepare all data
    
    Args:
        main_filepath: Path to ethiopia_fi_unified_data.csv (defaults to DEFAULT_DATA_PATH)
        ref_filepath: Path to reference_codes.csv (defaults to DEFAULT_REF_PATH)
        
    Returns:
        dict: Dictionary containing all data and metadata
    """
    logger.info("=" * 60)
    logger.info("Loading Ethiopia Financial Inclusion Data")
    logger.info("=" * 60)
    
    # Load main dataset
    df = load_unified_data(main_filepath)
    
    # Validate schema
    is_valid, validation_report = validate_unified_schema(df)
    if not is_valid:
        logger.error("Dataset validation failed!")
        for key, value in validation_report.items():
            logger.error(f"{key}: {value}")
    
    # Separate by record type
    separated = separate_by_record_type(df)
    
    # Load reference codes if provided
    ref_codes = None
    if ref_filepath:
        ref_codes = load_reference_codes(ref_filepath)
    
    # Generate summary
    summary = get_data_summary(df, separated)
    
    # Prepare result dictionary
    result = {
        'full_data': df,
        'separated': separated,
        'reference_codes': ref_codes,
        'validation_report': validation_report,
        'summary': summary,
        'is_valid': is_valid
    }
    
    logger.info("Data loading complete!")
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Observations: {len(separated.get('observations', pd.DataFrame()))}")
    logger.info(f"Events: {len(separated.get('events', pd.DataFrame()))}")
    logger.info(f"Impact links: {len(separated.get('impact_links', pd.DataFrame()))}")
    logger.info(f"Targets: {len(separated.get('targets', pd.DataFrame()))}")
    
    return result