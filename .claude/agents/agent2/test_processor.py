"""
Unit tests for the processor module.

Tests cover:
- Multi-threaded processing
- Result aggregation
- Thread safety
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import Future

from processor import (
    ProcessingResult,
    RepositoryProcessor,
    ProcessorBuilder
)
from analyzer import RepositoryAnalysis
from excel_processor import RepositoryEntry


class TestProcessingResult:
    """Tests for ProcessingResult dataclass."""

    def test_init_default(self):
        """Test default initialization."""
        result = ProcessingResult(total_entries=10)

        assert result.total_entries == 10
        assert result.successful == 0
        assert result.failed == 0
        assert result.results == {}
        assert result.errors == {}
        assert result.processing_time == 0.0

    def test_success_rate_all_successful(self):
        """Test success rate calculation with all successful."""
        result = ProcessingResult(total_entries=10)
        result.successful = 10

        assert result.success_rate() == 100.0

    def test_success_rate_partial(self):
        """Test success rate with partial success."""
        result = ProcessingResult(total_entries=10)
        result.successful = 7
        result.failed = 3

        assert result.success_rate() == 70.0

    def test_success_rate_no_success(self):
        """Test success rate with no successes."""
        result = ProcessingResult(total_entries=10)
        result.successful = 0
        result.failed = 10

        assert result.success_rate() == 0.0

    def test_success_rate_zero_entries(self):
        """Test success rate with zero entries."""
        result = ProcessingResult(total_entries=0)

        assert result.success_rate() == 0.0


class TestRepositoryProcessor:
    """Tests for RepositoryProcessor class."""

    def test_init_default(self):
        """Test default initialization."""
        processor = RepositoryProcessor()

        assert processor.max_workers == RepositoryProcessor.DEFAULT_MAX_WORKERS
        assert processor.analyzer is not None

    def test_init_custom_workers(self):
        """Test initialization with custom worker count."""
        processor = RepositoryProcessor(max_workers=8)

        assert processor.max_workers == 8

    def test_init_clamps_workers_max(self):
        """Test that max workers is clamped to 16."""
        processor = RepositoryProcessor(max_workers=100)

        assert processor.max_workers == 16

    def test_init_clamps_workers_min(self):
        """Test that max workers is clamped to 1."""
        processor = RepositoryProcessor(max_workers=0)

        assert processor.max_workers == 1

    def test_process_entries_empty(self):
        """Test processing empty entry list."""
        processor = RepositoryProcessor()

        result = processor.process_entries([])

        assert result.total_entries == 0
        assert result.successful == 0
        assert result.failed == 0

    @patch('processor.RepositoryAnalyzer.analyze')
    def test_process_entries_single(self, mock_analyze):
        """Test processing single entry."""
        mock_analyze.return_value = RepositoryAnalysis(
            url="https://github.com/test/repo",
            total_py_files=10,
            small_py_files=7,
            grade=70.0
        )

        processor = RepositoryProcessor()
        entries = [
            RepositoryEntry(2, {"url": "https://github.com/test/repo"})
        ]

        result = processor.process_entries(entries)

        assert result.total_entries == 1
        assert result.successful == 1
        assert result.failed == 0
        assert result.results["https://github.com/test/repo"] == 70.0

    @patch('processor.RepositoryAnalyzer.analyze')
    def test_process_entries_multiple(self, mock_analyze):
        """Test processing multiple entries."""
        mock_analyze.side_effect = [
            RepositoryAnalysis("https://github.com/test/repo1", 10, 7, 70.0),
            RepositoryAnalysis("https://github.com/test/repo2", 20, 10, 50.0),
            RepositoryAnalysis("https://github.com/test/repo3", 5, 5, 100.0),
        ]

        processor = RepositoryProcessor()
        entries = [
            RepositoryEntry(2, {"url": "https://github.com/test/repo1"}),
            RepositoryEntry(3, {"url": "https://github.com/test/repo2"}),
            RepositoryEntry(4, {"url": "https://github.com/test/repo3"}),
        ]

        result = processor.process_entries(entries)

        assert result.total_entries == 3
        assert result.successful == 3
        assert result.failed == 0
        assert len(result.results) == 3

    @patch('processor.RepositoryAnalyzer.analyze')
    def test_process_entries_with_errors(self, mock_analyze):
        """Test processing with some errors."""
        mock_analyze.side_effect = [
            RepositoryAnalysis(
                "https://github.com/test/repo1",
                10, 7, 70.0
            ),
            RepositoryAnalysis(
                "https://github.com/test/repo2",
                0, 0, 0.0,
                error="Clone failed"
            ),
        ]

        processor = RepositoryProcessor()
        entries = [
            RepositoryEntry(2, {"url": "https://github.com/test/repo1"}),
            RepositoryEntry(3, {"url": "https://github.com/test/repo2"}),
        ]

        result = processor.process_entries(entries)

        assert result.total_entries == 2
        assert result.successful == 1
        assert result.failed == 1
        assert "https://github.com/test/repo2" in result.errors

    @patch('processor.RepositoryAnalyzer.analyze')
    def test_process_entries_thread_count(self, mock_analyze):
        """Test that correct number of threads is used."""
        mock_analyze.return_value = RepositoryAnalysis(
            "https://github.com/test/repo",
            10, 7, 70.0
        )

        processor = RepositoryProcessor(max_workers=2)
        entries = [
            RepositoryEntry(i, {"url": f"https://github.com/test/repo{i}"})
            for i in range(5)
        ]

        result = processor.process_entries(entries)

        assert result.total_entries == 5
        assert result.successful == 5

    @patch('processor.RepositoryAnalyzer.analyze')
    def test_process_entries_records_timing(self, mock_analyze):
        """Test that processing time is recorded."""
        mock_analyze.return_value = RepositoryAnalysis(
            "https://github.com/test/repo",
            10, 7, 70.0
        )

        processor = RepositoryProcessor()
        entries = [
            RepositoryEntry(2, {"url": "https://github.com/test/repo"})
        ]

        result = processor.process_entries(entries)

        assert result.processing_time > 0.0

    def test_record_result_thread_safe(self):
        """Test that result recording is thread-safe."""
        processor = RepositoryProcessor()
        result = ProcessingResult(total_entries=1)

        # Simulate concurrent access
        analysis = RepositoryAnalysis(
            "https://github.com/test/repo",
            10, 7, 70.0
        )

        processor._record_result(analysis, result)

        assert result.successful == 1
        assert result.results["https://github.com/test/repo"] == 70.0


class TestProcessorBuilder:
    """Tests for ProcessorBuilder class."""

    def test_create_default(self):
        """Test creating processor with default configuration."""
        processor = ProcessorBuilder.create_default()

        assert processor is not None
        assert processor.max_workers == RepositoryProcessor.DEFAULT_MAX_WORKERS

    def test_create_with_workers(self):
        """Test creating processor with custom worker count."""
        processor = ProcessorBuilder.create_with_workers(8)

        assert processor is not None
        assert processor.max_workers == 8

    def test_builder_returns_processor_instance(self):
        """Test that builder returns RepositoryProcessor instances."""
        processor1 = ProcessorBuilder.create_default()
        processor2 = ProcessorBuilder.create_with_workers(6)

        assert isinstance(processor1, RepositoryProcessor)
        assert isinstance(processor2, RepositoryProcessor)
        assert processor1 is not processor2  # Different instances
