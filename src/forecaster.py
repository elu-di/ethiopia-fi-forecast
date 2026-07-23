import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
from .impact_model import ImpactModel

# Default historical cutoff: last Findex survey date (Nov 2024)
# Events on or before this date are already reflected in the OLS trend
DEFAULT_HISTORICAL_CUTOFF = pd.Timestamp('2024-11-29')

class InclusionForecaster:
    """
    Forecasting System for Ethiopia Financial Inclusion (Access & Usage) 2025-2027.
    Combines trend regression with event-augmented intervention modeling and uncertainty bounds.
    """
    def __init__(self, impact_model: Optional[ImpactModel] = None):
        self.impact_model = impact_model
        self.models = {}

    def fit_trend(
        self,
        df_hist: pd.DataFrame,
        value_col: str = 'value_numeric',
        date_col: str = 'observation_date'
    ) -> Dict:
        """
        Fits OLS linear trend model on historical time series data.
        """
        df = df_hist.copy()
        df['year'] = pd.to_datetime(df[date_col]).dt.year
        df = df.dropna(subset=[value_col, 'year']).sort_values('year')
        
        if len(df) < 2:
            raise ValueError("Insufficient data points to fit trend model (at least 2 required).")
            
        X = df['year'].values - 2011  # Years since 2011 baseline
        y = df[value_col].values
        
        X_design = add_constant(X)
        ols_res = OLS(y, X_design).fit()
        
        # Calculate residual std error
        residuals = y - ols_res.predict(X_design)
        dof = max(1, len(y) - 2)
        rmse = float(np.sqrt(np.sum(residuals**2) / dof))
        
        fit_summary = {
            'slope': float(ols_res.params[1]),
            'intercept': float(ols_res.params[0]),
            'r2': float(ols_res.rsquared),
            'rmse': rmse,
            'ols_results': ols_res,
            'base_year': 2011,
            'n_obs': len(df)
        }
        return fit_summary

    def forecast_baseline(
        self,
        fit_summary: Dict,
        target_years: List[int] = [2025, 2026, 2027],
        confidence_level: float = 0.95
    ) -> pd.DataFrame:
        """
        Generates baseline trend predictions with 95% confidence intervals.
        """
        records = []
        slope = fit_summary['slope']
        intercept = fit_summary['intercept']
        rmse = fit_summary['rmse']
        
        # t-statistic approximation for ~95% CI
        t_crit = 2.132 if fit_summary['n_obs'] <= 5 else 1.96
        
        for yr in target_years:
            t = yr - fit_summary['base_year']
            pred = intercept + slope * t
            
            # Prediction interval expands with distance from historical mean
            mean_t = 6.0  # Approx midpoint between 2011 and 2024
            distance_factor = np.sqrt(1 + 1/fit_summary['n_obs'] + ((t - mean_t)**2) / 50.0)
            margin = t_crit * rmse * distance_factor
            
            records.append({
                'year': yr,
                'forecast_baseline': round(pred, 2),
                'ci_lower': round(max(0.0, pred - margin), 2),
                'ci_upper': round(min(100.0, pred + margin), 2)
            })
            
        return pd.DataFrame(records)

    def forecast_event_augmented(
        self,
        fit_summary: Dict,
        indicator_code: str,
        target_years: List[int] = [2025, 2026, 2027],
        scenario: str = 'base',
        curve_type: str = 'logistic',
        historical_cutoff: Optional[pd.Timestamp] = None
    ) -> pd.DataFrame:
        """
        Generates event-augmented forecasts combining trend baseline + cumulative event intervention.

        Only events with an `event_date` **after** `historical_cutoff` are added on top of the
        OLS baseline.  Events before (or on) the cutoff are already embedded in the historical
        trend and must not be double-counted.

        Scenarios: 'base' (1.0x), 'optimistic' (1.25x), 'pessimistic' (0.75x).
        """
        if historical_cutoff is None:
            historical_cutoff = DEFAULT_HISTORICAL_CUTOFF

        multiplier_map = {
            'base': 1.0,
            'optimistic': 1.25,
            'pessimistic': 0.75
        }
        scenario_multiplier = multiplier_map.get(scenario.lower(), 1.0)

        base_fc = self.forecast_baseline(fit_summary, target_years)
        records = []

        for _, row in base_fc.iterrows():
            yr = int(row['year'])
            target_date = pd.to_datetime(f"{yr}-12-31")

            event_impact = 0.0
            event_breakdown = {}

            if self.impact_model is not None:
                impact_res = self.impact_model.compute_cumulative_impact(
                    indicator_code=indicator_code,
                    target_date=target_date,
                    curve_type=curve_type,
                    scenario_multiplier=scenario_multiplier,
                    historical_cutoff=historical_cutoff
                )
                event_impact = impact_res['total_impact_pp']
                event_breakdown = impact_res['event_breakdown']

            base_val = row['forecast_baseline']

            # Cap at 100% — account ownership cannot exceed 100%
            final_pred = min(100.0, base_val + event_impact)

            # Scenario specific adjustments to CI width
            ci_margin = (row['ci_upper'] - row['ci_lower']) / 2.0
            if scenario == 'optimistic':
                lower = max(0.0, final_pred - ci_margin * 0.8)
                upper = min(100.0, final_pred + ci_margin * 1.2)
            elif scenario == 'pessimistic':
                lower = max(0.0, final_pred - ci_margin * 1.2)
                upper = min(100.0, final_pred + ci_margin * 0.8)
            else:
                lower = max(0.0, final_pred - ci_margin)
                upper = min(100.0, final_pred + ci_margin)

            records.append({
                'year': yr,
                'scenario': scenario,
                'baseline_trend': base_val,
                'event_impact_pp': event_impact,
                'forecast_final': round(final_pred, 2),
                'ci_lower': round(lower, 2),
                'ci_upper': round(upper, 2),
                'event_breakdown': event_breakdown
            })

        return pd.DataFrame(records)

    def forecast_all_scenarios(
        self,
        fit_summary: Dict,
        indicator_code: str,
        target_years: List[int] = [2025, 2026, 2027]
    ) -> pd.DataFrame:
        """
        Returns predictions across all 3 scenarios (Base, Optimistic, Pessimistic).
        """
        dfs = []
        for sc in ['base', 'optimistic', 'pessimistic']:
            df_sc = self.forecast_event_augmented(
                fit_summary,
                indicator_code,
                target_years=target_years,
                scenario=sc
            )
            dfs.append(df_sc)
        return pd.concat(dfs, ignore_index=True)
