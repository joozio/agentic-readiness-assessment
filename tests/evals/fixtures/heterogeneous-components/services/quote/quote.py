"""Quote service behavior."""


def quote(weight):
    if weight <= 0:
        raise ValueError("weight must be positive")
    return {"currency": "USD", "amount": 5 + 2 * weight}

