"""
Unit tests for the UKGovernmentScraper class methods.
Tests the core scraping functionality, filtering, and data processing.
"""

import pytest
import tempfile
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from typing import Any, Dict, List

from app import UKGovernmentScraper


class TestScraperInitialization:
    """Test scraper initialization and basic properties."""
    
    def test_initialization(self):
        """Test scraper initializes with empty cache and no last_updated."""
        scraper = UKGovernmentScraper()
        assert scraper.cache == {}
        assert scraper.last_updated is None


class TestDataConversion:
    """Test data conversion and processing methods."""
    
    def test_convert_to_dict_with_dataframe(self):
        """Test converting pandas DataFrame to dict records."""
        scraper = UKGovernmentScraper()
        
        # Create test DataFrame
        df = pd.DataFrame({
            'name': ['John', 'Jane'],
            'age': [30, 25],
            'city': ['London', 'Manchester']
        })
        
        result = scraper._convert_to_dict(df)
        expected = [
            {'name': 'John', 'age': 30, 'city': 'London'},
            {'name': 'Jane', 'age': 25, 'city': 'Manchester'}
        ]
        assert result == expected
    
    def test_convert_to_dict_with_list(self):
        """Test that lists are returned unchanged."""
        scraper = UKGovernmentScraper()
        data = [{'name': 'John'}, {'name': 'Jane'}]
        result = scraper._convert_to_dict(data)
        assert result == data
    
    def test_convert_to_dict_with_other_types(self):
        """Test that other data types are returned unchanged."""
        scraper = UKGovernmentScraper()
        
        # Test with string
        result = scraper._convert_to_dict("test string")
        assert result == "test string"
        
        # Test with dict
        data = {'key': 'value'}
        result = scraper._convert_to_dict(data)
        assert result == data


class TestCurrentMemberFiltering:
    """Test filtering logic for current members."""
    
    def test_filter_current_members_with_none_end_dates(self):
        """Test filtering keeps members with None end dates."""
        scraper = UKGovernmentScraper()
        data = [
            {'name': 'Current Member', 'end_date': None},
            {'name': 'Former Member', 'end_date': '2023-12-31'},
        ]
        
        result = scraper._filter_current_members(data, 'end_date')
        assert len(result) == 1
        assert result[0]['name'] == 'Current Member'
    
    def test_filter_current_members_with_empty_string_end_dates(self):
        """Test filtering keeps members with empty string end dates."""
        scraper = UKGovernmentScraper()
        data = [
            {'name': 'Current Member', 'end_date': ''},
            {'name': 'Former Member', 'end_date': '2023-12-31'},
        ]
        
        result = scraper._filter_current_members(data, 'end_date')
        assert len(result) == 1
        assert result[0]['name'] == 'Current Member'
    
    def test_filter_current_members_with_nan_end_dates(self):
        """Test filtering keeps members with NaN end dates."""
        scraper = UKGovernmentScraper()
        data = [
            {'name': 'Current Member', 'end_date': pd.NaT},
            {'name': 'Former Member', 'end_date': '2023-12-31'},
        ]
        
        result = scraper._filter_current_members(data, 'end_date')
        assert len(result) == 1
        assert result[0]['name'] == 'Current Member'
    
    def test_filter_current_members_with_missing_field(self):
        """Test filtering handles missing end date fields."""
        scraper = UKGovernmentScraper()
        data = [
            {'name': 'Member Without Field'},
            {'name': 'Former Member', 'end_date': '2023-12-31'},
        ]
        
        result = scraper._filter_current_members(data, 'end_date')
        assert len(result) == 1
        assert result[0]['name'] == 'Member Without Field'


class TestMPsScrapingMethods:
    """Test MPs scraping functionality."""
    
    @patch('app.pdpy')
    def test_scrape_mps_basic(self, mock_pdpy):
        """Test basic MPs scraping without filters."""
        scraper = UKGovernmentScraper()
        
        # Mock pdpy response
        mock_df = pd.DataFrame([
            {'name': 'John Smith', 'constituency': 'Test Constituency'},
            {'name': 'Jane Doe', 'constituency': 'Another Constituency'}
        ])
        mock_pdpy.fetch_mps.return_value = mock_df
        
        result = scraper.scrape_mps()
        
        assert len(result) == 2
        assert result[0]['name'] == 'John Smith'
        assert result[1]['name'] == 'Jane Doe'
        mock_pdpy.fetch_mps.assert_called_once_with()
    
    @patch('app.pdpy')
    def test_scrape_mps_with_date_filters(self, mock_pdpy):
        """Test MPs scraping with date filtering parameters."""
        scraper = UKGovernmentScraper()
        mock_pdpy.fetch_mps.return_value = pd.DataFrame([])
        
        # Test all date parameters
        scraper.scrape_mps(
            from_date="2024-01-01",
            to_date="2024-12-31", 
            on_date="2024-06-01"
        )
        
        mock_pdpy.fetch_mps.assert_called_with(
            from_date="2024-01-01",
            to_date="2024-12-31",
            on_date="2024-06-01"
        )
    
    @patch('app.pdpy')
    @patch('app.datetime')
    def test_scrape_mps_current_without_on_date(self, mock_datetime, mock_pdpy):
        """Test MPs scraping with current=True adds today's date."""
        scraper = UKGovernmentScraper()
        mock_pdpy.fetch_mps.return_value = pd.DataFrame([])
        
        # Mock today's date
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-06-03"
        mock_datetime.now.return_value = mock_now
        
        scraper.scrape_mps(current=True)
        
        mock_pdpy.fetch_mps.assert_called_with(on_date="2024-06-03")
    
    @patch('app.pdpy')
    def test_scrape_mps_current_with_on_date(self, mock_pdpy):
        """Test MPs scraping with current=True and specified on_date."""
        scraper = UKGovernmentScraper()
        mock_pdpy.fetch_mps.return_value = pd.DataFrame([])
        
        scraper.scrape_mps(current=True, on_date="2024-05-01")
        
        # Should use the specified on_date, not today's date
        mock_pdpy.fetch_mps.assert_called_with(on_date="2024-05-01")
    
    @patch('app.pdpy')
    def test_scrape_mps_caching(self, mock_pdpy):
        """Test that MPs data is cached correctly."""
        scraper = UKGovernmentScraper()
        mock_pdpy.fetch_mps.return_value = pd.DataFrame([{'name': 'Test MP'}])
        
        scraper.scrape_mps(current=True, from_date="2024-01-01")
        
        # Check cache was populated
        cache_key = "mps_current_True_from_2024-01-01_to_None_on_None"
        assert cache_key in scraper.cache
        assert 'data' in scraper.cache[cache_key]
        assert 'timestamp' in scraper.cache[cache_key]
    
    @patch('app.pdpy')
    def test_scrape_mps_exception_handling(self, mock_pdpy):
        """Test MPs scraping handles exceptions properly."""
        scraper = UKGovernmentScraper()
        mock_pdpy.fetch_mps.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            scraper.scrape_mps()


class TestLordsScrapingMethods:
    """Test Lords scraping functionality."""
    
    @patch('app.pdpy')
    def test_scrape_lords_basic(self, mock_pdpy):
        """Test basic Lords scraping."""
        scraper = UKGovernmentScraper()
        mock_df = pd.DataFrame([{'name': 'Lord Test', 'party': 'Test Party'}])
        mock_pdpy.fetch_lords.return_value = mock_df
        
        result = scraper.scrape_lords()
        
        assert len(result) == 1
        assert result[0]['name'] == 'Lord Test'
        mock_pdpy.fetch_lords.assert_called_once_with()
    
    @patch('app.pdpy')
    @patch('app.datetime')
    def test_scrape_lords_current_filter(self, mock_datetime, mock_pdpy):
        """Test Lords scraping with current filter."""
        scraper = UKGovernmentScraper()
        mock_pdpy.fetch_lords.return_value = pd.DataFrame([])
        
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-06-03"
        mock_datetime.now.return_value = mock_now
        
        scraper.scrape_lords(current=True)
        
        mock_pdpy.fetch_lords.assert_called_with(on_date="2024-06-03")


class TestGovernmentRolesMethods:
    """Test government roles scraping functionality."""
    
    @patch('app.pdpy')
    def test_scrape_government_roles_basic(self, mock_pdpy):
        """Test basic government roles scraping."""
        scraper = UKGovernmentScraper()
        
        # Mock DataFrames
        mps_df = pd.DataFrame([{'name': 'Minister MP', 'role': 'Secretary'}])
        lords_df = pd.DataFrame([{'name': 'Minister Lord', 'role': 'Minister'}])
        
        mock_pdpy.fetch_mps_government_roles.return_value = mps_df
        mock_pdpy.fetch_lords_government_roles.return_value = lords_df
        
        result = scraper.scrape_government_roles()
        
        assert 'mps_government_roles' in result
        assert 'lords_government_roles' in result
        assert len(result['mps_government_roles']) == 1
        assert len(result['lords_government_roles']) == 1
    
    @patch('app.pdpy')
    def test_scrape_government_roles_with_current_filter(self, mock_pdpy):
        """Test government roles scraping with current filter."""
        scraper = UKGovernmentScraper()
        
        # Mock data with both current and former roles
        mps_data = [
            {'name': 'Current Minister', 'government_incumbency_end_date': None},
            {'name': 'Former Minister', 'government_incumbency_end_date': '2023-12-31'}
        ]
        lords_data = [
            {'name': 'Current Lord Minister', 'government_incumbency_end_date': ''},
            {'name': 'Former Lord Minister', 'government_incumbency_end_date': '2023-06-30'}
        ]
        
        mock_pdpy.fetch_mps_government_roles.return_value = pd.DataFrame(mps_data)
        mock_pdpy.fetch_lords_government_roles.return_value = pd.DataFrame(lords_data)
        
        result = scraper.scrape_government_roles(current=True)
        
        # Should only return current roles
        assert len(result['mps_government_roles']) == 1
        assert len(result['lords_government_roles']) == 1
        assert result['mps_government_roles'][0]['name'] == 'Current Minister'
        assert result['lords_government_roles'][0]['name'] == 'Current Lord Minister'


class TestCommitteeMembershipMethods:
    """Test committee membership scraping functionality."""
    
    @patch('app.pdpy')
    def test_scrape_committee_memberships_basic(self, mock_pdpy):
        """Test basic committee memberships scraping."""
        scraper = UKGovernmentScraper()
        
        mps_df = pd.DataFrame([{'name': 'MP Member', 'committee': 'Test Committee'}])
        lords_df = pd.DataFrame([{'name': 'Lord Member', 'committee': 'Lords Committee'}])
        
        mock_pdpy.fetch_mps_committee_memberships.return_value = mps_df
        mock_pdpy.fetch_lords_committee_memberships.return_value = lords_df
        
        result = scraper.scrape_committee_memberships()
        
        assert 'mps_committee_memberships' in result
        assert 'lords_committee_memberships' in result
        assert len(result['mps_committee_memberships']) == 1
        assert len(result['lords_committee_memberships']) == 1
    
    @patch('app.pdpy')
    def test_scrape_committee_memberships_with_current_filter(self, mock_pdpy):
        """Test committee memberships with current filter."""
        scraper = UKGovernmentScraper()
        
        # Mock data with current and former memberships
        mps_data = [
            {'name': 'Current Member', 'committee_membership_end_date': None},
            {'name': 'Former Member', 'committee_membership_end_date': '2023-12-31'}
        ]
        
        mock_pdpy.fetch_mps_committee_memberships.return_value = pd.DataFrame(mps_data)
        mock_pdpy.fetch_lords_committee_memberships.return_value = pd.DataFrame([])
        
        result = scraper.scrape_committee_memberships(current=True)
        
        assert len(result['mps_committee_memberships']) == 1
        assert result['mps_committee_memberships'][0]['name'] == 'Current Member'


class TestScrapeAllDataMethod:
    """Test the comprehensive scrape_all_data method."""
    
    @patch.object(UKGovernmentScraper, 'scrape_committee_memberships')
    @patch.object(UKGovernmentScraper, 'scrape_government_roles')
    @patch.object(UKGovernmentScraper, 'scrape_lords')
    @patch.object(UKGovernmentScraper, 'scrape_mps')
    def test_scrape_all_data_basic(self, mock_mps, mock_lords, mock_gov, mock_comm):
        """Test scrape_all_data coordinates all scraping methods."""
        scraper = UKGovernmentScraper()
        
        # Mock return values
        mock_mps.return_value = [{'name': 'Test MP'}]
        mock_lords.return_value = [{'name': 'Test Lord'}]
        mock_gov.return_value = {
            'mps_government_roles': [{'name': 'Minister'}],
            'lords_government_roles': []
        }
        mock_comm.return_value = {
            'mps_committee_memberships': [{'name': 'Committee Member'}],
            'lords_committee_memberships': []
        }
        
        result = scraper.scrape_all_data()
        
        # Verify all methods were called
        mock_mps.assert_called_once_with(current=False)
        mock_lords.assert_called_once_with(current=False)
        mock_gov.assert_called_once_with(current=False)
        mock_comm.assert_called_once_with(current=False)
        
        # Verify response structure
        assert 'metadata' in result
        assert 'members_of_parliament' in result
        assert 'house_of_lords' in result
        assert 'government_roles' in result
        assert 'committee_memberships' in result
        assert 'summary' in result
        
        # Verify summary statistics
        summary = result['summary']
        assert summary['total_mps'] == 1
        assert summary['total_lords'] == 1
        assert summary['total_mps_gov_roles'] == 1
        assert summary['total_lords_gov_roles'] == 0
        assert summary['total_mps_committee_memberships'] == 1
        assert summary['total_lords_committee_memberships'] == 0
    
    @patch.object(UKGovernmentScraper, 'scrape_committee_memberships')
    @patch.object(UKGovernmentScraper, 'scrape_government_roles')
    @patch.object(UKGovernmentScraper, 'scrape_lords')
    @patch.object(UKGovernmentScraper, 'scrape_mps')
    def test_scrape_all_data_with_current_filter(self, mock_mps, mock_lords, mock_gov, mock_comm):
        """Test scrape_all_data passes current filter to all methods."""
        scraper = UKGovernmentScraper()
        
        # Mock return values
        mock_mps.return_value = []
        mock_lords.return_value = []
        mock_gov.return_value = {'mps_government_roles': [], 'lords_government_roles': []}
        mock_comm.return_value = {'mps_committee_memberships': [], 'lords_committee_memberships': []}
        
        scraper.scrape_all_data(current=True)
        
        # Verify current=True was passed to all methods
        mock_mps.assert_called_once_with(current=True)
        mock_lords.assert_called_once_with(current=True)
        mock_gov.assert_called_once_with(current=True)
        mock_comm.assert_called_once_with(current=True)
    
    def test_scrape_all_data_safe_len_with_none_values(self):
        """Test safe_len handles None and invalid values."""
        scraper = UKGovernmentScraper()
        
        # Mock methods to return None or invalid data
        with patch.object(scraper, 'scrape_mps', return_value=None), \
             patch.object(scraper, 'scrape_lords', return_value="invalid"), \
             patch.object(scraper, 'scrape_government_roles', return_value={}), \
             patch.object(scraper, 'scrape_committee_memberships', return_value={}):
            
            result = scraper.scrape_all_data()
            
            # Should handle None/invalid gracefully
            summary = result['summary']
            assert summary['total_mps'] == 0  # safe_len(None) = 0
            assert summary['total_lords'] == 0  # safe_len("invalid") = 0


class TestCSVExportMethods:
    """Test CSV export functionality."""
    
    def test_create_outputs_dir(self):
        """Test outputs directory creation."""
        scraper = UKGovernmentScraper()
        
        with patch('app.Path') as mock_path:
            mock_file_path = MagicMock()
            mock_parent = MagicMock()
            mock_outputs_dir = MagicMock()
            
            mock_file_path.parent = mock_parent
            mock_parent.__truediv__.return_value = mock_outputs_dir
            mock_path.__file__ = "/fake/path/app.py"
            mock_path.return_value = mock_file_path
            
            result = scraper._create_outputs_dir()
            
            mock_outputs_dir.mkdir.assert_called_once_with(exist_ok=True)
            assert result == mock_outputs_dir
    
    def test_export_dataframe_to_csv(self):
        """Test CSV export with real data."""
        scraper = UKGovernmentScraper()
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            
            test_data = [
                {'name': 'John', 'age': 30, 'city': 'London'},
                {'name': 'Jane', 'age': 25, 'city': 'Manchester'}
            ]
            
            scraper._export_dataframe_to_csv(test_data, temp_path)
            
            # Verify file was created and contains correct data
            assert temp_path.exists()
            
            # Read back and verify
            df = pd.read_csv(temp_path)
            assert len(df) == 2
            assert list(df.columns) == ['name', 'age', 'city']
            assert df.iloc[0]['name'] == 'John'
            assert df.iloc[1]['name'] == 'Jane'
            
            # Cleanup
            temp_path.unlink()
    
    @patch.object(UKGovernmentScraper, '_create_outputs_dir')
    @patch.object(UKGovernmentScraper, 'scrape_all_data')
    @patch.object(UKGovernmentScraper, '_export_dataframe_to_csv')
    def test_export_all_data_to_csv(self, mock_export_df, mock_scrape_all, mock_create_dir):
        """Test exporting all data types to CSV."""
        scraper = UKGovernmentScraper()
        
        # Mock directory
        mock_outputs_dir = MagicMock()
        mock_create_dir.return_value = mock_outputs_dir
        
        # Mock comprehensive data
        mock_all_data = {
            'members_of_parliament': [{'name': 'MP1'}],
            'house_of_lords': [{'name': 'Lord1'}],
            'government_roles': {
                'mps_government_roles': [{'name': 'Minister1'}],
                'lords_government_roles': [{'name': 'LordMinister1'}]
            },
            'committee_memberships': {
                'mps_committee_memberships': [{'name': 'CommitteeMember1'}],
                'lords_committee_memberships': [{'name': 'LordCommitteeMember1'}]
            }
        }
        mock_scrape_all.return_value = mock_all_data
        
        result = scraper._export_all_data_to_csv(mock_outputs_dir, "20240603_120000")
        
        # Should have called export 6 times (MPs, Lords, 2 gov roles, 2 committees)
        assert mock_export_df.call_count == 6
        assert len(result) == 6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])