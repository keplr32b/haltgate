"""Structural checks for HaltGate helpers (no network)."""

def host_of(url: str) -> str:
    u = (url or "").strip().lower()
    assert u.startswith("https://"), "only https"
    rest = u[8:]
    host = rest.split("/")[0].split("?")[0].split("#")[0]
    assert len(host) > 0
    assert "@" not in host
    assert not host.replace(".", "").isdigit()
    assert "localhost" not in host
    assert not host.endswith(".local")
    return host


def test_host_https_ok():
    assert host_of("https://docs.genlayer.com/path") == "docs.genlayer.com"


def test_host_rejects_http():
    try:
        host_of("http://docs.genlayer.com")
        assert False
    except AssertionError:
        pass


def test_host_rejects_localhost():
    try:
        host_of("https://localhost/x")
        assert False
    except AssertionError:
        pass


def test_verdict_labels():
    allowed = {"CONFIRMED", "CLEAR", "INCONCLUSIVE"}
    assert "CONFIRMED" in allowed
    assert "CLEAR" in allowed


def test_repo_markers():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    text = (root / "contracts" / "haltgate.py").read_text(encoding="utf-8")
    assert "owner_clear_halt" in text
    assert "prompt_comparative" in text
    assert "is_halted" in text
