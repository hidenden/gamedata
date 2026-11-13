import importlib.util
from pathlib import Path


_MODULE_PATH = Path(__file__).parents[1] / "database" / "update" / "famitsu.py"
_SPEC = importlib.util.spec_from_file_location("famitsu", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
famitsu = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(famitsu)


def test_write_source_log_writes_url_and_raw_sales_in_order(tmp_path):
    log_path = tmp_path / "famitsu-source.txt"
    url = "https://www.famitsu.com/article/202609/87520"
    raw_sales = [
        "Switch2／24281台（累計626万5473台）",
        "PS5／102台（累計591万9917台）",
    ]
    raw_report_dates = ["集計期間：2026年8月31日～9月6日"]

    famitsu.write_source_log(str(log_path), url, raw_sales, raw_report_dates)

    assert log_path.read_text(encoding="utf-8") == (
        "https://www.famitsu.com/article/202609/87520\n"
        "\n"
        "Switch2／24281台（累計626万5473台）\n"
        "PS5／102台（累計591万9917台）\n"
        "\n"
        "集計期間：2026年8月31日～9月6日\n"
    )


def test_famitsu_main_writes_log_before_processing(monkeypatch, tmp_path):
    log_path = tmp_path / "famitsu-source.txt"
    url = "https://www.famitsu.com/article/202609/87520"
    raw_sales = ["Switch2／24281台（累計626万5473台）"]

    monkeypatch.setattr(
        famitsu,
        "get_famitsu_hwsales_page",
        lambda _url: (raw_sales, ["集計期間：2026年8月31日～9月6日"]),
    )

    famitsu.famitsu_main(
        db_path=str(tmp_path / "unused.db"),
        target_url=url,
        dry_run=True,
        log_path=str(log_path),
    )

    assert log_path.read_text(encoding="utf-8").splitlines() == [
        url,
        "",
        *raw_sales,
        "",
        "集計期間：2026年8月31日～9月6日",
    ]


def test_famitsu_main_defaults_to_reporting_end_date_log(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "logs").mkdir()
    monkeypatch.setattr(
        famitsu,
        "get_famitsu_hwsales_page",
        lambda _url: (
            ["Switch2／24281台（累計626万5473台）"],
            ["集計期間：2026年8月31日～9月6日"],
        ),
    )

    famitsu.famitsu_main("unused.db", "https://www.famitsu.com/", dry_run=True)

    assert (tmp_path / "logs" / "20260906.log").read_text(encoding="utf-8").startswith(
        "https://www.famitsu.com/\n"
    )


def test_log_failure_reports_to_stderr_and_continues_database_update(
    monkeypatch, tmp_path, capsys
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        famitsu,
        "get_famitsu_hwsales_page",
        lambda _url: (
            ["Switch2／24281台（累計626万5473台）"],
            ["集計期間：2026年8月31日～9月6日"],
        ),
    )
    updates = []
    monkeypatch.setattr(famitsu, "upsert_to_database", lambda db, rows: updates.append(rows))

    famitsu.famitsu_main("unused.db", "https://www.famitsu.com/")

    captured = capsys.readouterr()
    assert "Could not write source log to logs/20260906.log" in captured.err
    assert "Source log written" not in captured.out
    assert not (tmp_path / "logs").exists()
    assert updates == [[["2026-09-06_NS2", "2026-09-06", 7, "NS2", 24281]]]
