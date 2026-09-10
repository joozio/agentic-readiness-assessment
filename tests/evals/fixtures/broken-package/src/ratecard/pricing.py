"""Pure pricing behavior."""


def quote(weight, base_fee, per_kilogram):
    if weight <= 0:
        raise ValueError("weight must be positive")
    return base_fee + per_kilogram * weight

