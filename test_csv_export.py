"""
Focused tests for CSV export functionality.
Tests the complex export logic and file handling.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app import UKGovernmentScraper


class TestCSVExportIntegration:
    """Integration tests for complete CSV export workflows."""
    
    @patch.object(UKGovernmentScraper, '_create_outputs_dir')
    @patch.object(UKGovernmentScraper, '_export_dataframe_to_csv')
    @patch.object(UKGovernmentScraper, 'scrape_mps')
    def test_export_single_mps_type(self, mock_scrape_mps, mock_export_df, mock_create_dir):
        """Test exporting single MPs data type."""
        scraper = UKGovernmentScraper()
        
        mock_outputs_dir = Path("/fake/outputs")
        mock_create_dir.return_value = mock_outputs_dir
        mock_scrape_mps.return_value = [{'name': 'Test MP'}]
        
        result = scraper._export_single_data_type(
            "mps", mock_outputs_dir, "20240603_120000", 
            current=True, from_date="2024-01-01"
        )
        
        # Verify scrape_mps was called with correct parameters
        mock_scrape_mps.assert_called_once_with(
            current=True, from_date="2024-01-01", to_date=None, on_date=None
        )
        
        # Verify export was called
        assert mock_export_df.call_count == 1
        assert len(result) == 1
    
    @patch.object(UKGovernmentScraper, '_create_outputs_dir')
    @patch.object(UKGovernmentScraper, '_export_dataframe_to_csv')
    @patch.object(UKGovernmentScraper, 'scrape_government_roles')
    def test_export_government_roles_type(self, mock_scrape_gov, mock_export_df, mock_create_dir):
        """Test exporting government roles data type."""
        scraper = UKGovernmentScraper()
        
        mock_outputs_dir = Path("/fake/outputs")
        mock_create_dir.return_value = mock_outputs_dir
        
        # Mock government roles data
        mock_scrape_gov.return_value = {
            'mps_government_roles': [{'name': 'Minister MP'}],
            'lords_government_roles': [{'name': 'Minister Lord'}]
        }
        
        result = scraper._export_single_data_type(
            "government-roles", mock_outputs_dir, "20240603_120000", current=True
        )
        
        mock_scrape_gov.assert_called_once_with(current=True)
        
        # Should export both MPs and Lords government roles
        assert mock_export_df.call_count == 2
        assert len(result) == 2
    
    @patch.object(UKGovernmentScraper, '_create_outputs_dir')
    @patch('app.datetime')
    def test_export_to_csv_main_method(self, mock_datetime, mock_create_dir):
        """Test the main export_to_csv method coordinates everything."""
        scraper = UKGovernmentScraper()
        
        # Mock datetime for timestamp
        mock_now = MagicMock()
        mock_now.strftime.return_value = "20240603_120000"
        mock_datetime.now.return_value = mock_now
        
        mock_outputs_dir = Path("/fake/outputs")
        mock_create_dir.return_value = mock_outputs_dir
        
        # Mock the export methods
        with patch.object(scraper, '_export_all_data_to_csv') as mock_export_all, \
             patch.object(scraper, '_export_single_data_type') as mock_export_single:
            
            mock_export_all.return_value = ["file1.csv", "file2.csv"]
            
            # Test exporting all data
            result = scraper.export_to_csv("all", current=True)
            
            mock_export_all.assert_called_once_with(mock_outputs_dir, "20240603_120000", True)
            assert result == ["file1.csv", "file2.csv"]
            
            # Test exporting single data type
            mock_export_single.return_value = ["single_file.csv"]
            result = scraper.export_to_csv("mps", current=False, from_date="2024-01-01")
            
            mock_export_single.assert_called_once_with(
                "mps", mock_outputs_dir, "20240603_120000", False, "2024-01-01", None, None
            )
            assert result == ["single_file.csv"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])