"""Configuration settings for the UK Government Scraper."""

import os


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Flask settings
    DEBUG = False
    TESTING = False

    # API settings
    API_RATE_LIMIT = os.environ.get("API_RATE_LIMIT", "1000 per hour")

    # Cache settings
    CACHE_TIMEOUT = int(os.environ.get("CACHE_TIMEOUT", "3600"))  # 1 hour default

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Request timeout for external APIs
    REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "30"))


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    LOG_LEVEL = "INFO"

    # Use environment variables for sensitive settings
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production")


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    CACHE_TIMEOUT = 0  # No caching in tests


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
