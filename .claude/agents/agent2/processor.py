"""
Multi-threaded repository processing engine.

This module provides:
- Concurrent repository analysis using thread pools
- Thread-safe result aggregation
- Progress tracking and error management
- Worker thread implementation
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from queue import Queue

from analyzer import RepositoryAnalyzer, RepositoryAnalysis
from excel_processor import RepositoryEntry

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing all repositories."""
    total_entries: int
    successful: int = 0
    failed: int = 0
    results: Dict[str, float] = field(default_factory=dict)  # URL -> grade
    errors: Dict[str, str] = field(default_factory=dict)  # URL -> error message
    processing_time: float = 0.0

    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_entries == 0:
            return 0.0
        return (self.successful / self.total_entries) * 100


class RepositoryProcessor:
    """Multi-threaded repository processor."""

    DEFAULT_MAX_WORKERS = 4  # Number of concurrent threads
    WORKER_TIMEOUT = 300  # seconds per repository

    def __init__(self, max_workers: int = DEFAULT_MAX_WORKERS):
        """
        Initialize repository processor.

        Args:
            max_workers: Maximum number of concurrent threads (4-8 recommended)
        """
        self.max_workers = max(1, min(max_workers, 16))  # Clamp between 1 and 16
        self.analyzer = RepositoryAnalyzer()
        self.result_lock = threading.Lock()
        logger.info(f"Initialized RepositoryProcessor with {self.max_workers} workers")

    def process_entries(self, entries: List[RepositoryEntry]) -> ProcessingResult:
        """
        Process multiple repository entries concurrently.

        Args:
            entries: List of repository entries to analyze

        Returns:
            ProcessingResult with aggregated results
        """
        start_time = time.time()
        result = ProcessingResult(total_entries=len(entries))

        if not entries:
            logger.warning("No entries to process")
            return result

        logger.info(f"Starting processing of {len(entries)} repositories with {self.max_workers} workers")

        try:
            # Use ThreadPoolExecutor for concurrent processing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_entry = {
                    executor.submit(self._process_single_entry, entry): entry
                    for entry in entries
                }

                # Process completed tasks
                for future in as_completed(future_to_entry, timeout=self.WORKER_TIMEOUT):
                    entry = future_to_entry[future]
                    try:
                        analysis = future.result(timeout=self.WORKER_TIMEOUT)
                        self._record_result(analysis, result)
                    except Exception as e:
                        error_msg = f"Worker exception: {str(e)}"
                        logger.error(f"Error processing {entry.url}: {error_msg}")
                        with self.result_lock:
                            result.failed += 1
                            result.errors[entry.url] = error_msg

        except Exception as e:
            logger.error(f"Thread pool error: {e}")
            # Mark remaining as failed
            failed_count = len(entries) - result.successful - result.failed
            result.failed += failed_count

        finally:
            # Clean up analyzer resources
            self.analyzer.cleanup()

        result.processing_time = time.time() - start_time
        logger.info(
            f"Processing complete: {result.successful} successful, {result.failed} failed, "
            f"time: {result.processing_time:.2f}s"
        )

        return result

    def _process_single_entry(self, entry: RepositoryEntry) -> RepositoryAnalysis:
        """
        Process a single repository entry (worker thread function).

        Args:
            entry: Repository entry to process

        Returns:
            RepositoryAnalysis with results

        Note:
            Called from worker threads, must be thread-safe
        """
        logger.debug(f"Worker thread processing {entry.url}")
        return self.analyzer.analyze(entry.url)

    def _record_result(self, analysis: RepositoryAnalysis, result: ProcessingResult):
        """
        Record analysis result in thread-safe manner.

        Args:
            analysis: Analysis result from single repository
            result: Aggregated processing result

        Note:
            Uses lock for thread-safe access to shared result object
        """
        with self.result_lock:
            if analysis.is_valid():
                result.successful += 1
                result.results[analysis.url] = analysis.grade
                logger.info(
                    f"Recorded result for {analysis.url}: "
                    f"grade={analysis.grade}, files={analysis.total_py_files}"
                )
            else:
                result.failed += 1
                result.errors[analysis.url] = analysis.error
                logger.warning(f"Recording error for {analysis.url}: {analysis.error}")


class ProcessorBuilder:
    """Builder for creating configured processors."""

    @staticmethod
    def create_default() -> RepositoryProcessor:
        """Create processor with default configuration."""
        return RepositoryProcessor(max_workers=RepositoryProcessor.DEFAULT_MAX_WORKERS)

    @staticmethod
    def create_with_workers(max_workers: int) -> RepositoryProcessor:
        """Create processor with specified worker count."""
        return RepositoryProcessor(max_workers=max_workers)
