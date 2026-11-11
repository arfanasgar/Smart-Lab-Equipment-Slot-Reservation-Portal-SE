from elevator_dispatch import next_direction, door_action, pick_elevator


def test_next_direction_every_branch():
    # direction == up: above / below / no requests
    assert next_direction(3, "up", [5]) == "up"
    assert next_direction(3, "up", [1]) == "down"
    assert next_direction(3, "up", []) == "idle"

    # direction == down: below / above / no requests
    assert next_direction(3, "down", [1]) == "down"
    assert next_direction(3, "down", [5]) == "up"
    assert next_direction(3, "down", []) == "idle"

    # Any other direction: above / below / no requests
    assert next_direction(3, "idle", [5]) == "up"
    assert next_direction(3, "idle", [1]) == "down"
    assert next_direction(3, "idle", []) == "idle"


def test_door_action_every_branch():
    assert door_action(100, False, True) == "hold_open"  # emergency true
    assert door_action(700, False, False) == "overload"  # overload true
    assert door_action(630, True, False) == "reopen"     # blocked true; boundary is not overload
    assert door_action(630, False, False) == "close"     # blocked false


def test_pick_elevator_every_branch():
    assert pick_elevator([], 5) is None  # loop executes zero times
    # First car initializes best; idle and moving paths are both exercised.
    assert pick_elevator([("A", 5, True)], 5) == "A"
    assert pick_elevator([("A", 5, False)], 5) == "A"
    # Later candidate has a smaller gap (comparison true).
    assert pick_elevator([("A", 1, True), ("B", 5, True)], 5) == "B"
    # Later candidate does not have a smaller gap (comparison false).
    assert pick_elevator([("A", 5, True), ("B", 1, False)], 5) == "A"
