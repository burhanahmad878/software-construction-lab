from unittest.mock import Mock

import pytest

from errors import ConflictError, ValidationError
from gradebook import add_assessment


def test_add_assessment_valid(state):
    assessment = {"id": "AX", "name": "Quiz 1", "weight": 30, "total": 20}
    save_mock = Mock()

    add_assessment(state, assessment, save_mock)

    if isinstance(state["assessments"], dict):
        assert assessment in state["assessments"].values()
    else:
        assert assessment in state["assessments"]

    save_mock.assert_called_once()


def test_add_assessment_exceeds_weight(state):
    state["assessments"] = [{"id": "A1", "name": "Exam", "weight": 80, "total": 100}]
    new_assessment = {"id": "A2", "name": "Quiz", "weight": 30, "total": 20}
    save_mock = Mock()

    with pytest.raises(ValidationError):
        add_assessment(state, new_assessment, save_mock)

    assert new_assessment not in state["assessments"]
    save_mock.assert_not_called()


def test_add_assessment_duplicate_id(state):
    state["assessments"] = [{"id": "A1", "name": "Quiz 1", "weight": 30, "total": 20}]
    duplicate = {"id": "A1", "name": "Quiz 1 Duplicate", "weight": 20, "total": 20}
    save_mock = Mock()

    with pytest.raises(ConflictError):
        add_assessment(state, duplicate, save_mock)

    save_mock.assert_not_called()


def test_failed_save_leaves_no_trace(state):
    def failing_save() -> None:
        raise OSError("disk full")

    with pytest.raises(OSError):
        add_assessment(
            state,
            {"id": "A3", "title": "Final", "weight": 10.0, "total": 50.0},
            failing_save,
        )

    assert "A3" not in state["assessments"]
