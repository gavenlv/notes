import pytest
from chapter4.is_palindrome import is_palindrome


@pytest.mark.parametrize("s,expected", [
    ("", True),
    ("a", True),
    ("Aa", True),
    ("A man, a plan, a canal: Panama", True),
    ("race a car", False),
    ("12321", True),
    ("1231", False),
])
def test_is_palindrome(s, expected):
    assert is_palindrome(s) is expected
