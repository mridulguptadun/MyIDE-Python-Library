import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "python"
CATALOG_PATH = ROOT / "catalog.json"


def build_catalog():
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    examples = []

    for path in sorted(EXAMPLES_DIR.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        required = {
            "id", "title", "topic", "difficulty", "question",
            "code", "expected_output", "explanation", "validation",
        }
        missing = required - data.keys()
        if missing:
            raise ValueError(f"{path.relative_to(ROOT)} missing: {', '.join(sorted(missing))}")
        examples.append({key: data[key] for key in (
            "id", "title", "topic", "difficulty", "question",
            "code", "expected_output", "explanation", "validation",
        )})

    ids = [item["id"] for item in examples]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate example IDs found; catalog was not written.")

    catalog["examples"] = examples
    CATALOG_PATH.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\\n",
        encoding="utf-8",
    )
    print(f"Built catalog with {len(examples)} examples.")


if __name__ == "__main__":
    build_catalog()
