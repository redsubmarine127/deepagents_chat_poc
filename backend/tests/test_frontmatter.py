from app.metadata.frontmatter import parse_frontmatter_lines


def test_parse_frontmatter_supports_colons_and_quotes():
    metadata = parse_frontmatter_lines(
        [
            "---",
            'name: "clock: utc"',
            "description: Return time: now",
            "---",
            "# Body",
        ]
    )

    assert metadata == {"name": "clock: utc", "description": "Return time: now"}


def test_parse_frontmatter_returns_empty_without_header():
    assert parse_frontmatter_lines(["# Body"]) == {}


def test_parse_frontmatter_tolerates_missing_closing_marker():
    metadata = parse_frontmatter_lines(["---", "name: demo"])

    assert metadata == {"name": "demo"}
