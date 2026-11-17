# DS Wet 1 - 220 Test Suite

A comprehensive test harness containing **220 tests** for the HW1 Wet assignment, generated via a Python reference oracle and automated test generator.

## How to Run

Run the test runner against your C++ solution directory:

```bash
python3 scripts/test_runner.py --code-dir /path/to/your/cpp_folder
To run a specific category of tests (e.g., invalid inputs):
python3 scripts/test_runner.py --code-dir /path/to/your/cpp_folder --filter 01_invalid_inputs
