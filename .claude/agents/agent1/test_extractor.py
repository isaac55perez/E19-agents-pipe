"""
Unit tests for the Email Extraction and Excel Generation Module

Tests cover:
- URL validation and extraction
- Date formatting
- Email processing
- Excel generation
- Error handling
"""

import pytest
import logging
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from extractor import (
    URLValidator,
    GitHubURLExtractor,
    DateFormatter,
    ExcelGenerator,
    EmailProcessor,
    EmailData,
    ExcelRow
)

# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestURLValidator:
    """Test cases for URL validation."""

    def test_valid_github_url(self):
        """Test validation of a valid GitHub URL."""
        url = "https://github.com/user/repo"
        assert URLValidator.is_valid_github_url(url) is True

    def test_valid_github_url_with_www(self):
        """Test validation of a valid GitHub URL with www."""
        url = "https://www.github.com/user/repo"
        assert URLValidator.is_valid_github_url(url) is True

    def test_valid_github_url_http(self):
        """Test validation of a valid GitHub URL with http."""
        url = "http://github.com/user/repo"
        assert URLValidator.is_valid_github_url(url) is True

    def test_valid_github_url_with_hyphens(self):
        """Test validation of GitHub URL with hyphens in names."""
        url = "https://github.com/user-name/repo-name"
        assert URLValidator.is_valid_github_url(url) is True

    def test_invalid_github_url_missing_repo(self):
        """Test rejection of GitHub URL without repo name."""
        url = "https://github.com/user/"
        assert URLValidator.is_valid_github_url(url) is False

    def test_invalid_github_url_missing_user(self):
        """Test rejection of GitHub URL without user name."""
        url = "https://github.com/"
        assert URLValidator.is_valid_github_url(url) is False

    def test_invalid_non_github_url(self):
        """Test rejection of non-GitHub URLs."""
        url = "https://gitlab.com/user/repo"
        assert URLValidator.is_valid_github_url(url) is False

    def test_invalid_empty_string(self):
        """Test rejection of empty string."""
        assert URLValidator.is_valid_github_url("") is False

    def test_invalid_none(self):
        """Test rejection of None."""
        assert URLValidator.is_valid_github_url(None) is False


class TestGitHubURLExtractor:
    """Test cases for GitHub URL extraction."""

    def test_extract_urls_from_email_body(self):
        """Test extraction of multiple URLs from email body."""
        content = "Check out https://github.com/user/repo and https://google.com"
        urls = GitHubURLExtractor.extract_urls(content)
        assert len(urls) == 2
        assert "https://github.com/user/repo" in urls

    def test_extract_single_github_url(self):
        """Test extraction of single valid GitHub URL."""
        content = "Here is the repository: https://github.com/user/repo"
        url = GitHubURLExtractor.extract_github_url(content)
        assert url == "https://github.com/user/repo"

    def test_extract_no_github_url(self):
        """Test extraction when no GitHub URL exists."""
        content = "No URLs here, just text"
        url = GitHubURLExtractor.extract_github_url(content)
        assert url is None

    def test_extract_github_url_with_trailing_text(self):
        """Test extraction of GitHub URL with trailing text."""
        content = "My repo: https://github.com/user/repo - please review"
        url = GitHubURLExtractor.extract_github_url(content)
        assert url == "https://github.com/user/repo"

    def test_extract_from_empty_content(self):
        """Test extraction from empty content."""
        content = ""
        url = GitHubURLExtractor.extract_github_url(content)
        assert url is None

    def test_extract_first_github_url_when_multiple(self):
        """Test extraction returns first valid GitHub URL."""
        content = "First: https://github.com/user1/repo1 and Second: https://github.com/user2/repo2"
        url = GitHubURLExtractor.extract_github_url(content)
        assert url == "https://github.com/user1/repo1"


class TestDateFormatter:
    """Test cases for date formatting."""

    def test_format_rfc2822_date(self):
        """Test formatting of RFC 2822 email date."""
        date_str = "Mon, 15 Nov 2021 10:30:00 +0000"
        formatted = DateFormatter.format_date(date_str)
        assert formatted == "11/15/2021"

    def test_format_iso_date(self):
        """Test formatting of ISO date format."""
        date_str = "2021-11-15"
        formatted = DateFormatter.format_date(date_str)
        assert formatted == "11/15/2021"

    def test_format_slash_date(self):
        """Test formatting of slash-separated date."""
        date_str = "11/15/2021"
        formatted = DateFormatter.format_date(date_str)
        assert formatted == "11/15/2021"

    def test_format_invalid_date(self):
        """Test formatting of unrecognized date format."""
        date_str = "invalid-date"
        formatted = DateFormatter.format_date(date_str)
        # Should return as-is when format can't be determined
        assert formatted is not None

    def test_format_date_with_timezone(self):
        """Test formatting of date with timezone info."""
        date_str = "Mon, 15 Nov 2021 10:30:00 (EST)"
        formatted = DateFormatter.format_date(date_str)
        assert formatted == "11/15/2021"


class TestExcelGenerator:
    """Test cases for Excel file generation."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_generate_excel_with_data(self, temp_dir):
        """Test generation of Excel file with data."""
        output_path = Path(temp_dir) / "test_output.xlsx"
        generator = ExcelGenerator(output_path)

        rows = [
            ExcelRow(1, "11/15/2021", "Exercise 1", "https://github.com/user/repo1", 1),
            ExcelRow(2, "11/16/2021", "Exercise 2", "", 0),
        ]

        success = generator.generate(rows)
        assert success is True
        assert output_path.exists()

    def test_generate_excel_empty_data(self, temp_dir):
        """Test generation of Excel file with no data rows."""
        output_path = Path(temp_dir) / "test_output.xlsx"
        generator = ExcelGenerator(output_path)

        rows = []
        success = generator.generate(rows)
        assert success is True
        assert output_path.exists()

    def test_generate_excel_creates_directory(self, temp_dir):
        """Test that generator creates output directory if it doesn't exist."""
        output_path = Path(temp_dir) / "nested" / "dir" / "test_output.xlsx"
        generator = ExcelGenerator(output_path)

        rows = [ExcelRow(1, "11/15/2021", "Test", "https://github.com/user/repo", 1)]
        success = generator.generate(rows)

        assert success is True
        assert output_path.exists()
        assert output_path.parent.exists()


class TestEmailProcessor:
    """Test cases for email processing."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_process_single_email_with_url(self, temp_dir):
        """Test processing a single email with GitHub URL."""
        processor = EmailProcessor(output_dir=temp_dir)

        emails = [
            EmailData(
                date="Mon, 15 Nov 2021 10:30:00 +0000",
                subject="Exercise 1",
                body="Check out my repo: https://github.com/user/repo"
            )
        ]

        rows, stats = processor.process_emails(emails)

        assert len(rows) == 1
        assert stats['total_emails'] == 1
        assert stats['entries_created'] == 1
        assert stats['urls_found'] == 1
        assert rows[0].repo_url == "https://github.com/user/repo"
        assert rows[0].success == 1

    def test_process_email_without_url(self, temp_dir):
        """Test processing email without GitHub URL."""
        processor = EmailProcessor(output_dir=temp_dir)

        emails = [
            EmailData(
                date="Mon, 15 Nov 2021 10:30:00 +0000",
                subject="Exercise 2",
                body="No repository link provided"
            )
        ]

        rows, stats = processor.process_emails(emails)

        assert len(rows) == 1
        assert stats['urls_found'] == 0
        assert rows[0].success == 0
        assert rows[0].repo_url == ""

    def test_process_multiple_emails(self, temp_dir):
        """Test processing multiple emails."""
        processor = EmailProcessor(output_dir=temp_dir)

        emails = [
            EmailData("Mon, 15 Nov 2021 10:30:00 +0000", "Ex1", "https://github.com/user/repo1"),
            EmailData("Tue, 16 Nov 2021 10:30:00 +0000", "Ex2", "No URL here"),
            EmailData("Wed, 17 Nov 2021 10:30:00 +0000", "Ex3", "https://github.com/user/repo3"),
        ]

        rows, stats = processor.process_emails(emails)

        assert len(rows) == 3
        assert stats['total_emails'] == 3
        assert stats['entries_created'] == 3
        assert stats['urls_found'] == 2
        assert rows[0].id == 1
        assert rows[1].id == 2
        assert rows[2].id == 3

    def test_generate_report(self, temp_dir):
        """Test Excel report generation."""
        processor = EmailProcessor(output_dir=temp_dir)

        emails = [
            EmailData("Mon, 15 Nov 2021 10:30:00 +0000", "Ex1", "https://github.com/user/repo1"),
        ]

        rows, stats = processor.process_emails(emails)
        success = processor.generate_report(rows, stats)

        assert success is True
        assert (Path(temp_dir) / "output12.xlsx").exists()

    def test_get_summary(self, temp_dir):
        """Test summary report generation."""
        processor = EmailProcessor(output_dir=temp_dir)

        stats = {
            'total_emails': 3,
            'entries_created': 3,
            'urls_found': 2,
            'errors': ['Email 2: Some error']
        }

        summary = processor.get_summary(stats)

        assert "3" in summary
        assert "2" in summary
        assert "output12.xlsx" in summary
        assert "Errors encountered: 1" in summary

    def test_empty_email_list(self, temp_dir):
        """Test processing of empty email list."""
        processor = EmailProcessor(output_dir=temp_dir)

        emails = []
        rows, stats = processor.process_emails(emails)

        assert len(rows) == 0
        assert stats['total_emails'] == 0
        assert stats['entries_created'] == 0
        assert stats['urls_found'] == 0


class TestIntegration:
    """Integration tests for complete workflow."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_full_workflow(self, temp_dir):
        """Test complete email extraction and Excel generation workflow."""
        processor = EmailProcessor(output_dir=temp_dir)

        # Create test emails
        emails = [
            EmailData(
                date="Mon, 15 Nov 2021 10:30:00 +0000",
                subject="Homework 1",
                body="Here is my work: https://github.com/student1/hw1-solution"
            ),
            EmailData(
                date="Tue, 16 Nov 2021 11:00:00 +0000",
                subject="Homework 2",
                body="Please check my code at https://www.github.com/student2/hw2"
            ),
            EmailData(
                date="Wed, 17 Nov 2021 09:30:00 +0000",
                subject="Homework 3",
                body="I couldn't complete this one"
            ),
        ]

        # Process emails
        rows, stats = processor.process_emails(emails)
        logger.info(f"Processing stats: {stats}")

        # Generate report
        success = processor.generate_report(rows, stats)
        logger.info(f"Report generation success: {success}")

        # Get summary
        summary = processor.get_summary(stats)
        logger.info(f"Summary:\n{summary}")

        # Verify results
        assert success is True
        assert (Path(temp_dir) / "output12.xlsx").exists()
        assert stats['total_emails'] == 3
        assert stats['entries_created'] == 3
        assert stats['urls_found'] == 2
        assert len(stats['errors']) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
