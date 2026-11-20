"""Phase 10: end-to-end regression of the student and admin journeys through the real API (isolated SQLite, mocked gateway)."""
import base64
import datetime as dt
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pytest
from test_payments import _load, Env

PNG = "data:image/png;base64," + base64.b64encode(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")).decode()
DOMAINS = {"Full Stack", "Python", "Java", "AI/ML", "UI/UX", "Cyber Security", "Data Analytics", "Digital Marketing", "Mobile App", "Cloud DevOps"}
REG = {"mobile": "9999999999", "college": "Test College", "degree": "B.E.", "department": "CSE", "year": "2026", "password": "Pass12345"}


@pytest.fixture
def env(monkeypatch, tmp_path):
    e = Env(_load(monkeypatch, tmp_path))
    e.adm = e.admin()
    yield e
    e.close()


def register(env, n, name=None):
    r = env.client.post("/api/register", json={**REG, "name": name or f"Student {n}", "email": f"s{n}@example.com"})
    assert r.status_code == 200, r.text
    return {"h": {"Authorization": f"Bearer {r.json()['token']}"}, "uid": r.json()["user"]["id"], "name": name or f"Student {n}"}


def domain_id(env, category):
    return next(i["id"] for i in env.client.get("/api/internships").json() if i["category"] == category)


def enroll_and_start(env, st, category, months, start=None):
    iid = domain_id(env, category)
    assert env.client.post(f"/api/internships/{iid}/apply", headers=st["h"], json={"months": months}).status_code == 200
    app = next(a for a in env.client.get("/api/applications", headers=st["h"]).json() if a["internship_id"] == iid)
    assert env.client.put(f"/api/admin/applications/{app['id']}", headers=env.adm, json={"status": "Approved"}).status_code == 200
    r = env.client.post(f"/api/admin/applications/{app['id']}/offer", headers=env.adm, json={"start_date": (start or dt.date.today()).isoformat()})
    assert r.status_code == 200, r.text
    return app["id"], iid


def tasks(env, st, aid):
    r = env.client.get(f"/api/applications/{aid}/tasks", headers=st["h"])
    assert r.status_code == 200, r.text
    return r.json()


def submit(env, st, aid, tid, **kw):
    return env.client.post(f"/api/applications/{aid}/tasks/{tid}/submit", headers=st["h"], json={"notes": "done", **kw})


def finish_all(env, st, aid):
    """Submit tasks in order, re-reading state each time (a task opens only after the previous one is submitted)."""
    for _ in range(200):
        nxt = next((t for t in tasks(env, st, aid)["tasks"] if t["state"] == "open"), None)
        if not nxt:
            return
        assert submit(env, st, aid, nxt["id"], link="https://x.example/" + str(nxt["day"])).status_code == 200
    raise AssertionError("plan never completed")


# ------------------------------------------------------------------ STUDENT 1-22
def test_student_full_journey(env):
    c = env.client
    # 1-3 registration, login, logout
    st = register(env, 1, "Asha Student")
    assert c.post("/api/register", json={**REG, "name": "x", "email": "s1@example.com"}).status_code in (400, 409)
    lg = c.post("/api/login", json={"email": "s1@example.com", "password": "Pass12345"})
    assert lg.status_code == 200 and lg.json()["token"]
    assert c.post("/api/login", json={"email": "s1@example.com", "password": "nope"}).status_code in (400, 401)
    assert c.get("/api/me", headers=st["h"]).json()["email"] == "s1@example.com"
    assert c.get("/api/me").status_code in (401, 403)                                    # "logged out" = no token = no access
    # 4 profile editing (name/email deliberately not editable)
    r = c.put("/api/me", headers=st["h"], json={"city": "Madurai", "state": "Tamil Nadu", "about": "Hello", "gender": "Female", "photo": PNG and c.post("/api/upload", headers=st["h"], json={"data": PNG}).json()["url"]})
    assert r.status_code == 200 and r.json()["city"] == "Madurai" and r.json()["photo"].startswith("/uploads/")
    # 5-6 domains + domain selection
    L = c.get("/api/internships").json()
    assert len(L) == 10 and {i["category"] for i in L} == DOMAINS
    assert c.get(f"/api/internships/{L[0]['id']}", headers=st["h"]).json()["id"] == L[0]["id"]
    # 7-8 plan selection and enrollment
    iid = domain_id(env, "Python")
    assert c.post(f"/api/internships/{iid}/apply", headers=st["h"], json={"months": 9}).status_code in (400, 422)
    assert c.post(f"/api/internships/{iid}/apply", headers=st["h"], json={"months": 1}).status_code == 200
    assert c.post(f"/api/internships/{iid}/apply", headers=st["h"], json={"months": 1}).status_code in (400, 409)  # no duplicate enrollment
    app = c.get("/api/applications", headers=st["h"]).json()[0]
    assert app["status"] == "Pending" and app["months"] == 1
    aid = app["id"]
    assert c.get(f"/api/applications/{aid}/tasks", headers=st["h"]).status_code == 403        # locked until approved + offer
    # 9 approval, 18 offer letter
    assert c.put(f"/api/admin/applications/{aid}", headers=env.adm, json={"status": "Approved"}).status_code == 200
    assert c.post(f"/api/admin/applications/{aid}/offer", headers=env.adm, json={"start_date": dt.date.today().isoformat(), "note": "Welcome"}).status_code == 200
    ol = c.get(f"/api/applications/{aid}/offer-letter", headers=st["h"])
    assert ol.status_code == 200 and "Asha Student" in ol.text and "UPNIVO INTERN" in ol.text and 'alt="UPNIVO INTERN"' in ol.text
    other = register(env, 2)
    assert c.get(f"/api/applications/{aid}/offer-letter", headers=other["h"]).status_code in (403, 404)
    # 10 daily tasks: exactly the first is open, the rest locked
    T = tasks(env, st, aid)["tasks"]
    assert len(T) == 20 and [t["state"] for t in T[:3]] == ["open", "locked", "locked"]
    assert submit(env, st, aid, T[1]["id"], link="https://x.example").status_code in (400, 403, 409)  # cannot skip ahead
    # 11-15 task submission with GitHub, demo, notes, screenshot
    shot = c.post("/api/upload", headers=st["h"], json={"data": PNG}).json()["url"]
    assert submit(env, st, aid, T[0]["id"], link="https://x.example/work", github="https://github.com/a/b", video="https://youtu.be/abc", image=shot).status_code == 200
    t0 = tasks(env, st, aid)["tasks"][0]
    assert (t0["state"], t0["github"], t0["video"], t0["notes"], t0["sub_image"]) == ("submitted", "https://github.com/a/b", "https://youtu.be/abc", "done", shot)
    assert tasks(env, st, aid)["tasks"][1]["state"] == "open"                                       # next task unlocks
    assert submit(env, st, aid, T[1]["id"], github="javascript:alert(1)").status_code in (200, 400)  # never stored as a live script URL
    stored = tasks(env, st, aid)["tasks"][1]["github"]
    assert not stored.lower().startswith("javascript:")
    # admin reviews: rework then approve
    sid = c.get("/api/admin/submissions", headers=env.adm).json()[0]["id"]
    assert c.put(f"/api/admin/submissions/{sid}", headers=env.adm, json={"status": "Rework", "feedback": "Add README"}).status_code == 200
    assert tasks(env, st, aid)["tasks"][0]["state"] == "rework" and tasks(env, st, aid)["tasks"][0]["feedback"] == "Add README"
    assert c.put(f"/api/admin/submissions/{sid}", headers=env.adm, json={"status": "Approved"}).status_code == 200
    assert c.put(f"/api/admin/submissions/{sid}", headers=env.adm, json={"status": "Bogus"}).status_code == 400
    # 16 progress through the whole plan
    finish_all(env, st, aid)
    data = tasks(env, st, aid)
    assert all(t["state"] in ("submitted", "approved") for t in data["tasks"])
    # 17 notifications
    n = c.get("/api/notifications", headers=st["h"]).json()
    assert n["unread"] >= 2 and any("Offer letter" in i["title"] for i in n["items"])
    c.post("/api/notifications/read", headers=st["h"])
    assert c.get("/api/notifications", headers=st["h"]).json()["unread"] == 0
    # 19-21 certificate: locked -> UPI payment -> admin verifies -> certificate HTML (print / save as PDF)
    assert data["cert"]["status"] == "payable"
    assert c.get(f"/api/applications/{aid}/certificate", headers=st["h"]).status_code == 403
    assert c.post(f"/api/admin/applications/{aid}/send-payment", headers=env.adm, json={}).status_code in (200, 422)
    assert c.post(f"/api/applications/{aid}/pay", headers=st["h"], json={"utr": "UTR9876543210"}).status_code == 200
    assert tasks(env, st, aid)["cert"]["status"] == "pending"
    pid = c.get("/api/admin/payments", headers=env.adm).json()[0]["id"]
    assert c.put(f"/api/admin/payments/{pid}", headers=env.adm, json={"status": "Paid"}).status_code == 200
    cert = c.get(f"/api/applications/{aid}/certificate", headers=st["h"])
    assert cert.status_code == 200 and "Asha Student" in cert.text and "Print" in cert.text
    ref = tasks(env, st, aid)["cert"]["ref"]
    assert re.fullmatch(r"UPN-CERT-\d{4}-\d{5}", ref) and ref in cert.text
    assert c.get(f"/api/applications/{aid}/certificate", headers=other["h"]).status_code in (403, 404)


def test_plan_task_counts_20_40_60(env):
    st = register(env, 1)
    for cat, months, expected in (("Java", 1, 20), ("AI/ML", 2, 40), ("Cloud DevOps", 3, 60)):
        aid, _ = enroll_and_start(env, st, cat, months)
        assert len(tasks(env, st, aid)["tasks"]) == expected, (cat, months)


def test_every_domain_has_a_full_one_month_plan(env):
    for i in env.client.get("/api/internships").json():
        n = len(env.client.get(f"/api/admin/internships/{i['id']}/tasks", headers=env.adm).json())
        assert n >= 20, (i["category"], n)


# ------------------------------------------------------------------ ADMIN 23-33
def test_admin_login_and_authorization(env):
    assert env.client.post("/api/admin/login", json={"email": "admin@example.com", "password": "wrong"}).status_code in (400, 401)
    st = register(env, 1)
    assert env.client.post("/api/admin/login", json={"email": "s1@example.com", "password": "Pass12345"}).status_code in (400, 401, 403)
    s = env.client.get("/api/admin/stats", headers=env.adm).json()
    assert s["students"] == 1 and s["internships"] == 10


def test_admin_student_management(env):
    st = register(env, 1)
    L = env.client.get("/api/admin/students", headers=env.adm).json()
    assert [x["email"] for x in L] == ["s1@example.com"]
    assert env.client.get(f"/api/admin/students/{st['uid']}", headers=env.adm).status_code == 200
    assert env.client.put(f"/api/admin/students/{st['uid']}", headers=env.adm, json={"college": "New College"}).status_code == 200
    assert env.client.get("/api/me", headers=st["h"]).json()["college"] == "New College"
    assert env.client.put(f"/api/admin/students/{st['uid']}/active?active=false", headers=env.adm).status_code == 200
    assert env.client.get("/api/me", headers=st["h"]).status_code == 403                          # disabled account is locked out
    assert env.client.post("/api/login", json={"email": "s1@example.com", "password": "Pass12345"}).status_code in (401, 403)
    assert env.client.put(f"/api/admin/students/{st['uid']}/active?active=true", headers=env.adm).status_code == 200
    assert env.client.get("/api/me", headers=st["h"]).status_code == 200


def test_admin_domain_and_task_management(env):
    c = env.client
    r = c.post("/api/admin/internships", headers=env.adm, json={"title": "Test Domain", "category": "Testing", "plans": "1,2,3"})
    assert r.status_code == 200, r.text
    iid = r.json()["id"]
    assert any(i["id"] == iid for i in c.get("/api/internships").json())
    assert c.put(f"/api/admin/internships/{iid}", headers=env.adm, json={"title": "Test Domain 2", "category": "Testing", "published": False}).status_code == 200
    assert not any(i["id"] == iid for i in c.get("/api/internships").json())                      # unpublished domains are hidden from students
    t1 = c.post(f"/api/admin/internships/{iid}/tasks", headers=env.adm, json={"title": "First", "months": 1}).json()
    t2 = c.post(f"/api/admin/internships/{iid}/tasks", headers=env.adm, json={"title": "Second", "months": 1}).json()
    assert c.put(f"/api/admin/tasks/{t1['id']}", headers=env.adm, json={"title": "First (edited)", "months": 1}).status_code == 200
    assert c.post(f"/api/admin/tasks/{t2['id']}/move?dir=up", headers=env.adm).status_code == 200
    order = [t["title"] for t in sorted(c.get(f"/api/admin/internships/{iid}/tasks", headers=env.adm).json(), key=lambda t: t["day"])]
    assert order == ["Second", "First (edited)"]
    assert c.delete(f"/api/admin/tasks/{t1['id']}", headers=env.adm).status_code == 200
    assert c.delete(f"/api/admin/internships/{iid}", headers=env.adm).status_code == 200


def test_deleting_an_internship_with_paid_certificates_is_blocked(env):
    st = register(env, 1)
    aid, iid = enroll_and_start(env, st, "Python", 1)
    finish_all(env, st, aid)
    assert env.client.post(f"/api/applications/{aid}/pay", headers=st["h"], json={"utr": "UTR1234567890"}).status_code == 200
    pid = env.client.get("/api/admin/payments", headers=env.adm).json()[0]["id"]
    env.client.put(f"/api/admin/payments/{pid}", headers=env.adm, json={"status": "Paid"})
    r = env.client.delete(f"/api/admin/internships/{iid}", headers=env.adm)
    assert r.status_code == 409 and "Unpublish" in r.json()["detail"]
    assert len(env.payments()) == 1 and any(i["id"] == iid for i in env.client.get("/api/internships").json())


def test_admin_messaging_and_notifications(env):
    a, b = register(env, 1), register(env, 2)
    assert env.client.post("/api/admin/announce", headers=env.adm, json={"title": "   "}).status_code == 400
    assert env.client.post("/api/admin/announce", headers=env.adm, json={"title": "Hello all", "body": "Everyone"}).json()["sent"] == 2
    assert env.client.post("/api/admin/announce", headers=env.adm, json={"title": "Just you", "user_id": a["uid"]}).json()["sent"] == 1
    ta = [i["title"] for i in env.client.get("/api/notifications", headers=a["h"]).json()["items"]]
    tb = [i["title"] for i in env.client.get("/api/notifications", headers=b["h"]).json()["items"]]
    assert "Just you" in ta and "Just you" not in tb and "Hello all" in tb
    assert env.client.post("/api/admin/announce", headers=a["h"], json={"title": "spoof"}).status_code == 403
    adm_n = env.client.get("/api/notifications", headers=env.adm).json()
    assert adm_n["unread"] >= 1                                                                        # admin sees "new student registered"


def test_admin_settings_change_certificate_fee(env):
    st = register(env, 1)
    aid, _ = enroll_and_start(env, st, "Python", 1)
    assert env.client.put("/api/admin/settings", headers=env.adm, json={"cert_fee": "349", "upi_id": "name@bank"}).status_code == 200
    assert tasks(env, st, aid)["cert"]["fee"] == 349
    assert env.client.put("/api/admin/settings", headers=st["h"], json={"cert_fee": "1"}).status_code == 403
