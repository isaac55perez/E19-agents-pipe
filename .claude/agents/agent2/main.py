#!/usr/bin/env python3
"""
Standalone runner for the Repository Python Analyzer Agent.

This script can be invoked directly to analyze repositories and generate
a grading report based on Python file size distribution.

Usage:
    python main.py                          # Uses default input/output paths
    python main.py --input <path>           # Custom input file
    python main.py --output <path>          # Custom output file
    python main.py --workers <num>          # Custom number of worker threads
    python main.py --help                   # Show help message
"""

import argparse
import logging
import sys
from pathlib import Path

from extractor import RepositoryAnalysisOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Repository Python Analyzer Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --input custom_input.xlsx --output results.xlsx
  python main.py --workers 8
  python main.py --verbose
        """
    )

    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to input Excel file (default: output/output12.xlsx)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output Excel file (default: output/output23.xlsx)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of concurrent worker threads (default: 4, recommended: 4-8)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)"
    )

    return parser.parse_args()


def main():
    """Main entry point for the analyzer."""
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    # Get project root (directory containing this script's parent)
    project_root = Path(__file__).parent.parent.parent.parent

    logger.info("=" * 60)
    logger.info("Repository Python Analyzer Agent")
    logger.info("=" * 60)

    # Create orchestrator
    logger.info(f"Configuration:")
    logger.info(f"  Project root: {project_root}")
    logger.info(f"  Input file: {args.input or 'default (output/output12.xlsx)'}")
    logger.info(f"  Output file: {args.output or 'default (output/output23.xlsx)'}")
    logger.info(f"  Worker threads: {args.workers}")
    logger.info("")

    try:
        orchestrator = RepositoryAnalysisOrchestrator(
            input_file=Path(args.input) if args.input else None,
            output_file=Path(args.output) if args.output else None,
            max_workers=args.workers,
            project_root=project_root
        )

        # Run the analysis
        success, result = orchestrator.run()

        # Print results
        logger.info("")
        logger.info("=" * 60)
        logger.info("Analysis Results")
        logger.info("=" * 60)
        logger.info(f"Total entries: {result.total_entries}")
        logger.info(f"Successful: {result.successful}")
        logger.info(f"Failed: {result.failed}")
        logger.info(f"Success rate: {result.success_rate():.1f}%")
        logger.info(f"Processing time: {result.processing_time:.2f}s")

        if result.errors:
            logger.warning("")
            logger.warning("Errors encountered:")
            for url, error in result.errors.items():
                logger.warning(f"  {url}: {error}")

        if result.results:
            logger.info("")
            logger.info("Grades generated:")
            for url, grade in sorted(result.results.items()):
                logger.info(f"  {url}: {grade:.2f}%")

        logger.info("")
        if success:
            logger.info(f"✓ Analysis complete. Results saved to: {orchestrator.output_file}")
            return 0
        else:
            logger.error("✗ Analysis failed. Check logs above for details.")
            return 1

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Please ensure the input file exists and check the path.")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error("Check logs above for details.")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
