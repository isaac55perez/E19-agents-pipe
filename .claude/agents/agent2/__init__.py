"""
Repository Python Analyzer Agent

This module implements the repository analysis specialist agent that processes Python
repositories from a spreadsheet, analyzes code metrics, and generates quality grades
based on Python file size distribution.

Package provides:
- Repository cloning and management
- Python file detection and line counting
- Grade calculation based on file size metrics
- Multi-threaded concurrent processing
- Excel file generation with results
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
logger.info("Repository Python Analyzer Agent initialized")
