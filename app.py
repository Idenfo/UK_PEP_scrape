"""UK Government Members and Employees Scraper.

A Flask microservice that scrapes UK government data using the pdpy library.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Flask, jsonify, request

# Import pdpy modules for scraping UK parliamentary data
try:
    import pdpy  # type: ignore[import-untyped]

    print("✅ pdpy imported successfully")
except ImportError as e:
    print(f"Error importing pdpy: {e}")
    print("Make sure pdpy is installed: pip install pdpy")

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type aliases for better readability
DataDict = dict[str, Any]
FileList = list[str]


class UKGovernmentScraper:
    """Main scraper class for UK government data."""

    def __init__(self) -> None:
        """Initialize the scraper with empty cache."""
        self.cache: dict[str, Any] = {}
        self.last_updated: datetime | None = None

    def _convert_to_dict(self, data: Any) -> list[dict[str, Any]] | Any:
        """Convert pandas DataFrame to dict if possible, otherwise return as-is."""
        return data.to_dict("records") if hasattr(data, "to_dict") else data

    def scrape_mps(self) -> list[dict[str, Any]]:
        """Scrape current Members of Parliament (MPs) from House of Commons."""
        try:
            data = pdpy.fetch_mps()  # type: ignore[attr-defined]
            data_dict = self._convert_to_dict(data)

            # Cache the data
            self.cache["mps"] = {
                "data": data_dict,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception:
            logger.exception("Error scraping MPs")
            raise
        else:
            return data_dict

    def scrape_lords(self) -> list[dict[str, Any]]:
        """Scrape current Members of House of Lords."""
        try:
            data = pdpy.fetch_lords()  # type: ignore[attr-defined]
            data_dict = self._convert_to_dict(data)

            # Cache the data
            self.cache["lords"] = {
                "data": data_dict,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception:
            logger.exception("Error scraping Lords")
            raise
        else:
            return data_dict

    def scrape_government_roles(self) -> dict[str, Any]:
        """Scrape government roles for both MPs and Lords."""
        try:
            mps_gov_roles = pdpy.fetch_mps_government_roles()  # type: ignore[attr-defined]
            lords_gov_roles = pdpy.fetch_lords_government_roles()  # type: ignore[attr-defined]

            # Convert DataFrames to dicts
            mps_roles = self._convert_to_dict(mps_gov_roles)
            lords_roles = self._convert_to_dict(lords_gov_roles)

        except Exception:
            logger.exception("Error scraping government roles")
            raise
        else:
            return {
                "mps_government_roles": mps_roles,
                "lords_government_roles": lords_roles,
            }

    def scrape_committee_memberships(self) -> dict[str, Any]:
        """Scrape committee memberships."""
        try:
            mps_committees = pdpy.fetch_mps_committee_memberships()  # type: ignore[attr-defined]
            lords_committees = pdpy.fetch_lords_committee_memberships()  # type: ignore[attr-defined]

            # Convert DataFrames to dicts
            mps_comm = self._convert_to_dict(mps_committees)
            lords_comm = self._convert_to_dict(lords_committees)

        except Exception:
            logger.exception("Error scraping committee memberships")
            raise
        else:
            return {
                "mps_committee_memberships": mps_comm,
                "lords_committee_memberships": lords_comm,
            }

    def scrape_all_data(self) -> dict[str, Any]:
        """Scrape all available UK government and parliamentary data."""
        try:
            logger.info("Starting comprehensive data scrape")

            # Scrape all data types
            mps = self.scrape_mps()
            lords = self.scrape_lords()
            government_roles = self.scrape_government_roles()
            committees = self.scrape_committee_memberships()

            data = {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "scraper_version": "1.0.0",
                    "data_source": "UK Parliament API via pdpy library",
                },
                "members_of_parliament": mps,
                "house_of_lords": lords,
                "government_roles": government_roles,
                "committee_memberships": committees,
            }

            # Add summary statistics with safe length calculation
            def safe_len(obj: Any) -> int:
                """Safely get length of object, return 0 if not possible."""
                try:
                    return len(obj)
                except (TypeError, AttributeError):
                    return 0

            data["summary"] = {
                "total_mps": safe_len(mps),
                "total_lords": safe_len(lords),
                "total_mps_gov_roles": safe_len(government_roles.get("mps_government_roles", [])),
                "total_lords_gov_roles": safe_len(government_roles.get("lords_government_roles", [])),
                "total_mps_committee_memberships": safe_len(committees.get("mps_committee_memberships", [])),
                "total_lords_committee_memberships": safe_len(committees.get("lords_committee_memberships", [])),
            }

            self.cache["all"] = data
            self.last_updated = datetime.now(timezone.utc)

            logger.info(
                "Scraping completed. Found %d MPs and %d Lords",
                data["summary"]["total_mps"],
                data["summary"]["total_lords"],
            )

        except Exception:
            logger.exception("Error during comprehensive scrape")
            raise
        else:
            return data

    def _create_outputs_dir(self) -> Path:
        """Create and return the outputs directory path."""
        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        return outputs_dir

    def _export_dataframe_to_csv(self, data: Any, file_path: Path) -> None:
        """Export data to CSV file."""
        data_frame = pd.DataFrame(data)
        data_frame.to_csv(file_path, index=False)

    def _export_all_data_to_csv(self, outputs_dir: Path, timestamp: str) -> FileList:
        """Export all data types to CSV files."""
        exported_files: FileList = []
        all_data = self.scrape_all_data()

        # Export MPs
        if "members_of_parliament" in all_data:
            mps_file = outputs_dir / f"uk_mps_{timestamp}.csv"
            self._export_dataframe_to_csv(all_data["members_of_parliament"], mps_file)
            exported_files.append(str(mps_file))

        # Export Lords
        if "house_of_lords" in all_data:
            lords_file = outputs_dir / f"uk_lords_{timestamp}.csv"
            self._export_dataframe_to_csv(all_data["house_of_lords"], lords_file)
            exported_files.append(str(lords_file))

        # Export Government Roles
        if "government_roles" in all_data:
            gov_roles = all_data["government_roles"]
            if isinstance(gov_roles, dict) and "mps_government_roles" in gov_roles:
                mps_gov_file = outputs_dir / f"uk_mps_government_roles_{timestamp}.csv"
                self._export_dataframe_to_csv(gov_roles["mps_government_roles"], mps_gov_file)
                exported_files.append(str(mps_gov_file))

            if isinstance(gov_roles, dict) and "lords_government_roles" in gov_roles:
                lords_gov_file = outputs_dir / f"uk_lords_government_roles_{timestamp}.csv"
                self._export_dataframe_to_csv(gov_roles["lords_government_roles"], lords_gov_file)
                exported_files.append(str(lords_gov_file))

        # Export Committee Memberships
        if "committee_memberships" in all_data:
            committees = all_data["committee_memberships"]
            if isinstance(committees, dict) and "mps_committee_memberships" in committees:
                mps_comm_file = outputs_dir / f"uk_mps_committee_memberships_{timestamp}.csv"
                self._export_dataframe_to_csv(committees["mps_committee_memberships"], mps_comm_file)
                exported_files.append(str(mps_comm_file))

            if isinstance(committees, dict) and "lords_committee_memberships" in committees:
                lords_comm_file = outputs_dir / f"uk_lords_committee_memberships_{timestamp}.csv"
                self._export_dataframe_to_csv(committees["lords_committee_memberships"], lords_comm_file)
                exported_files.append(str(lords_comm_file))

        return exported_files

    def _export_single_data_type(self, data_type: str, outputs_dir: Path, timestamp: str) -> FileList:
        """Export a single data type to CSV."""
        exported_files: FileList = []

        if data_type == "mps":
            mps_data = self.scrape_mps()
            mps_file = outputs_dir / f"uk_mps_{timestamp}.csv"
            self._export_dataframe_to_csv(mps_data, mps_file)
            exported_files.append(str(mps_file))

        elif data_type == "lords":
            lords_data = self.scrape_lords()
            lords_file = outputs_dir / f"uk_lords_{timestamp}.csv"
            self._export_dataframe_to_csv(lords_data, lords_file)
            exported_files.append(str(lords_file))

        elif data_type == "government-roles":
            gov_roles_data = self.scrape_government_roles()
            if "mps_government_roles" in gov_roles_data:
                mps_gov_file = outputs_dir / f"uk_mps_government_roles_{timestamp}.csv"
                self._export_dataframe_to_csv(gov_roles_data["mps_government_roles"], mps_gov_file)
                exported_files.append(str(mps_gov_file))

            if "lords_government_roles" in gov_roles_data:
                lords_gov_file = outputs_dir / f"uk_lords_government_roles_{timestamp}.csv"
                self._export_dataframe_to_csv(gov_roles_data["lords_government_roles"], lords_gov_file)
                exported_files.append(str(lords_gov_file))

        elif data_type == "committees":
            committees_data = self.scrape_committee_memberships()
            if "mps_committee_memberships" in committees_data:
                mps_comm_file = outputs_dir / f"uk_mps_committee_memberships_{timestamp}.csv"
                self._export_dataframe_to_csv(committees_data["mps_committee_memberships"], mps_comm_file)
                exported_files.append(str(mps_comm_file))

            if "lords_committee_memberships" in committees_data:
                lords_comm_file = outputs_dir / f"uk_lords_committee_memberships_{timestamp}.csv"
                self._export_dataframe_to_csv(committees_data["lords_committee_memberships"], lords_comm_file)
                exported_files.append(str(lords_comm_file))

        return exported_files

    def export_to_csv(self, data_type: str = "all") -> FileList:
        """Export scraped data to CSV files in the outputs folder."""
        try:
            outputs_dir = self._create_outputs_dir()
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

            if data_type == "all":
                exported_files = self._export_all_data_to_csv(outputs_dir, timestamp)
            else:
                exported_files = self._export_single_data_type(data_type, outputs_dir, timestamp)

            logger.info("Exported %d CSV files to outputs directory", len(exported_files))

        except Exception:
            logger.exception("Error exporting to CSV")
            raise
        else:
            return exported_files


# Initialize the scraper
scraper = UKGovernmentScraper()


@app.route("/")
def index() -> Any:
    """Health check and API information endpoint."""
    return jsonify(
        {
            "service": "UK Government Members Scraper",
            "status": "active",
            "version": "1.0.0",
            "endpoints": {
                "/scrape/all": "Scrape all government members and employees",
                "/scrape/mps": "Scrape only MPs from House of Commons",
                "/scrape/lords": "Scrape only members of House of Lords",
                "/scrape/committees": "Scrape committee memberships",
                "/scrape/government-roles": "Scrape government roles",
                "/health": "Service health check",
                "/export/csv": "Export scraped data to CSV files",
            },
            "last_updated": scraper.last_updated.isoformat() if scraper.last_updated else None,
        },
    )


@app.route("/health")
def health() -> Any:
    """Service health check."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache_status": "populated" if scraper.cache else "empty",
        },
    )


@app.route("/scrape/all")
def scrape_all() -> tuple[Any, int]:
    """Scrape all UK government members and employees."""
    try:
        # Check if we should use cached data (optional query parameter)
        use_cache = request.args.get("cache", "false").lower() == "true"

        if use_cache and "all" in scraper.cache:
            logger.info("Returning cached data")
            return jsonify(scraper.cache["all"]), 200

        # Perform fresh scrape
        data = scraper.scrape_all_data()
        return jsonify(data), 200

    except Exception:
        logger.exception("Error in scrape_all endpoint")
        return jsonify(
            {
                "error": "Failed to scrape data",
                "message": "An error occurred while scraping data",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ), 500


@app.route("/scrape/mps")
def scrape_mps_endpoint() -> tuple[Any, int]:
    """Scrape only Members of Parliament from House of Commons."""
    try:
        mps_data = scraper.scrape_mps()
        return jsonify(
            {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "data_type": "Members of Parliament - House of Commons",
                },
                "members_of_parliament": mps_data,
                "summary": {
                    "total_count": len(mps_data),
                    "current_count": len(mps_data),  # All MPs returned are current
                },
            },
        ), 200
    except Exception:
        logger.exception("Error in scrape_mps endpoint")
        return jsonify(
            {
                "error": "Failed to scrape MPs data",
                "message": "An error occurred while scraping MPs data",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ), 500


@app.route("/scrape/lords")
def scrape_lords_endpoint() -> tuple[Any, int]:
    """Scrape only members of House of Lords."""
    try:
        lords_data = scraper.scrape_lords()
        return jsonify(
            {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "data_type": "Members of House of Lords",
                },
                "house_of_lords": lords_data,
                "summary": {
                    "total_count": len(lords_data),
                    "current_count": len(lords_data),  # All Lords returned are current
                },
            },
        ), 200
    except Exception:
        logger.exception("Error in scrape_lords endpoint")
        return jsonify(
            {
                "error": "Failed to scrape Lords data",
                "message": "An error occurred while scraping Lords data",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ), 500


@app.route("/scrape/committees")
def scrape_committees() -> tuple[Any, int]:
    """Scrape committee memberships."""
    try:
        committees_data = scraper.scrape_committee_memberships()
        return jsonify(
            {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "data_type": "Committee Memberships",
                },
                "committee_memberships": committees_data,
                "summary": {
                    "total_mps_committee_memberships": len(committees_data.get("mps_committee_memberships", [])),
                    "total_lords_committee_memberships": len(committees_data.get("lords_committee_memberships", [])),
                },
            },
        ), 200
    except Exception:
        logger.exception("Error in scrape_committees endpoint")
        return jsonify(
            {
                "error": "Failed to scrape committees data",
                "message": "An error occurred while scraping committees data",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ), 500


@app.route("/scrape/government-roles")
def scrape_government_roles_endpoint() -> tuple[Any, int]:
    """Scrape government roles."""
    try:
        gov_roles_data = scraper.scrape_government_roles()
        return jsonify(
            {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "data_type": "Government Roles",
                },
                "government_roles": gov_roles_data,
                "summary": {
                    "total_mps_government_roles": len(gov_roles_data.get("mps_government_roles", [])),
                    "total_lords_government_roles": len(gov_roles_data.get("lords_government_roles", [])),
                },
            },
        ), 200
    except Exception:
        logger.exception("Error in scrape_government_roles endpoint")
        return jsonify(
            {
                "error": "Failed to scrape government roles data",
                "message": "An error occurred while scraping government roles data",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ), 500


@app.route("/export/csv", methods=["POST", "GET"])
def export_csv() -> tuple[Any, int]:
    """Export data to CSV files in outputs folder."""
    try:
        # Get data type from query parameter, default to 'all'
        data_type = request.args.get("type", "all")

        # Validate data type
        valid_types = ["all", "mps", "lords", "government-roles", "committees"]
        if data_type not in valid_types:
            return jsonify(
                {
                    "error": "Invalid data type",
                    "message": f"Data type must be one of: {', '.join(valid_types)}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            ), 400

        # Export to CSV
        exported_files = scraper.export_to_csv(data_type)

        return jsonify(
            {
                "success": True,
                "message": f"Successfully exported {data_type} data to CSV",
                "data_type": data_type,
                "exported_files": [Path(f).name for f in exported_files],
                "file_count": len(exported_files),
                "output_directory": "outputs/",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ), 200

    except Exception:
        logger.exception("Error in export_csv endpoint")
        return jsonify(
            {
                "error": "Failed to export CSV files",
                "message": "An error occurred while exporting CSV files",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ), 500


@app.errorhandler(404)
def not_found(_error: Any) -> tuple[Any, int]:
    """Handle 404 errors."""
    return jsonify(
        {
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    ), 404


@app.errorhandler(500)
def internal_error(_error: Any) -> tuple[Any, int]:
    """Handle 500 errors."""
    return jsonify(
        {
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    ), 500


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5001)
