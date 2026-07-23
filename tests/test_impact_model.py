"""
Unit tests for ImpactModel package.
"""
import pytest
import pandas as pd
from src.data_loader import DataLoader
from src.impact_model import ImpactModel

def test_impact_model_association_matrix():
    loader = DataLoader()
    joined_links = loader.get_joined_impact_links()
    model = ImpactModel(joined_links)
    matrix = model.get_association_matrix()
    assert not matrix.empty

def test_temporal_factor_calculation():
    # Before event
    factor_before = ImpactModel.calculate_temporal_factor(months_since_event=-2, lag_months=6, curve_type='logistic')
    assert factor_before == 0.0
    
    # Linear curve test
    factor_half = ImpactModel.calculate_temporal_factor(months_since_event=3, lag_months=6, curve_type='linear')
    assert pytest.approx(factor_half, 0.01) == 0.5

def test_compute_cumulative_impact():
    loader = DataLoader()
    joined_links = loader.get_joined_impact_links()
    model = ImpactModel(joined_links)
    
    res = model.compute_cumulative_impact('ACC_OWNERSHIP', pd.to_datetime('2026-12-31'))
    assert 'total_impact_pp' in res
    assert 'event_breakdown' in res
    assert isinstance(res['total_impact_pp'], float)
