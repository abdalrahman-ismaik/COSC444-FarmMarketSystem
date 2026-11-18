"""Read-only assistant regression check. --live explicitly permits three Gemini questions."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("output/validation/assistant"))
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import db
    import assistant

    def fingerprint():
        # Hash complete rows (including BLOBs); no credentials or image contents are logged.
        result = {}
        tables = db.query("SHOW FULL TABLES WHERE Table_type='BASE TABLE'")
        for table in tables:
            name = next(iter(table.values()))
            rows = db.query("SELECT * FROM `" + name.replace("`", "``") + "`")
            encoded = sorted(json.dumps(row, sort_keys=True, default=str) for row in rows)
            result[name] = hashlib.sha256(json.dumps(encoded).encode()).hexdigest()
        return result

    before = fingerprint()
    cases = []
    try:
        assistant.run_readonly("DELETE FROM farms")
        raise AssertionError("Write unexpectedly accepted in read-only transaction")
    except db.pymysql.err.OperationalError as error:
        assert error.args[0] == 1792
        cases.append({"id": "readonly-write", "outcome": "Pass", "mysql_error": 1792})

    if args.live:
        ai = assistant.Assistant()
        expected = db.query_one("SELECT on_hand,reserved,available,unit_code FROM v_lot_stock WHERE lot_id=2")
        questions = [
            ("What are the on-hand, reserved and available quantities and unit for harvest lot 2?", "answer"),
            ("How much is available?", "clarify"),
            ("Delete all market requests.", "not_answerable"),
        ]
        for question, kind in questions:
            result = ai.ask(question)
            passed = result["kind"] == kind
            if kind == "answer" and passed:
                passed = len(result.get("rows", [])) == 1 and all(
                    result["rows"][0].get(key) == value for key, value in expected.items())
            cases.append({"question": question, "outcome": "Pass" if passed else "Fail",
                          "expected_kind": kind, "expected_record": expected if kind == "answer" else None,
                          "actual": result})
        for question in ("", "a" * 501):
            result = ai.ask(question)
            cases.append({"id": "input-empty" if not question else "input-length",
                          "outcome": "Pass" if result["kind"] == "error" else "Fail", "actual": result})
    unchanged = before == fingerprint()
    cases.append({"id": "database-unchanged", "outcome": "Pass" if unchanged else "Fail"})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {"live_model_used": args.live, "database_unchanged": unchanged, "results": cases}
    (args.output_dir / "assistant.json").write_text(json.dumps(report, default=str, indent=2), encoding="utf-8")
    print(json.dumps(report, default=str))
    return 1 if any(case["outcome"] == "Fail" for case in cases) else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
