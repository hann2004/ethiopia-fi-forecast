"""
Data enrichment utilities for adding new observations and events
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def add_new_observation(
    observations_df: pd.DataFrame,
    indicator: str,
    indicator_code: str,
    value_numeric: float,
    observation_date: str,
    pillar: str,
    source_name: str,
    source_url: str,
    confidence: str = 'medium',
    notes: str = '',
    collected_by: str = 'Data Scientist'
) -> pd.DataFrame:
    """
    Add a new observation to the dataset
    
    Args:
        observations_df: Existing observations DataFrame
        indicator: Description of what's measured
        indicator_code: Short code for the indicator
        value_numeric: The measured value
        observation_date: Date of measurement
        pillar: 'ACC' for Access or 'USG' for Usage
        source_name: Source of the data
        source_url: URL to the source
        confidence: Data confidence (high/medium/low)
        notes: Additional notes
        collected_by: Who collected this data
        
    Returns:
        Updated observations DataFrame
    """
    # Create a new ID
    new_id = f"OBS_{len(observations_df) + 1:03d}"
    
    # Create new observation record
    new_obs = pd.DataFrame([{
        'id': new_id,
        'parent_id': None,
        'record_type': 'observation',
        'pillar': pillar,
        'indicator': indicator,
        'indicator_code': indicator_code,
        'value_numeric': value_numeric,
        'observation_date': observation_date,
        'source_name': source_name,
        'source_url': source_url,
        'confidence': confidence,
        'category': None,
        'impact_direction': None,
        'impact_magnitude': None,
        'lag_months': None,
        'evidence_basis': None,
        'original_text': notes,
        'collected_by': collected_by,
        'collection_date': datetime.now().strftime('%Y-%m-%d'),
        'notes': notes
    }])
    
    # Add to existing observations
    updated_obs = pd.concat([observations_df, new_obs], ignore_index=True)
    
    logger.info(f"Added new observation: {indicator} = {value_numeric} on {observation_date}")
    
    return updated_obs


def add_new_event(
    events_df: pd.DataFrame,
    indicator: str,
    observation_date: str,
    category: str,
    source_name: str,
    source_url: str,
    confidence: str = 'medium',
    notes: str = '',
    collected_by: str = 'Data Scientist'
) -> pd.DataFrame:
    """
    Add a new event to the dataset
    
    Args:
        events_df: Existing events DataFrame
        indicator: Description of the event
        observation_date: Date the event occurred
        category: Type of event (policy, product_launch, infrastructure, etc.)
        source_name: Source of the information
        source_url: URL to the source
        confidence: Data confidence (high/medium/low)
        notes: Additional notes
        collected_by: Who collected this data
        
    Returns:
        Updated events DataFrame
    """
    # Create a new ID
    new_id = f"EVT_{len(events_df) + 1:03d}"
    
    # Create new event record
    new_event = pd.DataFrame([{
        'id': new_id,
        'parent_id': None,
        'record_type': 'event',
        'pillar': None,  # Events don't have pillars by design
        'indicator': indicator,
        'indicator_code': f"EVENT_{category.upper()}",
        'value_numeric': None,
        'observation_date': observation_date,
        'source_name': source_name,
        'source_url': source_url,
        'confidence': confidence,
        'category': category,
        'impact_direction': None,
        'impact_magnitude': None,
        'lag_months': None,
        'evidence_basis': None,
        'original_text': notes,
        'collected_by': collected_by,
        'collection_date': datetime.now().strftime('%Y-%m-%d'),
        'notes': notes
    }])
    
    # Add to existing events
    updated_events = pd.concat([events_df, new_event], ignore_index=True)
    
    logger.info(f"Added new event: {indicator} ({category}) on {observation_date}")
    
    return updated_events


def add_impact_link(
    impact_links_df: pd.DataFrame,
    event_id: str,
    pillar: str,
    related_indicator: str,
    impact_direction: int,
    impact_magnitude: float,
    lag_months: int,
    evidence_basis: str,
    confidence: str = 'medium',
    notes: str = '',
    collected_by: str = 'Data Scientist'
) -> pd.DataFrame:
    """
    Add a new impact link between an event and an indicator
    
    Args:
        impact_links_df: Existing impact links DataFrame
        event_id: ID of the event this links to
        pillar: 'ACC' or 'USG'
        related_indicator: Which indicator is affected
        impact_direction: +1 for positive effect, -1 for negative
        impact_magnitude: Strength of the effect
        lag_months: Months until effect is seen
        evidence_basis: Source of this impact estimate
        confidence: Estimate confidence (high/medium/low)
        notes: Additional notes
        collected_by: Who created this link
        
    Returns:
        Updated impact links DataFrame
    """
    # Create a new ID
    new_id = f"IMP_{len(impact_links_df) + 1:03d}"
    
    # Create new impact link record
    new_link = pd.DataFrame([{
        'id': new_id,
        'parent_id': event_id,
        'record_type': 'impact_link',
        'pillar': pillar,
        'indicator': f"Impact of event {event_id} on {related_indicator}",
        'indicator_code': f"IMPACT_{pillar}_{related_indicator[:10]}",
        'value_numeric': None,
        'observation_date': None,
        'source_name': evidence_basis,
        'source_url': None,
        'confidence': confidence,
        'category': None,
        'impact_direction': impact_direction,
        'impact_magnitude': impact_magnitude,
        'lag_months': lag_months,
        'evidence_basis': evidence_basis,
        'original_text': notes,
        'collected_by': collected_by,
        'collection_date': datetime.now().strftime('%Y-%m-%d'),
        'notes': notes
    }])
    
    # Add to existing impact links
    updated_links = pd.concat([impact_links_df, new_link], ignore_index=True)
    
    logger.info(f"Added new impact link: Event {event_id} → {pillar}:{related_indicator}")
    
    return updated_links


def save_enriched_data(
    enriched_data: Dict[str, pd.DataFrame],
    output_dir: str,
    filename_prefix: str = 'ethiopia_fi_enriched'
) -> None:
    """
    Save enriched data to CSV files
    
    Args:
        enriched_data: Dictionary with dataframes for each record type
        output_dir: Directory to save files
        filename_prefix: Prefix for output files
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each dataframe
    for record_type, df in enriched_data.items():
        filename = f"{filename_prefix}_{record_type}.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {record_type} to {filepath}")
    
    # Also save combined dataset
    combined = pd.concat(enriched_data.values(), ignore_index=True)
    combined_filepath = os.path.join(output_dir, f"{filename_prefix}_combined.csv")
    combined.to_csv(combined_filepath, index=False)
    logger.info(f"Saved combined dataset to {combined_filepath}")