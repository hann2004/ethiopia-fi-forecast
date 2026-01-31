"""
Impact modeling utilities for creating impact links between events and indicators
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_impact_link_template() -> Dict:
    """
    Create a template for impact link records that matches your schema
    
    Returns:
        dict: Template dictionary for impact link records
    """
    return {
        'record_id': '',  # Will be IMP_001, IMP_002, etc.
        'record_type': 'impact_link',
        'category': None,
        'pillar': '',  # ACCESS, USAGE, etc.
        'indicator': '',  # Description of the impact
        'indicator_code': '',  # IMP_TELEBIRR_MM, etc.
        'indicator_direction': 'higher_better',
        'value_numeric': None,
        'value_text': None,
        'value_type': None,
        'unit': None,
        'observation_date': None,
        'period_start': None,
        'period_end': None,
        'fiscal_year': None,
        'gender': 'all',
        'location': 'national',
        'region': None,
        'source_name': '',
        'source_type': 'calculated',
        'source_url': None,
        'confidence': 'medium',
        'related_indicator': '',  # Which indicator is affected (e.g., ACC_MM_ACCOUNT)
        'relationship_type': '',  # direct, indirect, enabling, constraining
        'impact_direction': '',  # increase, decrease, stabilize, mixed
        'impact_magnitude': '',  # high, medium, low, negligible
        'impact_estimate': None,  # Numeric estimate of impact
        'lag_months': None,  # How many months until effect
        'evidence_basis': '',  # empirical, literature, theoretical, expert
        'comparable_country': None,
        'collected_by': '',  # Your name
        'collection_date': datetime.now().strftime('%Y-%m-%d'),
        'original_text': '',
        'notes': ''
    }


def analyze_telebirr_impact(observations: pd.DataFrame) -> Dict:
    """
    Analyze the impact of Telebirr launch based on observed data
    
    Args:
        observations: Observations dataframe
        
    Returns:
        dict: Analysis results
    """
    # Get mobile money account data before and after Telebirr
    mm_data = observations[
        (observations['indicator_code'] == 'ACC_MM_ACCOUNT') &
        (observations['gender'] == 'all')
    ].sort_values('observation_date')
    
    # Get account ownership data
    acc_data = observations[
        (observations['indicator_code'] == 'ACC_OWNERSHIP') &
        (observations['gender'] == 'all') &
        (observations['observation_date'].astype(str).str.contains('2021|2024'))
    ].sort_values('observation_date')
    
    analysis = {
        'mm_growth': None,
        'acc_growth': None,
        'mm_before_after': {}
    }
    
    if len(mm_data) >= 2:
        # Calculate growth in mobile money accounts
        mm_2021 = mm_data[mm_data['observation_date'].astype(str).str.contains('2021')]['value_numeric'].values
        mm_2024 = mm_data[mm_data['observation_date'].astype(str).str.contains('2024')]['value_numeric'].values
        
        if len(mm_2021) > 0 and len(mm_2024) > 0:
            growth = mm_2024[0] - mm_2021[0]
            analysis['mm_growth'] = growth
            analysis['mm_before_after'] = {
                'before': mm_2021[0],
                'after': mm_2024[0],
                'growth_pp': growth
            }
    
    if len(acc_data) >= 2:
        # Get 2021 and 2024 account ownership
        acc_2021 = acc_data[acc_data['observation_date'].astype(str).str.contains('2021')]
        acc_2024 = acc_data[acc_data['observation_date'].astype(str).str.contains('2024')]
        
        if not acc_2021.empty and not acc_2024.empty:
            growth = acc_2024['value_numeric'].iloc[0] - acc_2021['value_numeric'].iloc[0]
            analysis['acc_growth'] = growth
    
    return analysis


def create_telebirr_impact_links(telebirr_event: pd.Series, analysis: Dict) -> List[Dict]:
    """
    Create impact links for Telebirr launch event
    
    Args:
        telebirr_event: Telebirr event record
        analysis: Analysis results from analyze_telebirr_impact
        
    Returns:
        list: List of impact link dictionaries
    """
    impact_links = []
    
    # Impact 1: Telebirr → Mobile Money Accounts
    link1 = create_impact_link_template()
    link1.update({
        'record_id': 'IMP_001',
        'parent_id': telebirr_event['record_id'],
        'pillar': 'ACCESS',
        'indicator': 'Impact: Telebirr Launch on Mobile Money Account Ownership',
        'indicator_code': 'IMP_TELEBIRR_MM',
        'related_indicator': 'ACC_MM_ACCOUNT',
        'relationship_type': 'direct',
        'impact_direction': 'increase',
        'impact_magnitude': 'high',
        'impact_estimate': analysis.get('mm_growth', 4.75),
        'lag_months': 6,
        'evidence_basis': 'empirical',
        'source_name': 'Analysis of Findex data before/after Telebirr launch',
        'original_text': f"Mobile money accounts increased from {analysis.get('mm_before_after', {}).get('before', 4.7)}% (2021) to {analysis.get('mm_before_after', {}).get('after', 9.45)}% (2024)",
        'notes': 'Conservative estimate assuming some growth would have occurred without Telebirr',
        'collected_by': 'Your Name'  # CHANGE THIS TO YOUR NAME
    })
    impact_links.append(link1)
    
    # Impact 2: Telebirr → Overall Account Ownership
    link2 = create_impact_link_template()
    link2.update({
        'record_id': 'IMP_002',
        'parent_id': telebirr_event['record_id'],
        'pillar': 'ACCESS',
        'indicator': 'Impact: Telebirr Launch on Overall Account Ownership',
        'indicator_code': 'IMP_TELEBIRR_ACC',
        'related_indicator': 'ACC_OWNERSHIP',
        'relationship_type': 'direct',
        'impact_direction': 'increase',
        'impact_magnitude': 'medium',
        'impact_estimate': analysis.get('acc_growth', 3.0),
        'lag_months': 12,
        'evidence_basis': 'empirical',
        'source_name': 'Comparison of Findex trends before and after Telebirr launch',
        'original_text': f"Account ownership grew by {analysis.get('acc_growth', 3.0):.1f} percentage points between 2021-2024",
        'notes': 'Growth slowed from previous periods despite Telebirr. Telebirr may have prevented larger slowdown.',
        'collected_by': 'Your Name'  # CHANGE THIS
    })
    impact_links.append(link2)
    
    return impact_links


def analyze_mpesa_impact(observations: pd.DataFrame) -> Dict:
    """
    Analyze the impact of M-Pesa launch based on observed data
    """
    # Get P2P transaction data
    p2p_data = observations[
        observations['indicator_code'] == 'USG_P2P_COUNT'
    ].sort_values('observation_date')
    
    analysis = {
        'p2p_growth_rate': None,
        'p2p_values': {}
    }
    
    if len(p2p_data) >= 2:
        # Calculate YoY growth
        p2p_2024 = p2p_data[p2p_data['observation_date'].astype(str).str.contains('2024')]
        p2p_2025 = p2p_data[p2p_data['observation_date'].astype(str).str.contains('2025')]
        
        if not p2p_2024.empty and not p2p_2025.empty:
            val_2024 = p2p_2024['value_numeric'].iloc[0]
            val_2025 = p2p_2025['value_numeric'].iloc[0]
            
            if val_2024 > 0:
                growth_rate = (val_2025 - val_2024) / val_2024
                analysis['p2p_growth_rate'] = growth_rate
                analysis['p2p_values'] = {
                    '2024': val_2024,
                    '2025': val_2025,
                    'growth': val_2025 - val_2024
                }
    
    return analysis


def create_mpesa_impact_links(mpesa_event: pd.Series, analysis: Dict) -> List[Dict]:
    """
    Create impact links for M-Pesa launch event
    """
    impact_links = []
    
    # Impact 3: M-Pesa → P2P Transaction Growth
    link1 = create_impact_link_template()
    link1.update({
        'record_id': 'IMP_003',
        'parent_id': mpesa_event['record_id'],
        'pillar': 'USAGE',
        'indicator': 'Impact: M-Pesa Launch on P2P Transaction Growth',
        'indicator_code': 'IMP_MPESA_P2P',
        'related_indicator': 'USG_P2P_COUNT',
        'relationship_type': 'direct',
        'impact_direction': 'increase',
        'impact_magnitude': 'high',
        'impact_estimate': analysis.get('p2p_growth_rate', 1.58),
        'lag_months': 3,
        'evidence_basis': 'empirical',
        'source_name': 'EthSwitch transaction data analysis',
        'original_text': f"P2P transactions grew from {analysis.get('p2p_values', {}).get('2024', 49.7):.1f}M to {analysis.get('p2p_values', {}).get('2025', 128.3):.1f}M after M-Pesa entry",
        'notes': 'M-Pesa launched Aug 2023, massive P2P growth observed 2024-2025',
        'collected_by': 'Your Name'  # CHANGE THIS
    })
    impact_links.append(link1)
    
    # Impact 4: M-Pesa → Mobile Money Competition
    link2 = create_impact_link_template()
    link2.update({
        'record_id': 'IMP_004',
        'parent_id': mpesa_event['record_id'],
        'pillar': 'ACCESS',
        'indicator': 'Impact: M-Pesa Entry on Market Competition',
        'indicator_code': 'IMP_MPESA_COMP',
        'related_indicator': 'ACC_MM_ACCOUNT',
        'relationship_type': 'indirect',
        'impact_direction': 'increase',
        'impact_magnitude': 'medium',
        'impact_estimate': 2.0,  # Estimated additional growth due to competition
        'lag_months': 9,
        'evidence_basis': 'literature',
        'comparable_country': 'Tanzania',
        'source_name': 'Market competition studies from similar markets',
        'original_text': 'Second mover effect: Competition typically increases adoption rates by 20-40%',
        'notes': 'Based on Vodacom M-Pesa entry impact in Tanzania',
        'collected_by': 'Your Name'  # CHANGE THIS
    })
    impact_links.append(link2)
    
    return impact_links


def create_fayda_impact_links(fayda_event: pd.Series, observations: pd.DataFrame) -> List[Dict]:
    """
    Create impact links for Fayda Digital ID rollout
    """
    impact_links = []
    
    # Get Fayda enrollment data
    fayda_data = observations[
        observations['indicator_code'] == 'ACC_FAYDA'
    ].sort_values('observation_date')
    
    enrollment_growth = None
    if len(fayda_data) >= 2:
        latest = fayda_data.iloc[-1]['value_numeric']
        earliest = fayda_data.iloc[0]['value_numeric']
        if earliest > 0:
            enrollment_growth = (latest - earliest) / earliest
    
    # Impact 5: Fayda → Digital ID Enrollment
    link1 = create_impact_link_template()
    link1.update({
        'record_id': 'IMP_005',
        'parent_id': fayda_event['record_id'],
        'pillar': 'ACCESS',
        'indicator': 'Impact: Fayda Digital ID on Enrollment',
        'indicator_code': 'IMP_FAYDA_ENROLL',
        'related_indicator': 'ACC_FAYDA',
        'relationship_type': 'direct',
        'impact_direction': 'increase',
        'impact_magnitude': 'high',
        'impact_estimate': enrollment_growth if enrollment_growth else 0.5,
        'lag_months': 1,
        'evidence_basis': 'empirical',
        'source_name': 'Fayda enrollment data analysis',
        'original_text': 'Digital ID enrollment showing rapid growth since program rollout',
        'notes': 'Critical enabler for financial inclusion through KYC simplification',
        'collected_by': 'Your Name'  # CHANGE THIS
    })
    impact_links.append(link1)
    
    # Impact 6: Fayda → Account Ownership
    link2 = create_impact_link_template()
    link2.update({
        'record_id': 'IMP_006',
        'parent_id': fayda_event['record_id'],
        'pillar': 'ACCESS',
        'indicator': 'Impact: Fayda Digital ID on Account Ownership',
        'indicator_code': 'IMP_FAYDA_ACC',
        'related_indicator': 'ACC_OWNERSHIP',
        'relationship_type': 'enabling',
        'impact_direction': 'increase',
        'impact_magnitude': 'medium',
        'impact_estimate': 0.05,  # 5% increase enabled by digital ID
        'lag_months': 24,
        'evidence_basis': 'theoretical',
        'source_name': 'Digital ID theory and comparable implementations',
        'original_text': 'Digital IDs reduce KYC costs and barriers to account opening',
        'notes': 'Long-term enabling effect; impact builds over time',
        'collected_by': 'Your Name'  # CHANGE THIS
    })
    impact_links.append(link2)
    
    return impact_links


def create_all_impact_links(events_df: pd.DataFrame, observations_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create all 14 impact links based on events and observations
    
    Args:
        events_df: Events dataframe
        observations_df: Observations dataframe
        
    Returns:
        pd.DataFrame: Dataframe with all impact links
    """
    all_links = []
    
    # Get specific events
    telebirr = events_df[events_df['indicator_code'] == 'EVT_TELEBIRR'].iloc[0]
    mpesa = events_df[events_df['indicator_code'] == 'EVT_MPESA'].iloc[0]
    fayda = events_df[events_df['indicator_code'] == 'EVT_FAYDA'].iloc[0]
    nfis = events_df[events_df['indicator_code'] == 'EVT_NFIS2'].iloc[0]
    crossover = events_df[events_df['indicator_code'] == 'EVT_CROSSOVER'].iloc[0]
    infrastructure = events_df[events_df['indicator_code'] == 'EVT_ETHIOPAY'].iloc[0]
    
    # Analyze impacts
    telebirr_analysis = analyze_telebirr_impact(observations_df)
    mpesa_analysis = analyze_mpesa_impact(observations_df)
    
    # Create impact links
    all_links.extend(create_telebirr_impact_links(telebirr, telebirr_analysis))
    all_links.extend(create_mpesa_impact_links(mpesa, mpesa_analysis))
    all_links.extend(create_fayda_impact_links(fayda, observations_df))
    
    # Create remaining impact links to reach 14 total
    # Impact 7: 4G Coverage → Mobile Money Usage
    link7 = create_impact_link_template()
    link7.update({
        'record_id': 'IMP_007',
        'parent_id': '',  # Need to find 4G expansion event or create one
        'pillar': 'ACCESS',
        'indicator': 'Impact: 4G Coverage Expansion on Mobile Money',
        'indicator_code': 'IMP_4G_MM',
        'related_indicator': 'ACC_MM_ACCOUNT',
        'relationship_type': 'enabling',
        'impact_direction': 'increase',
        'impact_magnitude': 'medium',
        'impact_estimate': 0.03,  # 3% increase per 10pp coverage increase
        'lag_months': 12,
        'evidence_basis': 'literature',
        'comparable_country': 'Multiple African markets',
        'source_name': 'GSMA research on mobile infrastructure impact',
        'original_text': '4G coverage expansion from 37.5% to 70.8% enables mobile money growth',
        'notes': 'Infrastructure enables usage; correlation observed in multiple markets',
        'collected_by': 'Your Name'  # CHANGE THIS
    })
    all_links.append(link7)
    
    # Continue creating more links...
    # You'll need to create links 8-14 similarly
    
    # Convert to DataFrame
    impact_links_df = pd.DataFrame(all_links)
    
    logger.info(f"Created {len(impact_links_df)} impact links")
    
    return impact_links_df
