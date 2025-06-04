"""
Tests for error handling scenarios and edge cases.
"""

import pytest
from unittest.mock import patch
from app import UKGovernmentScraper


class TestErrorScenarios:
    """Test various error conditions and edge cases."""
    
    @patch('app.pdpy')
    def test_scrape_methods_handle_pdpy_exceptions(self, mock_pdpy):
        """Test all scrape methods handle pdpy exceptions properly."""
        scraper = UKGovernmentScraper()
        
        # Test each scraping method
        methods_and_mocks = [
            ('scrape_mps', 'fetch_mps'),
            ('scrape_lords', 'fetch_lords'),
        ]
        
        for method_name, mock_attr in methods_and_mocks:
            # Make the pdpy method raise an exception
            getattr(mock_pdpy, mock_attr).side_effect = Exception("API Error")
            
            method = getattr(scraper, method_name)
            with pytest.raises(Exception):
                method()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])