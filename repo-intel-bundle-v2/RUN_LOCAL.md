# Running Locally (Enterprise Edition)

This guide describes how to run the AI DevOps Governance Console in environments where `make` is not available.

## 1. Prerequisites
- Python 3.10+ installed
- `GITHUB_TOKEN` set in `.env`

## 2. Dependencies
Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[ui]"
```

## 3. Running the Console (UI)
To launch the dashboard:

```bash
python3 scripts/run_ui.py
```
> Access at `http://localhost:8501`

## 4. Running the Orchestrator
To run an assessment pipeline from the command line:

```bash
python3 scripts/run_orchestrator.py \
    --project my-audit \
    --repos https://github.com/myorg/repo1 https://github.com/myorg/repo2
```

## 5. Running a Sample
To test the system with default data:

```bash
python3 scripts/run_sample_project.py
```

## 6. Directory Structure
- `ui/`: Streamlit application code
- `orchestrator/`: Pipeline logic and EventBus
- `agents/`: AI Agent implementations
- `scripts/`: Execution entry points (No Make required)
