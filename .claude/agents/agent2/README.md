# Repository Python Analyzer Agent

A Python-based agent that analyzes GitHub repositories and grades them based on code quality metrics, specifically measuring the distribution of Python file sizes.

## Overview

The Repository Python Analyzer Agent processes a list of Git repository URLs, analyzes the Python code structure, and generates a quality grade for each repository. The grade is calculated as the percentage of Python files that are "small" (fewer than 150 lines of code).

### Key Features

- **Repository Analysis**: Clones and analyzes Git repositories from URLs
- **Python File Detection**: Identifies and counts all Python files recursively
- **Code Metrics**: Measures lines of code (LOC) in each Python file
- **Quality Grading**: Calculates grades based on file size distribution
- **Multi-threaded Processing**: Analyzes multiple repositories concurrently
- **Excel Integration**: Reads input from and writes results to Excel files
- **Comprehensive Error Handling**: Gracefully handles network issues, missing files, and other errors
- **Detailed Logging**: Tracks all operations for debugging and monitoring

## Architecture

### Components

#### 1. **analyzer.py** - Core Analysis Engine
- `PythonFileAnalyzer`: Analyzes Python files and counts lines of code
- `RepositoryCloner`: Manages Git repository cloning and cleanup
- `RepositoryAnalyzer`: Orchestrates the analysis of single repositories
- `RepositoryAnalysis`: Data class for analysis results

**Key Classes:**
- `PythonFileAnalyzer.count_lines()`: Counts lines in a Python file
- `PythonFileAnalyzer.is_small_file()`: Checks if file < 150 lines
- `PythonFileAnalyzer.find_python_files()`: Recursively finds Python files
- `RepositoryCloner.clone_repository()`: Clones a Git repository
- `RepositoryAnalyzer.analyze()`: Analyzes a repository and returns grade

#### 2. **excel_processor.py** - Excel File Handling
- `ExcelReader`: Reads repository data from Excel files
- `ExcelWriter`: Writes analysis results to Excel files
- `RepositoryEntry`: Data class for repository entries

**Key Functions:**
- `ExcelReader.read_input_file()`: Reads input Excel file
- `ExcelReader.extract_urls()`: Extracts and validates GitHub URLs
- `ExcelWriter.write_output_file()`: Writes results to output Excel file

#### 3. **processor.py** - Multi-threaded Processing
- `RepositoryProcessor`: Manages concurrent repository analysis
- `ProcessingResult`: Aggregates results from all repositories
- `ProcessorBuilder`: Factory for creating configured processors

**Key Features:**
- Thread-safe result aggregation using locks
- Configurable worker thread pool (4-8 recommended)
- Timeout handling for long-running operations
- Progress tracking and error logging

#### 4. **extractor.py** - Workflow Orchestration
- `RepositoryAnalysisOrchestrator`: Coordinates the complete workflow
- `AnalysisWorkflow`: Simplified interface for users

**Workflow:**
1. Read input Excel file (output/output12.xlsx)
2. Extract repository URLs from entries
3. Process repositories concurrently
4. Write results to output Excel file (output/output23.xlsx)

## Grading System

### Grade Calculation

```
Grade = (Small Python Files / Total Python Files) × 100
```

Where:
- **Small Python File**: A Python file with fewer than 150 lines of code
- **Total Python Files**: All .py files found in the repository
- **Grade**: Percentage representing code modularity (higher is better)

### Grade Interpretation

- **90-100%**: Excellent code modularity and organization
- **70-89%**: Good code structure with some larger modules
- **50-69%**: Mixed code sizes, potential refactoring opportunities
- **30-49%**: Several large modules, consider breaking down
- **0-29%**: Mostly large files, significant refactoring recommended

### Edge Cases

- **No Python Files**: Grade = 0.0, error message recorded
- **One Python File**: Grade = 100.0 if < 150 lines, 0.0 otherwise
- **All Large Files**: Grade = 0.0
- **All Small Files**: Grade = 100.0

## Input/Output Formats

### Input File (output12.xlsx)

Expected format from Agent 1 (Gmail Exercise Extractor):

| Column | Type | Description |
|--------|------|-------------|
| email | string | Email address of submitter |
| name | string | Name of student/submitter |
| url | string | GitHub repository URL |
| date | string | Submission date |
| status | string | Submission status |
| (other columns) | any | Additional metadata |

### Output File (output23.xlsx)

Generated analysis results:

| Column | Type | Description |
|--------|------|-------------|
| (all input columns) | any | Original data preserved |
| grade | float | Code quality grade (0-100) |

**Example Output:**
```
email                    | name        | url                               | date       | status | grade
student@example.com      | John Doe    | https://github.com/john/project1  | 2024-01-15 | valid  | 75.50
student2@example.com     | Jane Smith  | https://github.com/jane/project2  | 2024-01-15 | valid  | 88.00
```

## Dependencies

### Required Packages

- **openpyxl** (>=3.0.0): Excel file reading and writing
- **GitPython** (>=3.1.0): Git repository cloning and management

### Python Version

- Python 3.9 or higher (3.10+ recommended)

### Standard Library

- `pathlib`: Cross-platform path handling
- `threading`: Multi-threaded concurrent processing
- `logging`: Comprehensive logging
- `tempfile`: Temporary directory management
- `os`: File system operations

## Installation and Setup

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -e .

# Using pip
pip install -e .
```

### 2. Verify Installation

```bash
# Run tests
python -m pytest -v

# Run with verbose output
python main.py --verbose
```

## Usage

### Basic Usage

```bash
# Use default paths (output/output12.xlsx -> output/output23.xlsx)
python main.py

# Customize worker threads
python main.py --workers 8

# Enable verbose logging
python main.py --verbose
```

### Advanced Usage

```bash
# Custom input file
python main.py --input my_repos.xlsx

# Custom output file
python main.py --output results.xlsx

# All options combined
python main.py \
    --input repositories.xlsx \
    --output analysis_results.xlsx \
    --workers 6 \
    --verbose
```

### Programmatic Usage

```python
from extractor import AnalysisWorkflow
from pathlib import Path

# Simple analysis with defaults
success, result = AnalysisWorkflow.analyze_repositories()

# Custom paths and workers
success, result = AnalysisWorkflow.analyze_repositories(
    input_file=Path("custom_input.xlsx"),
    output_file=Path("custom_output.xlsx"),
    max_workers=8
)

# Check results
if success:
    print(f"Successfully analyzed {result.successful} repositories")
    print(f"Failed: {result.failed}")
    print(f"Success rate: {result.success_rate():.1f}%")
    for url, grade in result.results.items():
        print(f"  {url}: {grade:.2f}%")
else:
    print("Analysis failed")
    if result.errors:
        for url, error in result.errors.items():
            print(f"  Error in {url}: {error}")
```

## Configuration

### Worker Threads

Adjust the number of concurrent threads based on system resources:

- **2-4 threads**: Conservative, minimal system load
- **4-6 threads**: Balanced, recommended for most systems
- **6-8 threads**: Aggressive, suitable for powerful machines
- **>8 threads**: May cause resource exhaustion

**Default**: 4 threads

### Timeout Settings

- **Repository Clone Timeout**: 60 seconds per repository
- **Thread Executor Timeout**: 300 seconds total

### File Exclusions

The analyzer automatically skips these directories:
- `.git`: Version control directories
- `__pycache__`: Python cache files
- `.venv`, `venv`: Virtual environments
- `node_modules`: npm packages

## Testing

### Run All Tests

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest test_analyzer.py -v
pytest test_excel_processor.py -v
pytest test_processor.py -v
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Test Categories

1. **test_analyzer.py** (30+ tests)
   - Python file analysis
   - Repository cloning
   - Error handling

2. **test_excel_processor.py** (25+ tests)
   - Excel reading/writing
   - URL extraction
   - Data formatting

3. **test_processor.py** (20+ tests)
   - Multi-threaded processing
   - Result aggregation
   - Thread safety

**Total Coverage**: 100+ comprehensive tests

## Error Handling

### Network Errors

- **Inaccessible Repository**: Logged as error, processing continues
- **Timeout**: 60-second timeout per clone operation
- **Authentication Issues**: Gracefully skipped with error message

### File Errors

- **No Python Files**: Recorded as 0.0 grade with error message
- **Unreadable Files**: Skipped with warning, processing continues
- **Permission Denied**: Handled gracefully with error logging

### Excel Errors

- **Missing Input File**: Raises FileNotFoundError with clear message
- **Invalid Format**: Logs warning and processes available data
- **Write Failure**: Returns False, detailed error logged

## Logging

### Log Levels

- **INFO**: High-level milestones, analysis completion
- **DEBUG**: Detailed operations, file analysis, thread info
- **WARNING**: Non-critical issues, skipped files
- **ERROR**: Processing failures, missing files

### Enable Debug Logging

```bash
python main.py --verbose
```

### Log Output Example

```
2024-01-15 10:30:45 - root - INFO - =============================================================
2024-01-15 10:30:45 - root - INFO - Repository Python Analyzer Agent
2024-01-15 10:30:45 - root - INFO - Configuration:
2024-01-15 10:30:45 - root - INFO -   Project root: /path/to/project
2024-01-15 10:30:45 - root - INFO -   Input file: output/output12.xlsx
2024-01-15 10:30:45 - root - INFO -   Worker threads: 4
2024-01-15 10:30:45 - analyzer - DEBUG - Worker thread processing https://github.com/test/repo
2024-01-15 10:30:46 - analyzer - INFO - Found 45 Python files in repository
2024-01-15 10:30:47 - analyzer - INFO - Grade: 78.50%
```

## Performance Considerations

### Repository Size Impact

- **Small repos** (<50 files): < 5 seconds
- **Medium repos** (50-500 files): 5-30 seconds
- **Large repos** (500+ files): 30-120 seconds

### Optimization Tips

1. **Increase Workers**: More threads for network-bound operations
2. **Local Clones**: Use file:// URLs for local testing
3. **Selective Analysis**: Filter input data before processing
4. **Timeout Tuning**: Adjust timeouts for very large repositories

## Troubleshooting

### GitPython Installation Issues

```bash
# Ensure Git is installed
git --version

# Reinstall GitPython
uv pip uninstall GitPython
uv pip install GitPython>=3.1.0
```

### Excel File Errors

```bash
# Verify input file exists
ls -l output/output12.xlsx

# Check Excel format
python -c "import openpyxl; wb = openpyxl.load_workbook('output/output12.xlsx')"
```

### Permission Denied Errors

```bash
# Ensure write permissions for output directory
mkdir -p output
chmod 755 output
```

### Memory Issues with Large Repositories

Reduce worker threads:
```bash
python main.py --workers 2
```

## Project Standards

### Code Quality

- **Type Hints**: Full type annotations throughout
- **Docstrings**: Comprehensive documentation for all classes/methods
- **Error Handling**: Try-except blocks with detailed logging
- **Logging**: Logging at all major operations
- **Testing**: 100+ test cases covering edge cases

### Path Handling

- Always use relative paths (relative to project root)
- Use `pathlib.Path` for cross-platform compatibility
- No absolute path hardcoding

### Package Structure

```
agent2/
├── __init__.py              # Package initialization with logging
├── analyzer.py              # Core analysis engine
├── excel_processor.py       # Excel file handling
├── processor.py             # Multi-threaded processing
├── extractor.py             # Workflow orchestration
├── main.py                  # Standalone runner
├── test_*.py                # Unit tests (100+ tests)
├── pyproject.toml           # Package configuration
├── README.md                # This file
├── IMPLEMENTATION_SUMMARY.md # Implementation details
├── PLAN.md                  # Original specification
└── .gitignore               # Git exclusions
```

## Future Enhancements

### Potential Improvements

1. **Repository Analysis**
   - Add cyclomatic complexity metrics
   - Measure code duplication
   - Analyze import dependencies
   - Track test coverage

2. **Performance**
   - Implement caching for analyzed repositories
   - Add incremental analysis (skip unchanged repos)
   - Support parallel file reading

3. **Output**
   - Generate HTML reports
   - Create visualization charts
   - Export to JSON/CSV formats

4. **Integration**
   - GitHub API integration for metadata
   - Automatic updates from repository changes
   - Slack/email notifications

## Support and Contribution

For issues, questions, or contributions:

1. Check the IMPLEMENTATION_SUMMARY.md for technical details
2. Review test cases in test_*.py for usage examples
3. Enable verbose logging with `--verbose` for debugging
4. Check project standards in CLAUDE.md

## License

This agent is part of the E19_agents_pipe project and follows the project's license.

## Changelog

### Version 0.1.0 (Initial Release)

- Full repository analysis implementation
- Multi-threaded processing with 4-8 workers
- Comprehensive unit tests (100+ test cases)
- Excel input/output integration
- Detailed logging and error handling
- Production-ready implementation
