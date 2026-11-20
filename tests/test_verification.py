import base64
import importlib
import struct
import sys
import zlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _reload_main(monkeypatch, tmp_path, app_env="development", admin_email="admin@example.com", admin_password="StrongPass123!"):
    monkeypatch.setenv("APP_ENV", app_env)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'app.db'}")
    monkeypatch.setenv("ADMIN_EMAIL", admin_email)
    monkeypatch.setenv("ADMIN_PASSWORD", admin_password)
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://example.com")
    monkeypatch.delenv("RAZORPAY_KEY_ID", raising=False)
    monkeypatch.delenv("RAZORPAY_KEY_SECRET", raising=False)
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("VAPID_PUBLIC_KEY", raising=False)
    import main
    importlib.reload(main)
    return main


def _png_data_url():
    def chunk(tag, data):
        return (
            struct.pack("!I", len(data))
            + tag
            + data
            + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = b"\x00\x00\x00\x00\x00"
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack("!IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw))
    png += chunk(b"IEND", b"")
    return "data:image/png;base64," + base64.b64encode(png).decode()


def test_production_requires_database_url(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "StrongPass123!")
    sys.modules.pop("main", None)
    with pytest.raises(RuntimeError):
        import main


def test_cors_and_admin_gate(monkeypatch, tmp_path):
    main = _reload_main(monkeypatch, tmp_path, admin_email="admin@example.com", admin_password="StrongPass123!")
    with TestClient(main.app) as client:
        response = client.options(
            "/api/login",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") in {"*", "https://example.com"}

        student_email = "student.verify@example.com"
        response = client.post(
            "/api/register",
            json={
                "name": "Student A",
                "email": student_email,
                "mobile": "9999999999",
                "college": "Test College",
                "degree": "B.E.",
                "department": "CSE",
                "year": "2025",
                "password": "Pass12345",
            },
        )
        assert response.status_code == 200
        token = response.json()["token"]

        response = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

        admin_login = client.post(
            "/api/admin/login",
            json={"email": "admin@example.com", "password": "StrongPass123!"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["token"]
        stats = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
        assert stats.status_code == 200
        assert stats.json()["students"] >= 1


def test_upload_validation_and_account_delete(monkeypatch, tmp_path):
    main = _reload_main(monkeypatch, tmp_path, admin_email="admin@example.com", admin_password="StrongPass123!")
    with TestClient(main.app) as client:
        email = "student.delete@example.com"
        register = client.post(
            "/api/register",
            json={
                "name": "Student B",
                "email": email,
                "mobile": "9999999998",
                "college": "Test College",
                "degree": "B.Tech",
                "department": "IT",
                "year": "2026",
                "password": "Pass12345",
            },
        )
        assert register.status_code == 200
        token = register.json()["token"]

        valid_upload = client.post(
            "/api/upload",
            json={"data": _png_data_url()},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert valid_upload.status_code == 200
        assert valid_upload.json()["url"].startswith("/uploads/") or valid_upload.json()["url"].startswith("http")

        invalid_upload = client.post(
            "/api/upload",
            json={"data": "data:text/plain;base64,SGVsbG8="},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert invalid_upload.status_code == 400

        delete_response = client.post(
            "/api/me/delete",
            json={"password": "Pass12345"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_response.status_code == 200

        db = main.SessionLocal()
        try:
            user = db.query(main.User).filter(main.User.active.is_(False)).filter(main.User.email.like("deleted%") | main.User.email.like("%deleted.invalid")).first()
            assert user is not None
            assert user.active is False
            assert user.deletion_status == "completed"
            assert user.deleted_at is not None
        finally:
            db.close()

        public_request = client.post(
            "/api/account-delete-request",
            json={"email": email, "password": "Pass12345"},
        )
        assert public_request.status_code == 404

        second_register = client.post(
            "/api/register",
            json={
                "name": "Student C",
                "email": "student.delete2@example.com",
                "mobile": "9999999997",
                "college": "Another College",
                "degree": "MCA",
                "department": "CS",
                "year": "2027",
                "password": "Pass12345",
            },
        )
        assert second_register.status_code == 200
        public_delete = client.post(
            "/api/account-delete-request",
            json={"email": "student.delete2@example.com", "password": "Pass12345"},
        )
        assert public_delete.status_code == 200


def test_storage_security_validates_paths(monkeypatch, tmp_path):
    main = _reload_main(monkeypatch, tmp_path)
    assert main.clean_url("/uploads/../secret.txt") == ""
    assert main.clean_url("https://example.com/../../evil.png") == ""
    assert main.clean_url("/uploads/sample-123.png") == "/uploads/sample-123.png"

    uploaded = main.save_image(_png_data_url())
    assert uploaded.startswith("/uploads/")
    assert (main.UPLOADS / Path(uploaded).name).exists()

    with pytest.raises(Exception):
        main.persist_upload(b"not-an-image", "php")


def test_local_dev_database_is_safe(monkeypatch, tmp_path):
    main = _reload_main(monkeypatch, tmp_path)
    with TestClient(main.app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "UPNIVO" in response.text or "app" in response.text.lower()
        assert "sqlite" in main.DB.lower()
