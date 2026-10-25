import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "python"
REQUIRED_FIELDS = {
    "id", "title", "topic", "difficulty", "question",
    "code", "expected_output", "explanation", "validation",
}

def main():
    files = sorted(EXAMPLES_DIR.rglob("*.json"))
    if not files:
        print("ERROR: No example JSON files found.")
        return 1

    errors = []
    seen_ids = {}
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue

        if not isinstance(data, dict):
            errors.append(f"{relative}: top-level JSON value must be an object.")
            continue

        missing = REQUIRED_FIELDS - data.keys()
        if missing:
            errors.append(f"{relative}: missing fields: {', '.join(sorted(missing))}")

        for field in REQUIRED_FIELDS:
            if field in data and not isinstance(data[field], str):
                errors.append(f"{relative}: {field} must be a string.")

        example_id = data.get("id")
        if isinstance(example_id, str):
            if example_id in seen_ids:
                errors.append(
                    f"{relative}: duplicate id {example_id!r}; "
                    f"first used in {seen_ids[example_id]}."
                )
            else:
                seen_ids[example_id] = relative

        code = data.get("code")
        if isinstance(code, str):
            try:
                compile(code, relative, "exec")
            except SyntaxError as exc:
                errors.append(
                    f"{relative}: Python syntax error on line {exc.lineno}: {exc.msg}"
                )

    if errors:
        print(f"FAILED: {len(errors)} issue(s) across {len(files)} example file(s).")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS: {len(files)} JSON examples have valid required fields and Python syntax.")
    print("Note: this checker does not execute examples or verify expected output.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
