"""SQLite の元テーブルからパッケージ同梱用の Parquet を生成する。"""

import argparse
import json
import os
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from gamedata.data_source import DEFAULT_DB_PATH, SCHEMA_VERSION, TABLE_SCHEMAS, SQLiteSource


def export_snapshot(db_path: Path, output_dir: Path) -> None:
    tables = SQLiteSource(db_path).read_tables(*TABLE_SCHEMAS)
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output_dir) as staging:
        stage = Path(staging)
        checksums = {}
        for name, frame in zip(TABLE_SCHEMAS, tables, strict=True):
            path = stage / f"{name}.parquet"
            frame.write_parquet(path, compression="zstd")
            checksums[name] = sha256(path.read_bytes()).hexdigest()
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "captured_at": captured_at,
            "sha256": checksums,
        }
        (stage / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        for name in TABLE_SCHEMAS:
            (stage / f"{name}.parquet").replace(output_dir / f"{name}.parquet")
        (stage / "manifest.json").replace(output_dir / "manifest.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=os.environ.get("GAMEHARD_DB") or DEFAULT_DB_PATH)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "src/gamedata/_parquet",
    )
    args = parser.parse_args()
    export_snapshot(args.db, args.output)


if __name__ == "__main__":
    main()
