# UK Government Members Scraper

A Python Flask microservice that scrapes UK government members and employees using the [pdpy library](https://github.com/houseofcommonslibrary/pdpy).

## Features

- Scrapes Members of Parliament (MPs) from the House of Commons
- Scrapes Members of the House of Lords
- Retrieves parliamentary committee information and memberships
- **Filter for current members only** - exclude historical/former members
- **Date-based filtering** - get members from specific date ranges
- Provides RESTful API endpoints for different data types
- Caching support for improved performance
- CSV export with filtering support
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

The service will be available at `http://localhost:5001`

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

#### Filtering Parameters
- **`current=true`** - **NEW!** Filter to only current/serving members (default: false, returns all members)
- **`from_date=YYYY-MM-DD`** - **NEW!** Get members from this date onwards (MPs/Lords only)
- **`to_date=YYYY-MM-DD`** - **NEW!** Get members up to this date (MPs/Lords only)  
- **`on_date=YYYY-MM-DD`** - **NEW!** Get members serving on specific date (MPs/Lords only)

#### Other Parameters
- `cache=true` - Use cached data if available (for `/scrape/all` endpoint only)
- `type=<data_type>` - Specify data type for CSV export (all, mps, lords, government-roles, committees)

## Example Usage

### Get all government data
```bash
curl http://localhost:5001/scrape/all
```

### Get only current/serving members
```bash
# Get only current MPs (those still serving)
curl "http://localhost:5001/scrape/mps?current=true"

# Get only current Lords
curl "http://localhost:5001/scrape/lords?current=true"

# Get all current government data
curl "http://localhost:5001/scrape/all?current=true"
```

### Date-based filtering
```bash
# Get MPs from 2024 onwards
curl "http://localhost:5001/scrape/mps?from_date=2024-01-01"

# Get Lords serving on specific date
curl "http://localhost:5001/scrape/lords?on_date=2023-12-31"

# Get MPs serving between specific dates
curl "http://localhost:5001/scrape/mps?from_date=2023-01-01&to_date=2023-12-31"
```

### Get specific data types
```bash
# Get only MPs (all historical and current)
curl http://localhost:5001/scrape/mps

# Get only Lords (all historical and current)
curl http://localhost:5001/scrape/lords

# Get current committee memberships only
curl "http://localhost:5001/scrape/committees?current=true"

# Get current government roles only
curl "http://localhost:5001/scrape/government-roles?current=true"
```

### Export data to CSV
```bash
# Export all current members to CSV files
curl -X POST "http://localhost:5001/export/csv?type=all&current=true"

# Export only current MPs data
curl -X POST "http://localhost:5001/export/csv?type=mps&current=true"

# Export all historical Lords data  
curl -X POST "http://localhost:5001/export/csv?type=lords"

# Export current government roles
curl -X POST "http://localhost:5001/export/csv?type=government-roles&current=true"

# Export current committee memberships
curl -X POST "http://localhost:5001/export/csv?type=committees&current=true"

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
  - **`current=true`** (optional): Export only current/serving members (default: false)

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
  "message": "Successfully exported current mps data to CSV",
  "data_type": "mps",
  "filter_current": true,
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

#### Export All Data with Current Filter
```bash
response=$(curl -s -X POST "http://localhost:5001/export/csv?type=all&current=true")
if echo "$response" | grep -q "success.*true"; then
    echo "Export of current members successful!"
    echo "$response" | python -m json.tool
else
    echo "Export failed:"
    echo "$response" | python -m json.tool
fi
```

#### Python Example with Current Filtering
```python
import requests
import json

# Export only current MPs
response = requests.post("http://localhost:5001/export/csv?type=mps&current=true")
if response.status_code == 200:
    data = response.json()
    print(f"Exported {data['file_count']} files:")
    for file in data['exported_files']:
        print(f"  - {file}")
    print(f"Current filter applied: {data.get('filter_current', False)}")
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

## Key Features Explained

### Current Member Filtering

**What it does:** The `current=true` parameter filters results to show only members who are currently serving (i.e., they don't have an end date for their position).

**How it works:**
- **MPs/Lords**: Filters based on `membership_end_date` field (empty = current)
- **Government roles**: Filters based on `government_incumbency_end_date` field (empty = current)  
- **Committee memberships**: Filters based on `committee_membership_end_date` field (empty = current)

**Default behavior:** When `current=false` (default), all historical and current records are returned.

**Example:**
```bash
# Get all MPs ever elected (historical + current)
curl "http://localhost:5001/scrape/mps"

# Get only currently serving MPs
curl "http://localhost:5001/scrape/mps?current=true"
```

### Date-Based Filtering (MPs and Lords only)

The pdpy library supports date-based filtering for MPs and Lords data:

- **`from_date=YYYY-MM-DD`**: Get members from this date onwards
- **`to_date=YYYY-MM-DD`**: Get members up to this date
- **`on_date=YYYY-MM-DD`**: Get members who were serving on this specific date

**Examples:**
```bash
# Get all MPs who started serving from January 2024
curl "http://localhost:5001/scrape/mps?from_date=2024-01-01"

# Get Lords who were serving on December 31, 2023
curl "http://localhost:5001/scrape/lords?on_date=2023-12-31"

# Combine current filter with date filter
curl "http://localhost:5001/scrape/mps?current=true&from_date=2024-01-01"
```

### Backward Compatibility

All existing API calls continue to work exactly as before:
- Default behavior unchanged (returns all members when no parameters specified)
- Existing query parameters (`cache`, `type`) work as before
- JSON response structure maintained with additional metadata fields
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

### MPs/Lords Response with Current Filtering (`/scrape/mps?current=true`)
```json
{
  "metadata": {
    "scraped_at": "2025-06-03T15:30:00.123456+00:00",
    "data_type": "Members of Parliament - House of Commons",
    "filter_current": true,
    "from_date": null,
    "to_date": null,
    "on_date": null
  },
  "members_of_parliament": [
    {
      "person_id": "https://id.parliament.uk/43RHonMf",
      "mnis_id": "172",
      "given_name": "Diane",
      "family_name": "Abbott",
      "other_names": "Julie",
      "display_name": "Ms Diane Abbott",
      "full_title": "Rt Hon Diane Abbott MP",
      "gender": "Female",
      "date_of_birth": null,
      "date_of_death": null,
      "membership_end_date": null
    }
  ],
  "summary": {
    "total_count": 650
  }
}
```

### Government Roles Response with Current Filtering
```json
{
  "metadata": {
    "scraped_at": "2025-06-03T15:30:00.123456+00:00",
    "data_type": "Government Roles",
    "filter_current": true
  },
  "government_roles": {
    "mps_government_roles": [
      {
        "person_id": "https://id.parliament.uk/abc123",
        "display_name": "John Smith MP",
        "position_name": "Secretary of State for Education",
        "government_incumbency_start_date": "2024-01-01",
        "government_incumbency_end_date": null
      }
    ],
    "lords_government_roles": [
      {
        "person_id": "https://id.parliament.uk/def456",
        "display_name": "The Baroness Example",
        "position_name": "Parliamentary Under-Secretary",
        "government_incumbency_start_date": "2024-02-01",
        "government_incumbency_end_date": null
      }
    ]
  },
  "summary": {
    "total_mps_government_roles": 95,
    "total_lords_government_roles": 15
  }
}
```

### Complete Data Response (`/scrape/all?current=true`)
```json
{
  "metadata": {
    "scraped_at": "2025-06-03T15:30:00.123456+00:00",
    "scraper_version": "1.0.0",
    "data_source": "UK Parliament API via pdpy library"
  },
  "members_of_parliament": [
    {
      "person_id": "https://id.parliament.uk/member123",
      "mnis_id": "123",
      "given_name": "John",
      "family_name": "Smith",
      "display_name": "John Smith",
      "full_title": "John Smith MP",
      "gender": "Male",
      "membership_end_date": null
    }
  ],
  "house_of_lords": [
    {
      "person_id": "https://id.parliament.uk/lord456",
      "mnis_id": "456",
      "given_name": "Lord",
      "family_name": "Example",
      "display_name": "Lord Example",
      "full_title": "The Rt Hon Lord Example",
      "gender": "Male",
      "membership_end_date": null
    }
  ],
  "government_roles": {
    "mps_government_roles": [
      {
        "person_id": "https://id.parliament.uk/member123",
        "position_name": "Secretary of State",
        "government_incumbency_start_date": "2024-01-01",
        "government_incumbency_end_date": null
      }
    ],
    "lords_government_roles": []
  },
  "committee_memberships": {
    "mps_committee_memberships": [
      {
        "person_id": "https://id.parliament.uk/member123",
        "committee_name": "Treasury Committee",
        "committee_membership_start_date": "2024-01-01",
        "committee_membership_end_date": null
      }
    ],
    "lords_committee_memberships": []
  },
  "summary": {
    "total_mps": 650,
    "total_lords": 780,
    "total_mps_gov_roles": 95,
    "total_lords_gov_roles": 15,
    "total_mps_committee_memberships": 250,
    "total_lords_committee_memberships": 120
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

## Frequently Asked Questions (FAQ)

### Q: What's the difference between using `current=true` and not using it?
**A:** By default (`current=false` or no parameter), the API returns all historical and current members. With `current=true`, you only get members who are currently serving (those without end dates).

**Example:**
- All MPs ever: `curl "http://localhost:5001/scrape/mps"` → ~3000+ records (historical + current)
- Current MPs only: `curl "http://localhost:5001/scrape/mps?current=true"` → ~650 records (current only)

### Q: Can I combine the `current` filter with date parameters?
**A:** Yes! You can combine them to get very specific datasets:
```bash
# Current MPs who started serving from 2024 onwards
curl "http://localhost:5001/scrape/mps?current=true&from_date=2024-01-01"
```

### Q: Which endpoints support the `current` parameter?
**A:** All data endpoints support `current=true`:
- `/scrape/all?current=true`
- `/scrape/mps?current=true`
- `/scrape/lords?current=true`
- `/scrape/government-roles?current=true`
- `/scrape/committees?current=true`
- `/export/csv?type=all&current=true`

### Q: Which endpoints support date parameters?
**A:** Only MP and Lords endpoints support date filtering:
- `/scrape/mps?from_date=2024-01-01&to_date=2024-12-31&on_date=2024-06-01`
- `/scrape/lords?from_date=2024-01-01&to_date=2024-12-31&on_date=2024-06-01`

Government roles and committees don't support date parameters (use `current=true` instead).

### Q: How does the filtering work technically?
**A:** The API checks specific end date fields:
- **MPs/Lords**: `membership_end_date` (null/empty = currently serving)
- **Government roles**: `government_incumbency_end_date` (null/empty = currently serving)
- **Committee memberships**: `committee_membership_end_date` (null/empty = currently serving)

### Q: Will existing API calls still work?
**A:** Yes! All existing API calls work exactly as before. The new parameters are optional and don't change default behavior.

### Q: Can I see what filters were applied in the response?
**A:** Yes! The API response includes metadata showing what filters were applied:
```json
{
  "metadata": {
    "filter_current": true,
    "from_date": "2024-01-01",
    "to_date": null,
    "on_date": null
  }
}
```

### Q: How do I know if a member is currently serving?
**A:** Look for empty/null end date fields:
- `membership_end_date: null` = currently serving MP/Lord
- `government_incumbency_end_date: null` = currently in government role
- `committee_membership_end_date: null` = currently on committee

## Development

### Adding New Data Sources
To add new data sources, extend the `UKGovernmentScraper` class in `app.py` and add corresponding Flask routes.

### Testing
```bash
# Test the service locally
curl http://localhost:5001/health

# Test basic data endpoints
curl http://localhost:5001/scrape/mps | python -m json.tool

# Test new current filtering functionality
curl "http://localhost:5001/scrape/mps?current=true" | python -m json.tool
curl "http://localhost:5001/scrape/lords?current=true" | python -m json.tool
curl "http://localhost:5001/scrape/government-roles?current=true" | python -m json.tool
curl "http://localhost:5001/scrape/committees?current=true" | python -m json.tool

# Test date-based filtering
curl "http://localhost:5001/scrape/mps?from_date=2024-01-01" | python -m json.tool
curl "http://localhost:5001/scrape/lords?on_date=2024-06-01" | python -m json.tool

# Test combined filtering
curl "http://localhost:5001/scrape/mps?current=true&from_date=2024-01-01" | python -m json.tool

# Test CSV export functionality
curl -X POST "http://localhost:5001/export/csv?type=mps" | python -m json.tool
curl -X POST "http://localhost:5001/export/csv?type=mps&current=true" | python -m json.tool

# Run the comprehensive test script
python test_api.py
```

#### Testing Current vs All Members

```bash
# Compare total counts: all vs current members
echo "=== All MPs (historical + current) ==="
curl -s "http://localhost:5001/scrape/mps" | jq '.summary.total_count'

echo "=== Current MPs only ==="
curl -s "http://localhost:5001/scrape/mps?current=true" | jq '.summary.total_count'

echo "=== All Lords (historical + current) ==="
curl -s "http://localhost:5001/scrape/lords" | jq '.summary.total_count'

echo "=== Current Lords only ==="
curl -s "http://localhost:5001/scrape/lords?current=true" | jq '.summary.total_count'
```

#### Performance Testing

```bash
# Test response times for different filtering options
echo "Testing response times..."

echo "All MPs:"
time curl -s "http://localhost:5001/scrape/mps" > /dev/null

echo "Current MPs only:"
time curl -s "http://localhost:5001/scrape/mps?current=true" > /dev/null

echo "All government roles:"
time curl -s "http://localhost:5001/scrape/government-roles" > /dev/null

echo "Current government roles:"
time curl -s "http://localhost:5001/scrape/government-roles?current=true" > /dev/null
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
