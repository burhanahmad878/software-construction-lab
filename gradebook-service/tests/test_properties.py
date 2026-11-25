from unittest.mock import patch
import pytest
from hypothesis import given, strategies as st
import gradebook

@given(scores=st.lists(st.integers(min_value=0, max_value=20), min_size=1, max_size=5))
def test_pct_never_exceeds_max(scores):
    """Property test: Percentage should never exceed 100% regardless of added marks."""
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {"A1": {"id": "A1", "title": "Quiz", "weight": 10, "total": 20}},
        "marks": []
    }
    
    for score in scores:
        gradebook.add_mark(
            state=state,
            mark=gradebook.Mark(student="S1", assessment="A1", score=score),
            now=lambda: "now",
            save=lambda: None
        )
        
    with patch.object(gradebook, "STATE", state):
        percentage = float(gradebook.pct("S1"))
        assert percentage <= 10.0