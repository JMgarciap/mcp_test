.PHONY: setup run test sample agents orchestrator clean

PYTHON ?= /opt/homebrew/bin/python3.12

setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -e .

run:
	. .venv/bin/activate && mcp run src/server.py

test:
	@echo "Running tests..."
	@# . .venv/bin/activate && pytest tests/

sample:
	@echo "Running sample analysis..."
	. .venv/bin/activate && python -m src.server --sample

agents:
	@echo "Running agents on latest output..."
	@# Find the latest output directory in outputs/
	@LATEST_DIR=$$(ls -dt outputs/*/ | head -1); \
	if [ -z "$$LATEST_DIR" ]; then \
		echo "No output directory found. Run 'make sample' first."; \
		exit 1; \
	fi; \
	echo "Targeting: $$LATEST_DIR"; \
	. .venv/bin/activate && \
	for f in $$LATEST_DIR/repos/*.json; do \
		echo "Analyzing $$f..."; \
		python agents/vulnerability_agent.py "$$f" "$$LATEST_DIR/agents"; \
		python agents/test_coverage_agent.py "$$f" "$$LATEST_DIR/agents"; \
	done; \
	echo "Running Integrator..."; \
	. .venv/bin/activate && python agents/integrator_agent.py "$$LATEST_DIR"

orchestrator:
	@echo "Running Orchestrator (End-to-End)..."
	. .venv/bin/activate && PYTHONPATH=. mcp run orchestrator/server.py

ui-install:
	@echo "Installing UI dependencies..."
	. .venv/bin/activate && pip install -e ".[ui]"

ui:
	@echo "Starting Streamlit UI..."
	. .venv/bin/activate && PYTHONPATH=. streamlit run ui/streamlit_app.py

tail:
	@echo "Tailing events..."
	@if [ -z "$(PROJECT)" ]; then \
		echo "Usage: make tail PROJECT=<project_name>"; \
		exit 1; \
	fi
	. .venv/bin/activate && PYTHONPATH=. python tools/tail_events.py --project $(PROJECT)

clean:
	rm -rf .venv outputs/*

mcp-http:
	$(PYTHON) scripts/start_mcp_server.py

mcp-stdio:
	$(PYTHON) -m orchestrator.server_stdio
