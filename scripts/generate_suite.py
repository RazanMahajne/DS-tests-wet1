#!/usr/bin/env python3
"""
Generates categorized test cases (.in / .out) covering:
  01_invalid_inputs        (001-025): Input validation & precedence over FAILURE
  02_lifecycle_basics      (026-055): Check-in/out, room collisions, AVL rotations
  03_dining_and_meals      (056-095): Meal stamps, reheatFood(), joinFriend() edge cases
  04_table_merging         (096-130): joinTables() migrations, capacity sums, stale IDs
  05_housekeeping_rotation (131-160): cleanNextRoom() wrap-around & deleted-room bugs
  06_randomized_fuzz       (161-200): Seeded differential fuzzing across dense/sparse IDs
  07_stress_complexity     (201-220): O(log n), O(log m), O(1) asymptotic stress tests
  08_comprehensive_system  (221-235): Full end-to-end multi-step system workflows
  09_mega_simulation       (236-240): Massive long-running tests with 600+ commands each
"""

import os
import random
from reference_oracle import ResortReferenceOracle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(BASE_DIR, "tests")


def write_test(category: str, test_id: int, commands: list[str]) -> None:
    cat_dir = os.path.join(TESTS_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    oracle = ResortReferenceOracle()
    outputs = oracle.execute_commands(commands)

    in_path = os.path.join(cat_dir, f"test_{test_id:03d}.in")
    out_path = os.path.join(cat_dir, f"test_{test_id:03d}.out")

    with open(in_path, "w", newline="\n") as f:
        f.write("\n".join(commands) + ("\n" if commands else ""))
    with open(out_path, "w", newline="\n") as f:
        f.write("\n".join(outputs) + ("\n" if outputs else ""))


def generate_all() -> None:
    tid = 1

    # 1. 01_invalid_inputs (001 - 025)
    cat1 = [
        [],
        ["checkIn 0 1", "checkIn -1 1", "checkIn -999999 50"],
        ["checkIn 1 0", "checkIn 1 -1", "checkIn 50 -2147483647"],
        ["checkIn 0 0", "checkIn -5 -10", "checkIn 0 -1", "checkIn -1 0"],
        ["checkOut 0", "checkOut -1", "checkOut -100000"],
        ["addTable 0 5", "addTable -1 5", "addTable -42 1"],
        ["addTable 1 0", "addTable 1 -1", "addTable 10 -50"],
        ["addTable 0 0", "addTable -1 -1", "addTable 0 -5", "addTable -5 0"],
        ["removeTable 0", "removeTable -1", "removeTable -77"],
        ["addTable 1 5", "enterDiningRoom 0 1", "enterDiningRoom -1 1"],
        ["checkIn 1 10", "enterDiningRoom 1 0", "enterDiningRoom 1 -1"],
        ["enterDiningRoom 0 0", "enterDiningRoom -2 -3", "enterDiningRoom 0 -1"],
        ["addTable 1 5", "leaveDiningRoom 0 1", "leaveDiningRoom -3 1"],
        ["checkIn 1 10", "leaveDiningRoom 1 0", "leaveDiningRoom 1 -3"],
        ["leaveDiningRoom 0 0", "leaveDiningRoom -1 -9"],
        ["addTable 5 2", "joinTables 0 5", "joinTables 5 0", "joinTables -1 5", "joinTables 5 -1", "joinTables 5 5", "joinTables 0 0", "joinTables -3 -3"],
        ["joinTables 99 99", "joinTables 1 1"],
        ["checkIn 5 10", "addTable 1 2", "enterDiningRoom 5 1", "joinFriend 0 5", "joinFriend 5 0", "joinFriend -1 5", "joinFriend 5 -1", "joinFriend 5 5", "joinFriend 0 0", "joinFriend -2 -2"],
        ["joinFriend 42 42", "joinFriend 1 1"],
        ["checkIn 1 10", "checkIn 1 0", "checkIn 0 10", "checkIn 1 -5", "checkIn -5 10"],
        ["addTable 10 4", "addTable 10 0", "addTable 10 -3"],
        ["checkIn 1 10", "addTable 5 2", "enterDiningRoom 1 5", "leaveDiningRoom 1 0", "leaveDiningRoom 1 -2", "enterDiningRoom 1 0", "enterDiningRoom 1 -2"],
        ["addTable 7 3", "joinTables 7 -7", "joinTables -7 7", "joinTables 7 0", "joinTables 0 7"],
        ["checkIn 1 1", "addTable 1 2", "enterDiningRoom 1 1", "joinFriend 1 0", "joinFriend 0 1", "joinFriend 1 -1", "joinFriend -1 1"],
        ["checkIn 2147483647 2147483647", "addTable 2147483647 2147483647", "enterDiningRoom 2147483647 2147483647", "cleanNextRoom", "leaveDiningRoom 2147483647 2147483647", "checkOut 2147483647", "removeTable 2147483647"],
    ]
    for cmds in cat1:
        write_test("01_invalid_inputs", tid, cmds)
        tid += 1

    # 2. 02_lifecycle_basics (026 - 055)
    cat2 = [
        ["checkIn 1 100", "checkOut 1"],
        ["checkOut 1", "checkIn 2 200", "checkOut 1", "checkOut 2", "checkOut 2"],
        ["checkIn 1 10", "checkIn 1 20", "checkOut 1", "checkIn 1 20"],
        ["checkIn 1 10", "checkIn 2 10", "checkOut 1", "checkIn 2 10"],
        ["checkIn 1 2", "checkIn 2 1", "checkOut 1", "checkIn 3 2", "checkOut 2", "checkOut 3"],
        ["checkIn 5 50", "checkOut 5", "checkIn 5 50", "checkOut 5", "checkIn 5 50"],
        ["checkIn 1 10", "checkOut 1", "checkIn 1 20", "checkIn 2 10", "checkOut 1", "checkOut 2"],
        ["addTable 10 5", "removeTable 10"],
        ["removeTable 1", "addTable 2 3", "removeTable 1", "removeTable 2", "removeTable 2"],
        ["addTable 10 5", "addTable 10 10", "addTable 10 5", "removeTable 10", "addTable 10 10"],
        ["checkIn 7 7", "addTable 7 7", "enterDiningRoom 7 7", "removeTable 7", "checkOut 7", "leaveDiningRoom 7 7", "removeTable 7", "checkOut 7"],
        ["checkIn 1 10", "addTable 1 1", "enterDiningRoom 1 1", "checkOut 1", "leaveDiningRoom 1 1", "checkOut 1"],
        ["checkIn 1 10", "addTable 5 2", "enterDiningRoom 1 5", "removeTable 5", "leaveDiningRoom 1 5", "removeTable 5"],
        ["checkIn 1 1", "checkIn 2 2", "checkIn 3 3", "addTable 10 3", "enterDiningRoom 1 10", "enterDiningRoom 2 10", "enterDiningRoom 3 10",
         "removeTable 10", "leaveDiningRoom 1 10", "removeTable 10", "leaveDiningRoom 2 10", "removeTable 10", "leaveDiningRoom 3 10", "removeTable 10"],
        [f"checkIn {i} {i*10}" for i in range(1, 31)] + [f"checkOut {i}" for i in range(1, 31)],
        [f"checkIn {i} {i*10}" for i in range(30, 0, -1)] + [f"checkOut {i}" for i in range(30, 0, -1)],
        [f"checkIn {x} {x}" for x in [10, 30, 20, 5, 15, 25, 35, 1, 7, 12, 18, 22, 27, 32, 40]] +
        [f"checkOut {x}" for x in [20, 10, 30, 15, 25, 5, 35, 1, 40, 12, 27, 7, 32, 18, 22]],
        [f"addTable {i} {i}" for i in range(1, 26)] + [f"removeTable {i}" for i in range(25, 0, -1)],
        ["checkIn 1 10", "checkIn 2 20", "checkOut 1", "checkIn 3 10", "checkOut 2", "checkIn 4 20", "checkOut 3", "checkOut 4"],
        ["checkIn 1 10", "addTable 1 2", "enterDiningRoom 1 1", "leaveDiningRoom 1 1", "checkOut 1",
         "checkIn 1 20", "enterDiningRoom 1 1", "leaveDiningRoom 1 1", "checkOut 1"],
        ["checkIn 5 50", "addTable 2 2", "enterDiningRoom 5 2", "leaveDiningRoom 5 2", "enterDiningRoom 5 2",
         "checkOut 5", "checkIn 5 51", "enterDiningRoom 5 2"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 10 2", "enterDiningRoom 1 10", "enterDiningRoom 2 10",
         "leaveDiningRoom 1 10", "leaveDiningRoom 2 10", "removeTable 10", "addTable 10 1", "reheatFood",
         "enterDiningRoom 1 10", "enterDiningRoom 2 10"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 10 1", "enterDiningRoom 1 10", "enterDiningRoom 2 10",
         "leaveDiningRoom 1 10", "removeTable 10", "addTable 10 2", "reheatFood",
         "enterDiningRoom 1 10", "enterDiningRoom 2 10"],
        ["addTable 1 5"] + [f"checkIn {i} {i}" for i in range(1, 6)] + [f"enterDiningRoom {i} 1" for i in range(1, 6)] +
        [f"leaveDiningRoom {i} 1" for i in range(5, 0, -1)] + ["removeTable 1"],
        ["addTable 1 5"] + [f"checkIn {i} {i}" for i in range(1, 6)] + [f"enterDiningRoom {i} 1" for i in range(1, 6)] +
        [f"leaveDiningRoom {i} 1" for i in range(1, 6)] + ["removeTable 1"],
        ["addTable 1 5"] + [f"checkIn {i} {i}" for i in range(1, 6)] + [f"enterDiningRoom {i} 1" for i in range(1, 6)] +
        [f"leaveDiningRoom {i} 1" for i in [3, 2, 4, 1, 5]] + ["removeTable 1"],
        ["checkIn 1 100", "checkIn 2 90", "checkIn 3 80", "checkIn 4 70", "checkOut 2", "checkIn 5 90", "checkOut 4", "checkOut 1", "checkOut 3", "checkOut 5"],
        ["checkIn 1 1", "addTable 1 1", "checkOut 1", "enterDiningRoom 1 1", "leaveDiningRoom 1 1", "cleanNextRoom", "removeTable 1"],
        ["checkIn 1 1", "addTable 1 1", "removeTable 1", "enterDiningRoom 1 1", "leaveDiningRoom 1 1", "checkOut 1"],
        ["checkIn 1 10", "checkIn 1 10", "checkIn 2 10", "checkIn 1 20", "addTable 5 2", "addTable 5 3", "enterDiningRoom 1 5", "leaveDiningRoom 1 5", "checkOut 1", "removeTable 5"],
    ]
    for cmds in cat2:
        write_test("02_lifecycle_basics", tid, cmds)
        tid += 1

    # 3. 03_dining_and_meals (056 - 095)
    cat3 = [
        ["checkIn 1 1", "addTable 1 5", "addTable 2 5", "enterDiningRoom 1 1", "enterDiningRoom 1 2", "leaveDiningRoom 1 1", "enterDiningRoom 1 1", "enterDiningRoom 1 2"],
        ["checkIn 1 1", "addTable 1 2", "enterDiningRoom 1 1", "leaveDiningRoom 1 1", "reheatFood", "enterDiningRoom 1 1"],
        ["checkIn 1 1", "addTable 1 2", "enterDiningRoom 1 1", "reheatFood", "leaveDiningRoom 1 1", "enterDiningRoom 1 1"],
        ["checkIn 1 1", "addTable 1 2", "enterDiningRoom 1 1", "reheatFood", "reheatFood", "reheatFood", "leaveDiningRoom 1 1", "enterDiningRoom 1 1", "reheatFood", "enterDiningRoom 1 1"],
        ["reheatFood", "reheatFood", "checkIn 1 1", "addTable 1 1", "enterDiningRoom 1 1"],
        ["checkIn 1 1", "addTable 1 2", "addTable 2 2", "enterDiningRoom 1 1", "leaveDiningRoom 1 2", "leaveDiningRoom 1 99", "leaveDiningRoom 99 1", "leaveDiningRoom 1 1", "leaveDiningRoom 1 1"],
        ["addTable 1 3"] + [f"checkIn {i} {i}" for i in range(1, 6)] + [f"enterDiningRoom {i} 1" for i in range(1, 6)] +
        ["leaveDiningRoom 2 1", "enterDiningRoom 4 1", "enterDiningRoom 5 1"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 42 3", "enterDiningRoom 2 42", "joinFriend 1 2"],
        ["checkIn 1 1", "checkIn 2 2", "checkIn 3 3", "addTable 10 2", "addTable 20 2",
         "joinFriend 1 2", "enterDiningRoom 2 10", "joinFriend 99 2", "joinFriend 1 99",
         "enterDiningRoom 3 20", "joinFriend 3 2", "joinFriend 1 2",
         "checkIn 4 4", "joinFriend 4 2",
         "leaveDiningRoom 1 10", "joinFriend 1 2", "reheatFood", "joinFriend 1 2"],
        ["addTable 7 4"] + [f"checkIn {i} {i}" for i in range(1, 6)] +
        ["enterDiningRoom 1 7", "joinFriend 2 1", "joinFriend 3 2", "joinFriend 4 3", "joinFriend 5 4"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 5 2", "enterDiningRoom 1 5", "enterDiningRoom 2 5", "leaveDiningRoom 2 5",
         "reheatFood", "joinFriend 2 1", "leaveDiningRoom 1 5", "joinFriend 1 2"],
    ]
    for k in range(29):
        n_g = 4 + (k % 6)
        cap = 1 + (k % 4)
        cmds = [f"checkIn {i} {i*3}" for i in range(1, n_g + 1)] + [f"addTable {t} {cap}" for t in range(10, 13)]
        for step in range(25):
            g = 1 + ((step + k) % n_g)
            g2 = 1 + ((step * 2 + k + 1) % n_g)
            t = 10 + ((step + k) % 3)
            action = (step + k) % 5
            if action == 0:
                cmds.append(f"enterDiningRoom {g} {t}")
            elif action == 1:
                cmds.append(f"joinFriend {g} {g2}")
            elif action == 2:
                cmds.append(f"leaveDiningRoom {g} {t}")
            elif action == 3 and step % 4 == 3:
                cmds.append("reheatFood")
            else:
                cmds.append(f"enterDiningRoom {g} {t}")
        cat3.append(cmds)

    for cmds in cat3:
        write_test("03_dining_and_meals", tid, cmds)
        tid += 1

    # 4. 04_table_merging (096 - 130)
    cat4 = [
        ["addTable 1 2", "addTable 2 3", "joinTables 1 2", "removeTable 2", "addTable 2 1", "removeTable 1", "removeTable 2"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 20 1", "addTable 10 1", "enterDiningRoom 1 20", "enterDiningRoom 2 10",
         "joinTables 20 10", "leaveDiningRoom 1 10", "leaveDiningRoom 2 10", "leaveDiningRoom 1 20", "leaveDiningRoom 2 20", "removeTable 20"],
        ["checkIn 1 1", "addTable 1 1", "addTable 2 1", "enterDiningRoom 1 2", "joinTables 1 2",
         "leaveDiningRoom 1 2", "leaveDiningRoom 1 1", "removeTable 1"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 10 1", "addTable 20 1", "enterDiningRoom 1 20",
         "joinFriend 2 1", "joinTables 10 20", "joinFriend 2 1"],
        [f"checkIn {i} {i}" for i in range(1, 6)] + [f"addTable {i} 1" for i in range(1, 6)] +
        [f"enterDiningRoom {i} {i}" for i in range(1, 6)] +
        ["joinTables 1 2", "joinTables 1 3", "joinTables 1 4", "joinTables 1 5"] +
        [f"leaveDiningRoom {i} 1" for i in range(1, 6)] + ["removeTable 1"],
        [f"checkIn {i} {i}" for i in range(1, 6)] + [f"addTable {i} 1" for i in range(1, 6)] +
        [f"enterDiningRoom {i} {i}" for i in range(1, 6)] +
        ["joinTables 5 4", "joinTables 5 3", "joinTables 5 2", "joinTables 5 1"] +
        [f"leaveDiningRoom {i} 5" for i in range(1, 6)] + ["removeTable 5"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 1 1", "addTable 2 1", "enterDiningRoom 1 1", "enterDiningRoom 2 1",
         "joinTables 1 2", "enterDiningRoom 2 1"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 1 1", "addTable 2 1", "enterDiningRoom 1 2", "enterDiningRoom 2 2",
         "joinTables 1 2", "enterDiningRoom 2 1"],
        ["checkIn 1 1", "addTable 1 1", "enterDiningRoom 1 1", "joinTables 1 2", "joinTables 2 1", "joinTables 2 3",
         "leaveDiningRoom 1 1", "removeTable 1"],
        ["checkIn 1 1", "checkIn 2 2", "addTable 1 1", "addTable 2 1", "enterDiningRoom 1 1", "enterDiningRoom 2 2",
         "joinTables 1 2", "addTable 2 2", "joinTables 2 1", "leaveDiningRoom 1 2", "leaveDiningRoom 2 2", "removeTable 2"],
    ]
    for k in range(25):
        rng = random.Random(4000 + k)
        cmds = [f"checkIn {i} {i*2}" for i in range(1, 13)] + [f"addTable {t} 1" for t in range(1, 9)]
        active_tables = list(range(1, 9))
        for _ in range(30):
            choice = rng.randint(0, 4)
            if choice == 0:
                cmds.append(f"enterDiningRoom {rng.randint(1, 12)} {rng.randint(1, 8)}")
            elif choice == 1 and len(active_tables) >= 2:
                t1, t2 = rng.sample(active_tables, 2)
                cmds.append(f"joinTables {t1} {t2}")
                active_tables.remove(t2)
            elif choice == 2:
                cmds.append(f"joinFriend {rng.randint(1, 12)} {rng.randint(1, 12)}")
            elif choice == 3:
                cmds.append(f"leaveDiningRoom {rng.randint(1, 12)} {rng.randint(1, 8)}")
            else:
                cmds.append("reheatFood")
        cat4.append(cmds)

    for cmds in cat4:
        write_test("04_table_merging", tid, cmds)
        tid += 1

    # 5. 05_housekeeping_rotation (131 - 160)
    cat5 = [
        ["cleanNextRoom", "cleanNextRoom"],
        ["checkIn 1 42", "cleanNextRoom", "cleanNextRoom", "cleanNextRoom", "checkOut 1", "cleanNextRoom"],
        ["checkIn 1 10", "checkIn 2 20", "checkIn 3 30", "cleanNextRoom", "cleanNextRoom", "cleanNextRoom", "cleanNextRoom"],
        ["checkIn 1 10", "checkIn 2 20", "checkIn 3 30", "cleanNextRoom", "cleanNextRoom", "checkOut 2", "cleanNextRoom", "cleanNextRoom"],
        ["checkIn 1 10", "checkIn 2 20", "checkIn 3 30", "cleanNextRoom", "cleanNextRoom", "cleanNextRoom", "checkOut 3", "cleanNextRoom"],
        ["checkIn 1 10", "checkIn 2 20", "checkIn 3 30", "cleanNextRoom", "cleanNextRoom", "cleanNextRoom", "checkOut 1", "cleanNextRoom"],
        ["checkIn 1 10", "checkIn 3 30", "cleanNextRoom", "checkIn 2 20", "cleanNextRoom", "cleanNextRoom"],
        ["checkIn 2 20", "checkIn 3 30", "cleanNextRoom", "checkIn 1 10", "cleanNextRoom", "cleanNextRoom"],
        ["checkIn 1 50", "cleanNextRoom", "checkOut 1", "cleanNextRoom", "checkIn 2 10", "cleanNextRoom"],
        ["checkIn 1 10", "checkIn 2 20", "cleanNextRoom", "checkOut 1", "checkIn 3 10", "cleanNextRoom"],
    ]
    for k in range(20):
        rng = random.Random(5000 + k)
        cmds = []
        for step in range(40):
            op = rng.choice(["in", "in", "out", "clean", "clean"])
            if op == "in":
                cmds.append(f"checkIn {rng.randint(1, 15)} {rng.randint(1, 20)}")
            elif op == "out":
                cmds.append(f"checkOut {rng.randint(1, 15)}")
            else:
                cmds.append("cleanNextRoom")
        cat5.append(cmds)

    for cmds in cat5:
        write_test("05_housekeeping_rotation", tid, cmds)
        tid += 1

    # 6. 06_randomized_fuzz (161 - 200)
    for k in range(40):
        rng = random.Random(6000 + k)
        id_bound = 15 if k % 2 == 0 else 500
        table_bound = 8 if k % 2 == 0 else 100
        n_ops = 120 + (k * 5)
        cmds = []
        for _ in range(n_ops):
            op = rng.choices(
                ["checkIn", "checkOut", "addTable", "removeTable", "enterDiningRoom",
                 "leaveDiningRoom", "reheatFood", "joinTables", "joinFriend", "cleanNextRoom"],
                weights=[18, 10, 12, 6, 16, 10, 4, 6, 10, 8],
                k=1
            )[0]
            if op == "checkIn":
                cmds.append(f"checkIn {rng.randint(-1, id_bound)} {rng.randint(-1, id_bound)}")
            elif op == "checkOut":
                cmds.append(f"checkOut {rng.randint(-1, id_bound)}")
            elif op == "addTable":
                cmds.append(f"addTable {rng.randint(-1, table_bound)} {rng.randint(0, 6)}")
            elif op == "removeTable":
                cmds.append(f"removeTable {rng.randint(-1, table_bound)}")
            elif op == "enterDiningRoom":
                cmds.append(f"enterDiningRoom {rng.randint(-1, id_bound)} {rng.randint(-1, table_bound)}")
            elif op == "leaveDiningRoom":
                cmds.append(f"leaveDiningRoom {rng.randint(-1, id_bound)} {rng.randint(-1, table_bound)}")
            elif op == "reheatFood":
                cmds.append("reheatFood")
            elif op == "joinTables":
                cmds.append(f"joinTables {rng.randint(-1, table_bound)} {rng.randint(-1, table_bound)}")
            elif op == "joinFriend":
                cmds.append(f"joinFriend {rng.randint(-1, id_bound)} {rng.randint(-1, id_bound)}")
            elif op == "cleanNextRoom":
                cmds.append("cleanNextRoom")
        write_test("06_randomized_fuzz", tid, cmds)
        tid += 1

    # 7. 07_stress_complexity (201 - 220)
    for k in range(20):
        rng = random.Random(7000 + k)
        n = 3000
        m = 1000
        cmds = []
        if k % 4 == 0:
            for i in range(1, n + 1):
                cmds.append(f"checkIn {i} {i}")
            for _ in range(n + 50):
                cmds.append("cleanNextRoom")
            for i in range(1, n + 1):
                cmds.append(f"checkOut {i}")
        elif k % 4 == 1:
            for i in range(1, n + 1):
                cmds.append(f"checkIn {i} {i}")
            for t in range(1, m + 1):
                cmds.append(f"addTable {t} 3")
            for i in range(1, m + 1):
                cmds.append(f"enterDiningRoom {i} {i}")
            for _ in range(2500):
                cmds.append("reheatFood")
            for i in range(1, m + 1):
                cmds.append(f"leaveDiningRoom {i} {i}")
        elif k % 4 == 2:
            power_m = 1024
            for i in range(1, power_m + 1):
                cmds.append(f"checkIn {i} {i}")
                cmds.append(f"addTable {i} 1")
                cmds.append(f"enterDiningRoom {i} {i}")
            step = 1
            while step < power_m:
                for base in range(1, power_m + 1, step * 2):
                    cmds.append(f"joinTables {base} {base + step}")
                step *= 2
            for i in range(1, power_m + 1):
                cmds.append(f"leaveDiningRoom {i} 1")
            cmds.append("removeTable 1")
        else:
            for i in range(1, 1501):
                cmds.append(f"checkIn {i} {1501 - i}")
            for t in range(1, 501):
                cmds.append(f"addTable {t} 4")
            for _ in range(3000):
                r = rng.randint(0, 4)
                if r == 0:
                    cmds.append(f"enterDiningRoom {rng.randint(1, 1500)} {rng.randint(1, 500)}")
                elif r == 1:
                    cmds.append(f"joinFriend {rng.randint(1, 1500)} {rng.randint(1, 1500)}")
                elif r == 2:
                    cmds.append(f"leaveDiningRoom {rng.randint(1, 1500)} {rng.randint(1, 500)}")
                elif r == 3:
                    cmds.append("cleanNextRoom")
                else:
                    cmds.append("reheatFood")

        write_test("07_stress_complexity", tid, cmds)
        tid += 1

    # 8. 08_comprehensive_system (Full end-to-end multi-step system workflows)
    for k in range(15):
        rng = random.Random(8000 + k)
        cmds = []
        for i in range(1, 21):
            cmds.append(f"checkIn {i} {i * 10}")
        for t in range(1, 11):
            cmds.append(f"addTable {t} 5")

        for _ in range(150):
            op = rng.choice([
                "enterDiningRoom", "leaveDiningRoom", "joinFriend", 
                "joinTables", "reheatFood", "cleanNextRoom", "checkOut", "checkIn"
            ])
            g1, g2 = rng.randint(1, 30), rng.randint(1, 30)
            t1, t2 = rng.randint(1, 15), rng.randint(1, 15)
            
            if op == "enterDiningRoom":
                cmds.append(f"enterDiningRoom {g1} {t1}")
            elif op == "leaveDiningRoom":
                cmds.append(f"leaveDiningRoom {g1} {t1}")
            elif op == "joinFriend":
                cmds.append(f"joinFriend {g1} {g2}")
            elif op == "joinTables":
                cmds.append(f"joinTables {t1} {t2}")
            elif op == "reheatFood":
                cmds.append("reheatFood")
            elif op == "cleanNextRoom":
                cmds.append("cleanNextRoom")
            elif op == "checkOut":
                cmds.append(f"checkOut {g1}")
            elif op == "checkIn":
                cmds.append(f"checkIn {g1} {g1 * 100}")

        write_test("08_comprehensive_system", tid, cmds)
        tid += 1

    # 9. 09_mega_simulation (Massive long-running tests with 600+ commands each)
    for k in range(5):
        rng = random.Random(9000 + k)
        cmds = []
        num_guests, num_tables = 100, 30
        
        for i in range(1, num_guests + 1):
            cmds.append(f"checkIn {i} {i * 10}")
        for t in range(1, num_tables + 1):
            cmds.append(f"addTable {t} 4")
            
        for _ in range(600):
            op = rng.choices(
                ["enter", "leave", "joinF", "joinT", "reheat", "clean", "out", "in"],
                weights=[25, 15, 10, 5, 5, 10, 15, 15],
                k=1
            )[0]
            g1, g2 = rng.randint(1, num_guests), rng.randint(1, num_guests)
            t1, t2 = rng.randint(1, num_tables), rng.randint(1, num_tables)
            
            if op == "enter":
                cmds.append(f"enterDiningRoom {g1} {t1}")
            elif op == "leave":
                cmds.append(f"leaveDiningRoom {g1} {t1}")
            elif op == "joinF":
                cmds.append(f"joinFriend {g1} {g2}")
            elif op == "joinT":
                cmds.append(f"joinTables {t1} {t2}")
            elif op == "reheat":
                cmds.append("reheatFood")
            elif op == "clean":
                cmds.append("cleanNextRoom")
            elif op == "out":
                cmds.append(f"checkOut {g1}")
            elif op == "in":
                cmds.append(f"checkIn {g1} {g1 * 100 + rng.randint(1, 9999)}")

        write_test("09_mega_simulation", tid, cmds)
        tid += 1

    print(f"Successfully generated {tid - 1} total tests across 9 categories!")


if __name__ == "__main__":
    generate_all()
