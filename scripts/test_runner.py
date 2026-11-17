#!/usr/bin/env python3
"""
Automated C++ Test Harness with Timeout Enforcement, Diff Diagnostics, and Valgrind Support.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def discover_tests(tests_root: Path) -> list[tuple[str, Path, Path]]:
    discovered = []
    for in_file in sorted(tests_root.rglob("*.in")):
        out_file = in_file.with_suffix(".out")
        if out_file.is_file():
            rel_name = str(in_file.relative_to(tests_root).with_suffix(""))
            discovered.append((rel_name, in_file, out_file))
    return discovered


def compile_solution(code_dir: Path, build_dir: Path, use_asan: bool) -> Path:
    cpp_files = sorted(code_dir.glob("*.cpp"))
    if not cpp_files:
        raise FileNotFoundError(f"No .cpp source files found in {code_dir}")

    exe_path = build_dir / "resort_test_bin"
    flags = ["-std=c++14", "-Wall", "-Wextra", "-Werror"]
    if use_asan:
        flags += ["-g", "-O1", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
    else:
        flags += ["-DNDEBUG", "-O2"]

    cmd = ["g++"] + flags + [str(p) for p in cpp_files] + ["-o", str(exe_path)]
    print(f"[BUILD] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    return exe_path


def run_single_test(
    exe_path: Path,
    in_file: Path,
    out_file: Path,
    timeout: float,
    use_valgrind: bool,
) -> tuple[bool, float, str]:
    cmd = [str(exe_path)]
    if use_valgrind:
        cmd = [
            "valgrind",
            "--leak-check=full",
            "--show-leak-kinds=all",
            "--errors-for-leak-kinds=all",
            "--error-exitcode=42",
            "-q",
            str(exe_path),
        ]

    start = time.perf_counter()
    try:
        with open(in_file, "r") as fin:
            proc = subprocess.run(
                cmd,
                stdin=fin,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
    except subprocess.TimeoutExpired:
        return False, timeout, f"TIMEOUT (> {timeout:.1f}s)"

    elapsed = time.perf_counter() - start

    if use_valgrind and proc.returncode == 42:
        return False, elapsed, f"VALGRIND MEMORY ERROR / LEAK:\n{proc.stderr.strip()}"
    if proc.returncode != 0:
        return False, elapsed, f"CRASH (exit code {proc.returncode}):\n{proc.stderr.strip()}"

    actual = proc.stdout.strip()
    expected = out_file.read_text().strip()

    if actual != expected:
        actual_lines = actual.splitlines()
        expected_lines = expected.splitlines()
        for idx, (a, e) in enumerate(zip(actual_lines, expected_lines), start=1):
            if a != e:
                return (
                    False,
                    elapsed,
                    f"MISMATCH at line {idx}:\n  Expected: {e}\n  Actual:   {a}",
                )
        return (
            False,
            elapsed,
            f"LINE COUNT MISMATCH (expected {len(expected_lines)}, got {len(actual_lines)})",
        )

    return True, elapsed, "OK"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run 220-test suite against C++ implementation.")
    parser.add_argument("--code-dir", type=Path, required=True, help="Directory containing your C++ solution files")
    parser.add_argument("--tests-dir", type=Path, default=Path("tests"), help="Root directory of tests")
    parser.add_argument("--filter", type=str, default="", help="Substring filter for test names/categories")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-test timeout in seconds")
    parser.add_argument("--valgrind", action="store_true", help="Run under Valgrind leak detector")
    parser.add_argument("--asan", action="store_true", help="Compile with AddressSanitizer & UBSan")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop immediately on first failure")
    args = parser.parse_args()

    tests = [t for t in discover_tests(args.tests_dir) if args.filter in t[0]]
    if not tests:
        print("No matching tests found.")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        exe_path = compile_solution(args.code_dir, Path(tmp), args.asan)
        passed = 0
        failed = 0

        for name, in_file, out_file in tests:
            ok, elapsed, msg = run_single_test(exe_path, in_file, out_file, args.timeout, args.valgrind)
            if ok:
                passed += 1
            else:
                failed += 1
                print(f"[FAIL] {name} ({elapsed:.3f}s) -> {msg}")
                if args.stop_on_fail:
                    break

        print(f"\nSummary: {passed}/{passed + failed} passed ({failed} failed).")
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
