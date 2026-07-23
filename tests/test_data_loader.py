"""
Unit tests for DataLoader package.
"""
import pytest
import pandas as pd
from src.data_loader import DataLoader

def test_data_loader_initialization():
    loader = DataLoader()
    assert not loader.df.empty
    assert 'record_type' in loader.df.columns
    assert not loader.observations.empty
    assert not loader.events.empty
    assert not loader.impact_links.empty

def test_get_findex_access_history():
    loader = DataLoader()
    access_hist = loader.get_findex_access_history()
    assert not access_hist.empty
    assert 'year' in access_hist.columns
    assert 'value_numeric' in access_hist.columns
    # Verify historical values exist
    years = access_hist['year'].tolist()
    assert 2011 in years or 2024 in years

def test_joined_impact_links():
    loader = DataLoader()
    joined = loader.get_joined_impact_links()
    assert not joined.empty
    assert 'parent_id' in joined.columns
    assert 'related_indicator' in joined.columns
    assert 'impact_estimate_clean' in joined.columns
