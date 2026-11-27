"""各 marimo notebook を public/dashboard に単一 HTML として出力する。"""

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = ROOT / "dashboard/notebooks"
OUTPUT = ROOT / "public/dashboard"


def main() -> None:
    notebooks = sorted(
        path
        for path in NOTEBOOKS.rglob("*.py")
        if "__marimo__" not in path.relative_to(NOTEBOOKS).parts
    )
    if not notebooks:
        raise SystemExit(f"notebook が見つかりません: {NOTEBOOKS}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=OUTPUT) as tmp:
        stage = Path(tmp)
        for notebook in notebooks:
            target = stage / notebook.relative_to(NOTEBOOKS).with_suffix(".html")
            target.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    sys.executable, "-m", "marimo", "export", "html-wasm", str(notebook),
                    "--mode", "run", "--single-file", "--no-execute", "-o", str(target),
                ],
                check=True,
            )
        for html in stage.rglob("*.html"):
            target = OUTPUT / html.relative_to(stage)
            target.parent.mkdir(parents=True, exist_ok=True)
            html.replace(target)


if __name__ == "__main__":
    main()
