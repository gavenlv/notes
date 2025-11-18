from unittest.mock import Mock, patch
from chapter5.fetcher import fetch_title


def test_fetch_title_ok():
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = '<html><head><title>Hi</title></head><body></body></html>'

    with patch("chapter5.fetcher.requests.get", return_value=mock_resp) as m:
        title = fetch_title("http://example.com")
        assert title == "Hi"
        m.assert_called_once()


def test_fetch_title_bad_status():
    mock_resp = Mock()
    mock_resp.status_code = 500
    mock_resp.text = ''

    with patch("chapter5.fetcher.requests.get", return_value=mock_resp):
        try:
            fetch_title("http://example.com")
            assert False, "Expected RuntimeError"
        except RuntimeError as e:
            assert "Bad status" in str(e)
