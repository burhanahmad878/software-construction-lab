import pytest
from rules import ensure_weight_fits
from gradebook import add_mark, STATE, ValidationError
from models import Mark

@pytest.mark.parametrize(
    "existing, new, expected_valid",
    [
        ([], 0, True),              # Weight 0 is accepted
        ([], 100, True),            # Weight 100 is accepted
        ([80], 20.01, False),       # 100.01 is rejected
        ([0], 0.01, True),          # Total 0.01 is accepted
    ]
)
def test_weight_boundaries(existing, new, expected_valid):
    if expected_valid:
        ensure_weight_fits(existing, new)
    else:
        with pytest.raises(ValidationError):
            ensure_weight_fits(existing, new)

def test_mark_score_boundaries():
    """Test score boundaries for an assessment with a total of 20."""
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {"A1": {"id": "A1", "title": "Quiz", "weight": 10, "total": 20}},
        "marks": []
    }
    
    fixed_now = lambda: "now"
    save_mock = lambda: None

    # Score 0 is accepted
    add_mark(state, Mark("S1", "A1", 0), fixed_now, save_mock)
    
    # Score 20 is accepted
    add_mark(state, Mark("S1", "A1", 20), fixed_now, save_mock)

    # Score -0.01 is rejected
    with pytest.raises(ValidationError):
        add_mark(state, Mark("S1", "A1", -0.01), fixed_now, save_mock)

    # Score 20.01 is rejected
    with pytest.raises(ValidationError):
        add_mark(state, Mark("S1", "A1", 20.01), fixed_now, save_mock)