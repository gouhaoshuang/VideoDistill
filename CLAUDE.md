# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VideoDistill is a Python-based AI video note generation tool using Google Gemini AI. It analyzes video content and generates structured Markdown notes through a Streamlit web interface.

## Development Commands

### Running the Application

```bash
# Windows
.\run.bat

# Using conda (cross-platform)
conda run -n videodistill streamlit run main.py

# Or with explicit Python
conda activate videodistill
streamlit run main.py
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_outline_parser.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov-report=html:tests/.temp/htmlcov --cov-report=term-missing
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint
ruff check .
```

### Environment Setup

```bash
# Create conda environment
conda create -n videodistill python=3.11 -y
conda activate videodistill

# Install dependencies
pip install -r requirements.txt
```

**API Key**: Set `GOOGLE_API_KEY` environment variable (no `.env` file - system env var only).

## Architecture

### Core Components

```
main.py                    # Streamlit web UI
├── GeminiClient          # API wrapper with retry logic
├── NoteGenerator         # Orchestration for note generation
│   ├── generate_outline()       # Step 1: Create video outline
│   ├── parse_outline_to_segments()  # Step 2: Parse outline into chapters
│   ├── generate_segment_note()  # Step 3: Generate per-chapter notes
│   └── merge_notes()            # Step 4: Combine final output
├── VideoFileManager      # Hash-based caching/resume system
└── OutlineParser         # Markdown chapter extraction
```

### Generation Modes

**Segmented Mode** (default for long videos):
1. Upload video → Generate outline
2. Parse outline into chapters (supports "第一章", "第1章", "Chapter 1")
3. Generate notes per-chapter (resume-capable)
4. Merge into final notes

**Direct Mode** (for short videos):
1. Upload video → Generate complete notes in one shot

### Caching System

Videos are identified by hash: `MD5(filename + filesize)[:12]`

Output directory structure:
```
outputs/
└── YYYYMMDD_hash/           # One per unique video
    ├── metadata.json        # Video metadata
    ├── outline.md           # Generated outline
    ├── segment_01.md        # Per-chapter notes
    ├── segment_02.md
    ├── ...
    ├── direct_note.md       # Direct mode output
    └── final_notes.md       # Merged final output
```

Caching enables:
- Skip re-processing on re-upload
- Resume interrupted segment generation
- Re-use cached outline/segments

### Key Files

| File | Purpose |
|------|---------|
| [config.py](config.py) | Constants for models, modes, paths |
| [src/gemini_client.py](src/gemini_client.py) | Gemini API wrapper with 429 retry (exponential backoff) |
| [src/note_generator.py](src/note_generator.py) | Core orchestration, mode selection |
| [src/file_utils.py](src/file_utils.py) | VideoFileManager for caching |
| [src/outline_parser.py](src/outline_parser.py) | Regex-based chapter extraction |
| [src/prompt_templates.py](src/prompt_templates.py) | Loads prompts from `src/prompts/*.txt` |

### Prompt Templates

Edit prompts in `src/prompts/`:
- `outline_prompt.txt` - Video analysis outline generation
- `segment_prompt.txt` - Per-chapter note generation
- `direct_prompt.txt` - One-shot note generation
- `system_instruction.txt` - System-level AI instructions

## Configuration

Models are configured in [config.py](config.py:5-10):
```python
DEFAULT_MODEL = "gemini-2.0-flash"
AVAILABLE_MODELS = ["gemini-3-pro-preview", "gemini-3-flash-preview"]
```

Update these when new Gemini models are released.

## Testing Patterns

Tests use pytest with fixtures. See [tests/test_outline_parser.py](tests/test_outline_parser.py) for patterns:
- `setup_method()` for per-test initialization
- `tmp_path` pytest fixture for file I/O tests
- Comprehensive edge case coverage (empty input, mixed formats, etc.)

Test output goes to `tests/.temp/` (configured in [pytest.ini](pytest.ini)).

## Important Notes

- **No .env file**: API key via `GOOGLE_API_KEY` environment variable only
- **File retention**: Gemini files expire after 48 hours
- **Rate limiting**: Built-in retry for 429 errors (max 5 retries, exponential backoff)
- **Video limit**: Max 2GB file size
- **Encoding**: All files UTF-8, supports Chinese filenames


