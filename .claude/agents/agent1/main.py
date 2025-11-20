#!/usr/bin/env python
"""
Gmail Exercise Extractor Agent Runner

This script extracts exercise submission emails from Gmail and generates
an Excel report with GitHub repository URLs.
"""

import logging
import sys
from pathlib import Path

from extractor import EmailProcessor, EmailData
from gmail_connector import GmailExerciseExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_with_gmail(use_real_gmail: bool = True, max_emails: int = 100):
    """
    Run the Gmail Exercise Extractor agent.

    Args:
        use_real_gmail: If True, fetch from real Gmail; if False, use sample data
        max_emails: Maximum number of emails to fetch from Gmail
    """
    logger.info("=" * 80)
    logger.info("Gmail Exercise Extractor Agent")
    logger.info("=" * 80)

    # Get project root (4 levels up from agent1 directory)
    project_root = Path(__file__).parent.parent.parent.parent

    # Create output directory relative to project root
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    # Initialize the email processor
    processor = EmailProcessor(output_dir=str(output_dir))

    # Fetch emails from Gmail
    if use_real_gmail:
        logger.info("Fetching emails from Gmail...")
        extractor = GmailExerciseExtractor()

        # Setup authentication with Gmail
        if not extractor.setup():
            logger.error("Failed to authenticate with Gmail. Falling back to sample data.")
            emails = _get_sample_emails()
        else:
            # Extract exercises from Gmail
            emails = extractor.extract_exercises(label_name="exercises", max_results=max_emails)

            if not emails:
                logger.warning("No emails found in Gmail 'exercises' folder. Using sample data.")
                emails = _get_sample_emails()
    else:
        logger.info("Using sample emails for demonstration...")
        emails = _get_sample_emails()

    logger.info(f"Processing {len(emails)} emails...")

    # Process the emails
    rows, stats = processor.process_emails(emails)

    logger.info(f"Email processing complete:")
    logger.info(f"  - Entries created: {stats['entries_created']}")
    logger.info(f"  - URLs found: {stats['urls_found']}")

    if stats['errors']:
        logger.warning(f"  - Errors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            logger.warning(f"    * {error}")

    # Generate the Excel report
    logger.info("Generating Excel report...")
    success = processor.generate_report(rows, stats)

    if success:
        logger.info(f"Excel report successfully created at: {processor.output_file}")
    else:
        logger.error("Failed to generate Excel report")
        return 1

    # Print the summary
    summary = processor.get_summary(stats)
    logger.info("\n" + "=" * 80)
    logger.info("Processing Summary:")
    logger.info("=" * 80)
    logger.info(summary)

    # Verify file exists and print file info
    if processor.output_file.exists():
        file_size = processor.output_file.stat().st_size
        logger.info(f"Output file size: {file_size} bytes")
        logger.info("=" * 80)
        return 0
    else:
        logger.error("Output file was not created!")
        return 1


def _get_sample_emails():
    """
    Get sample email data for testing.

    Returns:
        List of sample EmailData objects
    """
    return [
        EmailData(
            date="Mon, 15 Nov 2021 10:30:00 +0000",
            subject="Exercise 1 - Python Basics",
            body="""
            Hi Professor,

            I've completed the Python basics exercise. You can find my solution at:
            https://github.com/student1/python-basics-solution

            Looking forward to your feedback!
            """
        ),
        EmailData(
            date="Tue, 16 Nov 2021 11:00:00 +0000",
            subject="Exercise 2 - Data Structures",
            body="""
            Hello,

            Here's my implementation of the data structures problem:
            https://www.github.com/student2/data-structures-hw

            Please let me know if you have any questions.
            """
        ),
        EmailData(
            date="Wed, 17 Nov 2021 09:30:00 +0000",
            subject="Exercise 3 - Algorithms",
            body="""
            I wasn't able to complete this exercise by the deadline.
            I'll submit it as soon as possible.
            """
        ),
        EmailData(
            date="Thu, 18 Nov 2021 14:15:00 +0000",
            subject="Exercise 4 - Advanced Python",
            body="""
            My solution for the advanced Python exercise:
            https://github.com/student4/advanced-python-solution

            I implemented additional optimizations as extra credit.
            """
        ),
    ]


if __name__ == "__main__":
    try:
        # Run with real Gmail (set to False to use sample data)
        use_gmail = True
        exit_code = run_with_gmail(use_real_gmail=use_gmail, max_emails=100)
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
