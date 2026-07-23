"""
Unit tests for InclusionForecaster package.
"""
import pytest
import pandas as pd
from src.data_loader import DataLoader
from src.impact_model import ImpactModel
from src.forecaster import InclusionForecaster

def test_fit_trend():
    loader = DataLoader()
    access_hist = loader.get_findex_access_history()
    forecaster = InclusionForecaster()
    
    fit_res = forecaster.fit_trend(access_hist)
    assert 'slope' in fit_res
    assert 'intercept' in fit_res
    assert 'rmse' in fit_res
    assert fit_res['slope'] > 0

def test_forecast_scenarios():
    loader = DataLoader()
    access_hist = loader.get_findex_access_history()
    joined_links = loader.get_joined_impact_links()
    impact_model = ImpactModel(joined_links)
    
    forecaster = InclusionForecaster(impact_model)
    fit_res = forecaster.fit_trend(access_hist)
    
    scenarios_df = forecaster.forecast_all_scenarios(fit_res, 'ACC_OWNERSHIP', target_years=[2025, 2026, 2027])
    assert not scenarios_df.empty
    assert set(scenarios_df['scenario'].unique()) == {'base', 'optimistic', 'pessimistic'}
    assert len(scenarios_df) == 9
