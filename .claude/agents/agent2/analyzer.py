"""
Core repository analysis functionality for Python repositories.

This module provides:
- Repository management and cloning
- Python file analysis and line counting
- Grade calculation based on file size metrics
- Error handling for various edge cases
"""

import logging
import os
import shutil
import tempfile
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


@dataclass
class RepositoryAnalysis:
    """Result of analyzing a single repository."""
    url: str
    total_py_files: int
    small_py_files: int  # Files with < 150 lines
    grade: float  # Percentage: (small_py_files / total_py_files) * 100
    error: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if analysis completed successfully."""
        return self.error is None


class PythonFileAnalyzer:
    """Analyzes Python files and counts lines of code."""

    SMALL_FILE_THRESHOLD = 150  # Lines of code threshold

    @staticmethod
    def count_lines(file_path: Path) -> int:
        """
        Count lines in a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Number of lines in the file

        Raises:
            IOError: If file cannot be read
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception as e:
            logger.warning(f"Failed to count lines in {file_path}: {e}")
            return 0

    @staticmethod
    def is_small_file(file_path: Path) -> bool:
        """
        Check if a Python file is considered 'small' (< 150 lines).

        Args:
            file_path: Path to Python file

        Returns:
            True if file has fewer than 150 lines
        """
        return PythonFileAnalyzer.count_lines(file_path) < PythonFileAnalyzer.SMALL_FILE_THRESHOLD

    @staticmethod
    def find_python_files(directory: Path) -> List[Path]:
        """
        Find all Python files in a directory recursively.

        Args:
            directory: Root directory to search

        Returns:
            List of paths to Python files
        """
        python_files = []
        try:
            for root, dirs, files in os.walk(directory):
                # Skip common non-essential directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}]

                for file in files:
                    if file.endswith('.py'):
                        python_files.append(Path(root) / file)
        except Exception as e:
            logger.warning(f"Error walking directory {directory}: {e}")

        return python_files


class RepositoryCloner:
    """Handles cloning and managing repository copies."""

    DEFAULT_TIMEOUT = 60  # seconds

    def __init__(self, temp_base: Optional[Path] = None):
        """
        Initialize repository cloner.

        Args:
            temp_base: Base directory for temporary clones. If None, uses system temp.
        """
        self.temp_base = temp_base or Path(tempfile.gettempdir())
        self.cloned_repos: List[Path] = []

    def clone_repository(self, url: str) -> Tuple[bool, Optional[Path], str]:
        """
        Clone a Git repository to a temporary location.

        Args:
            url: Git repository URL

        Returns:
            Tuple of (success, repo_path, error_message)
        """
        try:
            # Try to import GitPython
            try:
                from git import Repo
                from git.exc import GitCommandError
            except ImportError:
                logger.error("GitPython not installed. Install with: uv pip install GitPython")
                return False, None, "GitPython not installed"

            # Create temporary directory for this clone with unique name
            # Use UUID to ensure uniqueness in concurrent scenarios
            clone_dir = self.temp_base / f"repo_{uuid.uuid4().hex[:8]}"
            clone_dir.mkdir(parents=True, exist_ok=True)

            try:
                logger.debug(f"Cloning repository: {url}")
                # Use kill_after_timeout for timeout instead of the timeout parameter
                # which may not be supported on older git versions
                repo = Repo.clone_from(url, str(clone_dir), kill_after_timeout=self.DEFAULT_TIMEOUT)
                self.cloned_repos.append(clone_dir)
                logger.info(f"Successfully cloned {url} to {clone_dir}")
                return True, clone_dir, ""
            except GitCommandError as e:
                error_msg = f"Git command failed: {str(e)}"
                logger.warning(f"{error_msg} for {url}")
                return False, None, error_msg
            except Exception as e:
                error_msg = f"Clone failed: {str(e)}"
                logger.warning(f"{error_msg} for {url}")
                return False, None, error_msg

        except Exception as e:
            error_msg = f"Unexpected error during clone: {str(e)}"
            logger.error(f"{error_msg} for {url}")
            return False, None, error_msg

    def cleanup(self):
        """Clean up all temporary cloned repositories."""
        for repo_path in self.cloned_repos:
            try:
                if repo_path.exists():
                    shutil.rmtree(repo_path)
                    logger.debug(f"Cleaned up {repo_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {repo_path}: {e}")

        self.cloned_repos.clear()


class RepositoryAnalyzer:
    """Main analyzer for Python repositories."""

    def __init__(self, cloner: Optional[RepositoryCloner] = None):
        """
        Initialize repository analyzer.

        Args:
            cloner: RepositoryCloner instance. If None, creates a new one.
        """
        self.cloner = cloner or RepositoryCloner()
        self.file_analyzer = PythonFileAnalyzer()

    def analyze(self, url: str) -> RepositoryAnalysis:
        """
        Analyze a Python repository.

        Args:
            url: Git repository URL

        Returns:
            RepositoryAnalysis with results and error information
        """
        logger.info(f"Starting analysis of {url}")

        # Clone the repository
        success, repo_path, error = self.cloner.clone_repository(url)
        if not success:
            logger.error(f"Failed to clone {url}: {error}")
            return RepositoryAnalysis(
                url=url,
                total_py_files=0,
                small_py_files=0,
                grade=0.0,
                error=error
            )

        try:
            # Find all Python files
            python_files = self.file_analyzer.find_python_files(repo_path)
            total_files = len(python_files)

            if total_files == 0:
                logger.info(f"No Python files found in {url}")
                return RepositoryAnalysis(
                    url=url,
                    total_py_files=0,
                    small_py_files=0,
                    grade=0.0,
                    error="No Python files found"
                )

            # Count small files
            small_files = sum(1 for f in python_files if self.file_analyzer.is_small_file(f))

            # Calculate grade
            grade = (small_files / total_files) * 100

            result = RepositoryAnalysis(
                url=url,
                total_py_files=total_files,
                small_py_files=small_files,
                grade=round(grade, 2)
            )

            logger.info(
                f"Analysis complete for {url}: "
                f"{total_files} total files, {small_files} small files, grade={grade:.2f}%"
            )
            return result

        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            logger.error(f"{error_msg} for {url}")
            return RepositoryAnalysis(
                url=url,
                total_py_files=0,
                small_py_files=0,
                grade=0.0,
                error=error_msg
            )

    def cleanup(self):
        """Clean up resources."""
        self.cloner.cleanup()
