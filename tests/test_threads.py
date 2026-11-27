import pytest

from meta_engine.threads import code_from_redirect


def test_code_from_redirect_strips_meta_suffix():
    assert code_from_redirect("https://localhost/?code=AQBx123#_") == "AQBx123"
    assert code_from_redirect("  https://localhost/?code=abc&state=1 ") == "abc"


def test_code_from_redirect_rejects_url_without_code():
    with pytest.raises(SystemExit):
        code_from_redirect("https://localhost/?error=access_denied")


def test_reads_retry_network_errors_but_writes_do_not(monkeypatch):
    import urllib.error
    from meta_engine import threads
    calls = []

    def flaky(req, timeout):
        calls.append(req.data)
        raise urllib.error.URLError("timed out")
    monkeypatch.setattr(threads.urllib.request, "urlopen", flaky)
    monkeypatch.setattr(threads.time, "sleep", lambda s: None)
    with pytest.raises(SystemExit) as e:
        threads._call("https://x/read")
    assert len(calls) == 3 and threads.is_transient(e.value)
    calls.clear()
    with pytest.raises(SystemExit):
        threads._call("https://x/write", {"a": 1})
    assert len(calls) == 1  # a lost write response may have posted: never resend


def test_is_transient_separates_hiccups_from_real_refusals():
    from meta_engine.threads import is_transient
    assert is_transient("Threads API error: Please retry your request later.")
    assert is_transient("Threads API error: boom (HTTP 503)")
    assert not is_transient("Threads API error: Invalid parameter")
