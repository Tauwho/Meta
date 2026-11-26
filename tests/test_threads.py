import pytest

from medium_engine.threads import code_from_redirect


def test_code_from_redirect_strips_meta_suffix():
    assert code_from_redirect("https://localhost/?code=AQBx123#_") == "AQBx123"
    assert code_from_redirect("  https://localhost/?code=abc&state=1 ") == "abc"


def test_code_from_redirect_rejects_url_without_code():
    with pytest.raises(SystemExit):
        code_from_redirect("https://localhost/?error=access_denied")
