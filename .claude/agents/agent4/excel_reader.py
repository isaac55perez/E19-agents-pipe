"""
Excel file reading and validation.

This module reads and validates data from output34.xlsx:
- Parse Excel files
- Validate email addresses
- Extract and validate repository URLs
- Handle errors gracefully
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Tuple

import openpyxl

logger = logging.getLogger(__name__)


class ExcelReader:
    """Read and validate data from Excel files."""

    # Email validation regex
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        return bool(re.match(ExcelReader.EMAIL_REGEX, email.strip()))

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate repository URL format.

        Args:
            url: Repository URL to validate

        Returns:
            True if valid GitHub URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False

        url_str = str(url).strip()
        # Check if it's a GitHub URL
        return (
            'github.com' in url_str.lower() and
            ('http://' in url_str or 'https://' in url_str)
        )

    @staticmethod
    def read_input_file(file_path: Path) -> Tuple[List[Dict], List[str]]:
        """
        Read input Excel file with entry data.

        Args:
            file_path: Path to input Excel file

        Returns:
            Tuple of (rows_data, headers)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid or missing required columns
        """
        if not file_path.exists():
            logger.error(f"Input file not found: {file_path}")
            raise FileNotFoundError(f"Input file not found: {file_path}")

        try:
            workbook = openpyxl.load_workbook(file_path)
            worksheet = workbook.active

            if worksheet is None:
                raise ValueError("No active worksheet found")

            # Read headers
            headers = []
            for cell in worksheet[1]:
                if cell.value is None:
                    break
                headers.append(cell.value)

            if not headers:
                logger.warning("No headers found in input file")
                return [], []

            logger.info(f"Found headers: {headers}")

            # Verify required columns - check for Repo URL and greeting at minimum
            # Email and name are optional if Subject column exists
            required_columns = ['Repo URL', 'greeting']
            missing_columns = [col for col in required_columns if col not in headers]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # Read data rows
            rows_data = []
            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=False), start=2):
                row_data = {}
                has_data = False

                for header, cell in zip(headers, row[:len(headers)]):
                    value = cell.value
                    row_data[header] = value
                    if value is not None:
                        has_data = True

                if has_data:
                    rows_data.append(row_data)

            logger.info(f"Read {len(rows_data)} data rows from {file_path}")
            workbook.close()
            return rows_data, headers

        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {e}")
            raise

    @staticmethod
    def validate_entries(rows_data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate entries and separate valid from invalid.

        Args:
            rows_data: List of row dictionaries

        Returns:
            Tuple of (valid_entries, invalid_entries)
        """
        valid_entries = []
        invalid_entries = []

        for idx, row in enumerate(rows_data, start=2):
            errors = []

            # For email: try to use email column, fall back to extracting from Subject
            email = row.get('email')
            if not email:
                # Try to extract email from Subject or other fields if available
                subject = row.get('Subject')
                if subject:
                    # Subject might contain email-like info, but we'll mark as missing
                    errors.append("Missing email address")
                else:
                    errors.append("Missing email address")
            elif not ExcelReader.validate_email(email):
                errors.append(f"Invalid email format: {email}")

            # For name: use 'name' field, or fall back to Subject
            name = row.get('name')
            if not name:
                # Use Subject as fallback for name
                subject = row.get('Subject')
                if not subject:
                    errors.append("Missing name (no 'name' or 'Subject' column)")

            # Validate repo URL (required)
            repo_url = row.get('Repo URL')
            if not repo_url:
                errors.append("Missing repository URL")
            elif not ExcelReader.validate_url(repo_url):
                errors.append(f"Invalid repository URL: {repo_url}")

            # Validate greeting (required)
            greeting = row.get('greeting')
            if not greeting:
                errors.append("Missing greeting message")

            # Add to appropriate list
            if errors:
                invalid_entries.append({
                    'row_index': idx,
                    'data': row,
                    'errors': errors
                })
                logger.warning(f"Row {idx} validation failed: {'; '.join(errors)}")
            else:
                valid_entries.append(row)
                logger.debug(f"Row {idx} validated successfully")

        logger.info(f"Validation complete: {len(valid_entries)} valid, {len(invalid_entries)} invalid")
        return valid_entries, invalid_entries
