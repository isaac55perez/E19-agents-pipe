"""
Email Extraction and Excel Generation Module

This module handles the core functionality of extracting emails from Gmail,
parsing GitHub URLs, and generating structured Excel reports.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    """Data class representing extracted email information."""
    date: str
    subject: str
    body: str


@dataclass
class ExcelRow:
    """Data class representing a row to be written to Excel."""
    id: int
    date: str
    subject: str
    repo_url: str
    success: int


class URLValidator:
    """Validates GitHub repository URLs."""

    GITHUB_URL_PATTERN = r'https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+'

    @staticmethod
    def is_valid_github_url(url: str) -> bool:
        """
        Validate if a URL is a valid GitHub repository URL.

        Args:
            url: The URL string to validate

        Returns:
            True if URL matches GitHub pattern, False otherwise
        """
        logger.debug(f"Validating URL: {url}")
        if not url:
            return False

        match = re.match(URLValidator.GITHUB_URL_PATTERN, url)
        is_valid = match is not None
        logger.debug(f"URL validation result: {is_valid}")
        return is_valid


class GitHubURLExtractor:
    """Extracts GitHub URLs from email content."""

    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'

    @staticmethod
    def extract_urls(content: str) -> List[str]:
        """
        Extract all URLs from email content.

        Args:
            content: Email body content

        Returns:
            List of found URLs
        """
        logger.debug(f"Extracting URLs from content (length: {len(content)} chars)")
        urls = re.findall(GitHubURLExtractor.URL_PATTERN, content)
        logger.debug(f"Found {len(urls)} URLs")
        return urls

    @staticmethod
    def extract_github_url(content: str) -> Optional[str]:
        """
        Extract the first valid GitHub URL from email content.

        Args:
            content: Email body content

        Returns:
            First valid GitHub URL or None
        """
        logger.info("Extracting GitHub URL from email content")
        urls = GitHubURLExtractor.extract_urls(content)

        for url in urls:
            if URLValidator.is_valid_github_url(url):
                logger.info(f"Found valid GitHub URL: {url}")
                return url

        logger.warning("No valid GitHub URL found in email content")
        return None


class DateFormatter:
    """Handles date formatting for Excel output."""

    @staticmethod
    def format_date(date_str: str) -> str:
        """
        Format date string to MM/DD/YYYY format.

        Args:
            date_str: Original date string from email

        Returns:
            Formatted date string in MM/DD/YYYY format
        """
        logger.debug(f"Formatting date: {date_str}")
        try:
            # Clean up the date string - remove timezone and extra info
            # Remove text after + (timezone offset)
            clean_date = date_str.split('+')[0]
            # Remove text after ( (timezone name)
            clean_date = clean_date.split('(')[0].strip()

            # Try common email date formats
            formats = [
                '%a, %d %b %Y %H:%M:%S',      # RFC 2822: Mon, 15 Nov 2021 10:30:00
                '%a, %d %b %Y',                # Mon, 15 Nov 2021
                '%Y-%m-%d %H:%M:%S',           # 2021-11-15 10:30:00
                '%Y-%m-%d',                    # 2021-11-15
                '%m/%d/%Y',                    # 11/15/2021
                '%d/%m/%Y',                    # 15/11/2021
                '%d %b %Y %H:%M:%S',          # 15 Nov 2021 10:30:00
                '%d %b %Y',                    # 15 Nov 2021
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(clean_date, fmt)
                    formatted = dt.strftime('%m/%d/%Y')
                    logger.debug(f"Successfully formatted date: {formatted}")
                    return formatted
                except ValueError:
                    continue

            # If no format matched, return as-is with warning
            logger.warning(f"Could not parse date format: {date_str}, returning as-is")
            return date_str
        except Exception as e:
            logger.error(f"Error formatting date: {e}")
            return date_str


class ExcelGenerator:
    """Generates Excel files with extracted email data."""

    def __init__(self, output_path: Path):
        """
        Initialize the Excel generator.

        Args:
            output_path: Path where Excel file will be saved
        """
        self.output_path = output_path
        logger.info(f"Excel generator initialized with output path: {output_path}")

    def generate(self, rows: List[ExcelRow]) -> bool:
        """
        Generate Excel file with extracted data.

        Args:
            rows: List of ExcelRow objects to write

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Generating Excel file with {len(rows)} rows")

        try:
            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "Exercises"

            # Write header row
            headers = ["ID", "Date", "Subject", "Repo URL", "Success"]
            ws.append(headers)
            logger.debug("Header row written to Excel")

            # Write data rows
            for row in rows:
                ws.append([row.id, row.date, row.subject, row.repo_url, row.success])

            logger.info(f"Writing {len(rows)} data rows to Excel")

            # Adjust column widths
            ws.column_dimensions['A'].width = 8
            ws.column_dimensions['B'].width = 12
            ws.column_dimensions['C'].width = 50
            ws.column_dimensions['D'].width = 60
            ws.column_dimensions['E'].width = 10

            # Ensure output directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save workbook
            wb.save(self.output_path)
            logger.info(f"Excel file successfully saved to: {self.output_path}")
            return True

        except ImportError:
            logger.error("openpyxl library not installed. Install with: pip install openpyxl")
            return False
        except Exception as e:
            logger.error(f"Error generating Excel file: {e}", exc_info=True)
            return False


class EmailProcessor:
    """Main processor for email extraction and Excel generation."""

    def __init__(self, output_dir: str = "output"):
        """
        Initialize the email processor.

        Args:
            output_dir: Directory where output files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_file = self.output_dir / "output12.xlsx"
        logger.info(f"EmailProcessor initialized with output dir: {output_dir}")

    def process_emails(self, emails: List[EmailData]) -> Tuple[List[ExcelRow], Dict[str, any]]:
        """
        Process a list of emails and extract data.

        Args:
            emails: List of EmailData objects

        Returns:
            Tuple of (processed rows, summary statistics)
        """
        logger.info(f"Processing {len(emails)} emails")

        rows: List[ExcelRow] = []
        stats = {
            'total_emails': len(emails),
            'entries_created': 0,
            'urls_found': 0,
            'errors': []
        }

        for idx, email in enumerate(emails, 1):
            try:
                logger.debug(f"Processing email {idx}/{len(emails)}")

                # Format date
                formatted_date = DateFormatter.format_date(email.date)

                # Extract GitHub URL
                github_url = GitHubURLExtractor.extract_github_url(email.body)
                success = 1 if github_url else 0

                if success:
                    stats['urls_found'] += 1

                # Create row
                row = ExcelRow(
                    id=idx,
                    date=formatted_date,
                    subject=email.subject,
                    repo_url=github_url or "",
                    success=success
                )
                rows.append(row)
                stats['entries_created'] += 1

                logger.debug(f"Email {idx} processed successfully")

            except Exception as e:
                logger.error(f"Error processing email {idx}: {e}", exc_info=True)
                stats['errors'].append(f"Email {idx}: {str(e)}")

        logger.info(f"Email processing complete. Entries created: {stats['entries_created']}, "
                   f"URLs found: {stats['urls_found']}")
        return rows, stats

    def generate_report(self, rows: List[ExcelRow], stats: Dict) -> bool:
        """
        Generate Excel report from processed data.

        Args:
            rows: List of processed rows
            stats: Summary statistics

        Returns:
            True if successful, False otherwise
        """
        logger.info("Generating Excel report")

        generator = ExcelGenerator(self.output_file)
        success = generator.generate(rows)

        if success:
            logger.info(f"Report successfully generated at: {self.output_file}")
        else:
            logger.error("Failed to generate Excel report")

        return success

    def get_summary(self, stats: Dict) -> str:
        """
        Generate a summary report of the processing.

        Args:
            stats: Summary statistics

        Returns:
            Formatted summary string
        """
        logger.info("Generating summary report")

        summary = (
            f"Email Extraction Summary:\n"
            f"  Total emails extracted: {stats['total_emails']}\n"
            f"  Total entries created: {stats['entries_created']}\n"
            f"  Successful URL detections: {stats['urls_found']}\n"
            f"  File path: {self.output_file}\n"
        )

        if stats['errors']:
            summary += f"  Errors encountered: {len(stats['errors'])}\n"
            for error in stats['errors']:
                summary += f"    - {error}\n"

        return summary
