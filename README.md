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
- pandas >= 1.3.0
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
curl http://localhost:5000/health

# Test data endpoints
curl http://localhost:5000/scrape/mps | python -m json.tool
```
