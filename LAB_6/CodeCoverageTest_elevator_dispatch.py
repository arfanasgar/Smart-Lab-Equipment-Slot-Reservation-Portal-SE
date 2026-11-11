from elevator_dispatch import next_direction, door_action, pick_elevator


def test_next_direction_all_outcomes():
    assert next_direction(3, "up", [5]) == "up"
    assert next_direction(3, "up", [1]) == "down"
    assert next_direction(3, "up", []) == "idle"
    assert next_direction(3, "down", [1]) == "down"
    assert next_direction(3, "down", [5]) == "up"
    assert next_direction(3, "down", []) == "idle"
    assert next_direction(3, "idle", [5]) == "up"
    assert next_direction(3, "idle", [1]) == "down"
    assert next_direction(3, "idle", []) == "idle"


def test_door_action_all_outcomes():
    assert door_action(100, False, True) == "hold_open"
    assert door_action(631, False, False) == "overload"
    assert door_action(100, True, False) == "reopen"
    assert door_action(100, False, False) == "close"


def test_pick_elevator_all_outcomes():
    assert pick_elevator([], 5) is None
    assert pick_elevator([("A", 5, True)], 5) == "A"
    assert pick_elevator([("A", 1, False)], 5) == "A"
    assert pick_elevator([("A", 1, True), ("B", 5, True)], 5) == "B"
    assert pick_elevator([("A", 5, True), ("B", 1, True)], 5) == "A"
