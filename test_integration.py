"""
Integration tests for complete workflows and real-world scenarios.
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from app import UKGovernmentScraper


class TestRealWorldWorkflows:
    """Test complete workflows that mirror real usage."""
    
    @patch('app.pdpy')
    def test_complete_current_members_workflow(self, mock_pdpy):
        """Test a complete workflow of getting current members only."""
        scraper = UKGovernmentScraper()
        
        # Mock realistic data with mixed current/former members
        mps_data = pd.DataFrame([
            {'name': 'Current MP', 'membership_end_date': None},
            {'name': 'Former MP', 'membership_end_date': '2023-12-31'}
        ])
        
        mock_pdpy.fetch_mps.return_value = mps_data
        mock_pdpy.fetch_lords.return_value = pd.DataFrame([])
        mock_pdpy.fetch_mps_government_roles.return_value = pd.DataFrame([])
        mock_pdpy.fetch_lords_government_roles.return_value = pd.DataFrame([])
        mock_pdpy.fetch_mps_committee_memberships.return_value = pd.DataFrame([])
        mock_pdpy.fetch_lords_committee_memberships.return_value = pd.DataFrame([])
        
        # Get all current data
        result = scraper.scrape_all_data(current=True)
        
        # Verify structure
        assert 'metadata' in result
        assert 'summary' in result
        assert isinstance(result['members_of_parliament'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])