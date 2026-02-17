# Limitations

## Static Analysis
This tool performs **static analysis** only. It does not:
-   Run the code.
-   Build the project.
-   Execute tests.
-   Verify if credentials are valid (live testing).

## GitHub API
-   Subject to GitHub API rate limits.
-   Requires a valid Token for private repos and higher rate limits.
-   Base64 decoding of large files may be slow or limited by memory.

## Signal Detection
-   **Secrets**: Uses simple regex patterns. **High false positive rate**. Not a replacement for a dedicated secret scanner (e.g., TruffleHog).
-   **Tests**: Relies on file naming conventions. May miss non-standard test setups.
-   **Docker**: Does not parse the full Dockerfile AST, uses line-based heuristics.
