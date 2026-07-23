import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

class ImpactModel:
    """
    Event Impact Modeling Engine for Ethiopia Financial Inclusion Forecasting System.
    Translates events, lag structures, and impact links into temporal indicator interventions.
    """
    def __init__(self, impact_links_df: pd.DataFrame):
        """
        Parameters:
        -----------
        impact_links_df : pd.DataFrame
            DataFrame containing joined impact links (from DataLoader.get_joined_impact_links()).
        """
        self.df = impact_links_df.copy()
        self.association_matrix = pd.DataFrame()
        if not self.df.empty:
            self._build_association_matrix()

    def _build_association_matrix(self) -> pd.DataFrame:
        """
        Builds an Event x Indicator matrix summarizing estimated impact magnitudes.
        """
        if self.df.empty:
            return pd.DataFrame()

        # Fill category from event if missing
        df_copy = self.df.copy()
        if 'category_event' in df_copy.columns:
            df_copy['category_final'] = df_copy['category_event'].fillna('unassigned')
        else:
            df_copy['category_final'] = df_copy['category'].fillna('unassigned')

        # Group by event_name and related_indicator
        pivot_df = df_copy.pivot_table(
            index=['parent_id', 'event_name', 'category_final'],
            columns='related_indicator',
            values='impact_estimate_clean',
            aggfunc='sum',
            fill_value=0.0
        )
        self.association_matrix = pivot_df
        return pivot_df

    def get_association_matrix(self) -> pd.DataFrame:
        """Returns the built association matrix."""
        if self.association_matrix.empty:
            self._build_association_matrix()
        return self.association_matrix

    @staticmethod
    def calculate_temporal_factor(
        months_since_event: float,
        lag_months: float,
        curve_type: str = 'logistic',
        steepness: float = 0.5
    ) -> float:
        """
        Calculates the proportion (0.0 to 1.0) of an event's full impact realized 
        given the elapsed months since event launch and lag parameters.
        """
        if months_since_event < 0:
            return 0.0
        
        if curve_type == 'step':
            return 1.0 if months_since_event >= lag_months else 0.0
        
        elif curve_type == 'linear':
            if lag_months <= 0:
                return 1.0
            return min(1.0, months_since_event / lag_months)
        
        elif curve_type == 'logistic':
            # S-curve centered around lag_months / 2
            if lag_months <= 0:
                return 1.0
            center = lag_months / 2.0
            # Standardized logistic shift
            k = steepness / (lag_months / 6.0 if lag_months > 6 else 1.0)
            val = 1.0 / (1.0 + np.exp(-k * (months_since_event - center)))
            # Clamp between 0 and 1
            return float(np.clip(val, 0.0, 1.0))
        
        else:
            return 1.0 if months_since_event >= lag_months else 0.0

    def compute_cumulative_impact(
        self,
        indicator_code: str,
        target_date: pd.Timestamp,
        curve_type: str = 'logistic',
        scenario_multiplier: float = 1.0,
        historical_cutoff: Optional[pd.Timestamp] = None
    ) -> Dict[str, float]:
        """
        Computes the net percentage point addition to `indicator_code` at `target_date`
        accumulated from all relevant events that occur **after** `historical_cutoff`.

        Events on or before `historical_cutoff` are already embedded in the OLS trend
        (fitted on historical data up to that date) and must not be double-counted.
        If `historical_cutoff` is None, all events are included.
        """
        if self.df.empty:
            return {'total_impact_pp': 0.0, 'event_breakdown': {}}

        # Filter impact links affecting this indicator
        links = self.df[self.df['related_indicator'] == indicator_code].copy()
        if links.empty:
            return {'total_impact_pp': 0.0, 'event_breakdown': {}}

        total_impact = 0.0
        breakdown = {}

        for _, row in links.iterrows():
            event_date = pd.to_datetime(row['event_date'])
            if pd.isna(event_date):
                continue

            # Skip events already captured in historical trend
            if historical_cutoff is not None and event_date <= historical_cutoff:
                continue

            # Elapsed months since event launch
            elapsed_days = (target_date - event_date).days
            elapsed_months = max(0.0, elapsed_days / 30.4375)

            lag = float(row.get('lag_months', 6.0))
            if np.isnan(lag):
                lag = 6.0

            est = float(row.get('impact_estimate_clean', 5.0))
            direction = str(row.get('impact_direction', 'increase')).lower()
            sign = 1.0 if direction in ['increase', 'positive', 'up'] else -1.0

            factor = self.calculate_temporal_factor(elapsed_months, lag, curve_type=curve_type)

            net_event_impact = sign * est * factor * scenario_multiplier
            total_impact += net_event_impact

            event_label = row.get('event_name', row['parent_id'])
            breakdown[event_label] = round(net_event_impact, 2)

        return {
            'total_impact_pp': round(total_impact, 2),
            'event_breakdown': breakdown
        }

    def validate_against_historical(self, obs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Validates predicted impact against historical actuals.
        e.g. Telebirr launch May 2021 impact on Mobile Money Accounts in Dec 2021 vs Nov 2024.
        """
        validation_results = []
        
        # Telebirr check
        telebirr_links = self.df[self.df['parent_id'] == 'EVT_0001']
        if not telebirr_links.empty:
            # Actual mm account growth 2021 -> 2024: 4.7% -> 9.45% (+4.75pp)
            pred_2024 = self.compute_cumulative_impact('ACC_MM_ACCOUNT', pd.to_datetime('2024-11-29'))
            validation_results.append({
                'event': 'Telebirr Launch (May 2021)',
                'indicator': 'ACC_MM_ACCOUNT',
                'actual_change_pp': 4.75,
                'predicted_impact_pp': pred_2024['total_impact_pp'],
                'difference_pp': round(pred_2024['total_impact_pp'] - 4.75, 2)
            })

        return pd.DataFrame(validation_results)
