import unittest
from unittest.mock import patch, MagicMock
from app import app

class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_endpoint(self):
        """Test the index/health endpoint returns service information."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('service', data)
        self.assertIn('status', data)
        self.assertEqual(data['service'], 'UK Government Members Scraper')

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')

    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_endpoint(self, mock_scrape_mps):
        """Test the MPs scraping endpoint."""
        mock_scrape_mps.return_value = [{'name': 'Test MP', 'party': 'Test Party'}]
        
        response = self.app.get('/scrape/mps')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('members_of_parliament', data)
        self.assertIn('metadata', data)
        self.assertIn('summary', data)

    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_with_current_filter(self, mock_scrape_mps):
        """Test MPs endpoint with current filter."""
        mock_scrape_mps.return_value = [{'name': 'Current MP'}]
        
        response = self.app.get('/scrape/mps?current=true')
        self.assertEqual(response.status_code, 200)
        mock_scrape_mps.assert_called_with(current=True, from_date=None, to_date=None, on_date=None)

    @patch('app.scraper.scrape_lords')
    def test_scrape_lords_endpoint(self, mock_scrape_lords):
        """Test the Lords scraping endpoint."""
        mock_scrape_lords.return_value = [{'name': 'Test Lord', 'title': 'Lord Test'}]
        
        response = self.app.get('/scrape/lords')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('house_of_lords', data)
        self.assertIn('metadata', data)

    @patch('app.scraper.scrape_all_data')
    def test_scrape_all_endpoint(self, mock_scrape_all):
        """Test the comprehensive scraping endpoint."""
        mock_scrape_all.return_value = {
            'members_of_parliament': [],
            'house_of_lords': [],
            'government_roles': {},
            'committee_memberships': {},
            'summary': {'total_mps': 0, 'total_lords': 0}
        }
        
        response = self.app.get('/scrape/all')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('members_of_parliament', data)
        self.assertIn('house_of_lords', data)

    @patch('app.scraper.export_to_csv')
    def test_export_csv_endpoint(self, mock_export):
        """Test the CSV export endpoint."""
        mock_export.return_value = ['test_file.csv']
        
        response = self.app.get('/export/csv')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])

    def test_export_csv_invalid_type(self):
        """Test CSV export with invalid data type."""
        response = self.app.get('/export/csv?type=invalid')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_404_handler(self):
        """Test 404 error handling for non-existent endpoints."""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Endpoint not found')

    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_error_handling(self, mock_scrape_mps):
        """Test error handling in MPs endpoint."""
        mock_scrape_mps.side_effect = Exception("Test error")
        
        response = self.app.get('/scrape/mps')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()