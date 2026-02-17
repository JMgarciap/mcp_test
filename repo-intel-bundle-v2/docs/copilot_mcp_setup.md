# Copilot & VS Code MCP Setup

To use `repo-intel` with GitHub Copilot Chat, you must register the STDIO server in your VS Code configuration.

## 1. Locate your Python Interpreter
Run this in your terminal to get the absolute path:
```bash
which python
# Example: /Users/username/repo-intel-bundle-v2/.venv/bin/python
```

## 2. Edit VS Code Settings
Open `.vscode/settings.json` (workspace) or your User Settings.
Add the `github.copilot.chat.mcpServers` block:

```json
{
  "github.copilot.chat.mcpServers": {
    "repo-intel": {
      "command": "/ABSOLUTE/PATH/TO/.venv/bin/python",
      "args": [
        "-m",
        "orchestrator.server_stdio"
      ],
      "cwd": "/ABSOLUTE/PATH/TO/repo-intel-bundle-v2",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "GITHUB_TOKEN": "ghp_your_token_here_if_not_in_env_file"
      }
    }
  }
}
```
> **Note**: Replace `/ABSOLUTE/PATH/TO/...` with your actual paths.

## 3. Verify Connection
1. Reload VS Code (`Cmd+Shift+P` -> `Developer: Reload Window`).
2. Open Copilot Chat.
3. Type `@repo-intel` and look for the tools list.
4. Try: `@repo-intel ping` (if implemented) or `@repo-intel /help`.

## 4. Troubleshooting
- **No Tools?**: Check the "Output" tab in VS Code and select "GitHub Copilot Chat" to see server logs.
- **Error 127?**: Python path is wrong.
- **Module not found?**: Ensure `cwd` is set correctly to the project root.
