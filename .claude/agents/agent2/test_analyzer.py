"""
Unit tests for the analyzer module.

Tests cover:
- Python file analysis
- Repository cloning
- Grade calculation
- Error handling
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from analyzer import (
    PythonFileAnalyzer,
    RepositoryCloner,
    RepositoryAnalyzer,
    RepositoryAnalysis
)


class TestPythonFileAnalyzer:
    """Tests for PythonFileAnalyzer class."""

    def test_count_lines_basic(self, tmp_path):
        """Test counting lines in a simple Python file."""
        py_file = tmp_path / "test.py"
        py_file.write_text("import os\nprint('hello')\n")

        line_count = PythonFileAnalyzer.count_lines(py_file)
        assert line_count == 2

    def test_count_lines_empty_file(self, tmp_path):
        """Test counting lines in an empty file."""
        py_file = tmp_path / "empty.py"
        py_file.write_text("")

        line_count = PythonFileAnalyzer.count_lines(py_file)
        assert line_count == 0

    def test_count_lines_multiline(self, tmp_path):
        """Test counting lines in a file with multiple lines."""
        py_file = tmp_path / "multiline.py"
        content = "\n".join([f"line {i}" for i in range(1, 101)])
        py_file.write_text(content)

        line_count = PythonFileAnalyzer.count_lines(py_file)
        assert line_count == 100

    def test_count_lines_nonexistent_file(self, tmp_path):
        """Test handling of nonexistent file."""
        py_file = tmp_path / "nonexistent.py"

        line_count = PythonFileAnalyzer.count_lines(py_file)
        assert line_count == 0

    def test_is_small_file_true(self, tmp_path):
        """Test identifying small files (< 150 lines)."""
        py_file = tmp_path / "small.py"
        py_file.write_text("\n".join([f"line {i}" for i in range(100)]))

        assert PythonFileAnalyzer.is_small_file(py_file) is True

    def test_is_small_file_false(self, tmp_path):
        """Test identifying large files (>= 150 lines)."""
        py_file = tmp_path / "large.py"
        py_file.write_text("\n".join([f"line {i}" for i in range(150)]))

        assert PythonFileAnalyzer.is_small_file(py_file) is False

    def test_is_small_file_boundary(self, tmp_path):
        """Test boundary case at 150 lines."""
        # Exactly 150 lines should be false (not small)
        py_file = tmp_path / "boundary.py"
        py_file.write_text("\n".join([f"line {i}" for i in range(150)]))

        assert PythonFileAnalyzer.is_small_file(py_file) is False

    def test_find_python_files(self, tmp_path):
        """Test finding Python files recursively."""
        # Create directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "module.py").write_text("# module")
        (tmp_path / "src" / "test.py").write_text("# test")
        (tmp_path / "README.md").write_text("# README")

        python_files = PythonFileAnalyzer.find_python_files(tmp_path)

        assert len(python_files) == 2
        assert all(f.suffix == ".py" for f in python_files)

    def test_find_python_files_skip_venv(self, tmp_path):
        """Test that venv directories are skipped."""
        (tmp_path / "venv" / "lib").mkdir(parents=True)
        (tmp_path / "venv" / "lib" / "site.py").write_text("# venv")
        (tmp_path / "main.py").write_text("# main")

        python_files = PythonFileAnalyzer.find_python_files(tmp_path)

        assert len(python_files) == 1
        assert python_files[0].name == "main.py"

    def test_find_python_files_skip_git(self, tmp_path):
        """Test that .git directories are skipped."""
        (tmp_path / ".git" / "objects").mkdir(parents=True)
        (tmp_path / ".git" / "objects" / "hook.py").write_text("# git")
        (tmp_path / "main.py").write_text("# main")

        python_files = PythonFileAnalyzer.find_python_files(tmp_path)

        assert len(python_files) == 1
        assert python_files[0].name == "main.py"

    def test_find_python_files_empty_directory(self, tmp_path):
        """Test finding Python files in empty directory."""
        python_files = PythonFileAnalyzer.find_python_files(tmp_path)

        assert len(python_files) == 0


class TestRepositoryCloner:
    """Tests for RepositoryCloner class."""

    def test_init_default(self):
        """Test default initialization."""
        cloner = RepositoryCloner()
        assert cloner.cloned_repos == []
        assert cloner.temp_base is not None

    def test_init_custom_temp_base(self, tmp_path):
        """Test initialization with custom temp base."""
        cloner = RepositoryCloner(temp_base=tmp_path)
        assert cloner.temp_base == tmp_path

    def test_cleanup_empty(self):
        """Test cleanup with no cloned repos."""
        cloner = RepositoryCloner()
        cloner.cleanup()  # Should not raise
        assert cloner.cloned_repos == []

    def test_cleanup_removes_directories(self, tmp_path):
        """Test that cleanup removes temporary directories."""
        cloner = RepositoryCloner(temp_base=tmp_path)
        test_dir = tmp_path / "test_repo"
        test_dir.mkdir()
        cloner.cloned_repos.append(test_dir)

        assert test_dir.exists()
        cloner.cleanup()
        assert not test_dir.exists()

    def test_clone_repository_success(self, tmp_path):
        """Test successful repository clone."""
        try:
            from git import Repo
            HAS_GITPYTHON = True
        except ImportError:
            HAS_GITPYTHON = False

        if not HAS_GITPYTHON:
            pytest.skip("GitPython not installed")

        cloner = RepositoryCloner(temp_base=tmp_path)

        # Mock the git.Repo class at the point of import
        with patch('git.Repo') as mock_repo_class:
            mock_repo_class.clone_from.return_value = MagicMock()

            success, repo_path, error = cloner.clone_repository("https://github.com/test/repo.git")

            assert success is True
            assert repo_path is not None
            assert error == ""
            assert len(cloner.cloned_repos) == 1

    def test_clone_repository_gitpython_missing(self, tmp_path, monkeypatch):
        """Test handling of missing GitPython."""
        def mock_import(name, *args, **kwargs):
            if name == 'git':
                raise ImportError("GitPython not found")
            return __import__(name, *args, **kwargs)

        cloner = RepositoryCloner(temp_base=tmp_path)

        with patch('builtins.__import__', side_effect=mock_import):
            success, repo_path, error = cloner.clone_repository("https://github.com/test/repo.git")

            # Should handle gracefully
            assert success is False
            assert "GitPython" in error or repo_path is None


class TestRepositoryAnalyzer:
    """Tests for RepositoryAnalyzer class."""

    def test_init_default(self):
        """Test default initialization."""
        analyzer = RepositoryAnalyzer()
        assert analyzer.cloner is not None
        assert analyzer.file_analyzer is not None

    def test_init_custom_cloner(self):
        """Test initialization with custom cloner."""
        cloner = RepositoryCloner()
        analyzer = RepositoryAnalyzer(cloner=cloner)
        assert analyzer.cloner is cloner

    def test_analyze_failure_clone(self):
        """Test analysis when cloning fails."""
        mock_cloner = Mock()
        mock_cloner.clone_repository.return_value = (False, None, "Clone failed")

        analyzer = RepositoryAnalyzer(cloner=mock_cloner)
        result = analyzer.analyze("https://github.com/test/repo.git")

        assert result.url == "https://github.com/test/repo.git"
        assert result.error == "Clone failed"
        assert result.total_py_files == 0
        assert result.grade == 0.0

    def test_analyze_no_python_files(self, tmp_path):
        """Test analysis of repository with no Python files."""
        cloner = RepositoryCloner(temp_base=tmp_path)

        # Create a test repo directory with no Python files
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "README.md").write_text("# Test")

        with patch.object(cloner, 'clone_repository', return_value=(True, repo_dir, "")):
            analyzer = RepositoryAnalyzer(cloner=cloner)
            result = analyzer.analyze("https://github.com/test/repo.git")

        assert result.error == "No Python files found"
        assert result.total_py_files == 0

    def test_analyze_all_small_files(self, tmp_path):
        """Test analysis with all small Python files."""
        cloner = RepositoryCloner(temp_base=tmp_path)

        # Create test repo with small Python files
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "small1.py").write_text("# Small file\n" * 50)
        (repo_dir / "small2.py").write_text("# Small file\n" * 50)

        with patch.object(cloner, 'clone_repository', return_value=(True, repo_dir, "")):
            analyzer = RepositoryAnalyzer(cloner=cloner)
            result = analyzer.analyze("https://github.com/test/repo.git")

        assert result.total_py_files == 2
        assert result.small_py_files == 2
        assert result.grade == 100.0
        assert result.is_valid()

    def test_analyze_all_large_files(self, tmp_path):
        """Test analysis with all large Python files."""
        cloner = RepositoryCloner(temp_base=tmp_path)

        # Create test repo with large Python files
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "large1.py").write_text("# Large file\n" * 200)
        (repo_dir / "large2.py").write_text("# Large file\n" * 200)

        with patch.object(cloner, 'clone_repository', return_value=(True, repo_dir, "")):
            analyzer = RepositoryAnalyzer(cloner=cloner)
            result = analyzer.analyze("https://github.com/test/repo.git")

        assert result.total_py_files == 2
        assert result.small_py_files == 0
        assert result.grade == 0.0
        assert result.is_valid()

    def test_analyze_mixed_files(self, tmp_path):
        """Test analysis with mixed small and large files."""
        cloner = RepositoryCloner(temp_base=tmp_path)

        # Create test repo with mixed files
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "small.py").write_text("# Small\n" * 50)
        (repo_dir / "large.py").write_text("# Large\n" * 200)
        (repo_dir / "medium.py").write_text("# Medium\n" * 100)

        with patch.object(cloner, 'clone_repository', return_value=(True, repo_dir, "")):
            analyzer = RepositoryAnalyzer(cloner=cloner)
            result = analyzer.analyze("https://github.com/test/repo.git")

        assert result.total_py_files == 3
        assert result.small_py_files == 2
        assert result.grade == pytest.approx(66.67, abs=0.01)
        assert result.is_valid()

    def test_analyze_cleanup_called(self, tmp_path):
        """Test that cleanup is called after analysis."""
        cloner = RepositoryCloner(temp_base=tmp_path)
        cloner.cleanup = Mock()

        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("# test")

        with patch.object(cloner, 'clone_repository', return_value=(True, repo_dir, "")):
            analyzer = RepositoryAnalyzer(cloner=cloner)
            analyzer.analyze("https://github.com/test/repo.git")

        # Cleanup should be called
        analyzer.cleanup()
        cloner.cleanup.assert_called()


class TestRepositoryAnalysisDataclass:
    """Tests for RepositoryAnalysis dataclass."""

    def test_valid_analysis(self):
        """Test valid analysis result."""
        result = RepositoryAnalysis(
            url="https://github.com/test/repo",
            total_py_files=10,
            small_py_files=7,
            grade=70.0
        )

        assert result.is_valid() is True
        assert result.error is None

    def test_invalid_analysis(self):
        """Test invalid analysis result with error."""
        result = RepositoryAnalysis(
            url="https://github.com/test/repo",
            total_py_files=0,
            small_py_files=0,
            grade=0.0,
            error="Clone failed"
        )

        assert result.is_valid() is False
        assert result.error == "Clone failed"
