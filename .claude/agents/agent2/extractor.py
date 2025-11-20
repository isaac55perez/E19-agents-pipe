"""
Main orchestrator for repository analysis workflow.

This module coordinates:
- Reading input Excel files
- Processing repositories
- Generating output Excel files
- Error management and logging
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

from analyzer import RepositoryAnalyzer
from excel_processor import ExcelReader, ExcelWriter, RepositoryEntry
from processor import RepositoryProcessor, ProcessingResult

logger = logging.getLogger(__name__)


class RepositoryAnalysisOrchestrator:
    """Main orchestrator for the repository analysis workflow."""

    DEFAULT_INPUT_FILE = "output/output12.xlsx"
    DEFAULT_OUTPUT_FILE = "output/output23.xlsx"

    def __init__(
        self,
        input_file: Optional[Path] = None,
        output_file: Optional[Path] = None,
        max_workers: int = 4,
        project_root: Optional[Path] = None
    ):
        """
        Initialize the orchestrator.

        Args:
            input_file: Path to input Excel file. If None, uses default relative path.
            output_file: Path to output Excel file. If None, uses default relative path.
            max_workers: Number of concurrent worker threads
            project_root: Project root directory for relative paths. If None, uses current directory.
        """
        self.project_root = project_root or Path.cwd()

        # Handle relative/absolute paths
        if input_file is None:
            self.input_file = self.project_root / self.DEFAULT_INPUT_FILE
        elif isinstance(input_file, str):
            input_file = Path(input_file)
            self.input_file = input_file if input_file.is_absolute() else (self.project_root / input_file)
        else:
            self.input_file = input_file if input_file.is_absolute() else (self.project_root / input_file)

        if output_file is None:
            self.output_file = self.project_root / self.DEFAULT_OUTPUT_FILE
        elif isinstance(output_file, str):
            output_file = Path(output_file)
            self.output_file = output_file if output_file.is_absolute() else (self.project_root / output_file)
        else:
            self.output_file = output_file if output_file.is_absolute() else (self.project_root / output_file)

        self.max_workers = max_workers
        logger.info(f"Initialized orchestrator with input={self.input_file}, output={self.output_file}")

    def run(self) -> Tuple[bool, ProcessingResult]:
        """
        Execute the complete analysis workflow.

        Returns:
            Tuple of (success, processing_result)
        """
        logger.info("Starting repository analysis workflow")

        try:
            # Step 1: Read input file
            logger.info(f"Reading input file: {self.input_file}")
            entries = ExcelReader.read_input_file(self.input_file)

            if not entries:
                logger.error("No entries found in input file")
                return False, ProcessingResult(total_entries=0)

            # Step 2: Extract URLs
            logger.info(f"Extracting URLs from {len(entries)} entries")
            entries_with_urls = ExcelReader.extract_urls(entries)

            if not entries_with_urls:
                logger.error("No valid repository URLs found in input file")
                return False, ProcessingResult(total_entries=len(entries))

            # Step 3: Process repositories
            logger.info(f"Processing {len(entries_with_urls)} repositories with {self.max_workers} workers")
            processor = RepositoryProcessor(max_workers=self.max_workers)
            result = processor.process_entries(entries_with_urls)

            # Step 4: Write output file
            logger.info(f"Writing output file: {self.output_file}")
            success = ExcelWriter.write_output_file(
                self.output_file,
                entries_with_urls,
                result.results
            )

            if not success:
                logger.error("Failed to write output file")
                return False, result

            logger.info(
                f"Analysis workflow complete: {result.successful}/{result.total_entries} successful "
                f"({result.success_rate():.1f}%), time: {result.processing_time:.2f}s"
            )
            return True, result

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return False, ProcessingResult(total_entries=0)


class AnalysisWorkflow:
    """Simplified interface for analysis workflow."""

    @staticmethod
    def analyze_repositories(
        input_file: Optional[Path] = None,
        output_file: Optional[Path] = None,
        max_workers: int = 4
    ) -> Tuple[bool, ProcessingResult]:
        """
        Analyze repositories from input file and generate output.

        Args:
            input_file: Path to input Excel file (optional)
            output_file: Path to output Excel file (optional)
            max_workers: Number of concurrent threads (optional)

        Returns:
            Tuple of (success, processing_result)
        """
        orchestrator = RepositoryAnalysisOrchestrator(
            input_file=input_file,
            output_file=output_file,
            max_workers=max_workers
        )
        return orchestrator.run()
