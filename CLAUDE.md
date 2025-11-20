# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**E19_agents_pipe** is an intelligent exercise submission pipeline that processes student submissions through a series of specialized agents. Each agent transforms data and adds value:

1. **Agent1** (Gmail Exercise Extractor): Extracts exercise submissions from Gmail and generates `output12.xlsx`
2. **Agent2** (Repository Python Analyzer): Analyzes code quality of student repositories and adds grades to `output23.xlsx`
3. **Agent3** (Excel Greeting Transformer): Adds personalized greetings based on grades to `output34.xlsx`
4. **Agent4** (Gmail Draft Creator): Creates personalized Gmail drafts for sending feedback to students

This is a **working implementation** demonstrating autonomous agent workflows with data transformation pipelines, not a template.

## High-Level Architecture

### Pipeline Flow

```
Student Submission (Gmail)
    ↓
[Agent1: Gmail Exercise Extractor]
    → Extracts email metadata and GitHub URLs
    → Outputs: output/output12.xlsx (ID, Date, Subject, Repo URL, Success)
    ↓
[Agent2: Repository Python Analyzer]
    → Clones repositories and analyzes Python code structure
    → Calculates grades based on file size distribution
    → Outputs: output/output23.xlsx (adds 'grade' column, 0-100%)
    ↓
[Agent3: Excel Greeting Transformer]
    → Generates personalized greetings (Eddie Murphy style for grades 0-60, Donald Trump style for grades >60)
    → Outputs: output/output34.xlsx (adds 'greeting' column)
    ↓
[Agent4: Gmail Draft Creator]
    → Creates Gmail drafts with personalized feedback
    → Outputs: Gmail Drafts folder (ready for manual review)
```

### Directory Structure

- **`.claude/agents/`**: Four independent agent implementations
  - Each agent is a standalone Python package with its own `pyproject.toml`
  - Each agent has comprehensive test suites (40-100+ tests per agent)
  - Each agent includes detailed README.md documentation
- **`output/`**: Pipeline output files
  - `output12.xlsx`: Agent1 extraction results
  - `output23.xlsx`: Agent2 analysis results
  - `output34.xlsx`: Agent3 transformation results
  - Additional files from various agent executions
- **`.claude/commands/`**: Workflow documentation (test.md, refactor.md, review.md)
- **`.claude/skills/`**: Custom skills (Eddie Murphy and Donald Trump joke generators)

## Python Project Standards

All Python development must follow:

- **Path Resolution**: Never use absolute paths. Use relative paths or `pathlib.Path` for cross-platform compatibility.
- **Package Structure**: Every component/module must be a proper Python package with `__init__.py` files.
- **Logging**: Implement logging at all major functional steps for observability.
- **Package Management**: Use `uv` for all dependency management.
- **Dependency Tracking**: Always update both `uv.lock` and `pyproject.toml` when adding/modifying dependencies.
- **Output Handling**: Save all generated files to the `output/` folder.

## Common Development Commands

### Running the Main Application

```bash
# From project root
python main.py
```

Interactive menu with options:
1. Clear output folder
2. Run Agent1
3. Run Agent2
4. Run Agent3
5. Run Agent4
6. Run full pipeline (1→2→3→4)
7. Exit

### Running Tests

```bash
# Run all tests in an agent
cd .claude/agents/agent1
pytest -v

# Run specific test file
pytest test_extractor.py -v

# Run with coverage report
pytest --cov=. --cov-report=html
```

### Building and Installation

```bash
# From agent directory
uv pip install -e .

# With development dependencies
uv pip install -e ".[dev]"
```

### Running Agents Directly

```bash
# Agent1: Gmail Exercise Extractor
cd .claude/agents/agent1
python main.py

# Agent2: Repository Python Analyzer
cd .claude/agents/agent2
python main.py --workers 4

# Agent3: Excel Greeting Transformer
cd .claude/agents/agent3
python main.py

# Agent4: Gmail Draft Creator
cd .claude/agents/agent4
python main.py --dry-run  # Preview mode before creating drafts
```

## Main Application

### Overview
The main application (`main.py` in project root) provides a unified CLI interface for managing the entire pipeline. It handles:
- Menu-driven user interaction
- Agent orchestration and execution
- Output folder management
- Pipeline sequencing
- Error handling and reporting

### Architecture
```
main.py (AgentPipeline class)
├── display_menu()      - Show menu options
├── get_user_choice()   - Get/validate user input
├── clear_output_folder() - Delete output files
├── run_agent(n)        - Execute single agent
├── run_pipeline()      - Run all agents sequentially
└── run()               - Main application loop
```

### Key Features
- ✓ Cross-platform (Windows/Linux/Mac)
- ✓ 10-minute timeout per agent (configurable)
- ✓ Real-time output streaming
- ✓ Pipeline summary reporting
- ✓ Graceful error handling
- ✓ Keyboard interrupt support (Ctrl+C)

### Path Resolution
The main application correctly resolves agent paths:
- All agents are in `.claude/agents/agent{1-4}/`
- Main app changes directory to agent directory before running
- Agents resolve paths relative to project root
- This enables proper file I/O for all pipeline stages

## Agent-Specific Architecture

### Agent1: Gmail Exercise Extractor (`.claude/agents/agent1/`)

**Purpose**: Extract exercise submissions from Gmail and generate structured Excel report.

**Key Components**:
- `gmail_connector.py`: OAuth 2.0 authentication and Gmail API integration
  - `GmailAuthenticator`: Handles OAuth flow and token management
  - `GmailFetcher`: Fetches emails from Gmail labels
  - `GmailExerciseExtractor`: Orchestrates the extraction workflow
- `extractor.py`: Email processing and Excel generation
  - `URLValidator`, `GitHubURLExtractor`: GitHub URL validation and extraction
  - `DateFormatter`: Standardizes date formats
  - `ExcelGenerator`: Creates formatted Excel output
  - `EmailProcessor`: Orchestrates email processing pipeline

**Output**: `output/output12.xlsx` with columns: ID, Date, Subject, Repo URL, Success

**Tests**: 59+ test cases covering Gmail integration, URL extraction, date formatting, and Excel generation

### Agent2: Repository Python Analyzer (`.claude/agents/agent2/`)

**Purpose**: Analyze GitHub repositories and grade code quality based on Python file size distribution.

**Key Components**:
- `analyzer.py`: Core analysis engine
  - `PythonFileAnalyzer`: Counts lines of code in Python files
  - `RepositoryCloner`: Manages Git cloning and cleanup
  - `RepositoryAnalyzer`: Orchestrates single repository analysis
- `excel_processor.py`: Excel file handling
  - `ExcelReader`: Reads input Excel files
  - `ExcelWriter`: Writes results to Excel
- `processor.py`: Multi-threaded processing
  - `RepositoryProcessor`: Manages concurrent repository analysis with configurable worker threads
- `extractor.py`: Workflow orchestration
  - `RepositoryAnalysisOrchestrator`: Coordinates the complete workflow

**Grading System**: Grade = (Small Python Files / Total Python Files) × 100, where small = <150 lines

**Output**: `output/output23.xlsx` with added 'grade' column (0-100%)

**Tests**: 100+ test cases covering file analysis, threading, error handling

**Performance**: Supports concurrent analysis with configurable worker threads (default: 4, range: 2-8)

### Agent3: Excel Greeting Transformer (`.claude/agents/agent3/`)

**Purpose**: Add personalized greetings based on code quality grades.

**Key Components**:
- `greeting_generator.py`: Generates personality-driven greeting messages
  - `GreetingGenerator.generate_greeting(grade)`: Creates greetings based on performance tier
  - Eddie Murphy style for grades 0-60, Donald Trump style for grades >60
- `excel_processor.py`: Excel read/write operations
- `main.py`: CLI orchestration

**Output**: `output/output34.xlsx` with added 'greeting' column

**Tests**: 40+ test cases covering greeting generation, data preservation, boundary conditions

### Agent4: Gmail Draft Creator (`.claude/agents/agent4/`)

**Purpose**: Create personalized Gmail drafts with feedback for students.

**Key Components**:
- `email_composer.py`: Generates professional email content
  - Subject line extraction from repository URL
  - HTML and plain text email formats
  - Includes greeting, grade, and repository information
- `excel_reader.py`: Reads and validates input Excel data
  - Email address validation
  - GitHub URL validation
  - Separates valid/invalid entries
- `gmail_client.py`: Gmail API integration
  - `GmailAuthenticator`: OAuth 2.0 authentication
  - `GmailDraftCreator`: Creates email drafts in Gmail

**Features**: Dry-run mode for preview, batch processing, rate limiting support

**Output**: Gmail drafts in authenticated user's Gmail account

**Tests**: 43 test cases covering email composition, Excel validation, API integration

## Development Workflows

### Adding Tests

Use `.claude/commands/test.md` for comprehensive testing guidelines:
- Write unit tests for individual components
- Cover edge cases and error conditions
- Verify error handling paths

### Code Quality

Use `.claude/commands/refactor.md` for code quality standards:
- Maintain readability and SOLID principles
- Remove duplication
- Ensure proper code organization

### Code Review

Use `.claude/commands/review.md` for quality checks before committing:
- Verify test coverage
- Check documentation completeness
- Identify potential bugs

## Important Notes on External Dependencies

### Gmail API Credentials

Agents 1 and 4 require Google Cloud OAuth2 credentials:
- Store credentials in `.claude/agents/agentX/credentials.json`
- **NEVER commit** `credentials.json` or `token.json` files
- These should be in `.gitignore`
- First run will guide through OAuth2 authentication

### Repository Cloning (Agent2)

Agent2 requires Git and GitPython:
- Clones repositories to temporary directories
- Automatically cleans up after analysis
- Respects `.gitignore` patterns
- Handles network errors gracefully with timeout (60 seconds per clone)
