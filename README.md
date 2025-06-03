# UK Government Members Scraper

A Python Flask microservice that scrapes UK government members and employees using the [pdpy library](https://github.com/houseofcommonslibrary/pdpy).

## Features

- Scrapes Members of Parliament (MPs) from the House of Commons
- Scrapes Members of the House of Lords
- Retrieves parliamentary committee information and memberships
- Provides RESTful API endpoints for different data types
- Caching support for improved performance
- Comprehensive error handling and logging

## Setup with Conda

### 1. Create the conda environment

```bash
conda env create -f environment.yml
```

### 2. Activate the environment

```bash
conda activate uk-pep-scraper
```

### 3. Run the Flask application

```bash
python app.py
```

The service will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /` - Service information and available endpoints
- `GET /health` - Service health status

### Data Scraping
- `GET /scrape/all` - Scrape all government members and employees
- `GET /scrape/mps` - Scrape only MPs from House of Commons
- `GET /scrape/lords` - Scrape only members of House of Lords
- `GET /scrape/committees` - Scrape parliamentary committees
- `GET /scrape/government-roles` - Scrape government roles and positions

### CSV Export
- `POST /export/csv?type=all` - Export all data to CSV files
- `POST /export/csv?type=mps` - Export MPs data to CSV
- `POST /export/csv?type=lords` - Export Lords data to CSV
- `POST /export/csv?type=government-roles` - Export government roles to CSV
- `POST /export/csv?type=committees` - Export committee memberships to CSV

### Query Parameters
- `cache=true` - Use cached data if available (for `/scrape/all` endpoint)
- `type=<data_type>` - Specify data type for CSV export (all, mps, lords, government-roles, committees)

## Example Usage

### Get all government data
```bash
curl http://localhost:5000/scrape/all
```

### Get only MPs
```bash
curl http://localhost:5000/scrape/mps
```

### Get only Lords
```bash
curl http://localhost:5000/scrape/lords
```

### Get committees
```bash
curl http://localhost:5000/scrape/committees
```

### Get government roles
```bash
curl http://localhost:5000/scrape/government-roles
```

### Export data to CSV
```bash
# Export all data to CSV files
curl -X POST http://localhost:5001/export/csv?type=all

# Export only MPs data
curl -X POST http://localhost:5001/export/csv?type=mps

# Export only Lords data  
curl -X POST http://localhost:5001/export/csv?type=lords

# Export government roles
curl -X POST http://localhost:5001/export/csv?type=government-roles

# Export committee memberships
curl -X POST http://localhost:5001/export/csv?type=committees
```

## CSV Export Endpoint Details

### Overview
The CSV export endpoint allows you to export scraped UK Parliament data to CSV files stored in the `outputs/` directory. This is useful for data analysis, reporting, and integration with external tools.

### Endpoint Specification
- **URL**: `/export/csv`
- **Method**: `POST` or `GET`
- **Query Parameters**: 
  - `type` (required): Data type to export (`all`, `mps`, `lords`, `government-roles`, `committees`)

### Supported Data Types

| Type | Description | Files Generated |
|------|-------------|-----------------|
| `all` | Export all available data | 6 CSV files (MPs, Lords, and their government roles and committee memberships) |
| `mps` | Export MPs only | 1 CSV file with House of Commons members |
| `lords` | Export Lords only | 1 CSV file with House of Lords members |
| `government-roles` | Export government positions | 2 CSV files (MPs and Lords with government roles) |
| `committees` | Export committee memberships | 2 CSV files (MPs and Lords committee memberships) |

### CSV File Naming Convention
Files are automatically named with timestamps for unique identification:
- `uk_mps_YYYYMMDD_HHMMSS.csv` - Members of Parliament
- `uk_lords_YYYYMMDD_HHMMSS.csv` - House of Lords members
- `uk_mps_government_roles_YYYYMMDD_HHMMSS.csv` - MPs with government positions
- `uk_lords_government_roles_YYYYMMDD_HHMMSS.csv` - Lords with government positions
- `uk_mps_committee_memberships_YYYYMMDD_HHMMSS.csv` - MPs committee memberships
- `uk_lords_committee_memberships_YYYYMMDD_HHMMSS.csv` - Lords committee memberships

### CSV Export Response Structure
```json
{
  "success": true,
  "message": "Successfully exported mps data to CSV",
  "data_type": "mps",
  "exported_files": ["uk_mps_20250603_113333.csv"],
  "file_count": 1,
  "output_directory": "outputs/",
  "timestamp": "2025-06-03T11:33:34.454105"
}
```

### Error Response
```json
{
  "error": "Invalid data type",
  "message": "Data type must be one of: all, mps, lords, government-roles, committees",
  "timestamp": "2025-06-03T11:33:34.454105"
}
```

### CSV File Structure Examples

#### Data Field Documentation

**Core Identity Fields**

**Person ID (`person_id`)**
- **Purpose**: Primary unique identifier for parliament members
- **Format**: URI format `https://id.parliament.uk/{unique_id}`
- **Example**: `https://id.parliament.uk/43RHonMf`
- **Usage**: Modern parliamentary API standard identifier for cross-referencing across all parliamentary systems

**MNIS ID (`mnis_id`)**
- **Purpose**: Legacy numeric identifier from the UK Parliament's **Members Names Information Service (MNIS)**
- **Format**: Numeric ID (e.g., 172, 4212, 662, 4057, 631)
- **Scope**: Present for all members across MPs, Lords, committee memberships, and government roles
- **Relationship**: Complements the primary `person_id` field
- **Usage**: Used for cross-referencing member data across different parliamentary systems and historical records

**Personal Information Fields**

**Name Fields**
- **`given_name`**: First name(s) of the member (e.g., "Diane", "Nigel")
- **`family_name`**: Surname/last name (e.g., "Abbott", "Adams")
- **`other_names`**: Middle names or additional names (e.g., "Julie", "Angela Elspeth Marie")
- **`display_name`**: Commonly used public name (e.g., "Ms Diane Abbott", "Nigel Adams")
- **`full_title`**: Complete formal title including honors (e.g., "Rt Hon Diane Abbott MP", "The Baroness Adams of Craigielea")

**Demographics**
- **`gender`**: Gender identification ("Male", "Female")
- **`date_of_birth`**: Birth date (ISO format YYYY-MM-DD, may be empty for privacy)
- **`date_of_death`**: Death date (ISO format YYYY-MM-DD, empty if living)

**Government Role Fields** (for `*_government_roles_*.csv` files)

**Position Information**
- **`position_id`**: Unique identifier for the government position (URI format)
- **`position_name`**: Official title of the government role (e.g., "Assistant Whip (HM Treasury)", "Parliamentary Under-Secretary")

**Incumbency Tracking**
- **`government_incumbency_id`**: Unique identifier for this specific appointment period
- **`government_incumbency_start_date`**: When the person started in this role (YYYY-MM-DD)
- **`government_incumbency_end_date`**: When the person left this role (YYYY-MM-DD, empty if current)

**Committee Membership Fields** (for `*_committee_memberships_*.csv` files)

**Committee Information**
- **`committee_id`**: Unique identifier for the committee (URI format)
- **`committee_name`**: Official name of the committee (e.g., "Treasury Committee", "Foreign Affairs Committee")
- **`committee_type_id`**: Identifier for the type of committee
- **`committee_type_name`**: Description of committee type (e.g., "Parliamentary - Select")

**Membership Tracking**
- **`committee_membership_id`**: Unique identifier for this specific membership period
- **`committee_membership_start_date`**: When the person joined the committee (YYYY-MM-DD)
- **`committee_membership_end_date`**: When the person left the committee (YYYY-MM-DD, empty if current)

**Data Quality Notes**
- Empty fields indicate missing or non-applicable data
- Date fields follow ISO 8601 format (YYYY-MM-DD)
- All URI-based IDs link to official UK Parliament API resources
- Historical data may have gaps due to record-keeping limitations
- The `mnis_id` provides backward compatibility with legacy parliamentary systems

#### MPs CSV (`uk_mps_*.csv`)
```csv
person_id,mnis_id,given_name,family_name,other_names,display_name,full_title,gender,date_of_birth,date_of_death
https://id.parliament.uk/43RHonMf,172,Diane,Abbott,Julie,Ms Diane Abbott,Rt Hon Diane Abbott MP,Female,,
```

#### Government Roles CSV (`uk_mps_government_roles_*.csv`)
```csv
person_id,display_name,position_name,department,start_date,end_date,is_current
https://id.parliament.uk/abc123,John Smith MP,Secretary of State,Department for Education,2024-01-01,,true
```

#### Committee Memberships CSV (`uk_mps_committee_memberships_*.csv`)
```csv
person_id,display_name,committee_name,role,start_date,end_date,is_current
https://id.parliament.uk/def456,Jane Doe MP,Treasury Committee,Chair,2024-01-01,,true
```

### Usage Examples with Response Handling

#### Export All Data with Error Handling
```bash
response=$(curl -s -X POST "http://localhost:5001/export/csv?type=all")
if echo "$response" | grep -q "success.*true"; then
    echo "Export successful!"
    echo "$response" | python -m json.tool
else
    echo "Export failed:"
    echo "$response" | python -m json.tool
fi
```

#### Python Example
```python
import requests
import json

response = requests.post("http://localhost:5001/export/csv?type=mps")
if response.status_code == 200:
    data = response.json()
    print(f"Exported {data['file_count']} files:")
    for file in data['exported_files']:
        print(f"  - {file}")
else:
    print(f"Error: {response.json()['message']}")
```

### File Storage
- **Directory**: `outputs/` (automatically created if it doesn't exist)
- **Permissions**: Files are created with standard read/write permissions
- **Encoding**: UTF-8
- **Format**: Standard CSV with comma separators and header row

### File Management
- Files are not automatically cleaned up - you may want to implement a cleanup strategy for production use
- Each export creates new files with unique timestamps
- Multiple exports of the same data type will create separate files
- Files can be safely deleted after processing as they are regenerated on each export

## Project Structure
```
UK_PEP_scrape_test/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── environment.yml       # Conda environment specification
├── README.md            # This documentation
├── setup_and_run.sh     # Setup and run script
├── test_api.py          # Comprehensive API test script
└── outputs/             # CSV export directory (auto-created)
    ├── uk_mps_*.csv
    ├── uk_lords_*.csv
    └── uk_*_committee_memberships_*.csv
```

## JSON Response Structure

### Complete Data Response (`/scrape/all`)
```json
{
  "metadata": {
    "scraped_at": "2025-06-03T10:30:00",
    "scraper_version": "1.0.0",
    "data_source": "UK Parliament API via pdpy library"
  },
  "members_of_parliament": [
    {
      "id": 123,
      "name": "John Smith",
      "full_name": "John Smith MP",
      "party": "Conservative",
      "constituency": "Example Constituency",
      "house": "Commons",
      "type": "MP",
      "current": true
    }
  ],
  "house_of_lords": [
    {
      "id": 456,
      "name": "Lord Example",
      "full_name": "The Rt Hon Lord Example",
      "party": "Labour",
      "house": "Lords",
      "type": "Lord",
      "current": true
    }
  ],
  "committees": [
    {
      "id": 789,
      "name": "Treasury Committee",
      "house": "Commons",
      "category": "Select Committee",
      "members": [
        {
          "id": 123,
          "name": "John Smith",
          "role": "Chair",
          "start_date": "2024-01-01",
          "end_date": null
        }
      ]
    }
  ],
  "summary": {
    "total_mps": 650,
    "total_lords": 780,
    "total_committees": 45,
    "current_mps": 650,
    "current_lords": 780
  }
}
```

## Production Deployment

### Using Gunicorn
```bash
conda activate uk-pep-scraper
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
You can set the following environment variables:
- `FLASK_ENV` - Set to `production` for production deployment
- `PORT` - Port number (default: 5000)

## Dependencies

- Python 3.9+
- Flask 2.3.3
- pdpy 0.1.6 (UK Parliament data library)
- pandas >= 1.3.0 (required for CSV export functionality)
- numpy >= 1.21.0
- requests >= 2.25.0
- gunicorn 21.2.0 (for production deployment)

## Data Sources

This microservice uses the [pdpy library](https://github.com/houseofcommonslibrary/pdpy) which provides access to UK Parliament data through official APIs.

## Logging

The application includes comprehensive logging for monitoring and debugging. Logs include:
- API request information
- Data scraping progress
- Error details and stack traces
- Performance metrics

## Error Handling

The service includes robust error handling:
- HTTP 404 for unknown endpoints
- HTTP 500 for internal server errors
- Detailed error messages in JSON format
- Graceful handling of pdpy library errors

## Development

### Adding New Data Sources
To add new data sources, extend the `UKGovernmentScraper` class in `app.py` and add corresponding Flask routes.

### Testing
```bash
# Test the service locally
curl http://localhost:5001/health

# Test data endpoints
curl http://localhost:5001/scrape/mps | python -m json.tool

# Test CSV export functionality
curl -X POST "http://localhost:5001/export/csv?type=mps" | python -m json.tool

# Run the comprehensive test script
python test_api.py
```

#### Test Script Features
The included `test_api.py` script provides comprehensive testing of all endpoints:
- Tests all JSON API endpoints with detailed output
- Tests all CSV export data types
- Provides curl examples for manual testing
- Shows response summaries and file counts
- Includes error handling and connection testing

```bash
# Run all tests including CSV export
python test_api.py
```
