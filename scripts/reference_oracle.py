#!/usr/bin/env python3
"""
Independent Reference Oracle for the Resort Management System Specification.
Implements an exact, verifiable state-machine model used to validate C++ data structure
implementations against functional invariants and edge-case transitions.
"""

from bisect import bisect_right
from typing import Dict, Optional, Set, List


class ResortReferenceOracle:
    def __init__(self) -> None:
        # guest_id -> {'room': int, 'table': Optional[int], 'meal_stamp': int}
        self.guests: Dict[int, dict] = {}
        # room_num -> guest_id
        self.rooms: Dict[int, int] = {}
        # table_id -> {'capacity': int, 'guests': Set[int]}
        self.tables: Dict[int, dict] = {}
        self.current_meal: int = 1
        self.last_cleaned_room: Optional[int] = None

    def check_in(self, guest_id: int, room_num: int) -> str:
        if guest_id <= 0 or room_num <= 0:
            return "checkIn: INVALID_INPUT"
        if guest_id in self.guests or room_num in self.rooms:
            return "checkIn: FAILURE"
        self.guests[guest_id] = {"room": room_num, "table": None, "meal_stamp": 0}
        self.rooms[room_num] = guest_id
        return "checkIn: SUCCESS"

    def check_out(self, guest_id: int) -> str:
        if guest_id <= 0:
            return "checkOut: INVALID_INPUT"
        if guest_id not in self.guests:
            return "checkOut: FAILURE"
        guest = self.guests[guest_id]
        if guest["table"] is not None:
            return "checkOut: FAILURE"
        del self.rooms[guest["room"]]
        del self.guests[guest_id]
        return "checkOut: SUCCESS"

    def add_table(self, table_id: int, capacity: int) -> str:
        if table_id <= 0 or capacity <= 0:
            return "addTable: INVALID_INPUT"
        if table_id in self.tables:
            return "addTable: FAILURE"
        self.tables[table_id] = {"capacity": capacity, "guests": set()}
        return "addTable: SUCCESS"

    def remove_table(self, table_id: int) -> str:
        if table_id <= 0:
            return "removeTable: INVALID_INPUT"
        if table_id not in self.tables:
            return "removeTable: FAILURE"
        if len(self.tables[table_id]["guests"]) > 0:
            return "removeTable: FAILURE"
        del self.tables[table_id]
        return "removeTable: SUCCESS"

    def enter_dining_room(self, guest_id: int, table_id: int) -> str:
        if guest_id <= 0 or table_id <= 0:
            return "enterDiningRoom: INVALID_INPUT"
        if guest_id not in self.guests or table_id not in self.tables:
            return "enterDiningRoom: FAILURE"
        guest = self.guests[guest_id]
        table = self.tables[table_id]
        if guest["table"] is not None:
            return "enterDiningRoom: FAILURE"
        if len(table["guests"]) >= table["capacity"]:
            return "enterDiningRoom: FAILURE"
        if guest["meal_stamp"] == self.current_meal:
            return "enterDiningRoom: FAILURE"
        guest["table"] = table_id
        guest["meal_stamp"] = self.current_meal
        table["guests"].add(guest_id)
        return "enterDiningRoom: SUCCESS"

    def leave_dining_room(self, guest_id: int, table_id: int) -> str:
        if guest_id <= 0 or table_id <= 0:
            return "leaveDiningRoom: INVALID_INPUT"
        if guest_id not in self.guests or table_id not in self.tables:
            return "leaveDiningRoom: FAILURE"
        guest = self.guests[guest_id]
        if guest["table"] != table_id:
            return "leaveDiningRoom: FAILURE"
        self.tables[table_id]["guests"].remove(guest_id)
        guest["table"] = None
        return "leaveDiningRoom: SUCCESS"

    def reheat_food(self) -> str:
        self.current_meal += 1
        for table in self.tables.values():
            for guest_id in table["guests"]:
                self.guests[guest_id]["meal_stamp"] = self.current_meal
        return "reheatFood: SUCCESS"

    def join_tables(self, table_id1: int, table_id2: int) -> str:
        if table_id1 <= 0 or table_id2 <= 0 or table_id1 == table_id2:
            return "joinTables: INVALID_INPUT"
        if table_id1 not in self.tables or table_id2 not in self.tables:
            return "joinTables: FAILURE"
        t1 = self.tables[table_id1]
        t2 = self.tables[table_id2]
        t1["capacity"] += t2["capacity"]
        for guest_id in t2["guests"]:
            self.guests[guest_id]["table"] = table_id1
            t1["guests"].add(guest_id)
        del self.tables[table_id2]
        return "joinTables: SUCCESS"

    def join_friend(self, guest_id1: int, guest_id2: int) -> str:
        if guest_id1 <= 0 or guest_id2 <= 0 or guest_id1 == guest_id2:
            return "joinFriend: INVALID_INPUT"
        if guest_id1 not in self.guests or guest_id2 not in self.guests:
            return "joinFriend: FAILURE"
        g1 = self.guests[guest_id1]
        g2 = self.guests[guest_id2]
        if g2["table"] is None:
            return "joinFriend: FAILURE"
        table_id = g2["table"]
        table = self.tables[table_id]
        if g1["table"] is not None:
            return "joinFriend: FAILURE"
        if len(table["guests"]) >= table["capacity"]:
            return "joinFriend: FAILURE"
        if g1["meal_stamp"] == self.current_meal:
            return "joinFriend: FAILURE"
        g1["table"] = table_id
        g1["meal_stamp"] = self.current_meal
        table["guests"].add(guest_id1)
        return f"joinFriend: SUCCESS, {table_id}"

    def clean_next_room(self) -> str:
        if not self.rooms:
            return "cleanNextRoom: FAILURE"
        sorted_rooms = sorted(self.rooms.keys())
        if self.last_cleaned_room is None:
            chosen = sorted_rooms[0]
        else:
            idx = bisect_right(sorted_rooms, self.last_cleaned_room)
            chosen = sorted_rooms[idx] if idx < len(sorted_rooms) else sorted_rooms[0]
        self.last_cleaned_room = chosen
        return f"cleanNextRoom: SUCCESS, {chosen}"

    def execute_commands(self, commands: List[str]) -> List[str]:
        outputs: List[str] = []
        for raw_line in commands:
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split()
            op = parts[0]
            if op == "checkIn":
                outputs.append(self.check_in(int(parts[1]), int(parts[2])))
            elif op == "checkOut":
                outputs.append(self.check_out(int(parts[1])))
            elif op == "addTable":
                outputs.append(self.add_table(int(parts[1]), int(parts[2])))
            elif op == "removeTable":
                outputs.append(self.remove_table(int(parts[1])))
            elif op == "enterDiningRoom":
                outputs.append(self.enter_dining_room(int(parts[1]), int(parts[2])))
            elif op == "leaveDiningRoom":
                outputs.append(self.leave_dining_room(int(parts[1]), int(parts[2])))
            elif op == "reheatFood":
                outputs.append(self.reheat_food())
            elif op == "joinTables":
                outputs.append(self.join_tables(int(parts[1]), int(parts[2])))
            elif op == "joinFriend":
                outputs.append(self.join_friend(int(parts[1]), int(parts[2])))
            elif op == "cleanNextRoom":
                outputs.append(self.clean_next_room())
            else:
                raise ValueError(f"Unsupported operation: {op}")
        return outputs


if __name__ == "__main__":
    import sys
    oracle = ResortReferenceOracle()
    results = oracle.execute_commands(sys.stdin.read().splitlines())
    if results:
        print("\n".join(results))
