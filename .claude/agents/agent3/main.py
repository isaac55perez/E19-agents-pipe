#!/usr/bin/env python3
"""
Excel Greeting Transformer - Agent3

Transform Excel files containing student grades into personalized greeting messages
based on performance tiers using celebrity-style personalities.

Usage:
    python main.py                          # Uses default input/output paths
    python main.py --input custom.xlsx      # Custom input file
    python main.py --output result.xlsx     # Custom output file
    python main.py --verbose                # Enable verbose logging
"""

import argparse
import logging
import sys
from pathlib import Path

from excel_processor import ExcelReader, ExcelWriter
from greeting_generator import GreetingGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Excel Greeting Transformer - Add personalized greetings to grades",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --input custom_input.xlsx --output results.xlsx
  python main.py --verbose
        """,
    )

    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to input Excel file (default: output/output23.xlsx)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output Excel file (default: output/output34.xlsx)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    return parser.parse_args()


def main():
    """Main entry point for the greeting transformer."""
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    # Get project root (navigate up from agent3 directory)
    project_root = Path(__file__).parent.parent.parent.parent

    # Set default paths relative to project root
    input_file = Path(args.input) if args.input else project_root / "output" / "output23.xlsx"
    output_file = Path(args.output) if args.output else project_root / "output" / "output34.xlsx"

    logger.info("=" * 60)
    logger.info("Excel Greeting Transformer")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Configuration:")
    logger.info(f"  Project root: {project_root}")
    logger.info(f"  Input file: {input_file}")
    logger.info(f"  Output file: {output_file}")
    logger.info("")

    try:
        # Read input file
        logger.info(f"Reading input file: {input_file}")
        rows_data, headers = ExcelReader.read_input_file(input_file)

        if not rows_data:
            logger.error("No data rows found in input file")
            return 1

        logger.info(f"Found {len(rows_data)} entries")

        # Validate grades
        logger.info("Validating grade values...")
        is_valid, errors = ExcelWriter.validate_grades(rows_data)
        if not is_valid:
            logger.warning(f"Grade validation found {len(errors)} issues")

        # Generate greetings
        logger.info("Generating greeting messages...")
        greetings = {}
        eddie_count = 0
        trump_count = 0

        for idx, row_data in enumerate(rows_data):
            grade = row_data.get("grade")
            greeting = GreetingGenerator.generate_greeting(grade)
            greetings[idx] = greeting

            # Count by personality style
            personality = GreetingGenerator.get_personality_style(grade)
            if personality == "Eddie Murphy":
                eddie_count += 1
            else:
                trump_count += 1

        logger.info(f"Generated greetings:")
        logger.info(f"  Eddie Murphy style (0-60): {eddie_count} entries")
        logger.info(f"  Donald Trump style (>60): {trump_count} entries")

        # Write output file
        logger.info(f"Writing output file: {output_file}")
        success = ExcelWriter.write_output_file(output_file, headers, rows_data, greetings)

        if not success:
            logger.error("Failed to write output file")
            return 1

        logger.info("")
        logger.info("=" * 60)
        logger.info("Transformation Complete!")
        logger.info("=" * 60)
        logger.info(f"✓ Processed {len(rows_data)} entries")
        logger.info(f"✓ Output file: {output_file}")
        logger.info("")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Please ensure the input file exists and check the path.")
        return 1

    except ValueError as e:
        logger.error(f"Data validation error: {e}")
        logger.error("Check the input file format and grade values.")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
