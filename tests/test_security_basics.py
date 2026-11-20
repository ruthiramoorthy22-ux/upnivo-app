"""Phase 10: security headers, CORS, auth boundaries, rate limiting, health."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pytest
from test_payments import _load, Env


@pytest.fixture
def env(monkeypatch, tmp_path):
    e = Env(_load(monkeypatch, tmp_path))
    yield e
    e.close()


def test_security_headers_present(env):
    for path in ("/", "/api/internships", "/delete-account-request", "/static/app.html"):
        h = env.client.get(path).headers
        assert h["x-content-type-options"] == "nosniff", path
        assert h["x-frame-options"] == "SAMEORIGIN" and "referrer-policy" in h and "permissions-policy" in h, path


def test_hsts_only_over_https(env):
    assert "strict-transport-security" not in env.client.get("/").headers
    assert "max-age" in env.client.get("/", headers={"x-forwarded-proto": "https"}).headers["strict-transport-security"]


def test_cors_allows_only_configured_origin(env):
    ok = env.client.options("/api/login", headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"})
    bad = env.client.options("/api/login", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert ok.headers.get("access-control-allow-origin") == "https://example.com"
    assert "access-control-allow-origin" not in bad.headers


def test_protected_routes_reject_anonymous_and_students(env):
    st = env.student()
    for path in ("/api/applications", "/api/me", "/api/notifications"):
        assert env.client.get(path).status_code in (401, 403), path
    for path in ("/api/admin/students", "/api/admin/payments", "/api/admin/settings", "/api/admin/applications"):
        assert env.client.get(path, headers=st["h"]).status_code == 403, path
        assert env.client.get(path).status_code in (401, 403), path


def test_forged_and_expired_tokens_rejected(env):
    import jwt, datetime as dt
    forged = jwt.encode({"sub": "1", "role": "admin", "exp": dt.datetime.utcnow() + dt.timedelta(days=1)}, "wrong-secret", "HS256")
    expired = jwt.encode({"sub": "1", "role": "admin", "exp": dt.datetime.utcnow() - dt.timedelta(days=1)}, "test-secret-key", "HS256")
    for t in (forged, expired, "garbage", ""):
        assert env.client.get("/api/admin/students", headers={"Authorization": f"Bearer {t}"}).status_code in (401, 403)


def test_token_role_claim_is_not_trusted(env):
    import jwt, datetime as dt
    st = env.student()
    tok = jwt.encode({"sub": str(st["uid"]), "role": "admin", "exp": dt.datetime.utcnow() + dt.timedelta(days=1)}, "test-secret-key", "HS256")
    assert env.client.get("/api/admin/students", headers={"Authorization": f"Bearer {tok}"}).status_code == 403


def test_student_cannot_read_another_students_program(env):
    a, b = env.student(1), env.student(2)
    assert env.client.get(f"/api/applications/{a['aid']}/tasks", headers=b["h"]).status_code in (403, 404)
    assert env.client.get(f"/api/applications/{a['aid']}/offer-letter", headers=b["h"]).status_code in (403, 404)


def test_login_is_rate_limited(env):
    codes = [env.client.post("/api/login", json={"email": "nobody@example.com", "password": "x"}).status_code for _ in range(8)]
    assert 429 in codes and codes[0] in (400, 401)


def test_login_error_does_not_reveal_which_part_was_wrong(env):
    env.student()
    a = env.client.post("/api/login", json={"email": "pay1@example.com", "password": "bad"})
    b = env.client.post("/api/login", json={"email": "nobody@example.com", "password": "bad"})
    assert a.status_code == b.status_code and a.json() == b.json()


def test_upload_rejects_non_images_and_oversize(env):
    st = env.student()
    for data in ("data:text/html;base64,PHNjcmlwdD4=", "data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=", "not-a-data-url"):
        assert env.client.post("/api/upload", headers=st["h"], json={"data": data}).status_code == 400
    import base64
    big = "data:image/png;base64," + base64.b64encode(b"0" * (env.main.UPLOAD_MAX_BYTES + 10)).decode()
    assert env.client.post("/api/upload", headers=st["h"], json={"data": big}).status_code == 413
    assert env.client.post("/api/upload", json={"data": big}).status_code in (401, 403)


def test_registration_validation_and_duplicates(env):
    ok = {"name": "A B", "email": "dup@example.com", "mobile": "9999999999", "college": "C", "degree": "B.E.", "department": "CSE", "year": "2025", "password": "Pass12345"}
    assert env.client.post("/api/register", json=ok).status_code == 200
    assert env.client.post("/api/register", json=ok).status_code in (400, 409)
    assert env.client.post("/api/register", json={**ok, "email": "short@example.com", "password": "123"}).status_code in (400, 422)


def test_health_check_ok_and_minimal(env):
    r = env.client.get("/api/health")
    assert r.status_code == 200 and r.json() == {"status": "ok", "database": "ok"}


def test_health_check_reports_db_failure_without_details(env):
    class Broken:
        def execute(self, *a, **k): raise RuntimeError("password=hunter2 host=internal-db")
        def close(self): pass
    env.main.app.dependency_overrides[env.main.db] = lambda: Broken()
    try:
        r = env.client.get("/api/health")
    finally:
        env.main.app.dependency_overrides.clear()
    assert r.status_code == 503 and "hunter2" not in r.text and "internal-db" not in r.text


def test_support_email_is_injected_only_when_valid(monkeypatch, env):
    assert "admin@yourdomain.com" in env.client.get("/").text                      # placeholder stays until you configure a real address
    monkeypatch.setenv("SUPPORT_EMAIL", "help@example.org")
    t = env.client.get("/").text
    assert "help@example.org" in t and "admin@yourdomain.com" not in t
    monkeypatch.setenv("SUPPORT_EMAIL", 'x"><script>alert(1)</script>@e.com')
    assert "<script>alert(1)" not in env.client.get("/").text                     # malformed values are ignored, never injected
    monkeypatch.delenv("SUPPORT_EMAIL")


def test_privacy_policy_matches_implementation(env):
    t = env.client.get("/static/app.html").text
    assert "anyone who verifies your certificate" not in t                          # no certificate-verification feature exists
    assert "push-notification registration" in t and "Razorpay" in t and "Google Fonts" in t


def test_policy_pages_are_standalone_html(monkeypatch, env):
    for path, needle in (("/privacy", "What we collect"), ("/terms", "Terms"), ("/refund", "Refund")):
        r = env.client.get(path, follow_redirects=False)
        assert r.status_code == 200 and needle in r.text and "<script" not in r.text and "${" not in r.text, path
        assert 'name="viewport"' in r.text
    monkeypatch.setenv("SUPPORT_EMAIL", "help@example.org")
    assert "help@example.org" in env.client.get("/privacy").text
    monkeypatch.delenv("SUPPORT_EMAIL")


@pytest.mark.parametrize("given,expected", [
    ("postgres://u:p@h:5432/d", "postgresql+psycopg://u:p@h:5432/d"),
    ("postgresql://u:p@h/d?sslmode=require", "postgresql+psycopg://u:p@h/d?sslmode=require"),
    ("postgresql+psycopg://u:p@h/d", "postgresql+psycopg://u:p@h/d"),
    ("sqlite:///./x.db", "sqlite:///./x.db"),
])
def test_database_url_normalisation(env, given, expected):
    assert env.main.normalize_db_url(given) == expected


def _admin_exists(main):
    s = main.SessionLocal()
    try:
        return s.query(main.User).filter_by(role="admin").count()
    finally:
        s.close()


def test_no_default_admin_password_on_a_real_database(monkeypatch, tmp_path):
    """Production or a non-SQLite DB without ADMIN_PASSWORD must not create/reset an admin with the well-known default."""
    from fastapi.testclient import TestClient
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'p.db'}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "u"))
    monkeypatch.setenv("SECRET_KEY", "k")
    monkeypatch.setenv("UPLOAD_STORAGE_PROVIDER", "cloudinary")   # production refuses local storage; no upload is made in this test
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    import importlib, main
    importlib.reload(main)
    with TestClient(main.app) as c:
        assert _admin_exists(main) == 0
        assert c.post("/api/admin/login", json={"email": "admin@yourdomain.com", "password": "change-me-in-production"}).status_code in (400, 401, 403)
    monkeypatch.setenv("ADMIN_PASSWORD", "A-real-Strong-Pass-1")
    importlib.reload(main)
    with TestClient(main.app) as c:
        assert _admin_exists(main) == 1
        assert c.post("/api/admin/login", json={"email": "admin@yourdomain.com", "password": "A-real-Strong-Pass-1"}).status_code == 200
        assert c.post("/api/admin/login", json={"email": "admin@yourdomain.com", "password": "change-me-in-production"}).status_code in (400, 401, 403)


def test_local_sqlite_development_keeps_the_convenience_default(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'd.db'}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "u"))
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    import importlib, main
    importlib.reload(main)
    with TestClient(main.app):
        assert _admin_exists(main) == 1
