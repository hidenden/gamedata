"""src/gamedata からブラウザ配信用の wheel とその参照ファイルを生成する。"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "public/dashboard/packages"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=OUTPUT) as tmp:
        stage = Path(tmp)
        # 開発中の build/lib や過去の package-data を持ち込まずにビルドする。
        for name in ("pyproject.toml", "README.md", "LICENSE"):
            shutil.copyfile(ROOT / name, stage / name)
        shutil.copytree(
            ROOT / "src/gamedata",
            stage / "src/gamedata",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(stage / "dist"), str(stage)],
            env={**os.environ, "SOURCE_DATE_EPOCH": "315532800"},
            check=True,
        )
        (wheel,) = (stage / "dist").glob("*.whl")
        wheel.replace(OUTPUT / wheel.name)
        manifest = stage / "wheel.json"
        manifest.write_text(json.dumps({"filename": wheel.name}) + "\n")
        manifest.replace(OUTPUT / manifest.name)


if __name__ == "__main__":
    main()
