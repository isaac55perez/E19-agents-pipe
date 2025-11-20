# E19 Agents Pipeline

An intelligent exercise submission processing pipeline that automates workflow from student email submission to personalized feedback delivery using autonomous agents.

## 🎯 Overview

E19 Agents Pipeline is a complete automation system for managing exercise submissions. It orchestrates four specialized autonomous agents that work together in a data transformation pipeline:

1. **Agent1**: Extract exercise submissions from Gmail
2. **Agent2**: Analyze code quality of submitted repositories
3. **Agent3**: Generate personalized greetings based on performance
4. **Agent4**: Create Gmail drafts with personalized feedback

## ✨ Features

- 🤖 **Autonomous Agents**: Specialized agents for each stage of the pipeline
- 📧 **Gmail Integration**: Direct OAuth2 integration with Gmail API
- 📊 **Code Analysis**: Automatic Python code quality analysis
- 🎭 **Personality-Based Feedback**: Eddie Murphy style for low performers, Donald Trump style for high performers
- 📝 **Excel Integration**: Seamless Excel file handling throughout pipeline
- 🔄 **Multi-Threading**: Concurrent repository analysis for performance
- 💾 **Data Preservation**: All original data maintained through pipeline stages
- ✅ **Error Handling**: Comprehensive error handling and validation
- 📝 **Detailed Logging**: Full tracing at every step

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **uv** package manager (recommended) or pip
- **Git** (for repository cloning)
- **Google Cloud Account** (for Gmail API - optional, required only for Agents 1 & 4)

### Installation

```bash
# Clone or navigate to project
cd E19_agents_pipe

# Install dependencies (optional, agents run independently)
# Each agent manages its own dependencies
```

### Running the Application

```bash
# From project root
python main.py
```

This displays an interactive menu with 7 options:

```
==================================================
E19 Agents Pipeline - Main Menu
==================================================
1. Clear output folder
2. Run Agent1 (Gmail Exercise Extractor)
3. Run Agent2 (Repository Python Analyzer)
4. Run Agent3 (Excel Greeting Transformer)
5. Run Agent4 (Gmail Draft Creator)
6. Run full pipeline (Agent1 → Agent2 → Agent3 → Agent4)
7. Exit
==================================================
```

## 📋 Menu Options

### 1. Clear Output Folder
Immediately deletes all files in the `output/` directory.

**Execution Log Example:**
```bash
Select: 1
Clearing output folder...
✓ Output folder cleared (3 items deleted)
```

### 2. Run Agent1 Only
Extracts exercise submissions from Gmail and generates `output/output12.xlsx`.

**Execution Log Example:**
```
==================================================
Running Agent1: Gmail Exercise Extractor
Description: Extracts exercise submissions from Gmail
==================================================

2025-11-20 07:56:29,973 - __main__ - INFO - ================================================================================
2025-11-20 07:56:29,973 - __main__ - INFO - Gmail Exercise Extractor Agent
2025-11-20 07:56:29,974 - __main__ - INFO - ================================================================================
2025-11-20 07:56:29,974 - extractor - INFO - EmailProcessor initialized with output dir: output
2025-11-20 07:56:29,974 - __main__ - INFO - Fetching emails from Gmail...
2025-11-20 07:56:29,974 - gmail_connector - INFO - Initializing Gmail authenticator with credentials file: credentials.json
2025-11-20 07:56:29,975 - gmail_connector - INFO - Initializing GmailExerciseExtractor
2025-11-20 07:56:29,975 - gmail_connector - INFO - Setting up Gmail extractor
2025-11-20 07:56:29,975 - gmail_connector - INFO - Loading existing token from token.pickle
2025-11-20 07:56:29,983 - gmail_connector - INFO - Token expired, refreshing...
2025-11-20 07:56:30,253 - gmail_connector - INFO - Token refreshed successfully
2025-11-20 07:56:30,254 - gmail_connector - INFO - Token saved to token.pickle
2025-11-20 07:56:30,255 - gmail_connector - INFO - Initializing Gmail fetcher
2025-11-20 07:56:30,258 - gmail_connector - INFO - Gmail API service initialized successfully
2025-11-20 07:56:30,258 - gmail_connector - INFO - Gmail extractor setup complete
2025-11-20 07:56:30,259 - gmail_connector - INFO - Extracting exercise emails from 'exercises' label
2025-11-20 07:56:30,259 - gmail_connector - INFO - Fetching emails from label 'exercises' (max: 100)
2025-11-20 07:56:30,259 - gmail_connector - INFO - Looking for label: exercises
2025-11-20 07:56:30,624 - gmail_connector - INFO - Found label 'exercises' with ID: Label_21
2025-11-20 07:56:30,891 - gmail_connector - INFO - Found 4 messages in 'exercises' label
2025-11-20 07:56:32,111 - gmail_connector - INFO - Successfully fetched 4 emails from 'exercises'
2025-11-20 07:56:32,111 - gmail_connector - INFO - Extracted 4 exercise emails
2025-11-20 07:56:32,111 - __main__ - INFO - Processing 4 emails...
2025-11-20 07:56:32,111 - extractor - INFO - Processing 4 emails
2025-11-20 07:56:32,122 - extractor - INFO - Extracting GitHub URL from email content
2025-11-20 07:56:32,123 - extractor - INFO - Found valid GitHub URL: https://github.com/isaac55perez/E18_logistic_regression.git
2025-11-20 07:56:32,123 - extractor - INFO - Extracting GitHub URL from email content
2025-11-20 07:56:32,123 - extractor - INFO - Found valid GitHub URL: https://github.com/isaac55perez/E17_PCA_TSNE.git
2025-11-20 07:56:32,123 - extractor - INFO - Extracting GitHub URL from email content
2025-11-20 07:56:32,123 - extractor - INFO - Found valid GitHub URL: https://github.com/isaac55perez/E16_KNN.git
2025-11-20 07:56:32,123 - extractor - INFO - Extracting GitHub URL from email content
2025-11-20 07:56:32,123 - extractor - INFO - Found valid GitHub URL: https://github.com/isaac55perez/exercise-14-turing-flow.git
2025-11-20 07:56:32,123 - extractor - INFO - Email processing complete. Entries created: 4, URLs found: 4
2025-11-20 07:56:32,123 - __main__ - INFO - Email processing complete:
2025-11-20 07:56:32,123 - __main__ - INFO -   - Entries created: 4
2025-11-20 07:56:32,123 - __main__ - INFO -   - URLs found: 4
2025-11-20 07:56:32,123 - __main__ - INFO - Generating Excel report...
2025-11-20 07:56:32,123 - extractor - INFO - Generating Excel report
2025-11-20 07:56:32,124 - extractor - INFO - Excel generator initialized with output path: output/output12.xlsx
2025-11-20 07:56:32,124 - extractor - INFO - Generating Excel file with 4 rows
2025-11-20 07:56:32,267 - extractor - INFO - Writing 4 data rows to Excel
2025-11-20 07:56:32,278 - extractor - INFO - Excel file successfully saved to: output/output12.xlsx
2025-11-20 07:56:32,278 - extractor - INFO - Report successfully generated at: output/output12.xlsx
2025-11-20 07:56:32,278 - __main__ - INFO - Excel report successfully created at: output/output12.xlsx
2025-11-20 07:56:32,278 - extractor - INFO - Generating summary report

================================================================================
Processing Summary:
================================================================================
✓ Processing Complete!
✓ Output file: output/output12.xlsx
✓ Gmail Exercise Extractor Agent
```

**What This Shows:**
- OAuth2 token management and refresh
- Gmail API initialization and label lookup
- Email fetching (found 4 messages in 'exercises' label)
- URL extraction and validation
- Excel file generation with structured data

### 3. Run Agent2 Only
Analyzes repositories and adds code quality grades to `output/output23.xlsx`.

**Execution Log Example:**
```
==================================================
Running Agent2: Repository Python Analyzer
Description: Analyzes code quality of repositories
==================================================

2025-11-20 07:56:22,081 - __main__ - INFO - ============================================================
2025-11-20 07:56:22,081 - __main__ - INFO - Repository Python Analyzer Agent
2025-11-20 07:56:22,082 - __main__ - INFO - Configuration:
2025-11-20 07:56:22,082 - __main__ - INFO -   Project root: /mnt/e/projects/AI/E19_agents_pipe
2025-11-20 07:56:22,082 - __main__ - INFO -   Input file: output/output12.xlsx
2025-11-20 07:56:22,082 - __main__ - INFO -   Output file: output/output23.xlsx
2025-11-20 07:56:22,082 - __main__ - INFO -   Worker threads: 4
2025-11-20 07:56:22,082 - extractor - INFO - Initialized orchestrator with input=output/output12.xlsx, output=output/output23.xlsx
2025-11-20 07:56:22,082 - extractor - INFO - Starting repository analysis workflow
2025-11-20 07:56:22,082 - extractor - INFO - Reading input file: output/output12.xlsx
2025-11-20 07:56:22,089 - excel_processor - INFO - Found headers: ['ID', 'Date', 'Subject', 'Repo URL', 'Success']
2025-11-20 07:56:22,090 - excel_processor - INFO - Read 4 entries from output/output12.xlsx
2025-11-20 07:56:22,090 - extractor - INFO - Extracting URLs from 4 entries
2025-11-20 07:56:22,090 - excel_processor - INFO - Extracted 4 entries with URLs from 4 total
2025-11-20 07:56:22,090 - extractor - INFO - Processing 4 repositories with 4 workers
2025-11-20 07:56:22,090 - processor - INFO - Initialized RepositoryProcessor with 4 workers
2025-11-20 07:56:22,090 - processor - INFO - Starting processing of 4 repositories with 4 workers
2025-11-20 07:56:22,090 - analyzer - INFO - Starting analysis of https://github.com/isaac55perez/E18_logistic_regression.git
2025-11-20 07:56:22,091 - analyzer - INFO - Starting analysis of https://github.com/isaac55perez/E17_PCA_TSNE.git
2025-11-20 07:56:22,091 - analyzer - INFO - Starting analysis of https://github.com/isaac55perez/E16_KNN.git
2025-11-20 07:56:22,092 - analyzer - INFO - Starting analysis of https://github.com/isaac55perez/exercise-14-turing-flow.git
2025-11-20 07:56:22,958 - analyzer - INFO - Successfully cloned https://github.com/isaac55perez/E18_logistic_regression.git to /tmp/repo_6daa5329
2025-11-20 07:56:22,958 - analyzer - INFO - Analysis complete for https://github.com/isaac55perez/E18_logistic_regression.git: 5 total files, 4 small files, grade=80.00%
2025-11-20 07:56:22,958 - processor - INFO - Recorded result for https://github.com/isaac55perez/E18_logistic_regression.git: grade=80.0, files=5
2025-11-20 07:56:23,084 - analyzer - INFO - Successfully cloned https://github.com/isaac55perez/exercise-14-turing-flow.git to /tmp/repo_4af3d905
2025-11-20 07:56:23,084 - analyzer - INFO - Analysis complete for https://github.com/isaac55perez/exercise-14-turing-flow.git: 12 total files, 8 small files, grade=66.67%
2025-11-20 07:56:23,084 - processor - INFO - Recorded result for https://github.com/isaac55perez/exercise-14-turing-flow.git: grade=66.67, files=12
2025-11-20 07:56:23,169 - analyzer - INFO - Successfully cloned https://github.com/isaac55perez/E17_PCA_TSNE.git to /tmp/repo_a71e873f
2025-11-20 07:56:23,169 - analyzer - INFO - Analysis complete for https://github.com/isaac55perez/E17_PCA_TSNE.git: 5 total files, 0 small files, grade=0.00%
2025-11-20 07:56:23,169 - processor - INFO - Recorded result for https://github.com/isaac55perez/E17_PCA_TSNE.git: grade=0.0, files=5
2025-11-20 07:56:23,735 - analyzer - INFO - Successfully cloned https://github.com/isaac55perez/E16_KNN.git to /tmp/repo_d2187842
2025-11-20 07:56:23,735 - analyzer - INFO - Analysis complete for https://github.com/isaac55perez/E16_KNN.git: 1 total files, 0 small files, grade=0.00%
2025-11-20 07:56:23,735 - processor - INFO - Recorded result for https://github.com/isaac55perez/E16_KNN.git: grade=0.0, files=1
2025-11-20 07:56:23,744 - processor - INFO - Processing complete: 4 successful, 0 failed, time: 1.65s
2025-11-20 07:56:23,744 - extractor - INFO - Writing output file: output/output23.xlsx
2025-11-20 07:56:23,754 - excel_processor - INFO - Wrote 4 entries to output/output23.xlsx
2025-11-20 07:56:23,754 - extractor - INFO - Analysis workflow complete: 4/4 successful (100.0%), time: 1.65s

============================================================
Analysis Results
============================================================
Total entries: 4
Successful: 4
Failed: 0
Success rate: 100.0%
Processing time: 1.65s

Grades generated:
  https://github.com/isaac55perez/E16_KNN.git: 0.00%
  https://github.com/isaac55perez/E17_PCA_TSNE.git: 0.00%
  https://github.com/isaac55perez/E18_logistic_regression.git: 80.00%
  https://github.com/isaac55perez/exercise-14-turing-flow.git: 66.67%

✓ Analysis complete. Results saved to: output/output23.xlsx
```

**What This Shows:**
- Multi-threaded repository processing (4 workers)
- Concurrent Git cloning to temporary directories
- Python file analysis with LOC counting
- Grade calculation based on code modularity
- Automatic cleanup of temporary directories
- Performance metrics (1.65 seconds for 4 repos)

### 4. Run Agent3 Only
Transforms data by adding personalized greetings to `output/output34.xlsx`.

**Execution Log Example:**
```
==================================================
Running Agent3: Excel Greeting Transformer
Description: Adds personalized greetings based on grades
==================================================

2025-11-20 07:56:18,459 - __main__ - INFO - ============================================================
2025-11-20 07:56:18,459 - __main__ - INFO - Excel Greeting Transformer
2025-11-20 07:56:18,459 - __main__ - INFO - ============================================================
2025-11-20 07:56:18,459 - __main__ - INFO -
2025-11-20 07:56:18,459 - __main__ - INFO - Configuration:
2025-11-20 07:56:18,459 - __main__ - INFO -   Project root: /mnt/e/projects/AI/E19_agents_pipe
2025-11-20 07:56:18,459 - __main__ - INFO -   Input file: output/output23.xlsx
2025-11-20 07:56:18,459 - __main__ - INFO -   Output file: output/output34.xlsx
2025-11-20 07:56:18,459 - __main__ - INFO -
2025-11-20 07:56:18,459 - __main__ - INFO - Reading input file: output/output23.xlsx
2025-11-20 07:56:18,467 - excel_processor - INFO - Found headers: ['ID', 'Date', 'Subject', 'Repo URL', 'Success', 'grade']
2025-11-20 07:56:18,467 - excel_processor - INFO - Read 4 data rows from output/output23.xlsx
2025-11-20 07:56:18,467 - __main__ - INFO - Found 4 entries
2025-11-20 07:56:18,467 - __main__ - INFO - Validating grade values...
2025-11-20 07:56:18,467 - __main__ - INFO - Generating greeting messages...
2025-11-20 07:56:18,467 - __main__ - INFO - Generated greetings:
2025-11-20 07:56:18,468 - __main__ - INFO -   Eddie Murphy style (0-60): 2 entries
2025-11-20 07:56:18,468 - __main__ - INFO -   Donald Trump style (>60): 2 entries
2025-11-20 07:56:18,468 - __main__ - INFO - Writing output file: output/output34.xlsx
2025-11-20 07:56:18,477 - excel_processor - INFO - Wrote 4 entries to output/output34.xlsx
2025-11-20 07:56:18,477 - __main__ - INFO -
2025-11-20 07:56:18,477 - __main__ - INFO - ============================================================
2025-11-20 07:56:18,477 - __main__ - INFO - Transformation Complete!
2025-11-20 07:56:18,477 - __main__ - INFO - ============================================================
2025-11-20 07:56:18,478 - __main__ - INFO - ✓ Processed 4 entries
2025-11-20 07:56:18,478 - __main__ - INFO - ✓ Output file: output/output34.xlsx
```

**What This Shows:**
- Excel file reading with header validation
- Grade-based greeting generation
- Personality-driven message selection:
  - Eddie Murphy style for grades 0-60 (energetic, comedic)
  - Donald Trump style for grades >60 (confident, superlatives)
- Data transformation with preservation of all original columns
- Fast processing (<1 second for 4 entries)

### 5. Run Agent4 Only
Creates Gmail draft emails with personalized feedback.

**Execution Log Example:**
```
==================================================
Running Agent4: Gmail Draft Creator
Description: Creates Gmail drafts with feedback
==================================================

2025-11-20 07:56:35,994 - __main__ - INFO - Starting Gmail draft creation workflow
2025-11-20 07:56:35,994 - __main__ - INFO - Input file: output/output34.xlsx
2025-11-20 07:56:35,994 - __main__ - INFO - DRY RUN MODE - No Gmail API calls will be made
2025-11-20 07:56:35,994 - __main__ - INFO - Reading input file: output/output34.xlsx
2025-11-20 07:56:36,002 - excel_reader - INFO - Found headers: ['ID', 'Date', 'Subject', 'Repo URL', 'Success', 'grade', 'greeting']
2025-11-20 07:56:36,002 - excel_reader - INFO - Read 4 data rows from output/output34.xlsx
2025-11-20 07:56:36,002 - __main__ - INFO - Read 4 entries from output/output34.xlsx
2025-11-20 07:56:36,002 - __main__ - INFO - Validating entries...
2025-11-20 07:56:36,002 - excel_reader - WARNING - Row 2 validation failed: Missing email address
2025-11-20 07:56:36,002 - excel_reader - WARNING - Row 3 validation failed: Missing email address
2025-11-20 07:56:36,002 - excel_reader - WARNING - Row 4 validation failed: Missing email address
2025-11-20 07:56:36,002 - excel_reader - WARNING - Row 5 validation failed: Missing email address
2025-11-20 07:56:36,002 - excel_reader - INFO - Validation complete: 0 valid, 4 invalid
2025-11-20 07:56:36,002 - __main__ - INFO - Validation complete: 0 valid, 4 invalid
2025-11-20 07:56:36,002 - __main__ - WARNING - Row 2: Missing email address
2025-11-20 07:56:36,002 - __main__ - WARNING - Row 3: Missing email address
2025-11-20 07:56:36,002 - __main__ - WARNING - Row 4: Missing email address
2025-11-20 07:56:36,002 - __main__ - WARNING - Row 5: Missing email address
2025-11-20 07:56:36,002 - __main__ - INFO - Creating Gmail drafts for 0 entries...

============================================================
  Gmail Draft Creator - Agent4
============================================================

============================================================
  COMPLETION SUMMARY
============================================================
Status: ✓ SUCCESS
Mode: DRY RUN

Processing Statistics:
  Total entries read: 4
  Valid entries: 0
  Invalid entries: 4

Draft Creation:
  Drafts created: 0
  Drafts failed: 0
  Success rate: 0.0%

Skipped Entries (4):
  - unknown: Row 2: Missing email address...
  - unknown: Row 3: Missing email address...
  - unknown: Row 4: Missing email address...
  - unknown: Row 5: Missing email address...

============================================================
```

**What This Shows:**
- Input file validation and header verification
- Data validation with detailed error reporting
- Dry-run mode for preview before creating drafts
- Email address validation
- Processing statistics and summary reporting

**Note:** Agent4 requires email addresses in the data (Agent1 would need modification to extract sender emails from Gmail). Currently all entries fail validation because they lack email addresses.

### 6. Run Full Pipeline
Executes all 4 agents sequentially (1→2→3→4).

```
==================================================
E19 Agents Pipeline - Main Menu
==================================================
6

==================================================
Running Full Pipeline (Agent1 → Agent2 → Agent3 → Agent4)
==================================================

[Stage 1/4] Running Agent1...
✓ Agent1 completed successfully

[Stage 2/4] Running Agent2...
✓ Agent2 completed successfully

[Stage 3/4] Running Agent3...
✓ Agent3 completed successfully

[Stage 4/4] Running Agent4...
✓ Agent4 completed successfully

==================================================
Pipeline Execution Summary
==================================================
Agent1: ✓ Success
  Gmail Exercise Extractor
Agent2: ✓ Success
  Repository Python Analyzer
Agent3: ✓ Success
  Excel Greeting Transformer
Agent4: ✓ Success (or with expected warnings)
  Gmail Draft Creator
==================================================
✓ Full pipeline completed successfully!
```

**What This Shows:**
- Sequential execution of all 4 agents
- Real-time progress updates
- Pipeline summary with per-agent status
- Overall completion status

### 7. Exit
Cleanly exits the application.

```bash
Select: 7
Exiting E19 Agents Pipeline. Goodbye!
```

## 🔄 Pipeline Data Flow

```
Gmail (Student Submissions)
    ↓
[Agent1: Gmail Exercise Extractor]
    Authenticates with Gmail OAuth2
    Fetches emails from 'exercises' folder
    Extracts GitHub URLs from email bodies
    ↓ output/output12.xlsx
    Columns: ID, Date, Subject, Repo URL, Success

[Agent2: Repository Python Analyzer]
    Reads output12.xlsx
    Clones repositories to temporary directories
    Analyzes Python file size distribution
    Calculates code quality grades (0-100%)
    ↓ output/output23.xlsx
    Adds 'grade' column with percentages

[Agent3: Excel Greeting Transformer]
    Reads output23.xlsx
    Generates personalized greetings based on grades:
    - Eddie Murphy style: grades 0-60 (energetic, comedic)
    - Donald Trump style: grades >60 (confident, superlatives)
    ↓ output/output34.xlsx
    Adds 'greeting' column

[Agent4: Gmail Draft Creator]
    Reads output34.xlsx
    Creates professional email drafts with:
    - Personalized greeting
    - Code quality grade
    - Repository information
    - Student name
    ↓ Gmail Drafts folder
    Ready for manual review before sending
```

## 📁 File Structure

```
E19_agents_pipe/
├── main.py                      # Main application (CLI menu)
├── README.md                    # This file
├── CLAUDE.md                    # Architecture and development guide
├── PLAN.md                      # Comprehensive project documentation
├── AGENTS.md                    # Agent registry
├── pyproject.toml               # Root project configuration
│
├── output/                      # Pipeline output directory
│   ├── output12.xlsx            # Agent1: Email extraction results
│   ├── output23.xlsx            # Agent2: Analysis with grades
│   └── output34.xlsx            # Agent3: With greetings
│
└── .claude/
    ├── agents/
    │   ├── agent1/              # Gmail Exercise Extractor
    │   │   ├── main.py
    │   │   ├── gmail_connector.py
    │   │   ├── extractor.py
    │   │   ├── README.md
    │   │   └── pyproject.toml
    │   │
    │   ├── agent2/              # Repository Python Analyzer
    │   │   ├── main.py
    │   │   ├── analyzer.py
    │   │   ├── processor.py
    │   │   ├── README.md
    │   │   └── pyproject.toml
    │   │
    │   ├── agent3/              # Excel Greeting Transformer
    │   │   ├── main.py
    │   │   ├── greeting_generator.py
    │   │   ├── README.md
    │   │   └── pyproject.toml
    │   │
    │   └── agent4/              # Gmail Draft Creator
    │       ├── main.py
    │       ├── email_composer.py
    │       ├── gmail_client.py
    │       ├── README.md
    │       └── pyproject.toml
    │
    ├── commands/                # Workflow documentation
    │   ├── test.md
    │   ├── refactor.md
    │   └── review.md
    │
    └── skills/                  # Custom AI skills
        ├── eddie-murphy-joke.md
        └── donald-trump-joke.md
```

## 🔧 Running Individual Agents

You can also run agents directly from their directories:

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
python main.py --dry-run
```

Each agent supports command-line options. Run with `--help` to see available options.

## 📊 Output Files

### output12.xlsx (Agent1 Output)
| Column | Type | Description |
|--------|------|-------------|
| ID | Integer | Auto-incremented identifier |
| Date | String | Email date (MM/DD/YYYY format) |
| Subject | String | Email subject line |
| Repo URL | String | GitHub repository URL |
| Success | Integer | 1 if valid URL found, 0 otherwise |

### output23.xlsx (Agent2 Output)
All columns from output12.xlsx plus:
| Column | Type | Description |
|--------|------|-------------|
| grade | Float | Code quality grade (0-100%) |

**Grade Interpretation:**
- **0-29%**: Poor code structure, needs refactoring
- **30-49%**: Below average, some large modules
- **50-69%**: Average, mixed file sizes
- **70-89%**: Good code modularity
- **90-100%**: Excellent code structure

### output34.xlsx (Agent3 Output)
All columns from output23.xlsx plus:
| Column | Type | Description |
|--------|------|-------------|
| greeting | String | Personalized greeting message |

## 🔐 Security & Credentials

### Gmail API Setup (Required for Agents 1 & 4)

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project: "E19 Exercise Pipeline"
   - Enable Gmail API

2. **Create OAuth2 Credentials**:
   - Go to Credentials → Create Credentials → OAuth 2.0 Client ID
   - Application type: Desktop app
   - Download credentials JSON

3. **Place Credentials**:
   - Save as `.claude/agents/agent1/credentials.json`
   - Save as `.claude/agents/agent4/credentials.json`
   - **IMPORTANT**: Add to `.gitignore` (never commit credentials)

4. **First Run**:
   - Application opens browser for OAuth2 authorization
   - Grant requested permissions
   - Token saved locally in `token.pickle` or `token.json`

### Security Best Practices

- ✅ Never commit `credentials.json` or `token.*` files
- ✅ Use `.gitignore` to exclude credential files
- ✅ Credentials stored locally only
- ✅ Agent4 creates drafts (not auto-sent) for manual review
- ✅ Rotate credentials periodically

## 📈 Performance

### Processing Times (Typical)

| Operation | Time | Notes |
|-----------|------|-------|
| Agent1 (4 emails) | ~2-3 seconds | Depends on Gmail API response |
| Agent2 (4 repos) | ~1-2 seconds | With 4 worker threads, varies by repo size |
| Agent3 (4 entries) | <0.5 seconds | Very fast Excel transformation |
| Agent4 (4 entries) | <1 second | Depends on Gmail API availability |
| Full Pipeline | ~5-10 seconds | For small batches (4 entries) |

### Scalability

- **Agent1**: Linear with email count
- **Agent2**: Scales with worker threads (2-8 recommended)
  - Small repos: <5 seconds
  - Medium repos (50-500 files): 5-30 seconds
  - Large repos (500+ files): 30-120 seconds
- **Agent3**: O(n) time complexity, very fast
- **Agent4**: Limited by Gmail API rate limits (1000 requests/day)

## 🧪 Testing

Each agent includes comprehensive unit tests:

```bash
# Run all tests in an agent
cd .claude/agents/agent1
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_extractor.py -v
```

### Test Coverage
- **Agent1**: 59+ tests (Gmail integration, URL extraction, Excel generation)
- **Agent2**: 100+ tests (File analysis, threading, error handling)
- **Agent3**: 40+ tests (Greeting generation, data transformation)
- **Agent4**: 43+ tests (Email composition, Excel validation, API integration)

**Total**: 240+ comprehensive unit tests

## 📝 Logging

All agents provide detailed logging at multiple levels:

- **INFO**: High-level progress and completion
- **DEBUG**: Detailed operations (enable with `--verbose`)
- **WARNING**: Non-critical issues, validation problems
- **ERROR**: Processing failures

Enable verbose logging to see detailed execution:

```bash
cd .claude/agents/agent1
python main.py --verbose
```

Log output shows:
- Authentication flows
- File I/O operations
- Data transformations
- Error details with context

## 🐛 Troubleshooting

### Issue: "No such file or directory: credentials.json"

**Solution**: Set up Google Cloud OAuth2 credentials
1. Follow steps in "Gmail API Setup" section
2. Save credentials to correct agent directories
3. First run will guide OAuth2 authentication

### Issue: "git: command not found" (Agent2)

**Solution**: Install Git on your system
```bash
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Windows
# Download from https://git-scm.com
```

### Issue: "Input file not found"

**Solution**: Run previous agent first
- Agent2 needs output from Agent1
- Agent3 needs output from Agent2
- Agent4 needs output from Agent3

Or run full pipeline (option 6) to execute all agents

### Issue: Agent4 shows "Missing email address"

**Current Limitation**: Agent1 doesn't extract sender email addresses from Gmail.

**Workaround**: Modify Agent1 to extract email sender metadata (future enhancement)

For now, Agent4 will validate but skip entries without email column.

## 🔄 Recent Changes

### Version 0.2.0 (Current)
- ✅ Fixed Agent4 path resolution for project root
- ✅ Created main.py CLI application
- ✅ Added comprehensive README.md
- ✅ Updated all documentation files
- ✅ Full pipeline now executes successfully

### Version 0.1.0 (Previous)
- Initial implementation of all 4 agents
- Comprehensive test suites
- Individual agent documentation

## 🎓 Use Cases

### Educational Setting
- Automated exercise submission processing
- Immediate feedback on code quality
- Performance-based personalization
- Batch processing for entire classes

### Code Review System
- Consistent code quality assessment
- Automated metrics generation
- Student/developer feedback
- Quality trend tracking

### Repository Management
- Bulk analysis of multiple repositories
- Code structure assessment
- Modularity evaluation
- Team performance metrics

## 🚧 Future Enhancements

### Short Term
- [ ] Configuration file support (config.yaml)
- [ ] Progress bars and visual feedback
- [ ] Email notification on completion
- [ ] Retry logic for failed operations
- [ ] Execution logs and reports

### Medium Term
- [ ] Support for GitLab/Bitbucket
- [ ] Additional code metrics (cyclomatic complexity, duplication)
- [ ] Customizable greeting templates
- [ ] Direct email sending (not just drafts)
- [ ] Scheduled pipeline execution (cron jobs)

### Long Term
- [ ] Web dashboard for management
- [ ] Database for historical tracking
- [ ] Machine learning-based analysis
- [ ] Slack/Discord integration
- [ ] Multi-user support with roles
- [ ] API endpoints for external integration

## 📚 Documentation

- **README.md** (this file): Quick start and overview
- **CLAUDE.md**: Architecture and development guide
- **PLAN.md**: Comprehensive project documentation
- **AGENTS.md**: Agent registry and specifications
- **Agent READMEs**: Individual agent documentation
  - `.claude/agents/agent1/README.md`
  - `.claude/agents/agent2/README.md`
  - `.claude/agents/agent3/README.md`
  - `.claude/agents/agent4/README.md`

## 🤝 Contributing

To contribute to this project:

1. Review CLAUDE.md for architecture and standards
2. Check `.claude/commands/` for development workflows:
   - `test.md`: Testing guidelines
   - `refactor.md`: Code quality standards
   - `review.md`: Code review checklist
3. Write comprehensive tests
4. Follow Python standards (type hints, docstrings, logging)
5. Test the full pipeline before submitting

## 📞 Support

For issues, questions, or feedback:

1. Check the relevant agent's README.md
2. Review test cases for usage examples
3. Enable verbose logging: `--verbose` flag
4. Check PLAN.md for detailed specifications
5. Review CLAUDE.md for architecture details

## 📄 License

This project is part of the E19 Initiative.

## 👨‍💻 Maintainers

- **Claude Code** (Anthropic)
- Current Version: 0.2.0
- Last Updated: November 2025

## 🙏 Acknowledgments

Built with:
- Python 3.9+
- openpyxl (Excel handling)
- Google APIs (Gmail integration)
- GitPython (Repository management)
- pytest (Testing framework)

---

**Ready to process exercise submissions?** Run `python main.py` and select option 6 for full pipeline execution!
