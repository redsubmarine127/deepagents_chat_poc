from pathlib import Path


def read_frontmatter(file_path: Path) -> dict[str, str]:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    return parse_frontmatter_lines(lines)


def parse_frontmatter_lines(lines: list[str]) -> dict[str, str]:
    if not lines or lines[0].strip() != "---":
        return {}

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = _strip_wrapping_quotes(value.strip())
    return metadata


def _strip_wrapping_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
