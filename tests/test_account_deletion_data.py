"""Phase 7/9: deleting an account must remove the personal data attached to it, and only that user's data."""
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


def _seed(env, st, tag):
    m = env.main
    (m.UPLOADS / f"{tag}.png").write_bytes(b"\x89PNG fixture")
    s = m.SessionLocal()
    try:
        sub = s.query(m.Submission).filter_by(application_id=st["aid"]).first()
        sub.link, sub.notes, sub.github, sub.video, sub.image = "https://x.example/l", "my private notes", "https://github.com/me/r", "https://v.example", f"/uploads/{tag}.png"
        s.add(m.PushSub(user_id=st["uid"], endpoint=f"https://push.example/{tag}", p256dh="k", auth="a"))
        s.add(m.Notification(user_id=st["uid"], title="hello", body="b"))
        s.add(m.Notification(user_id=None, to_admin=True, title="admin note about " + tag, body="b"))
        s.commit()
    finally:
        s.close()


def test_delete_purges_personal_data_but_only_for_that_user(env):
    a, b = env.student(1), env.student(2)
    _seed(env, a, "aaa"); _seed(env, b, "bbb")
    r = env.client.post("/api/me/delete", headers=a["h"], json={"password": "Pass12345"})
    assert r.status_code == 200, r.text
    m = env.main; s = m.SessionLocal()
    try:
        ua = s.get(m.User, a["uid"])
        assert ua.deletion_status == "completed" and not ua.active and ua.email.endswith("@deleted.invalid") and ua.name == "Deleted user"
        sa = s.query(m.Submission).filter_by(application_id=a["aid"]).one()
        assert (sa.link, sa.notes, sa.github, sa.video, sa.image) == ("", "", "", "", "")          # content removed, row kept
        assert s.query(m.PushSub).filter_by(user_id=a["uid"]).count() == 0
        assert s.query(m.Notification).filter_by(user_id=a["uid"]).count() == 0
        assert not (m.UPLOADS / "aaa.png").exists()                                                  # local screenshot file removed
        assert s.query(m.Application).filter_by(id=a["aid"]).count() == 1                           # enrollment record retained
        # the other student is untouched
        sb = s.query(m.Submission).filter_by(application_id=b["aid"]).one()
        assert sb.notes == "my private notes" and sb.image == "/uploads/bbb.png"
        assert s.query(m.PushSub).filter_by(user_id=b["uid"]).count() == 1
        assert s.query(m.Notification).filter_by(user_id=b["uid"]).count() == 1
        assert (m.UPLOADS / "bbb.png").exists()
        bodies = " ".join((n.body or "") + (n.title or "") for n in s.query(m.Notification).filter_by(to_admin=True))
        assert "pay1@example.com" not in bodies and "Pay 1" not in bodies                           # admin-side copies of the name/email are redacted
        assert "Pay 2" in bodies and "pay2@example.com" in bodies                                    # other students' admin notifications are untouched
    finally:
        s.close()
    assert env.client.get("/api/me", headers=a["h"]).status_code == 403                               # old token no longer works


def test_public_deletion_page_route_requires_password_and_purges(env):
    a = env.student(1); _seed(env, a, "ccc")
    assert env.client.post("/api/account-delete-request", json={"email": "pay1@example.com", "password": "wrong"}).status_code == 401
    assert env.client.post("/api/account-delete-request", json={"email": "pay1@example.com", "password": "Pass12345"}).status_code == 200
    assert not (env.main.UPLOADS / "ccc.png").exists()
    assert env.client.post("/api/account-delete-request", json={"email": "pay1@example.com", "password": "Pass12345"}).status_code in (404, 409)


def test_path_traversal_in_stored_url_cannot_delete_other_files(env, tmp_path):
    victim = tmp_path / "victim.txt"; victim.write_text("keep")
    env.main.delete_local_upload("/uploads/../victim.txt")
    env.main.delete_local_upload("/uploads/sub/../../victim.txt")
    assert victim.exists()


def test_deletion_page_states_scope(env):
    r = env.client.get("/delete-account-request")
    assert r.status_code == 200 and "What is deleted" in r.text and "What is kept" in r.text and "com.upnivo.app" in r.text
