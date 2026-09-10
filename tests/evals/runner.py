#!/usr/bin/env python3
"""Deterministic integrity and fixture checks for the readiness eval suite.

This runner never invokes an LLM or a shell and never consumes commands produced by
an agent. All executed argv lists and working directories are fixed below.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
MANIFEST = ROOT / "cases.json"
INTEGRITY = ROOT / "fixture-integrity.json"
TIMEOUT_SECONDS = 10


class CheckFailure(RuntimeError):
    pass


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(path):
    return {
        file.relative_to(path).as_posix(): digest(file)
        for file in sorted(path.rglob("*"))
        if file.is_file() and not file.is_symlink()
    }


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def case_by_id(case_id):
    cases = {case["id"]: case for case in load_manifest()["cases"]}
    try:
        return cases[case_id]
    except KeyError as error:
        raise CheckFailure("unknown case: {}".format(case_id)) from error


def validate_manifest():
    data = load_manifest()
    if data.get("schema_version") != 1 or not isinstance(data.get("cases"), list):
        raise CheckFailure("cases.json has an unsupported shape")
    seen = set()
    required_permissions = {
        "inspect",
        "execute_documented_commands",
        "mutate_disposable_copy",
        "write_report_in_target",
        "install",
        "network",
        "credentials",
        "live_services",
    }
    for case in data["cases"]:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise CheckFailure("case IDs must be unique non-empty strings")
        seen.add(case_id)
        fixture = Path(case.get("fixture", ""))
        if fixture.is_absolute() or ".." in fixture.parts or fixture.parts[:1] != ("fixtures",):
            raise CheckFailure("{} has an unsafe fixture path".format(case_id))
        if not (ROOT / fixture).is_dir():
            raise CheckFailure("{} fixture does not exist".format(case_id))
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise CheckFailure("{} has no prompt".format(case_id))
        permissions = case.get("permitted_operations", {})
        if set(permissions) != required_permissions:
            raise CheckFailure("{} has incomplete permissions".format(case_id))
        for forbidden in ("install", "network", "credentials", "live_services"):
            if permissions[forbidden] is not False:
                raise CheckFailure("{} permits {}".format(case_id, forbidden))
        expected = case.get("expected", {})
        if not expected.get("must") or not expected.get("must_not"):
            raise CheckFailure("{} lacks must/must_not criteria".format(case_id))
        if not expected.get("observable_outcomes"):
            raise CheckFailure("{} lacks observable outcomes".format(case_id))


def validate_integrity():
    expected = json.loads(INTEGRITY.read_text(encoding="utf-8"))["sha256"]
    actual = tree(FIXTURES)
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        added = sorted(set(actual) - set(expected))
        changed = sorted(path for path in set(actual) & set(expected) if actual[path] != expected[path])
        raise CheckFailure(
            "fixture integrity mismatch: missing={!r}, added={!r}, changed={!r}".format(
                missing, added, changed
            )
        )
    forbidden_names = ("oracle", "rubric", "expected")
    for relative in actual:
        if any(token in part.lower() for part in Path(relative).parts for token in forbidden_names):
            raise CheckFailure("oracle-like path is inside a presented fixture: {}".format(relative))


def fixed_env():
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "READINESS_EVAL_OFFLINE": "1",
        }
    )
    return environment


def run_fixed(argv, cwd, expected_exit, contains=None, stderr_contains=None):
    result = subprocess.run(
        argv,
        cwd=str(cwd),
        env=fixed_env(),
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        shell=False,
    )
    if result.returncode != expected_exit:
        raise CheckFailure(
            "fixed command {!r} in {} exited {}, expected {}\nstdout:\n{}\nstderr:\n{}".format(
                argv, cwd, result.returncode, expected_exit, result.stdout, result.stderr
            )
        )
    combined = result.stdout + result.stderr
    if contains and contains not in combined:
        raise CheckFailure("fixed command {!r} did not contain {!r}".format(argv, contains))
    if stderr_contains and stderr_contains not in result.stderr:
        raise CheckFailure("fixed command {!r} stderr did not contain {!r}".format(argv, stderr_contains))
    return result


def copy_fixture(name, destination):
    shutil.copytree(FIXTURES / name, destination)


def check_healthy(temp_root):
    target = temp_root / "healthy"
    copy_fixture("healthy-minimal", target)
    baseline = tree(target)
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    run_fixed(command, target, 0, "Ran 3 tests")
    source = target / "quote.py"
    original = source.read_bytes()
    marker = b"return 5 + 2 * weight"
    if original.count(marker) != 1:
        raise CheckFailure("healthy probe marker is not unique")
    try:
        source.write_bytes(original.replace(marker, b"return 5 + 3 * weight"))
        run_fixed(command, target, 1, "FAILED")
    finally:
        source.write_bytes(original)
    run_fixed(command, target, 0, "Ran 3 tests")
    if tree(target) != baseline:
        raise CheckFailure("healthy probe did not restore the exact fixture tree")


def require_node():
    node = shutil.which("node")
    if not node:
        raise CheckFailure("Node is unavailable; JavaScript fixtures are harness-limited")
    return node


def check_misleading_green(temp_root, node):
    target = temp_root / "misleading-green"
    copy_fixture("misleading-green-js", target)
    baseline = tree(target)
    command = [node, "check.js"]
    run_fixed(command, target, 0, "2 examples checked")
    source = target / "shipping.js"
    original = source.read_bytes()
    marker = b"return 5 + 2 * weight;"
    if original.count(marker) != 1:
        raise CheckFailure("misleading-green probe marker is not unique")
    try:
        source.write_bytes(original.replace(marker, b"return 5 + 3 * weight;"))
        result = run_fixed(command, target, 0, "2 examples checked")
        if "got 8, expected 7" not in result.stdout or "got 17, expected 13" not in result.stdout:
            raise CheckFailure("misleading-green probe did not expose the expected mismatches")
    finally:
        source.write_bytes(original)
    run_fixed(command, target, 0, "2 examples checked")
    if tree(target) != baseline:
        raise CheckFailure("misleading-green probe did not restore the exact fixture tree")


def check_broken_package(temp_root):
    target = temp_root / "broken-package"
    copy_fixture("broken-package", target)
    tests = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    run_fixed(tests, target, 0, "Ran 2 tests")
    run_fixed([sys.executable, "build.py"], target, 0, "dist/ratecard")
    run_fixed(
        [sys.executable, "dist/ratecard/app.py", "4"],
        target,
        1,
        stderr_contains="rates.json",
    )


def check_heterogeneous(temp_root, node):
    target = temp_root / "heterogeneous"
    copy_fixture("heterogeneous-components", target)
    baseline = tree(target)
    run_fixed(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        target / "services" / "quote",
        0,
        "Ran 2 tests",
    )
    run_fixed([node, "check.js"], target / "web" / "widget", 0, "2 widget checks passed")
    if tree(target) != baseline:
        raise CheckFailure("heterogeneous checks changed the fixture tree")


def check_docs(temp_root):
    target = temp_root / "docs"
    copy_fixture("docs-only", target)
    link_pattern = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    checked = 0
    for markdown in target.rglob("*.md"):
        for raw_target in link_pattern.findall(markdown.read_text(encoding="utf-8")):
            if "://" in raw_target or raw_target.startswith("#"):
                continue
            checked += 1
            relative = raw_target.split("#", 1)[0]
            if not (markdown.parent / relative).resolve().is_file():
                raise CheckFailure("broken docs link in {}: {}".format(markdown, raw_target))
    if checked != 3:
        raise CheckFailure("expected to check 3 relative documentation links, got {}".format(checked))


def check_implementation_oracle(temp_root):
    target = temp_root / "implementation"
    copy_fixture("healthy-minimal", target)
    baseline = tree(target)
    source = target / "quote.py"
    tests = target / "tests" / "test_quote.py"
    original_source = source.read_bytes()
    original_tests = tests.read_bytes()
    if original_source.count(b"return 5 + 2 * weight") != 1:
        raise CheckFailure("implementation source marker is not unique")
    if original_tests.count(b"quote(1), 7") != 1 or original_tests.count(b"quote(4), 13") != 1:
        raise CheckFailure("implementation test markers are not unique")
    try:
        source.write_bytes(original_source.replace(b"return 5 + 2 * weight", b"return 7 + 2 * weight"))
        tests.write_bytes(
            original_tests.replace(b"quote(1), 7", b"quote(1), 9").replace(
                b"quote(4), 13", b"quote(4), 15"
            )
        )
        run_fixed(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            target,
            0,
            "Ran 3 tests",
        )
        if run_fixed([sys.executable, "quote.py", "1"], target, 0).stdout.strip() != "9":
            raise CheckFailure("implementation oracle produced the wrong one-kilogram quote")
        if run_fixed([sys.executable, "quote.py", "4"], target, 0).stdout.strip() != "15":
            raise CheckFailure("implementation oracle produced the wrong four-kilogram quote")
    finally:
        source.write_bytes(original_source)
        tests.write_bytes(original_tests)
    if tree(target) != baseline:
        raise CheckFailure("implementation oracle did not restore the exact fixture tree")


def check_all():
    validate_manifest()
    validate_integrity()
    node = require_node()
    with tempfile.TemporaryDirectory(prefix="readiness-evals-") as temporary:
        temp_root = Path(temporary)
        check_healthy(temp_root)
        check_misleading_green(temp_root, node)
        check_broken_package(temp_root)
        check_heterogeneous(temp_root, node)
        check_docs(temp_root)
        check_implementation_oracle(temp_root)
    print("PASS: manifest and fixture integrity")
    print("PASS: healthy baseline, detected probe, exact restoration")
    print("PASS: misleading-green baseline, missed probe, exact restoration")
    print("PASS: source-green/package-broken workflow")
    print("PASS: Python and JavaScript component checks from documented cwd")
    print("PASS: documentation-only relative links")
    print("PASS: implementation near-miss outcome and exact restoration")


def prepare(case_id, destination):
    case = case_by_id(case_id)
    destination = destination.resolve()
    if destination.exists():
        raise CheckFailure("destination already exists: {}".format(destination))
    source = ROOT / case["fixture"]
    shutil.copytree(source, destination)
    print(destination)


def diff_copy(case_id, candidate):
    case = case_by_id(case_id)
    candidate = candidate.resolve()
    if not candidate.is_dir():
        raise CheckFailure("candidate is not a directory: {}".format(candidate))
    baseline = tree(ROOT / case["fixture"])
    observed = tree(candidate)
    baseline_dirs = {p.relative_to(ROOT / case['fixture']).as_posix()
                     for p in (ROOT / case['fixture']).rglob('*') if p.is_dir()}
    observed_dirs = {p.relative_to(candidate).as_posix()
                     for p in candidate.rglob('*') if p.is_dir() and not p.is_symlink()}
    result = {
        "added": sorted(set(observed) - set(baseline)),
        "deleted": sorted(set(baseline) - set(observed)),
        "modified": sorted(
            path for path in set(baseline) & set(observed) if baseline[path] != observed[path]
        ),
        "added_directories": sorted(observed_dirs - baseline_dirs),
        "deleted_directories": sorted(baseline_dirs - observed_dirs),
        "symlinks": {p.relative_to(candidate).as_posix(): os.readlink(p)
                     for p in candidate.rglob('*') if p.is_symlink()},
    }
    print(json.dumps(result, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="validate and exercise fixed fixture scenarios")
    prepare_parser = subparsers.add_parser("prepare", help="copy only one fixture for a trial")
    prepare_parser.add_argument("case_id")
    prepare_parser.add_argument("destination", type=Path)
    diff_parser = subparsers.add_parser("diff", help="inventory byte changes in a trial copy")
    diff_parser.add_argument("case_id")
    diff_parser.add_argument("candidate", type=Path)
    arguments = parser.parse_args()
    try:
        if arguments.command == "check":
            check_all()
        elif arguments.command == "prepare":
            prepare(arguments.case_id, arguments.destination)
        elif arguments.command == "diff":
            diff_copy(arguments.case_id, arguments.candidate)
    except (CheckFailure, json.JSONDecodeError, OSError, subprocess.TimeoutExpired) as error:
        print("FAIL: {}".format(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
