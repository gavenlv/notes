import re


def is_palindrome(s: str) -> bool:
    """Check if string s is palindrome ignoring non-alphanumeric and case."""
    s = re.sub(r"[^0-9a-zA-Z]", "", s).lower()
    return s == s[::-1]
