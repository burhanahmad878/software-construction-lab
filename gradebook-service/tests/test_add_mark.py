"""Unit tests for the add_mark seam function."""

from unittest.mock import Mock
import pytest
from errors import NotFoundError, ValidationError
from gradebook import add_mark
from models import Mark


def fixed_now() -> str:
    """Provide a fixed timestamp for testing."""
    return "2026-10-12 09:00:00"


def test_valid_mark_is_stored_with_the_time(state: dict) -> None:
    """A valid mark should be recorded along with the current timestamp."""
    save = Mock()
    add_mark(state, Mark("S1", "A1", 15.0), fixed_now, save)
    assert state["marks"] == [
        {"student": "S1", "assessment": "A1", "score": 15.0, "at": "2026-10-12 09:00:00"}
    ]


def test_valid_mark_calls_save_once(state: dict) -> None:
    """Adding a valid mark must trigger saving the gradebook state exactly once."""
    save = Mock()
    add_mark(state, Mark("S1", "A1", 15.0), fixed_now, save)
    save.assert_called_once_with()


@pytest.mark.parametrize(
    ("mark", "error"),
    [
        pytest.param(Mark("NOPE", "A1", 5.0), NotFoundError, id="unknown-student"),
        pytest.param(Mark("S1", "GHOST", 5.0), NotFoundError, id="unknown-assessment"),
        pytest.param(Mark("S1", "A1", 21.0), ValidationError, id="score-above-total"),
    ],
)
def test_rejected_mark_changes_nothing(state: dict, mark: Mark, error: type[Exception]) -> None:
    """Invalid marks should raise an error, mutate nothing, and never save."""
    save = Mock()
    with pytest.raises(error):
        add_mark(state, mark, fixed_now, save)
    assert state["marks"] == []
    save.assert_not_called()
def test_add_mark_replaces_existing():
    """Adding a second mark for the same student and assessment should replace the old mark."""
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {"A1": {"id": "A1", "title": "Quiz", "weight": 10, "total": 20}},
        "marks": []
    }
    
    # Add first mark (score 5)
    add_mark(
        state=state,
        mark=Mark(student="S1", assessment="A1", score=5),
        now=lambda: "now",
        save=lambda: None
    )
    
    # Add second mark (score 18) for the same student and assessment
    add_mark(
        state=state,
        mark=Mark(student="S1", assessment="A1", score=18),
        now=lambda: "now",
        save=lambda: None
    )
    
    # Assert there is exactly one mark and its score is 18
    assert len(state["marks"]) == 1
    assert state["marks"][0]["score"] == 18