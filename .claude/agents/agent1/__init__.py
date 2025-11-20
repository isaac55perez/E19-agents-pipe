"""
Gmail Exercise Extractor Agent

This module implements the email-to-Excel conversion specialist agent that extracts
exercise-related emails from a Gmail folder and transforms them into a structured
Excel file with quality assurance.

Package provides:
- Email extraction from Gmail
- GitHub URL parsing and validation
- Excel file generation with metadata
- Comprehensive error handling and logging
"""

__version__ = "0.1.0"
__author__ = "Agent Development Team"

import logging

# Configure logging for this package
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Gmail Exercise Extractor Agent initialized")
