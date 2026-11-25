from errors import ValidationError

MAX_TOTAL_WEIGHT: float = 100.0
TOLERANCE: float = 1e-9

def ensure_weight_fits(existing_weights: list[float], new_weight: float) -> None:
    """Ensure that adding a new assessment weight does not exceed the maximum total weight of 100."""
    if sum(existing_weights) + new_weight > MAX_TOTAL_WEIGHT + TOLERANCE:
        raise ValidationError("Total weight cannot exceed 100")