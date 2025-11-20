"""
Agent4: Gmail Draft Creator

Create Gmail draft emails from processed exercise submissions with personalized
greetings and repository URLs.

This package provides:
- Gmail API authentication and draft creation
- Excel file reading and validation
- Email composition with professional formatting
- Comprehensive logging and error handling
"""

import logging

# Configure logging for the package
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = "0.1.0"
__author__ = "Claude Code"
__all__ = ["gmail_client", "email_composer", "excel_reader"]
