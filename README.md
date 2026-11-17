# Resort Data Structures - Test Harness

A comprehensive test suite containing **240 tests** for the HW1 Wet C++ data structures assignment.

## Categories (`tests/`)

1. **`01_invalid_inputs`**: Input validation and error-code precedence.
2. **`02_lifecycle_basics`**: Guest check-in/out, room collisions, and AVL rotations.
3. **`03_dining_and_meals`**: Meal stamps, `reheatFood()`, and friend joining.
4. **`04_table_merging`**: Table merging, capacity updates, and pointer migrations.
5. **`05_housekeeping_rotation`**: Circular housekeeping and room cleanup logic.
6. **`06_randomized_fuzz`**: Randomized multi-operation fuzz tests.
7. **`07_stress_complexity`**: Performance and asymptotic complexity stress tests.
8. **`08_comprehensive_system`**: End-to-end multi-step system workflows.
9. **`09_mega_simulation`**: Large-scale simulations with 600+ commands per
test.

## Proof of Work
```bash
Summary: 240/240 passed (0 failed).
```
## How to Run
Run the test runner against your C++ solution directory:
```bash
python3 scripts/test_runner.py --code-dir /path/to/cpp_folder
```
## To run a specific category:
```bash
python3 scripts/test_runner.py --code-dir /path/to/cpp_folder --filter 01_invalid_inputs
```
