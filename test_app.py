#!/usr/bin/env python3
"""
Comprehensive test suite for the UK PEP scraper Flask application.

This test suite provides extensive coverage of all endpoints, error handling,
and unit tests for the UKGovernmentScraper class methods.
"""

import json
import pytest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Generator

import pandas as pd
from flask.testing import FlaskClient

# Import the Flask app and scraper class
from app import app, UKGovernmentScraper


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    """Create Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_scraper() -> MagicMock:
    """Create a mock scraper with sample data."""
    mock = MagicMock()
    
    # Sample MP data
    sample_mp_data = [
        {
            "name": "John Smith",
            "constituency": "Test Constituency",
            "party": "Test Party",
            "start_date": "2019-12-12",
            "end_date": None
        }
    ]
    
    # Sample Lords data
    sample_lords_data = [
        {
            "name": "Lord Test",
            "house": "Lords",
            "party": "Test Party",
            "start_date": "2020-01-01",
            "end_date": None
        }
    ]
    
    # Sample committee data
    sample_committee_data = {
        "mps_committee_memberships": [
            {
                "name": "Jane Doe",
                "committee": "Test Committee",
                "role": "Member",
                "start_date": "2020-01-01",
                "end_date": None
            }
        ],
        "lords_committee_memberships": [
            {
                "name": "Lord Member",
                "committee": "Lords Committee", 
                "role": "Chair",
                "start_date": "2020-01-01",
                "end_date": None
            }
        ]
    }
    
    # Sample government roles data
    sample_gov_roles_data = {
        "mps_government_roles": [
            {
                "name": "Minister Test",
                "role": "Secretary of State",
                "department": "Test Department",
                "start_date": "2021-01-01",
                "end_date": None
            }
        ],
        "lords_government_roles": [
            {
                "name": "Lord Minister",
                "role": "Minister of State",
                "department": "Lords Department",
                "start_date": "2021-01-01",
                "end_date": None
            }
        ]
    }
    
    # Sample all data
    sample_all_data = {
        "members_of_parliament": sample_mp_data,
        "house_of_lords": sample_lords_data,
        "committee_memberships": sample_committee_data,
        "government_roles": sample_gov_roles_data,
        "metadata": {
            "data_type": "Complete UK Government Data",
            "filter_current": False,
            "from_date": None,
            "to_date": None,
            "on_date": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache_used": False
        },
        "summary": {
            "total_mps": 1,
            "total_lords": 1,
            "total_committee_members": 1,
            "total_government_roles": 1,
            "total_count": 4
        }
    }
    
    # Configure mock returns
    mock.scrape_mps.return_value = sample_mp_data
    mock.scrape_lords.return_value = sample_lords_data
    mock.scrape_committee_memberships.return_value = sample_committee_data
    mock.scrape_government_roles.return_value = sample_gov_roles_data
    mock.scrape_all_data.return_value = sample_all_data
    mock.export_to_csv.return_value = ["test.csv", "test2.csv"]
    mock.cache = {}
    
    return mock


@pytest.mark.integration
@pytest.mark.api
class TestHealthEndpoints:
    """Test health check and info endpoints."""
    
    def test_index_endpoint(self, client: FlaskClient) -> None:
        """Test the index endpoint returns correct service information."""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['service'] == "UK Government Members Scraper"
        assert data['status'] == "active"
        assert data['version'] == "1.0.0"
        assert 'endpoints' in data
        assert 'query_parameters' in data
        
        # Check that all expected endpoints are documented
        expected_endpoints = [
            "/scrape/all", "/scrape/mps", "/scrape/lords",
            "/scrape/committees", "/scrape/government-roles",
            "/health", "/export/csv"
        ]
        for endpoint in expected_endpoints:
            assert endpoint in data['endpoints']
    
    def test_health_endpoint(self, client: FlaskClient) -> None:
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == "healthy"
        assert 'timestamp' in data
        assert 'cache_status' in data
        
        # Validate timestamp format
        timestamp = data['timestamp']
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


class TestScrapingEndpoints:
    """Test all data scraping endpoints."""
    
    @patch('app.scraper')
    def test_scrape_mps_basic(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test basic MPs scraping without parameters."""
        mock_scraper_instance.scrape_mps.return_value = mock_scraper.scrape_mps.return_value
        
        response = client.get('/scrape/mps')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'metadata' in data
        assert 'members_of_parliament' in data
        assert 'summary' in data
        
        # Check metadata
        metadata = data['metadata']
        assert metadata['data_type'] == "Members of Parliament - House of Commons"
        assert metadata['filter_current'] is False
        assert metadata['from_date'] is None
        assert metadata['to_date'] is None
        assert metadata['on_date'] is None
        
        # Check data structure
        assert isinstance(data['members_of_parliament'], list)
        assert data['summary']['total_count'] == 1
        
        # Verify scraper was called correctly
        mock_scraper_instance.scrape_mps.assert_called_once_with(
            current=False, from_date=None, to_date=None, on_date=None
        )
    
    @patch('app.scraper')
    def test_scrape_mps_with_filters(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test MPs scraping with all filter parameters."""
        mock_scraper_instance.scrape_mps.return_value = mock_scraper.scrape_mps.return_value
        
        response = client.get('/scrape/mps?current=true&from_date=2024-01-01&to_date=2024-12-31&on_date=2024-06-01')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        metadata = data['metadata']
        assert metadata['filter_current'] is True
        assert metadata['from_date'] == "2024-01-01"
        assert metadata['to_date'] == "2024-12-31"
        assert metadata['on_date'] == "2024-06-01"
        
        # Verify scraper was called with correct parameters
        mock_scraper_instance.scrape_mps.assert_called_once_with(
            current=True, from_date="2024-01-01", to_date="2024-12-31", on_date="2024-06-01"
        )
    
    @patch('app.scraper')
    def test_scrape_lords_basic(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test basic Lords scraping without parameters."""
        mock_scraper_instance.scrape_lords.return_value = mock_scraper.scrape_lords.return_value
        
        response = client.get('/scrape/lords')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'metadata' in data
        assert 'house_of_lords' in data
        assert 'summary' in data
        
        metadata = data['metadata']
        assert metadata['data_type'] == "Members of House of Lords"
        assert metadata['filter_current'] is False
        
        mock_scraper_instance.scrape_lords.assert_called_once_with(
            current=False, from_date=None, to_date=None, on_date=None
        )
    
    @patch('app.scraper')
    def test_scrape_lords_with_filters(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test Lords scraping with filter parameters."""
        mock_scraper_instance.scrape_lords.return_value = mock_scraper.scrape_lords.return_value
        
        response = client.get('/scrape/lords?current=true&on_date=2024-06-01')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        metadata = data['metadata']
        assert metadata['filter_current'] is True
        assert metadata['on_date'] == "2024-06-01"
        
        mock_scraper_instance.scrape_lords.assert_called_once_with(
            current=True, from_date=None, to_date=None, on_date="2024-06-01"
        )
    
    @patch('app.scraper')
    def test_scrape_committees(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test committee memberships scraping."""
        mock_scraper_instance.scrape_committee_memberships.return_value = mock_scraper.scrape_committee_memberships.return_value
        
        response = client.get('/scrape/committees?current=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'metadata' in data
        assert 'committee_memberships' in data
        assert 'summary' in data
        
        metadata = data['metadata']
        assert metadata['data_type'] == "Committee Memberships"
        assert metadata['filter_current'] is True
        
        mock_scraper_instance.scrape_committee_memberships.assert_called_once_with(current=True)
    
    @patch('app.scraper')
    def test_scrape_government_roles(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test government roles scraping."""
        mock_scraper_instance.scrape_government_roles.return_value = mock_scraper.scrape_government_roles.return_value
        
        response = client.get('/scrape/government-roles?current=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'metadata' in data
        assert 'government_roles' in data
        assert 'summary' in data
        
        metadata = data['metadata']
        assert metadata['data_type'] == "Government Roles"
        assert metadata['filter_current'] is True
        
        mock_scraper_instance.scrape_government_roles.assert_called_once_with(current=True)
    
    @patch('app.scraper')
    def test_scrape_all_basic(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test scraping all data without cache."""
        mock_scraper_instance.scrape_all_data.return_value = mock_scraper.scrape_all_data.return_value
        
        response = client.get('/scrape/all')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'metadata' in data
        assert 'members_of_parliament' in data
        assert 'house_of_lords' in data
        assert 'government_roles' in data
        assert 'committee_memberships' in data
        assert 'summary' in data
        
        mock_scraper_instance.scrape_all_data.assert_called_once_with(current=False)
    
    @patch('app.scraper')
    def test_scrape_all_with_cache(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test scraping all data with cache enabled."""
        # Set up cached data
        cached_data = mock_scraper.scrape_all_data.return_value
        mock_scraper_instance.cache = {"all": cached_data}
        
        response = client.get('/scrape/all?cache=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data == cached_data
        
        # Should not call scrape_all_data when using cache
        mock_scraper_instance.scrape_all_data.assert_not_called()


class TestCSVExportEndpoints:
    """Test CSV export functionality."""
    
    @patch('app.scraper')
    def test_export_csv_all_data(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test exporting all data to CSV."""
        mock_scraper_instance.export_to_csv.return_value = mock_scraper.export_to_csv.return_value
        
        response = client.post('/export/csv?type=all')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data_type'] == "all"
        assert 'exported_files' in data
        assert data['file_count'] == 2
        
        mock_scraper_instance.export_to_csv.assert_called_once_with(
            "all", False, None, None, None
        )
    
    @patch('app.scraper')
    def test_export_csv_mps_with_filters(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test exporting MPs data with date filters."""
        mock_scraper_instance.export_to_csv.return_value = mock_scraper.export_to_csv.return_value
        
        response = client.post('/export/csv?type=mps&current=true&from_date=2024-01-01&to_date=2024-12-31')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data_type'] == "mps"
        
        mock_scraper_instance.export_to_csv.assert_called_once_with(
            "mps", True, "2024-01-01", "2024-12-31", None
        )
    
    @patch('app.scraper')
    def test_export_csv_invalid_type(self, mock_scraper_instance: MagicMock, client: FlaskClient) -> None:
        """Test CSV export with invalid data type."""
        response = client.post('/export/csv?type=invalid')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid data type' in data['error']
    
    @patch('app.scraper')
    def test_export_csv_get_method(self, mock_scraper_instance: MagicMock, client: FlaskClient, mock_scraper: MagicMock) -> None:
        """Test CSV export using GET method."""
        mock_scraper_instance.export_to_csv.return_value = mock_scraper.export_to_csv.return_value
        
        response = client.get('/export/csv?type=lords')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data_type'] == "lords"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_404_handler(self, client: FlaskClient) -> None:
        """Test 404 error handler."""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == "Endpoint not found"
    
    @patch('app.scraper')
    def test_scrape_mps_exception(self, mock_scraper_instance: MagicMock, client: FlaskClient) -> None:
        """Test error handling when scraping MPs fails."""
        mock_scraper_instance.scrape_mps.side_effect = Exception("Scraping failed")
        
        response = client.get('/scrape/mps')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == "Failed to scrape MPs data"
    
    @patch('app.scraper')
    def test_export_csv_exception(self, mock_scraper_instance: MagicMock, client: FlaskClient) -> None:
        """Test error handling when CSV export fails."""
        mock_scraper_instance.export_to_csv.side_effect = Exception("Export failed")
        
        response = client.post('/export/csv')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == "Failed to export CSV files"


class TestUKGovernmentScraperUnit:
    """Unit tests for UKGovernmentScraper class."""
    
    def setup_method(self) -> None:
        """Set up test instance."""
        self.scraper = UKGovernmentScraper()
    
    def test_scraper_initialization(self) -> None:
        """Test scraper initialization."""
        assert isinstance(self.scraper.cache, dict)
        assert len(self.scraper.cache) == 0
        assert self.scraper.last_updated is None
    
    def test_convert_to_dict_with_dataframe(self) -> None:
        """Test _convert_to_dict with pandas DataFrame."""
        # Create a mock DataFrame
        df = pd.DataFrame({'name': ['John', 'Jane'], 'age': [30, 25]})
        result = self.scraper._convert_to_dict(df)  # type: ignore[misc]
        
        expected = [{'name': 'John', 'age': 30}, {'name': 'Jane', 'age': 25}]
        assert result == expected
    
    def test_convert_to_dict_with_other_data(self) -> None:
        """Test _convert_to_dict with non-DataFrame data."""
        data = [{'name': 'John'}, {'name': 'Jane'}]
        result = self.scraper._convert_to_dict(data)  # type: ignore[misc]
        assert result == data
    
    def test_filter_current_members(self) -> None:
        """Test _filter_current_members functionality."""
        data = [
            {'name': 'Current Member', 'end_date': None},
            {'name': 'Former Member', 'end_date': '2023-12-31'},
            {'name': 'Another Current', 'end_date': ''},
            {'name': 'Also Current', 'end_date': pd.NaT},
        ]
        
        filtered = self.scraper._filter_current_members(data, 'end_date')  # type: ignore[misc]
        assert len(filtered) == 3
        
        names = [member['name'] for member in filtered]
        assert 'Current Member' in names
        assert 'Another Current' in names
        assert 'Also Current' in names
        assert 'Former Member' not in names
    
    @patch('app.pdpy')
    def test_scrape_mps_success(self, mock_pdpy: MagicMock) -> None:
        """Test successful MPs scraping."""
        # Mock pdpy response
        mock_df = pd.DataFrame({'name': ['MP1'], 'constituency': ['Test Constituency']})
        mock_pdpy.fetch_mps.return_value = mock_df
        
        result = self.scraper.scrape_mps(current=False)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == 'MP1'
        
        mock_pdpy.fetch_mps.assert_called_once_with()
    
    @patch('app.pdpy')
    def test_scrape_mps_with_date_filters(self, mock_pdpy: MagicMock) -> None:
        """Test MPs scraping with date filters."""
        mock_df = pd.DataFrame({'name': ['MP1']})
        mock_pdpy.fetch_mps.return_value = mock_df
        
        self.scraper.scrape_mps(
            current=True,
            from_date="2024-01-01",
            to_date="2024-12-31",
            on_date="2024-06-01"
        )
        
        # Should call with on_date since current=True and on_date is specified
        mock_pdpy.fetch_mps.assert_called_once_with(
            from_date="2024-01-01",
            to_date="2024-12-31",
            on_date="2024-06-01"
        )
    
    @patch('app.pdpy')
    def test_scrape_mps_current_without_on_date(self, mock_pdpy: MagicMock) -> None:
        """Test MPs scraping with current=True but no on_date."""
        mock_df = pd.DataFrame({'name': ['MP1']})
        mock_pdpy.fetch_mps.return_value = mock_df
        
        with patch('app.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-06-03"
            mock_datetime.now.return_value = datetime(2024, 6, 3, tzinfo=timezone.utc)
            
            self.scraper.scrape_mps(current=True)
            
            # Should add today's date as on_date
            mock_pdpy.fetch_mps.assert_called_once_with(on_date="2024-06-03")
    
    def test_create_outputs_dir(self) -> None:
        """Test outputs directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the file path
            with patch('app.Path') as mock_path:
                mock_path.__file__ = temp_dir
                mock_path.return_value.parent = Path(temp_dir)
                
                outputs_dir = self.scraper._create_outputs_dir()  # type: ignore[misc]
                
                assert outputs_dir.name == "outputs"
    
    def test_export_dataframe_to_csv(self) -> None:
        """Test CSV export functionality."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            
            # Test data
            data = [{'name': 'John', 'age': 30}, {'name': 'Jane', 'age': 25}]
            
            self.scraper._export_dataframe_to_csv(data, temp_path)  # type: ignore[misc]
            
            # Verify file was created and contains data
            assert temp_path.exists()
            df = pd.read_csv(temp_path)  # type: ignore[misc]
            assert len(df) == 2
            assert 'name' in df.columns
            assert 'age' in df.columns
            
            # Cleanup
            temp_path.unlink()


class TestParameterValidation:
    """Test query parameter validation and edge cases."""
    
    def test_boolean_parameter_parsing(self, client: FlaskClient) -> None:
        """Test various boolean parameter formats."""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('invalid', False),  # Default to False for invalid values
            ('', False),  # Empty string defaults to False
        ]
        
        with patch('app.scraper') as mock_scraper:
            mock_scraper.scrape_mps.return_value = []
            
            for param_value, expected in test_cases:
                response = client.get(f'/scrape/mps?current={param_value}')
                assert response.status_code == 200
                
                # Check that the scraper was called with the expected boolean value
                calls = mock_scraper.scrape_mps.call_args_list
                if calls:
                    last_call = calls[-1]
                    assert last_call[1]['current'] == expected
    
    def test_date_parameter_formats(self, client: FlaskClient) -> None:
        """Test date parameter handling."""
        with patch('app.scraper') as mock_scraper:
            mock_scraper.scrape_mps.return_value = []
            
            # Test valid date format
            response = client.get('/scrape/mps?from_date=2024-01-01')
            assert response.status_code == 200
            
            # Test multiple date parameters
            response = client.get('/scrape/mps?from_date=2024-01-01&to_date=2024-12-31&on_date=2024-06-01')
            assert response.status_code == 200
            
            last_call = mock_scraper.scrape_mps.call_args_list[-1]
            assert last_call[1]['from_date'] == '2024-01-01'
            assert last_call[1]['to_date'] == '2024-12-31'
            assert last_call[1]['on_date'] == '2024-06-01'


class TestCacheHandling:
    """Test caching functionality."""
    
    @patch('app.scraper')
    def test_cache_population(self, mock_scraper_instance: MagicMock, client: FlaskClient) -> None:
        """Test that cache is populated correctly."""
        sample_data = {"test": "data"}
        mock_scraper_instance.scrape_all_data.return_value = sample_data
        
        # First request should populate cache
        response = client.get('/scrape/all')
        assert response.status_code == 200
        
        # Verify cache was used in subsequent request
        mock_scraper_instance.cache = {"all": sample_data}
        response = client.get('/scrape/all?cache=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data == sample_data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
