"""
Agent4: Gmail Draft Creator - Main entry point.

Orchestrates the workflow of reading exercise submissions and creating Gmail drafts.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from excel_reader import ExcelReader
from email_composer import EmailComposer
from gmail_client import GmailAuthenticator, GmailDraftCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Create Gmail draft emails from exercise submissions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create drafts for all entries
  python main.py

  # Dry run (show what would be created)
  python main.py --dry-run

  # Custom input file
  python main.py --input /path/to/input.xlsx

  # Verbose logging
  python main.py --verbose

  # Limit to 10 entries
  python main.py --limit 10

  # Custom delay between API calls (seconds)
  python main.py --delay 2
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        default='output/output34.xlsx',
        help='Input Excel file (default: output/output34.xlsx)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output report file (optional, for dry-run summary)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without calling Gmail API'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Process only first N entries (for testing)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Delay between API calls in seconds (default: 0.5)'
    )

    return parser.parse_args()


def print_header(title: str) -> None:
    """
    Print a formatted header.

    Args:
        title: Header title
    """
    width = 60
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def run_workflow(
    input_file: str,
    dry_run: bool = False,
    limit: Optional[int] = None,
    delay: float = 0.5
) -> dict:
    """
    Run the complete Gmail draft creation workflow.

    Args:
        input_file: Path to input Excel file
        dry_run: If True, don't create drafts, just show summary
        limit: Maximum number of entries to process
        delay: Delay between API calls in seconds

    Returns:
        Dictionary with workflow results
    """
    results = {
        'success': False,
        'total_entries': 0,
        'valid_entries': 0,
        'invalid_entries': 0,
        'drafts_created': 0,
        'drafts_failed': 0,
        'errors': [],
        'skipped_entries': []
    }

    try:
        # Step 1: Read input file
        logger.info(f"Reading input file: {input_file}")

        # Resolve path relative to project root
        input_path = Path(input_file)
        if not input_path.is_absolute():
            # If relative path, resolve from project root (3 levels up from this file)
            project_root = Path(__file__).parent.parent.parent.parent
            input_path = project_root / input_file

        logger.debug(f"Resolved input file path: {input_path}")
        input_path = input_path

        try:
            rows_data, headers = ExcelReader.read_input_file(input_path)
            logger.info(f"Read {len(rows_data)} entries from {input_file}")
            results['total_entries'] = len(rows_data)
        except FileNotFoundError as e:
            logger.error(f"Input file not found: {e}")
            results['errors'].append(f"Input file not found: {input_file}")
            return results
        except ValueError as e:
            logger.error(f"Invalid Excel file: {e}")
            results['errors'].append(f"Invalid Excel file: {str(e)}")
            return results

        # Step 2: Validate entries
        logger.info("Validating entries...")
        valid_entries, invalid_entries = ExcelReader.validate_entries(rows_data)
        logger.info(f"Validation complete: {len(valid_entries)} valid, {len(invalid_entries)} invalid")
        results['valid_entries'] = len(valid_entries)
        results['invalid_entries'] = len(invalid_entries)

        # Log invalid entries
        for invalid in invalid_entries:
            error_msg = f"Row {invalid['row_index']}: {'; '.join(invalid['errors'])}"
            logger.warning(error_msg)
            results['skipped_entries'].append({
                'email': invalid['data'].get('email', 'unknown'),
                'reason': error_msg
            })

        # Apply limit if specified
        entries_to_process = valid_entries
        if limit and limit > 0:
            entries_to_process = valid_entries[:limit]
            if len(valid_entries) > limit:
                logger.info(f"Limiting to first {limit} entries (total valid: {len(valid_entries)})")

        # Step 3: Authenticate Gmail (skip if dry-run)
        authenticator = GmailAuthenticator()
        if not dry_run:
            logger.info("Authenticating with Gmail API...")
            if not authenticator.authenticate():
                logger.error("Gmail authentication failed")
                results['errors'].append("Gmail authentication failed")
                return results
            logger.info("Successfully authenticated with Gmail API")

        # Step 4: Create drafts
        logger.info(f"Creating Gmail drafts for {len(entries_to_process)} entries...")
        draft_creator = GmailDraftCreator(authenticator)

        # Set custom delay if provided
        if delay != GmailDraftCreator.API_CALL_DELAY:
            draft_creator.API_CALL_DELAY = delay
            logger.debug(f"Using custom API call delay: {delay}s")

        # Create drafts batch
        batch_results = draft_creator.create_drafts_batch(
            entries=entries_to_process,
            dry_run=dry_run
        )

        results['drafts_created'] = batch_results['successful']
        results['drafts_failed'] = batch_results['failed']

        # Log individual results
        for result in batch_results['results']:
            if result['success']:
                logger.info(f"Draft created for {result['email']}: {result['draft_id']}")
            else:
                logger.error(f"Failed to create draft for {result['email']}: {result['message']}")

        # Log any errors from batch
        for error in batch_results['errors']:
            results['errors'].append(f"{error['email']}: {error['error']}")

        results['success'] = True
        return results

    except Exception as e:
        logger.error(f"Workflow error: {e}", exc_info=True)
        results['errors'].append(f"Unexpected error: {str(e)}")
        return results


def print_summary(results: dict, dry_run: bool = False) -> None:
    """
    Print workflow completion summary.

    Args:
        results: Dictionary with workflow results
        dry_run: Whether this was a dry-run
    """
    print_header("COMPLETION SUMMARY")

    print(f"Status: {'✓ SUCCESS' if results['success'] else '✗ FAILED'}")
    print(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
    print()

    print("Processing Statistics:")
    print(f"  Total entries read: {results['total_entries']}")
    print(f"  Valid entries: {results['valid_entries']}")
    print(f"  Invalid entries: {results['invalid_entries']}")
    print()

    print("Draft Creation:")
    print(f"  Drafts created: {results['drafts_created']}")
    print(f"  Drafts failed: {results['drafts_failed']}")

    if results['total_entries'] > 0:
        success_rate = (results['drafts_created'] / results['valid_entries'] * 100) if results['valid_entries'] > 0 else 0
        print(f"  Success rate: {success_rate:.1f}%")
    print()

    if results['skipped_entries']:
        print(f"Skipped Entries ({len(results['skipped_entries'])}):")
        for skipped in results['skipped_entries'][:5]:  # Show first 5
            print(f"  - {skipped['email']}: {skipped['reason'][:50]}...")
        if len(results['skipped_entries']) > 5:
            print(f"  ... and {len(results['skipped_entries']) - 5} more")
        print()

    if results['errors']:
        print(f"Errors ({len(results['errors'])}):")
        for error in results['errors'][:5]:  # Show first 5
            print(f"  - {error[:70]}...")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more")
        print()

    print("=" * 60)


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_arguments()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    print_header("Gmail Draft Creator - Agent4")
    logger.info("Starting Gmail draft creation workflow")
    logger.info(f"Input file: {args.input}")

    if args.dry_run:
        logger.info("DRY RUN MODE - No Gmail API calls will be made")

    if args.limit:
        logger.info(f"Processing limited to first {args.limit} entries")

    # Run workflow
    results = run_workflow(
        input_file=args.input,
        dry_run=args.dry_run,
        limit=args.limit,
        delay=args.delay
    )

    # Print summary
    print()
    print_summary(results, dry_run=args.dry_run)

    return 0 if results['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
