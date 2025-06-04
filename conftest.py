"""
Pytest configuration and shared fixtures for UK PEP Scraper tests.

This file contains common fixtures and configuration used across all test files.
"""

import pytest
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Generator, Any, Dict, List

import pandas as pd
from flask.testing import FlaskClient

from app import app, UKGovernmentScraper


@pytest.fixture(scope="session")
def test_app():
    """Create a Flask app configured for testing."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def client(test_app) -> FlaskClient:
    """Create a test client for the Flask application."""
    with test_app.test_client() as client:
        yield client


@pytest.fixture
def temp_outputs_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    outputs_dir = Path(temp_dir) / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    
    yield outputs_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_mp_data() -> List[Dict[str, Any]]:
    """Sample MP data for testing."""
    return [
        {
            "person_id": 1001,
            "display_name": "John Smith",
            "full_title": "John Smith MP",
            "constituency_name": "Test Constituency",
            "party_name": "Test Party",
            "house_membership_start_date": "2020-01-01",
            "house_membership_end_date": None
        },
        {
            "person_id": 1002,
            "display_name": "Jane Doe",
            "full_title": "Jane Doe MP",
            "constituency_name": "Another Constituency",
            "party_name": "Another Party",
            "house_membership_start_date": "2019-06-01",
            "house_membership_end_date": "2023-12-31"  # Former MP
        }
    ]


@pytest.fixture
def sample_lord_data() -> List[Dict[str, Any]]:
    """Sample Lords data for testing."""
    return [
        {
            "person_id": 2001,
            "display_name": "Lord Test",
            "full_title": "The Rt Hon. Lord Test",
            "party_name": "Test Party",
            "house_membership_start_date": "2015-01-01",
            "house_membership_end_date": None
        },
        {
            "person_id": 2002,
            "display_name": "Baroness Example",
            "full_title": "The Rt Hon. Baroness Example",
            "party_name": "Example Party",
            "house_membership_start_date": "2010-01-01",
            "house_membership_end_date": "2022-06-30"  # Former member
        }
    ]


@pytest.fixture
def sample_government_roles() -> Dict[str, List[Dict[str, Any]]]:
    """Sample government roles data for testing."""
    return {
        "mps_government_roles": [
            {
                "person_id": 1001,
                "display_name": "John Smith",
                "position_name": "Secretary of State for Testing",
                "government_incumbency_start_date": "2023-01-01",
                "government_incumbency_end_date": None
            },
            {
                "person_id": 1003,
                "display_name": "Bob Johnson",
                "position_name": "Minister for Examples",
                "government_incumbency_start_date": "2022-01-01",
                "government_incumbency_end_date": "2023-12-31"  # Former role
            }
        ],
        "lords_government_roles": [
            {
                "person_id": 2001,
                "display_name": "Lord Test",
                "position_name": "Minister of State for Testing",
                "government_incumbency_start_date": "2023-06-01",
                "government_incumbency_end_date": None
            }
        ]
    }


@pytest.fixture
def sample_committee_memberships() -> Dict[str, List[Dict[str, Any]]]:
    """Sample committee memberships data for testing."""
    return {
        "mps_committee_memberships": [
            {
                "person_id": 1001,
                "display_name": "John Smith",
                "committee_name": "Test Committee",
                "committee_membership_start_date": "2023-01-01",
                "committee_membership_end_date": None
            },
            {
                "person_id": 1002,
                "display_name": "Jane Doe",
                "committee_name": "Example Committee",
                "committee_membership_start_date": "2022-01-01",
                "committee_membership_end_date": "2023-06-30"  # Former membership
            }
        ],
        "lords_committee_memberships": [
            {
                "person_id": 2001,
                "display_name": "Lord Test",
                "committee_name": "Lords Test Committee",
                "committee_membership_start_date": "2023-01-01",
                "committee_membership_end_date": None
            }
        ]
    }


@pytest.fixture
def mock_pdpy():
    """Mock pdpy module for testing."""
    mock = MagicMock()
    
    # Configure DataFrame returns
    mp_df = pd.DataFrame([
        {"person_id": 1001, "display_name": "Test MP", "constituency_name": "Test Constituency"}
    ])
    lord_df = pd.DataFrame([
        {"person_id": 2001, "display_name": "Test Lord", "party_name": "Test Party"}
    ])
    
    mock.fetch_mps.return_value = mp_df
    mock.fetch_lords.return_value = lord_df
    mock.fetch_mps_government_roles.return_value = pd.DataFrame([
        {"person_id": 1001, "display_name": "Test MP", "position_name": "Test Minister"}
    ])
    mock.fetch_lords_government_roles.return_value = pd.DataFrame([
        {"person_id": 2001, "display_name": "Test Lord", "position_name": "Test Lord Minister"}
    ])
    mock.fetch_mps_committee_memberships.return_value = pd.DataFrame([
        {"person_id": 1001, "display_name": "Test MP", "committee_name": "Test Committee"}
    ])
    mock.fetch_lords_committee_memberships.return_value = pd.DataFrame([
        {"person_id": 2001, "display_name": "Test Lord", "committee_name": "Test Committee"}
    ])
    
    return mock


@pytest.fixture
def mock_scraper_with_data(sample_mp_data, sample_lord_data, sample_government_roles, sample_committee_memberships):
    """Create a mock scraper with realistic test data."""
    mock = Mock(spec=UKGovernmentScraper)
    
    # Configure return values
    mock.scrape_mps.return_value = sample_mp_data
    mock.scrape_lords.return_value = sample_lord_data
    mock.scrape_government_roles.return_value = sample_government_roles
    mock.scrape_committee_memberships.return_value = sample_committee_memberships
    
    # Complete dataset
    mock.scrape_all_data.return_value = {
        "metadata": {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "scraper_version": "1.0.0",
            "data_source": "UK Parliament API via pdpy library"
        },
        "members_of_parliament": sample_mp_data,
        "house_of_lords": sample_lord_data,
        "government_roles": sample_government_roles,
        "committee_memberships": sample_committee_memberships,
        "summary": {
            "total_mps": len(sample_mp_data),
            "total_lords": len(sample_lord_data),
            "total_mps_gov_roles": len(sample_government_roles["mps_government_roles"]),
            "total_lords_gov_roles": len(sample_government_roles["lords_government_roles"]),
            "total_mps_committee_memberships": len(sample_committee_memberships["mps_committee_memberships"]),
            "total_lords_committee_memberships": len(sample_committee_memberships["lords_committee_memberships"])
        }
    }
    
    # CSV export
    mock.export_to_csv.return_value = ["/tmp/test_export.csv"]
    
    # Cache and state
    mock.cache = {}
    mock.last_updated = datetime.now(timezone.utc)
    
    return mock


@pytest.fixture
def real_scraper():
    """Create a real scraper instance for unit testing."""
    return UKGovernmentScraper()


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API endpoint test"
    )
    config.addinivalue_line(
        "markers", "scraper: mark test as scraper functionality test"
    )
    config.addinivalue_line(
        "markers", "csv: mark test as CSV export test"
    )
    config.addinivalue_line(
        "markers", "error: mark test as error handling test"
    )
    config.addinivalue_line(
        "markers", "cache: mark test as caching functionality test"
    )


# Pytest hooks for better test output
def pytest_runtest_setup(item):
    """Called before each test is run."""
    print(f"\n🧪 Running: {item.name}")


def pytest_runtest_teardown(item):
    """Called after each test is run."""
    if hasattr(item, 'rep_call'):
        if item.rep_call.failed:
            print(f"❌ Failed: {item.name}")
        elif item.rep_call.passed:
            print(f"✅ Passed: {item.name}")
    else:
        # Fallback if rep_call isn't available
        print(f"🔄 Completed: {item.name}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test results for teardown reporting."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{call.when}", rep)
