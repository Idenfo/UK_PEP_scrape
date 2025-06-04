import pytest

def test_error_handling():
    with pytest.raises(ValueError):
        raise ValueError("This is a test error")

    with pytest.raises(KeyError):
        raise KeyError("This is a test key error")