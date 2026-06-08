# Tools

Add local tools as subdirectories containing `TOOL.md` and `tool.py`.

Example:

```text
tools/
  current-time/
    TOOL.md
    tool.py
```

`tool.py` must expose `get_tool()`. The returned object may be a LangChain `BaseTool` or a callable supported by DeepAgents.
