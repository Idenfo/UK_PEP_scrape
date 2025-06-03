"""UK Government Members and Employees Scraper
A Flask microservice that scrapes UK government data using the pdpy library
"""

import logging
import os
import traceback
from datetime import datetime

import pandas as pd
from flask import Flask, jsonify, request

# Import pdpy modules for scraping UK parliamentary data
try:
    import pdpy

    print("✅ pdpy imported successfully")
except ImportError as e:
    print(f"Error importing pdpy: {e}")
    print("Make sure pdpy is installed: pip install pdpy")

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UKGovernmentScraper:
    """Main scraper class for UK government data"""

    def __init__(self):
        self.cache = {}
        self.last_updated = None

    def scrape_mps(self):
        """Scrape current Members of Parliament (MPs) from House of Commons"""
        try:
            data = pdpy.fetch_mps()

            # Convert DataFrame to dict/list for JSON serialization
            if hasattr(data, "to_dict"):
                data_dict = data.to_dict("records")
            else:
                data_dict = data

            # Cache the data
            self.cache["mps"] = {
                "data": data_dict,
                "timestamp": datetime.now().isoformat(),
            }

            return data_dict
        except Exception as e:
            logger.error(f"Error scraping MPs: {e!s}")
            raise

    def scrape_lords(self):
        """Scrape current Members of House of Lords"""
        try:
            data = pdpy.fetch_lords()

            # Convert DataFrame to dict/list for JSON serialization
            if hasattr(data, "to_dict"):
                data_dict = data.to_dict("records")
            else:
                data_dict = data

            # Cache the data
            self.cache["lords"] = {
                "data": data_dict,
                "timestamp": datetime.now().isoformat(),
            }

            return data_dict
        except Exception as e:
            logger.error(f"Error scraping Lords: {e!s}")
            raise

    def scrape_government_roles(self):
        """Scrape government roles for both MPs and Lords"""
        try:
            mps_gov_roles = pdpy.fetch_mps_government_roles()
            lords_gov_roles = pdpy.fetch_lords_government_roles()

            # Convert DataFrames to dicts
            mps_roles = mps_gov_roles.to_dict("records") if hasattr(mps_gov_roles, "to_dict") else mps_gov_roles
            lords_roles = lords_gov_roles.to_dict("records") if hasattr(lords_gov_roles, "to_dict") else lords_gov_roles

            return {
                "mps_government_roles": mps_roles,
                "lords_government_roles": lords_roles,
            }
        except Exception as e:
            logger.error(f"Error scraping government roles: {e!s}")
            raise

    def scrape_committee_memberships(self):
        """Scrape committee memberships"""
        try:
            mps_committees = pdpy.fetch_mps_committee_memberships()
            lords_committees = pdpy.fetch_lords_committee_memberships()

            # Convert DataFrames to dicts
            mps_comm = mps_committees.to_dict("records") if hasattr(mps_committees, "to_dict") else mps_committees
            lords_comm = (
                lords_committees.to_dict("records") if hasattr(lords_committees, "to_dict") else lords_committees
            )

            return {
                "mps_committee_memberships": mps_comm,
                "lords_committee_memberships": lords_comm,
            }
        except Exception as e:
            logger.error(f"Error scraping committee memberships: {e!s}")
            raise

    def scrape_all_data(self):
        """Scrape all available UK government and parliamentary data"""
        try:
            logger.info("Starting comprehensive data scrape")

            # Scrape all data types
            mps = self.scrape_mps()
            lords = self.scrape_lords()
            government_roles = self.scrape_government_roles()
            committees = self.scrape_committee_memberships()

            data = {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "scraper_version": "1.0.0",
                    "data_source": "UK Parliament API via pdpy library",
                },
                "members_of_parliament": mps,
                "house_of_lords": lords,
                "government_roles": government_roles,
                "committee_memberships": committees,
            }

            # Add summary statistics
            data["summary"] = {
                "total_mps": len(mps),
                "total_lords": len(lords),
                "total_mps_gov_roles": len(government_roles.get("mps_government_roles", [])),
                "total_lords_gov_roles": len(government_roles.get("lords_government_roles", [])),
                "total_mps_committee_memberships": len(committees.get("mps_committee_memberships", [])),
                "total_lords_committee_memberships": len(committees.get("lords_committee_memberships", [])),
            }

            self.cache["all"] = data
            self.last_updated = datetime.now()

            logger.info(
                f"Scraping completed. Found {data['summary']['total_mps']} MPs and {data['summary']['total_lords']} Lords",
            )
            return data

        except Exception as e:
            logger.error(f"Error during comprehensive scrape: {e!s}")
            logger.error(traceback.format_exc())
            raise

    def export_to_csv(self, data_type="all"):
        """Export scraped data to CSV files in the outputs folder"""
        try:
            outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
            os.makedirs(outputs_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exported_files = []

            if data_type == "all":
                # Export all data types
                all_data = self.scrape_all_data()

                # Export MPs
                if "members_of_parliament" in all_data:
                    mps_df = pd.DataFrame(all_data["members_of_parliament"])
                    mps_file = os.path.join(outputs_dir, f"uk_mps_{timestamp}.csv")
                    mps_df.to_csv(mps_file, index=False)
                    exported_files.append(mps_file)

                # Export Lords
                if "house_of_lords" in all_data:
                    lords_df = pd.DataFrame(all_data["house_of_lords"])
                    lords_file = os.path.join(outputs_dir, f"uk_lords_{timestamp}.csv")
                    lords_df.to_csv(lords_file, index=False)
                    exported_files.append(lords_file)

                # Export Government Roles
                if "government_roles" in all_data:
                    gov_roles = all_data["government_roles"]
                    if "mps_government_roles" in gov_roles:
                        mps_gov_df = pd.DataFrame(gov_roles["mps_government_roles"])
                        mps_gov_file = os.path.join(outputs_dir, f"uk_mps_government_roles_{timestamp}.csv")
                        mps_gov_df.to_csv(mps_gov_file, index=False)
                        exported_files.append(mps_gov_file)

                    if "lords_government_roles" in gov_roles:
                        lords_gov_df = pd.DataFrame(gov_roles["lords_government_roles"])
                        lords_gov_file = os.path.join(outputs_dir, f"uk_lords_government_roles_{timestamp}.csv")
                        lords_gov_df.to_csv(lords_gov_file, index=False)
                        exported_files.append(lords_gov_file)

                # Export Committee Memberships
                if "committee_memberships" in all_data:
                    committees = all_data["committee_memberships"]
                    if "mps_committee_memberships" in committees:
                        mps_comm_df = pd.DataFrame(committees["mps_committee_memberships"])
                        mps_comm_file = os.path.join(outputs_dir, f"uk_mps_committee_memberships_{timestamp}.csv")
                        mps_comm_df.to_csv(mps_comm_file, index=False)
                        exported_files.append(mps_comm_file)

                    if "lords_committee_memberships" in committees:
                        lords_comm_df = pd.DataFrame(committees["lords_committee_memberships"])
                        lords_comm_file = os.path.join(outputs_dir, f"uk_lords_committee_memberships_{timestamp}.csv")
                        lords_comm_df.to_csv(lords_comm_file, index=False)
                        exported_files.append(lords_comm_file)

            elif data_type == "mps":
                mps_data = self.scrape_mps()
                mps_df = pd.DataFrame(mps_data)
                mps_file = os.path.join(outputs_dir, f"uk_mps_{timestamp}.csv")
                mps_df.to_csv(mps_file, index=False)
                exported_files.append(mps_file)

            elif data_type == "lords":
                lords_data = self.scrape_lords()
                lords_df = pd.DataFrame(lords_data)
                lords_file = os.path.join(outputs_dir, f"uk_lords_{timestamp}.csv")
                lords_df.to_csv(lords_file, index=False)
                exported_files.append(lords_file)

            elif data_type == "government-roles":
                gov_roles_data = self.scrape_government_roles()
                if "mps_government_roles" in gov_roles_data:
                    mps_gov_df = pd.DataFrame(gov_roles_data["mps_government_roles"])
                    mps_gov_file = os.path.join(outputs_dir, f"uk_mps_government_roles_{timestamp}.csv")
                    mps_gov_df.to_csv(mps_gov_file, index=False)
                    exported_files.append(mps_gov_file)

                if "lords_government_roles" in gov_roles_data:
                    lords_gov_df = pd.DataFrame(gov_roles_data["lords_government_roles"])
                    lords_gov_file = os.path.join(outputs_dir, f"uk_lords_government_roles_{timestamp}.csv")
                    lords_gov_df.to_csv(lords_gov_file, index=False)
                    exported_files.append(lords_gov_file)

            elif data_type == "committees":
                committees_data = self.scrape_committee_memberships()
                if "mps_committee_memberships" in committees_data:
                    mps_comm_df = pd.DataFrame(committees_data["mps_committee_memberships"])
                    mps_comm_file = os.path.join(outputs_dir, f"uk_mps_committee_memberships_{timestamp}.csv")
                    mps_comm_df.to_csv(mps_comm_file, index=False)
                    exported_files.append(mps_comm_file)

                if "lords_committee_memberships" in committees_data:
                    lords_comm_df = pd.DataFrame(committees_data["lords_committee_memberships"])
                    lords_comm_file = os.path.join(outputs_dir, f"uk_lords_committee_memberships_{timestamp}.csv")
                    lords_comm_df.to_csv(lords_comm_file, index=False)
                    exported_files.append(lords_comm_file)

            logger.info(f"Exported {len(exported_files)} CSV files to outputs directory")
            return exported_files

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e!s}")
            raise


# Initialize the scraper
scraper = UKGovernmentScraper()


@app.route("/")
def index():
    """Health check and API information endpoint"""
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
def health():
    """Service health check"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "cache_status": "populated" if scraper.cache else "empty",
        },
    )


@app.route("/scrape/all")
def scrape_all():
    """Scrape all UK government members and employees"""
    try:
        # Check if we should use cached data (optional query parameter)
        use_cache = request.args.get("cache", "false").lower() == "true"

        if use_cache and "all" in scraper.cache:
            logger.info("Returning cached data")
            return jsonify(scraper.cache["all"])

        # Perform fresh scrape
        data = scraper.scrape_all_data()
        return jsonify(data)

    except Exception as e:
        logger.error(f"Error in scrape_all endpoint: {e!s}")
        return jsonify(
            {
                "error": "Failed to scrape data",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        ), 500


@app.route("/scrape/mps")
def scrape_mps():
    """Scrape only Members of Parliament from House of Commons"""
    try:
        mps_data = scraper.scrape_mps()
        return jsonify(
            {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "data_type": "Members of Parliament - House of Commons",
                },
                "members_of_parliament": mps_data,
                "summary": {
                    "total_count": len(mps_data),
                    "current_count": len(mps_data),  # All MPs returned are current
                },
            },
        )
    except Exception as e:
        logger.error(f"Error in scrape_mps endpoint: {e!s}")
        return jsonify(
            {
                "error": "Failed to scrape MPs data",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        ), 500


@app.route("/scrape/lords")
def scrape_lords():
    """Scrape only members of House of Lords"""
    try:
        lords_data = scraper.scrape_lords()
        return jsonify(
            {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "data_type": "Members of House of Lords",
                },
                "house_of_lords": lords_data,
                "summary": {
                    "total_count": len(lords_data),
                    "current_count": len(lords_data),  # All Lords returned are current
                },
            },
        )
    except Exception as e:
        logger.error(f"Error in scrape_lords endpoint: {e!s}")
        return jsonify(
            {
                "error": "Failed to scrape Lords data",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        ), 500


@app.route("/scrape/committees")
def scrape_committees():
    """Scrape committee memberships"""
    try:
        committees_data = scraper.scrape_committee_memberships()
        return jsonify(
            {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "data_type": "Committee Memberships",
                },
                "committee_memberships": committees_data,
                "summary": {
                    "total_mps_committee_memberships": len(committees_data.get("mps_committee_memberships", [])),
                    "total_lords_committee_memberships": len(committees_data.get("lords_committee_memberships", [])),
                },
            },
        )
    except Exception as e:
        logger.error(f"Error in scrape_committees endpoint: {e!s}")
        return jsonify(
            {
                "error": "Failed to scrape committees data",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        ), 500


@app.route("/scrape/government-roles")
def scrape_government_roles():
    """Scrape government roles"""
    try:
        gov_roles_data = scraper.scrape_government_roles()
        return jsonify(
            {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "data_type": "Government Roles",
                },
                "government_roles": gov_roles_data,
                "summary": {
                    "total_mps_government_roles": len(gov_roles_data.get("mps_government_roles", [])),
                    "total_lords_government_roles": len(gov_roles_data.get("lords_government_roles", [])),
                },
            },
        )
    except Exception as e:
        logger.error(f"Error in scrape_government_roles endpoint: {e!s}")
        return jsonify(
            {
                "error": "Failed to scrape government roles data",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        ), 500


@app.route("/export/csv", methods=["POST", "GET"])
def export_csv():
    """Export data to CSV files in outputs folder"""
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
                    "timestamp": datetime.now().isoformat(),
                },
            ), 400

        # Export to CSV
        exported_files = scraper.export_to_csv(data_type)

        return jsonify(
            {
                "success": True,
                "message": f"Successfully exported {data_type} data to CSV",
                "data_type": data_type,
                "exported_files": [os.path.basename(f) for f in exported_files],
                "file_count": len(exported_files),
                "output_directory": "outputs/",
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Error in export_csv endpoint: {e!s}")
        return jsonify(
            {
                "error": "Failed to export CSV files",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        ), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "timestamp": datetime.now().isoformat(),
        },
    ), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify(
        {
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat(),
        },
    ), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
