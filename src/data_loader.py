import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional

class DataLoader:
    """
    DataLoader for loading, parsing, and splitting Ethiopia Financial Inclusion Unified Dataset.
    """
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            # Default to processed enriched dataset
            base_dir = Path(__file__).resolve().parent.parent
            data_path = base_dir / "data" / "processed" / "enriched_unified_data.csv"
            if not data_path.exists():
                data_path = base_dir / "data" / "raw" / "ethiopia_fi_unified_data.csv"
        
        self.data_path = Path(data_path)
        self.df = pd.DataFrame()
        self.observations = pd.DataFrame()
        self.events = pd.DataFrame()
        self.impact_links = pd.DataFrame()
        self.targets = pd.DataFrame()
        self.load_data()

    def load_data(self) -> pd.DataFrame:
        """Loads and parses the unified CSV file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found at {self.data_path}")
            
        self.df = pd.read_csv(self.data_path)
        
        # Parse dates
        if 'observation_date' in self.df.columns:
            self.df['observation_date'] = pd.to_datetime(self.df['observation_date'], errors='coerce')
        if 'period_start' in self.df.columns:
            self.df['period_start'] = pd.to_datetime(self.df['period_start'], errors='coerce')
        if 'period_end' in self.df.columns:
            self.df['period_end'] = pd.to_datetime(self.df['period_end'], errors='coerce')
            
        # Split by record_type
        self.observations = self.df[self.df['record_type'] == 'observation'].copy()
        self.events = self.df[self.df['record_type'] == 'event'].copy()
        self.impact_links = self.df[self.df['record_type'] == 'impact_link'].copy()
        self.targets = self.df[self.df['record_type'] == 'target'].copy()
        
        return self.df

    def get_indicator_series(self, indicator_code: str) -> pd.DataFrame:
        """Retrieves historical observations for a specific indicator code."""
        obs = self.observations[self.observations['indicator_code'] == indicator_code].copy()
        obs = obs.sort_values('observation_date').dropna(subset=['value_numeric'])
        return obs[['observation_date', 'value_numeric', 'indicator', 'unit', 'source_name', 'confidence']]

    def get_findex_access_history(self) -> pd.DataFrame:
        """
        Returns Global Findex Account Ownership Rate (ACC_OWNERSHIP) historical trajectory.
        """
        df_acc = self.get_indicator_series('ACC_OWNERSHIP')
        # Filter for national total level (where gender is 'total' or null/national)
        if 'gender' in self.observations.columns:
            national_acc = self.observations[
                (self.observations['indicator_code'] == 'ACC_OWNERSHIP') &
                ((self.observations['gender'] == 'total') | (self.observations['gender'].isna()) | (self.observations['gender'] == 'all'))
            ].copy()
            if not national_acc.empty:
                df_acc = national_acc.sort_values('observation_date')[['observation_date', 'value_numeric']]
        
        df_acc['year'] = df_acc['observation_date'].dt.year
        return df_acc.drop_duplicates(subset=['year']).reset_index(drop=True)

    def get_findex_usage_history(self) -> pd.DataFrame:
        """
        Returns Global Findex / Digital Payment Adoption (USG_DIGITAL_PAYMENT / ACC_MM_ACCOUNT) historical trajectory.
        """
        df_usg = self.get_indicator_series('USG_DIGITAL_PAYMENT')
        if df_usg.empty:
            # Fallback to mobile money account rate if usage series sparse
            df_usg = self.get_indicator_series('ACC_MM_ACCOUNT')
        df_usg['year'] = df_usg['observation_date'].dt.year
        return df_usg.drop_duplicates(subset=['year']).reset_index(drop=True)

    def get_joined_impact_links(self) -> pd.DataFrame:
        """
        Joins impact_links with their parent events to provide full metadata (event date, category, indicator, etc.).
        """
        if self.impact_links.empty or self.events.empty:
            return pd.DataFrame()
            
        links = self.impact_links.copy()
        events = self.events.copy()
        
        # Merge on parent_id == record_id
        merged = pd.merge(
            links,
            events[['record_id', 'indicator', 'category', 'observation_date', 'source_name']],
            left_on='parent_id',
            right_on='record_id',
            suffixes=('', '_event')
        )
        
        merged.rename(columns={
            'indicator_event': 'event_name',
            'observation_date_event': 'event_date'
        }, inplace=True)
        
        # Standardize numeric impact estimate
        if 'impact_estimate' in merged.columns and 'impact_magnitude' in merged.columns:
            # Fill NaN impact_estimate from impact_magnitude if numeric string
            merged['impact_estimate_clean'] = merged['impact_estimate']
            mask_missing = merged['impact_estimate_clean'].isna()
            
            # Map text magnitude if numeric string
            def parse_mag(val):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    if str(val).lower() == 'high':
                        return 15.0
                    elif str(val).lower() == 'medium':
                        return 8.0
                    elif str(val).lower() == 'low':
                        return 3.0
                    return 5.0
            
            merged.loc[mask_missing, 'impact_estimate_clean'] = merged.loc[mask_missing, 'impact_magnitude'].apply(parse_mag)
        else:
            merged['impact_estimate_clean'] = 5.0

        return merged

    def get_targets(self) -> pd.DataFrame:
        return self.targets
