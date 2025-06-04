import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timezone
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
        
        # Test all documented endpoints are listed
        expected_endpoints = [
            '/scrape/all', '/scrape/mps', '/scrape/lords',
            '/scrape/committees', '/scrape/government-roles',
            '/health', '/export/csv'
        ]
        for endpoint in expected_endpoints:
            self.assertIn(endpoint, data['endpoints'])
        
        # Test query parameters documentation
        expected_params = ['current', 'from_date', 'to_date', 'on_date', 'cache', 'type']
        for param in expected_params:
            self.assertIn(param, data['query_parameters'])

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('cache_status', data)

    # === MPs Endpoint Tests ===
    
    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_basic(self, mock_scrape_mps):
        """Test basic MPs scraping without parameters."""
        mock_scrape_mps.return_value = [
            {'name': 'Test MP', 'party': 'Test Party', 'constituency': 'Test Seat'}
        ]
        
        response = self.app.get('/scrape/mps')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('members_of_parliament', data)
        self.assertIn('metadata', data)
        self.assertIn('summary', data)
        
        # Check metadata structure
        metadata = data['metadata']
        self.assertEqual(metadata['data_type'], 'Members of Parliament - House of Commons')
        self.assertFalse(metadata['filter_current'])
        self.assertIsNone(metadata['from_date'])
        self.assertIsNone(metadata['to_date'])
        self.assertIsNone(metadata['on_date'])
        
        mock_scrape_mps.assert_called_once_with(
            current=False, from_date=None, to_date=None, on_date=None
        )

    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_current_filter(self, mock_scrape_mps):
        """Test MPs endpoint with current=true filter."""
        mock_scrape_mps.return_value = [{'name': 'Current MP'}]
        
        response = self.app.get('/scrape/mps?current=true')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['metadata']['filter_current'])
        mock_scrape_mps.assert_called_with(current=True, from_date=None, to_date=None, on_date=None)

    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_date_filters(self, mock_scrape_mps):
        """Test MPs endpoint with date filtering parameters."""
        mock_scrape_mps.return_value = []
        
        # Test from_date parameter
        response = self.app.get('/scrape/mps?from_date=2024-01-01')
        self.assertEqual(response.status_code, 200)
        mock_scrape_mps.assert_called_with(
            current=False, from_date='2024-01-01', to_date=None, on_date=None
        )
        
        # Test to_date parameter
        response = self.app.get('/scrape/mps?to_date=2024-12-31')
        self.assertEqual(response.status_code, 200)
        mock_scrape_mps.assert_called_with(
            current=False, from_date=None, to_date='2024-12-31', on_date=None
        )
        
        # Test on_date parameter
        response = self.app.get('/scrape/mps?on_date=2024-06-01')
        self.assertEqual(response.status_code, 200)
        mock_scrape_mps.assert_called_with(
            current=False, from_date=None, to_date=None, on_date='2024-06-01'
        )

    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_combined_filters(self, mock_scrape_mps):
        """Test MPs endpoint with combined filter parameters."""
        mock_scrape_mps.return_value = []
        
        # Test all parameters combined
        response = self.app.get('/scrape/mps?current=true&from_date=2024-01-01&to_date=2024-12-31&on_date=2024-06-01')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        metadata = data['metadata']
        self.assertTrue(metadata['filter_current'])
        self.assertEqual(metadata['from_date'], '2024-01-01')
        self.assertEqual(metadata['to_date'], '2024-12-31')
        self.assertEqual(metadata['on_date'], '2024-06-01')
        
        mock_scrape_mps.assert_called_with(
            current=True, from_date='2024-01-01', to_date='2024-12-31', on_date='2024-06-01'
        )

    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_boolean_variations(self, mock_scrape_mps):
        """Test various boolean parameter formats for current filter."""
        mock_scrape_mps.return_value = []
        
        # Test different true values
        for true_val in ['true', 'True', 'TRUE']:
            response = self.app.get(f'/scrape/mps?current={true_val}')
            self.assertEqual(response.status_code, 200)
            mock_scrape_mps.assert_called_with(
                current=True, from_date=None, to_date=None, on_date=None
            )
        
        # Test different false values
        for false_val in ['false', 'False', 'FALSE', 'invalid', '']:
            response = self.app.get(f'/scrape/mps?current={false_val}')
            self.assertEqual(response.status_code, 200)
            mock_scrape_mps.assert_called_with(
                current=False, from_date=None, to_date=None, on_date=None
            )

    # === Lords Endpoint Tests ===
    
    @patch('app.scraper.scrape_lords')
    def test_scrape_lords_basic(self, mock_scrape_lords):
        """Test basic Lords scraping."""
        mock_scrape_lords.return_value = [
            {'name': 'Lord Test', 'title': 'The Rt Hon Lord Test'}
        ]
        
        response = self.app.get('/scrape/lords')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('house_of_lords', data)
        self.assertIn('metadata', data)
        self.assertEqual(data['metadata']['data_type'], 'Members of House of Lords')
        mock_scrape_lords.assert_called_with(
            current=False, from_date=None, to_date=None, on_date=None
        )

    @patch('app.scraper.scrape_lords')
    def test_scrape_lords_with_filters(self, mock_scrape_lords):
        """Test Lords endpoint with all filter combinations."""
        mock_scrape_lords.return_value = []
        
        response = self.app.get('/scrape/lords?current=true&from_date=2023-01-01&on_date=2024-06-01')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        metadata = data['metadata']
        self.assertTrue(metadata['filter_current'])
        self.assertEqual(metadata['from_date'], '2023-01-01')
        self.assertEqual(metadata['on_date'], '2024-06-01')
        
        mock_scrape_lords.assert_called_with(
            current=True, from_date='2023-01-01', to_date=None, on_date='2024-06-01'
        )

    # === Government Roles Tests ===
    
    @patch('app.scraper.scrape_government_roles')
    def test_scrape_government_roles_basic(self, mock_scrape_gov):
        """Test government roles scraping."""
        mock_scrape_gov.return_value = {
            'mps_government_roles': [{'name': 'Minister MP'}],
            'lords_government_roles': [{'name': 'Minister Lord'}]
        }
        
        response = self.app.get('/scrape/government-roles')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('government_roles', data)
        self.assertIn('metadata', data)
        self.assertIn('summary', data)
        self.assertEqual(data['metadata']['data_type'], 'Government Roles')
        mock_scrape_gov.assert_called_with(current=False)

    @patch('app.scraper.scrape_government_roles')
    def test_scrape_government_roles_current(self, mock_scrape_gov):
        """Test government roles with current filter."""
        mock_scrape_gov.return_value = {
            'mps_government_roles': [],
            'lords_government_roles': []
        }
        
        response = self.app.get('/scrape/government-roles?current=true')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['metadata']['filter_current'])
        mock_scrape_gov.assert_called_with(current=True)

    # === Committees Tests ===
    
    @patch('app.scraper.scrape_committee_memberships')
    def test_scrape_committees_basic(self, mock_scrape_comm):
        """Test committee memberships scraping."""
        mock_scrape_comm.return_value = {
            'mps_committee_memberships': [{'name': 'Committee MP'}],
            'lords_committee_memberships': [{'name': 'Committee Lord'}]
        }
        
        response = self.app.get('/scrape/committees')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('committee_memberships', data)
        self.assertIn('metadata', data)
        self.assertIn('summary', data)
        self.assertEqual(data['metadata']['data_type'], 'Committee Memberships')
        mock_scrape_comm.assert_called_with(current=False)

    @patch('app.scraper.scrape_committee_memberships')
    def test_scrape_committees_current(self, mock_scrape_comm):
        """Test committee memberships with current filter."""
        mock_scrape_comm.return_value = {
            'mps_committee_memberships': [],
            'lords_committee_memberships': []
        }
        
        response = self.app.get('/scrape/committees?current=true')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['metadata']['filter_current'])
        mock_scrape_comm.assert_called_with(current=True)

    # === Scrape All Tests ===
    
    @patch('app.scraper.scrape_all_data')
    def test_scrape_all_basic(self, mock_scrape_all):
        """Test comprehensive scraping endpoint."""
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
        self.assertIn('government_roles', data)
        self.assertIn('committee_memberships', data)
        self.assertIn('summary', data)
        mock_scrape_all.assert_called_with(current=False)

    @patch('app.scraper.scrape_all_data')
    def test_scrape_all_current_filter(self, mock_scrape_all):
        """Test scrape all with current filter."""
        mock_scrape_all.return_value = {
            'members_of_parliament': [],
            'house_of_lords': [],
            'government_roles': {},
            'committee_memberships': {},
            'summary': {'total_mps': 0, 'total_lords': 0}
        }
        
        response = self.app.get('/scrape/all?current=true')
        self.assertEqual(response.status_code, 200)
        mock_scrape_all.assert_called_with(current=True)

    @patch('app.scraper')
    def test_scrape_all_with_cache(self, mock_scraper_instance):
        """Test scrape all with cache functionality."""
        cached_data = {
            'members_of_parliament': [{'name': 'Cached MP'}],
            'metadata': {'cached': True}
        }
        mock_scraper_instance.cache = {'all': cached_data}
        
        response = self.app.get('/scrape/all?cache=true')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data, cached_data)
        # Should not call scrape_all_data when using cache
        mock_scraper_instance.scrape_all_data.assert_not_called()

    @patch('app.scraper')
    def test_scrape_all_cache_miss(self, mock_scraper_instance):
        """Test cache behavior when cache is empty."""
        mock_scraper_instance.cache = {}
        mock_scraper_instance.scrape_all_data.return_value = {'test': 'data'}
        
        response = self.app.get('/scrape/all?cache=true')
        self.assertEqual(response.status_code, 200)
        
        # Should call scrape_all_data when cache is empty
        mock_scraper_instance.scrape_all_data.assert_called_once()

    # === CSV Export Tests ===
    
    @patch('app.scraper.export_to_csv')
    def test_export_csv_all_data(self, mock_export):
        """Test CSV export for all data types."""
        mock_export.return_value = [
            'uk_mps_20240603_120000.csv',
            'uk_lords_20240603_120000.csv'
        ]
        
        response = self.app.get('/export/csv?type=all')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data_type'], 'all')
        self.assertEqual(data['file_count'], 2)
        self.assertIn('exported_files', data)
        mock_export.assert_called_with('all', False, None, None, None)

    @patch('app.scraper.export_to_csv')
    def test_export_csv_specific_types(self, mock_export):
        """Test CSV export for specific data types."""
        mock_export.return_value = ['test_file.csv']
        
        data_types = ['mps', 'lords', 'government-roles', 'committees']
        for data_type in data_types:
            response = self.app.post(f'/export/csv?type={data_type}')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            
            self.assertTrue(data['success'])
            self.assertEqual(data['data_type'], data_type)
            mock_export.assert_called_with(data_type, False, None, None, None)

    @patch('app.scraper.export_to_csv')
    def test_export_csv_with_current_filter(self, mock_export):
        """Test CSV export with current filter."""
        mock_export.return_value = ['current_mps.csv']
        
        response = self.app.post('/export/csv?type=mps&current=true')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['success'])
        mock_export.assert_called_with('mps', True, None, None, None)

    @patch('app.scraper.export_to_csv')
    def test_export_csv_with_date_filters(self, mock_export):
        """Test CSV export with date filtering."""
        mock_export.return_value = ['filtered_mps.csv']
        
        response = self.app.post('/export/csv?type=mps&from_date=2024-01-01&to_date=2024-12-31&on_date=2024-06-01')
        self.assertEqual(response.status_code, 200)
        
        mock_export.assert_called_with('mps', False, '2024-01-01', '2024-12-31', '2024-06-01')

    @patch('app.scraper.export_to_csv')
    def test_export_csv_combined_filters(self, mock_export):
        """Test CSV export with combined filters."""
        mock_export.return_value = ['combined_filter.csv']
        
        response = self.app.post('/export/csv?type=lords&current=true&from_date=2024-01-01')
        self.assertEqual(response.status_code, 200)
        
        mock_export.assert_called_with('lords', True, '2024-01-01', None, None)

    def test_export_csv_invalid_type(self):
        """Test CSV export with invalid data type."""
        response = self.app.get('/export/csv?type=invalid')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        
        self.assertIn('error', data)
        self.assertIn('Invalid data type', data['error'])
        self.assertIn('all, mps, lords, government-roles, committees', data['message'])

    @patch('app.scraper.export_to_csv')
    def test_export_csv_both_methods(self, mock_export):
        """Test CSV export supports both GET and POST methods."""
        mock_export.return_value = ['test.csv']
        
        # Test GET method
        response = self.app.get('/export/csv?type=mps')
        self.assertEqual(response.status_code, 200)
        
        # Test POST method
        response = self.app.post('/export/csv?type=mps')
        self.assertEqual(response.status_code, 200)

    # === Error Handling Tests ===
    
    def test_404_handler(self):
        """Test 404 error handling for non-existent endpoints."""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Endpoint not found')
        self.assertIn('timestamp', data)

    @patch('app.scraper.scrape_mps')
    def test_scrape_mps_error_handling(self, mock_scrape_mps):
        """Test error handling in MPs endpoint."""
        mock_scrape_mps.side_effect = Exception("Test error")
        
        response = self.app.get('/scrape/mps')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to scrape MPs data')
        self.assertIn('timestamp', data)

    @patch('app.scraper.scrape_lords')
    def test_scrape_lords_error_handling(self, mock_scrape_lords):
        """Test error handling in Lords endpoint."""
        mock_scrape_lords.side_effect = Exception("Test error")
        
        response = self.app.get('/scrape/lords')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to scrape Lords data')

    @patch('app.scraper.scrape_government_roles')
    def test_scrape_government_roles_error_handling(self, mock_scrape_gov):
        """Test error handling in government roles endpoint."""
        mock_scrape_gov.side_effect = Exception("Test error")
        
        response = self.app.get('/scrape/government-roles')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to scrape government roles data')

    @patch('app.scraper.scrape_committee_memberships')
    def test_scrape_committees_error_handling(self, mock_scrape_comm):
        """Test error handling in committees endpoint."""
        mock_scrape_comm.side_effect = Exception("Test error")
        
        response = self.app.get('/scrape/committees')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to scrape committees data')

    @patch('app.scraper.scrape_all_data')
    def test_scrape_all_error_handling(self, mock_scrape_all):
        """Test error handling in scrape all endpoint."""
        mock_scrape_all.side_effect = Exception("Test error")
        
        response = self.app.get('/scrape/all')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to scrape data')

    @patch('app.scraper.export_to_csv')
    def test_export_csv_error_handling(self, mock_export):
        """Test error handling in CSV export endpoint."""
        mock_export.side_effect = Exception("Export failed")
        
        response = self.app.post('/export/csv')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to export CSV files')

    # === Response Structure Tests ===
    
    @patch('app.scraper.scrape_mps')
    def test_response_structure_consistency(self, mock_scrape_mps):
        """Test that all endpoints return consistent response structures."""
        mock_scrape_mps.return_value = [{'name': 'Test'}]
        
        response = self.app.get('/scrape/mps')
        data = response.get_json()
        
        # Check required fields
        required_fields = ['metadata', 'summary']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Check metadata structure
        metadata = data['metadata']
        required_metadata = ['scraped_at', 'data_type']
        for field in required_metadata:
            self.assertIn(field, metadata)
        
        # Check timestamp format
        timestamp = metadata['scraped_at']
        # Should be valid ISO format
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

    @patch('app.scraper.export_to_csv')
    def test_csv_export_response_structure(self, mock_export):
        """Test CSV export response structure matches documentation."""
        mock_export.return_value = ['test_file.csv']
        
        response = self.app.post('/export/csv?type=mps&current=true')
        data = response.get_json()
        
        # Check all documented fields are present
        expected_fields = [
            'success', 'message', 'data_type', 'exported_files',
            'file_count', 'output_directory', 'timestamp'
        ]
        for field in expected_fields:
            self.assertIn(field, data)
        
        # Check field types and values
        self.assertIsInstance(data['success'], bool)
        self.assertIsInstance(data['exported_files'], list)
        self.assertIsInstance(data['file_count'], int)
        self.assertEqual(data['output_directory'], 'outputs/')

    # === Integration-style Tests ===
    
    @patch('app.scraper.scrape_all_data')
    def test_realistic_data_flow(self, mock_scrape_all):
        """Test realistic data flow with comprehensive dataset."""
        # Mock comprehensive realistic data
        realistic_data = {
            'metadata': {
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'scraper_version': '1.0.0',
                'data_source': 'UK Parliament API via pdpy library'
            },
            'members_of_parliament': [
                {
                    'person_id': 'https://id.parliament.uk/abc123',
                    'mnis_id': '172',
                    'given_name': 'John',
                    'family_name': 'Smith',
                    'display_name': 'John Smith MP',
                    'party_name': 'Conservative',
                    'constituency_name': 'Test Constituency'
                }
            ],
            'house_of_lords': [
                {
                    'person_id': 'https://id.parliament.uk/def456',
                    'mnis_id': '456',
                    'given_name': 'Lord',
                    'family_name': 'Example',
                    'display_name': 'Lord Example',
                    'party_name': 'Liberal Democrat'
                }
            ],
            'government_roles': {
                'mps_government_roles': [
                    {
                        'person_id': 'https://id.parliament.uk/abc123',
                        'display_name': 'John Smith MP',
                        'position_name': 'Secretary of State for Testing',
                        'government_incumbency_start_date': '2024-01-01',
                        'government_incumbency_end_date': None
                    }
                ],
                'lords_government_roles': []
            },
            'committee_memberships': {
                'mps_committee_memberships': [
                    {
                        'person_id': 'https://id.parliament.uk/abc123',
                        'display_name': 'John Smith MP',
                        'committee_name': 'Treasury Committee',
                        'committee_membership_start_date': '2024-01-01',
                        'committee_membership_end_date': None
                    }
                ],
                'lords_committee_memberships': []
            },
            'summary': {
                'total_mps': 1,
                'total_lords': 1,
                'total_mps_gov_roles': 1,
                'total_lords_gov_roles': 0,
                'total_mps_committee_memberships': 1,
                'total_lords_committee_memberships': 0
            }
        }
        
        mock_scrape_all.return_value = realistic_data
        
        response = self.app.get('/scrape/all?current=true')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Verify comprehensive data structure
        self.assertEqual(data['summary']['total_mps'], 1)
        self.assertEqual(data['summary']['total_lords'], 1)
        self.assertEqual(len(data['members_of_parliament']), 1)
        self.assertEqual(len(data['house_of_lords']), 1)
        
        # Verify person IDs follow correct format
        mp = data['members_of_parliament'][0]
        self.assertTrue(mp['person_id'].startswith('https://id.parliament.uk/'))

if __name__ == '__main__':
    unittest.main()