"""
Agent3: Excel Greeting Transformer

Transform Excel files containing student grades into personalized greeting messages
based on performance tiers using celebrity-style personalities.

This package provides:
- Excel file reading and writing
- Greeting generation with personality styles
- Error handling and validation
- Comprehensive logging
"""

import logging

# Configure logging for the package
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = "0.1.0"
__author__ = "Claude Code"
__all__ = ["excel_processor", "greeting_generator"]
