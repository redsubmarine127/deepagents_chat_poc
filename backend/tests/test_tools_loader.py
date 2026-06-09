from app.tools.loader import discover_tools, load_tool_catalog, load_tools


def test_discover_tools_reads_metadata(tmp_path):
    tool_file = tmp_path / "tools" / "echo" / "TOOL.md"
    tool_file.parent.mkdir(parents=True)
    tool_file.write_text(
        """---
name: echo
description: Echo input text.
---

# Echo
""",
        encoding="utf-8",
    )
    (tool_file.parent / "tool.py").write_text(
        "def get_tool():\n    return lambda text: text\n",
        encoding="utf-8",
    )

    tools = discover_tools(tmp_path, "tools")

    assert len(tools) == 1
    assert tools[0].id == "echo"
    assert tools[0].name == "echo"
    assert tools[0].description == "Echo input text."


def test_load_tools_skips_bad_tool(tmp_path, caplog):
    good = tmp_path / "tools" / "good"
    bad = tmp_path / "tools" / "bad"
    good.mkdir(parents=True)
    bad.mkdir(parents=True)
    (good / "TOOL.md").write_text("---\nname: good\n---\n", encoding="utf-8")
    (good / "tool.py").write_text("def get_tool():\n    return lambda: 'ok'\n", encoding="utf-8")
    (bad / "TOOL.md").write_text("---\nname: bad\n---\n", encoding="utf-8")
    (bad / "tool.py").write_text("raise RuntimeError('broken')\n", encoding="utf-8")

    tools = load_tools(tmp_path, "tools")

    assert len(tools) == 1
    assert "tools.skip" in "\n".join(record.getMessage() for record in caplog.records)


def test_load_tool_catalog_returns_metadata_and_loaded_tools(tmp_path):
    tool_dir = tmp_path / "tools" / "echo"
    tool_dir.mkdir(parents=True)
    (tool_dir / "TOOL.md").write_text("---\nname: echo\ndescription: Echo input.\n---\n", encoding="utf-8")
    (tool_dir / "tool.py").write_text("def get_tool():\n    return lambda text: text\n", encoding="utf-8")

    catalog = load_tool_catalog(tmp_path, "tools")

    assert [tool.id for tool in catalog.metadata] == ["echo"]
    assert len(catalog.tools) == 1
    assert catalog.tools[0]("ok") == "ok"
