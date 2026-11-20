"""Phase 6 payment tests.

Everything here is local: Razorpay is replaced by a mock, credentials are obvious fixtures
(not real keys), and each test gets a fresh throw-away SQLite database. No real payment is made
and no network call leaves the machine.
"""
import hashlib
import hmac
import importlib
import json
import os
import sqlite3
import sys
import urllib.error
import datetime as dt
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

KEY, SECRET, WH = "rzp_test_FIXTURE", "fixture_key_secret", "fixture_webhook_secret"


def _load(monkeypatch, tmp_path, webhook=True, db_path=None):
    monkeypatch.setenv("APP_ENV", "development")
    pg = os.getenv("TEST_DATABASE_URL")  # opt-in: run the same tests against a throw-away PostgreSQL database (its public schema is wiped per test)
    if pg and not db_path:
        import psycopg
        with psycopg.connect(pg.replace("postgresql+psycopg://", "postgresql://"), autocommit=True) as c:
            c.execute("DROP SCHEMA public CASCADE"); c.execute("CREATE SCHEMA public")
        monkeypatch.setenv("DATABASE_URL", pg)
    else:
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path or tmp_path / 'pay.db'}")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "StrongPass123!")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://example.com")
    monkeypatch.setenv("RAZORPAY_KEY_ID", KEY)
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", SECRET)
    if webhook:
        monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", WH)
    else:
        monkeypatch.delenv("RAZORPAY_WEBHOOK_SECRET", raising=False)
    monkeypatch.setenv("CERT_FEE", "199")
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("VAPID_PUBLIC_KEY", raising=False)
    import main
    importlib.reload(main)
    return main


class Env:
    """A loaded app plus helpers: students with a finished internship, a mocked gateway, signed callbacks."""

    def __init__(self, main):
        self.main = main
        self.client = TestClient(main.app)
        self.client.__enter__()
        self.orders = 0
        self.calls = []
        main.rzp_request = self._fake_gateway

    def _fake_gateway(self, path, payload):
        self.calls.append((path, payload))
        self.orders += 1
        return {"id": f"order_FIX{self.orders:04d}", "amount": payload["amount"], "currency": payload["currency"]}

    def close(self):
        self.client.__exit__(None, None, None)

    def student(self, n=1):
        email = f"pay{n}@example.com"
        r = self.client.post("/api/register", json={"name": f"Pay {n}", "email": email, "mobile": "9999999999", "college": "C",
                                                    "degree": "B.E.", "department": "CSE", "year": "2025", "password": "Pass12345"})
        assert r.status_code == 200, r.text
        tok = r.json()["token"]
        h = {"Authorization": f"Bearer {tok}"}
        uid = self.client.get("/api/me", headers=h).json()["id"]
        m = self.main
        s = m.SessionLocal()
        try:
            i = m.Internship(title=f"Fixture {n}", category="Fixture")
            s.add(i); s.flush()
            t = m.Task(internship_id=i.id, months=1, day=1, title="Only task")
            s.add(t); s.flush()
            start = (m.today() - dt.timedelta(days=3)).isoformat()
            a = m.Application(user_id=uid, internship_id=i.id, months=1, status="Offer Sent", start_date=start)
            s.add(a); s.flush()
            s.add(m.Submission(application_id=a.id, task_id=t.id, status="Submitted"))
            s.commit()
            aid = a.id
        finally:
            s.close()
        return {"h": h, "aid": aid, "uid": uid}

    def admin(self):
        r = self.client.post("/api/admin/login", json={"email": "admin@example.com", "password": "StrongPass123!"})
        return {"Authorization": f"Bearer {r.json()['token']}"}

    def order(self, st):
        return self.client.post(f"/api/applications/{st['aid']}/razorpay-order", headers=st["h"])

    @staticmethod
    def sign(order_id, payment_id, secret=SECRET):
        return hmac.new(secret.encode(), f"{order_id}|{payment_id}".encode(), hashlib.sha256).hexdigest()

    def verify(self, st, order_id, payment_id, sig=None):
        return self.client.post(f"/api/applications/{st['aid']}/razorpay-verify", headers=st["h"],
                                json={"razorpay_order_id": order_id, "razorpay_payment_id": payment_id,
                                      "razorpay_signature": self.sign(order_id, payment_id) if sig is None else sig})

    def hook(self, event, entity_key="payment", entity=None, event_id="evt_1", secret=WH, sig=None, raw=None):
        body = raw if raw is not None else json.dumps({"event": event, "payload": {entity_key: {"entity": entity or {}}}}).encode()
        signature = sig if sig is not None else hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return self.client.post("/api/razorpay-webhook", content=body,
                                headers={"x-razorpay-signature": signature, "x-razorpay-event-id": event_id, "content-type": "application/json"})

    def payments(self):
        s = self.main.SessionLocal()
        try:
            return [self.main.row(p) for p in s.query(self.main.Payment).order_by(self.main.Payment.id)]
        finally:
            s.close()

    def cert_status(self, st):
        r = self.client.get(f"/api/applications/{st['aid']}/tasks", headers=st["h"])
        assert r.status_code == 200, r.text
        return r.json()["cert"]["status"]

    def unlocked_notes(self, st):
        r = self.client.get("/api/notifications", headers=st["h"]).json()
        return [n for n in r["items"] if n["title"].startswith("Certificate unlocked")]


@pytest.fixture
def env(monkeypatch, tmp_path):
    e = Env(_load(monkeypatch, tmp_path))
    yield e
    e.close()


def captured(order_id, payment_id="pay_FIX1", amount=19900, currency="INR"):
    return {"id": payment_id, "order_id": order_id, "amount": amount, "currency": currency, "status": "captured"}


# ---------------------------------------------------------------- order creation
def test_order_amount_is_set_by_the_server(env):
    st = env.student()
    r = env.order(st)
    assert r.status_code == 200, r.text
    assert r.json()["amount"] == 19900 and "secret" not in json.dumps(r.json()).lower()
    assert env.calls[0][1]["amount"] == 19900 and env.calls[0][1]["currency"] == "INR"
    row = env.payments()[0]
    assert (row["status"], row["provider"], row["amount_paise"], row["currency"]) == ("Created", "razorpay", 19900, "INR")


def test_client_supplied_amount_is_ignored(env):
    st = env.student()
    r = env.client.post(f"/api/applications/{st['aid']}/razorpay-order", headers=st["h"], json={"amount": 1, "fee": 1})
    assert r.status_code == 200 and env.calls[0][1]["amount"] == 19900


def test_order_requires_login_and_ownership(env):
    a, b = env.student(1), env.student(2)
    assert env.client.post(f"/api/applications/{a['aid']}/razorpay-order").status_code in (401, 403)
    assert env.client.post(f"/api/applications/{a['aid']}/razorpay-order", headers=b["h"]).status_code == 404


def test_abandoned_checkout_can_be_resumed_not_stuck(env):
    """Regression: previously an abandoned order blocked the student with a permanent 409."""
    st = env.student()
    first = env.order(st).json()
    again = env.order(st)
    assert again.status_code == 200 and again.json()["order_id"] == first["order_id"]
    assert len(env.calls) == 1 and len(env.payments()) == 1


def test_stale_order_expires_and_a_new_one_is_issued(env):
    st = env.student()
    first = env.order(st).json()
    s = env.main.SessionLocal()
    s.query(env.main.Payment).update({"created": dt.datetime.utcnow() - dt.timedelta(days=3)})
    s.commit(); s.close()
    second = env.order(st).json()
    assert second["order_id"] != first["order_id"]
    assert [p["status"] for p in env.payments()] == ["Expired", "Created"]


def test_gateway_response_mismatch_is_rejected(env):
    st = env.student()
    env.main.rzp_request = lambda path, payload: {"id": "order_X", "amount": 100, "currency": "INR"}
    assert env.order(st).status_code == 502
    assert env.payments() == []


def test_gateway_errors_do_not_leak_details(env, monkeypatch):
    st = env.student()
    # reload to get the genuine rzp_request (the fixture replaced it) and fail its network layer
    fresh = importlib.reload(env.main)
    err = urllib.error.HTTPError("u", 400, "bad", {}, __import__("io").BytesIO(b'{"error":"SECRETDETAIL key_secret=abc"}'))
    monkeypatch.setattr(fresh.urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(err))
    with pytest.raises(fresh.HTTPException) as ei:
        fresh.rzp_request("/orders", {})
    assert ei.value.status_code == 502 and "SECRETDETAIL" not in ei.value.detail and "abc" not in ei.value.detail


def test_order_not_available_until_all_tasks_done(env):
    st = env.student()
    s = env.main.SessionLocal()
    s.query(env.main.Submission).delete(); s.commit(); s.close()
    assert env.order(st).status_code == 409


# ---------------------------------------------------------------- browser-side verification
def test_valid_signature_unlocks_certificate(env):
    st = env.student()
    o = env.order(st).json()
    assert env.cert_status(st) == "payable"
    r = env.verify(st, o["order_id"], "pay_FIX1")
    assert r.status_code == 200, r.text
    assert env.cert_status(st) == "paid"
    p = env.payments()[0]
    assert (p["status"], p["rzp_payment_id"]) == ("Paid", "pay_FIX1")
    assert env.client.get(f"/api/applications/{st['aid']}/certificate", headers=st["h"]).status_code == 200


def test_bad_signature_is_rejected_and_nothing_changes(env):
    st = env.student()
    o = env.order(st).json()
    r = env.verify(st, o["order_id"], "pay_FIX1", sig="0" * 64)
    assert r.status_code == 400 and env.payments()[0]["status"] == "Created" and env.cert_status(st) == "payable"
    assert env.verify(st, o["order_id"], "pay_FIX1", sig=env.sign(o["order_id"], "pay_FIX1", secret="wrong")).status_code == 400


def test_non_ascii_signature_does_not_crash(env):
    st = env.student()
    o = env.order(st).json()
    assert env.verify(st, o["order_id"], "pay_FIX1", sig="é" * 64).status_code == 400
    assert env.hook("payment.captured", sig=("é" * 64).encode("latin-1")).status_code == 400


def test_other_students_order_cannot_be_verified(env):
    a, b = env.student(1), env.student(2)
    oa = env.order(a).json()
    sig_ok_for_a_order = env.sign(oa["order_id"], "pay_FIX1")
    r = env.client.post(f"/api/applications/{b['aid']}/razorpay-verify", headers=b["h"],
                        json={"razorpay_order_id": oa["order_id"], "razorpay_payment_id": "pay_FIX1", "razorpay_signature": sig_ok_for_a_order})
    assert r.status_code == 400
    assert env.payments()[0]["status"] == "Created"


def test_replay_is_idempotent_but_a_different_payment_id_is_refused(env):
    st = env.student()
    o = env.order(st).json()
    assert env.verify(st, o["order_id"], "pay_FIX1").status_code == 200
    assert env.verify(st, o["order_id"], "pay_FIX1").status_code == 200  # same confirmation again: harmless
    assert env.verify(st, o["order_id"], "pay_OTHER").status_code == 409  # different payment against a paid order
    assert len(env.unlocked_notes(st)) == 1 and len(env.payments()) == 1


def test_oversized_identifiers_rejected(env):
    st = env.student()
    assert env.verify(st, "order_" + "x" * 80, "pay_1").status_code == 400


# ---------------------------------------------------------------- webhook
def test_webhook_needs_configuration_and_a_valid_signature(monkeypatch, tmp_path):
    e = Env(_load(monkeypatch, tmp_path, webhook=False))
    try:
        assert e.hook("payment.captured").status_code == 503
    finally:
        e.close()


def test_webhook_bad_signature_and_oversize(env):
    assert env.hook("payment.captured", sig="deadbeef").status_code == 400
    assert env.client.post("/api/razorpay-webhook", content=b"{}").status_code == 400  # no header at all
    assert env.hook("payment.captured", raw=b"x" * 300000, sig="a").status_code == 413


def test_webhook_unlocks_once_and_duplicate_delivery_is_ignored(env):
    st = env.student()
    o = env.order(st).json()
    r1 = env.hook("payment.captured", entity=captured(o["order_id"]), event_id="evt_A")
    assert r1.status_code == 200 and env.cert_status(st) == "paid"
    r2 = env.hook("payment.captured", entity=captured(o["order_id"]), event_id="evt_A")
    assert r2.json().get("duplicate") is True
    assert len(env.unlocked_notes(st)) == 1


def test_webhook_then_browser_verify_do_not_double_apply(env):
    st = env.student()
    o = env.order(st).json()
    env.hook("payment.captured", entity=captured(o["order_id"]), event_id="evt_B")
    assert env.verify(st, o["order_id"], "pay_FIX1").status_code == 200
    assert len(env.unlocked_notes(st)) == 1 and [p["status"] for p in env.payments()] == ["Paid"]


def test_webhook_amount_or_currency_mismatch_never_unlocks(env):
    st = env.student()
    o = env.order(st).json()
    env.hook("payment.captured", entity=captured(o["order_id"], amount=100), event_id="e1")
    env.hook("payment.captured", entity=captured(o["order_id"], currency="USD"), event_id="e2")
    assert env.payments()[0]["status"] == "Created" and env.cert_status(st) == "payable"
    assert "mismatch" in env.payments()[0]["note"].lower()


def test_webhook_unknown_order_and_unknown_event_are_acknowledged(env):
    assert env.hook("payment.captured", entity=captured("order_NOPE"), event_id="e3").status_code == 200
    assert env.hook("some.other.event", event_id="e4").status_code == 200
    assert env.payments() == []


def test_failed_attempt_keeps_order_open_for_retry(env):
    st = env.student()
    o = env.order(st).json()
    env.hook("payment.failed", entity={"id": "pay_F", "order_id": o["order_id"], "error_code": "BAD_REQUEST_ERROR"}, event_id="ef")
    p = env.payments()[0]
    assert p["status"] == "Created" and "BAD_REQUEST_ERROR" in p["note"]
    assert env.verify(st, o["order_id"], "pay_RETRY").status_code == 200  # the customer retries and succeeds


def test_full_refund_locks_certificate_partial_refund_does_not(env):
    st = env.student()
    o = env.order(st).json()
    env.verify(st, o["order_id"], "pay_FIX1")
    env.hook("refund.processed", "refund", {"id": "rfnd_1", "payment_id": "pay_FIX1", "amount": 5000}, event_id="r1")
    p = env.payments()[0]
    assert (p["status"], p["refunded_paise"]) == ("Paid", 5000) and env.cert_status(st) == "paid"
    env.hook("refund.processed", "refund", {"id": "rfnd_1", "payment_id": "pay_FIX1", "amount": 5000}, event_id="r1")  # redelivery
    assert env.payments()[0]["refunded_paise"] == 5000
    env.hook("refund.processed", "refund", {"id": "rfnd_2", "payment_id": "pay_FIX1", "amount": 14900}, event_id="r2")
    p = env.payments()[0]
    assert (p["status"], p["refunded_paise"]) == ("Refunded", 19900)
    assert env.cert_status(st) == "payable"
    assert env.client.get(f"/api/applications/{st['aid']}/certificate", headers=st["h"]).status_code == 403


def test_late_payment_on_an_expired_order_is_still_honoured(env):
    st = env.student()
    o = env.order(st).json()
    s = env.main.SessionLocal()
    s.query(env.main.Payment).update({"created": dt.datetime.utcnow() - dt.timedelta(days=3)}); s.commit(); s.close()
    env.order(st)  # expires the old order, opens a new one
    assert env.payments()[0]["status"] == "Expired"
    env.hook("payment.captured", entity=captured(o["order_id"]), event_id="late")
    assert env.payments()[0]["status"] == "Paid"


def test_double_payment_is_flagged_for_refund(env):
    st = env.student()
    o1 = env.order(st).json()
    s = env.main.SessionLocal()
    s.query(env.main.Payment).update({"created": dt.datetime.utcnow() - dt.timedelta(days=3)}); s.commit(); s.close()
    o2 = env.order(st).json()
    env.verify(st, o2["order_id"], "pay_SECOND")
    env.hook("payment.captured", entity=captured(o1["order_id"], "pay_FIRST"), event_id="dup")
    notes = " | ".join(p["note"] for p in env.payments())
    assert "DUPLICATE" in notes


# ---------------------------------------------------------------- admin + UPI
def test_admin_cannot_override_gateway_payments(env):
    st = env.student()
    o = env.order(st).json()
    env.verify(st, o["order_id"], "pay_FIX1")
    pid = env.payments()[0]["id"]
    adm = env.admin()
    for status in ("Rejected", "Paid"):
        assert env.client.put(f"/api/admin/payments/{pid}", headers=adm, json={"status": status}).status_code == 409
    assert env.payments()[0]["status"] == "Paid"


def test_admin_payment_endpoints_require_admin(env):
    st = env.student()
    assert env.client.get("/api/admin/payments", headers=st["h"]).status_code == 403
    assert env.client.put("/api/admin/payments/1", headers=st["h"], json={"status": "Paid"}).status_code == 403
    assert env.client.get("/api/admin/payments").status_code in (401, 403)


def test_upi_flow_is_reviewed_once(env):
    st = env.student()
    r = env.client.post(f"/api/applications/{st['aid']}/pay", headers=st["h"], json={"utr": "UTR123456789"})
    assert r.status_code == 200, r.text
    pid = env.payments()[0]["id"]
    adm = env.admin()
    assert env.client.put(f"/api/admin/payments/{pid}", headers=adm, json={"status": "Paid"}).status_code == 200
    assert env.cert_status(st) == "paid"
    assert env.client.put(f"/api/admin/payments/{pid}", headers=adm, json={"status": "Rejected"}).status_code == 409
    assert env.cert_status(st) == "paid"


def test_admin_cannot_review_unpaid_gateway_orders(env):
    st = env.student()
    env.order(st)
    pid = env.payments()[0]["id"]
    assert env.client.put(f"/api/admin/payments/{pid}", headers=env.admin(), json={"status": "Paid"}).status_code == 409
    assert env.cert_status(st) == "payable"


def test_same_utr_cannot_be_used_by_two_students(env):
    a, b = env.student(1), env.student(2)
    assert env.client.post(f"/api/applications/{a['aid']}/pay", headers=a["h"], json={"utr": "SAMEUTR0001"}).status_code == 200
    assert env.client.post(f"/api/applications/{b['aid']}/pay", headers=b["h"], json={"utr": "sameutr0001"}).status_code == 409


# ---------------------------------------------------------------- abuse limits / config
def test_payment_endpoints_are_rate_limited(env):
    st = env.student()
    codes = [env.order(st).status_code for _ in range(12)]
    assert codes[:10] == [200] * 10 and 429 in codes[10:]


def test_admin_settings_expose_mode_but_never_secrets(env):
    body = env.client.get("/api/admin/settings", headers=env.admin())
    text = body.text
    assert body.json()["razorpay_mode"] == "test" and body.json()["razorpay_webhook"] is True
    assert SECRET not in text and WH not in text


# ---------------------------------------------------------------- existing data survives the upgrade
def test_existing_database_is_upgraded_without_losing_payments(monkeypatch, tmp_path):
    db = tmp_path / "legacy.db"
    con = sqlite3.connect(db)
    con.executescript("""
        CREATE TABLE payments (id INTEGER PRIMARY KEY, application_id INTEGER, amount INTEGER, utr VARCHAR(60), status VARCHAR(12), note TEXT, created TIMESTAMP);
        INSERT INTO payments VALUES (1, 1, 199, 'UTRLEGACY01', 'Paid', 'ok', '2026-01-01 00:00:00');
        INSERT INTO payments VALUES (2, 2, 199, 'order_LEGACY2', 'Created', '', '2026-01-02 00:00:00');
        INSERT INTO payments VALUES (3, 3, 199, 'pay_LEGACY3', 'Paid', 'Razorpay', '2026-01-03 00:00:00');
    """)
    con.commit(); con.close()
    main = _load(monkeypatch, tmp_path, db_path=db)
    con = sqlite3.connect(db)
    cols = {r[1] for r in con.execute("PRAGMA table_info(payments)")}
    rows = con.execute("SELECT id, utr, status FROM payments ORDER BY id").fetchall()
    idx = {r[1] for r in con.execute("PRAGMA index_list(payments)")}
    con.close()
    assert {"provider", "order_id", "rzp_payment_id", "currency", "amount_paise", "refunded_paise", "updated"} <= cols
    assert rows == [(1, "UTRLEGACY01", "Paid"), (2, "order_LEGACY2", "Created"), (3, "pay_LEGACY3", "Paid")]
    assert {"ix_payments_order_id", "uq_payments_rzp_payment_id", "uq_payments_one_open_per_app"} <= idx
    s = main.SessionLocal()
    legacy_created = s.get(main.Payment, 2)
    assert main.is_rzp(legacy_created) and main.find_rzp_payment(s, "order_LEGACY2") is not None  # old rows still resolve by their order id
    assert main.expected_paise(legacy_created) == 19900
    s.close()


def test_concurrent_confirmations_settle_exactly_once(env):
    """Browser callbacks and webhooks racing on the same order: one winner, one notification, no duplicate records."""
    from concurrent.futures import ThreadPoolExecutor
    st = env.student()
    o = env.order(st).json()

    def verify(_):
        return env.verify(st, o["order_id"], "pay_RACE").status_code

    def hook(i):
        return env.hook("payment.captured", entity=captured(o["order_id"], "pay_RACE"), event_id=f"race_{i}").status_code

    with ThreadPoolExecutor(max_workers=8) as ex:
        codes = list(ex.map(lambda i: verify(i) if i % 2 else hook(i), range(8)))
    assert all(c in (200, 409, 500) for c in codes), codes
    pays = env.payments()
    assert [p["status"] for p in pays] == ["Paid"] and len(pays) == 1
    assert len(env.unlocked_notes(st)) == 1                                   # exactly one winner sent the notification
    assert env.cert_status(st) == "paid"
