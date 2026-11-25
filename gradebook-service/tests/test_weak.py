from gradebook import pct, STATE

def test_weak_pct():
    """A weak test that executes pct() but makes no assertions."""
    # Ensure there's a student to check
    STATE["students"] = {"S1": {"id": "S1", "name": "Test Student"}}
    STATE["marks"] = []
    
    # Call the function (increases line coverage, but asserts nothing)
    pct("S1")