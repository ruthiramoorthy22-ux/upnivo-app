"""Phase 8: Digital Asset Links endpoint, web manifest and service worker checks (local, no network)."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pytest
from fastapi.testclient import TestClient
from test_payments import _load

ROOT = Path(__file__).resolve().parents[1]
GOOD = ":".join(f"{i:02X}" for i in range(32))            # obviously synthetic fingerprint, not a real certificate
GOOD2 = ":".join("AB" for _ in range(32))


def client(monkeypatch, tmp_path, pkg=None, fp=None):
    for k, v in (("ANDROID_PACKAGE", pkg), ("ANDROID_SHA256", fp)):
        monkeypatch.delenv(k, raising=False) if v is None else monkeypatch.setenv(k, v)
    main = _load(monkeypatch, tmp_path)
    return TestClient(main.app)


def test_assetlinks_empty_until_configured(monkeypatch, tmp_path):
    r = client(monkeypatch, tmp_path).get("/.well-known/assetlinks.json")
    assert r.status_code == 200 and r.json() == [] and "json" in r.headers["content-type"]


def test_assetlinks_valid_config(monkeypatch, tmp_path):
    r = client(monkeypatch, tmp_path, "com.upnivo.app", f"{GOOD.lower()}, {GOOD2}").get("/.well-known/assetlinks.json")
    t = r.json()[0]
    assert r.json()[0]["relation"] == ["delegate_permission/common.handle_all_urls"]
    assert t["target"]["namespace"] == "android_app" and t["target"]["package_name"] == "com.upnivo.app"
    assert t["target"]["sha256_cert_fingerprints"] == [GOOD, GOOD2]          # normalised to upper-case, both keys listed


@pytest.mark.parametrize("pkg,fp", [("com.upnivo.app", "not-a-fingerprint"), ("com.upnivo.app", GOOD[:-3]), ("bad package!", GOOD), ("", GOOD)])
def test_assetlinks_rejects_malformed_values(monkeypatch, tmp_path, pkg, fp):
    assert client(monkeypatch, tmp_path, pkg, fp).get("/.well-known/assetlinks.json").json() == []


def test_assetlinks_drops_only_the_bad_fingerprint(monkeypatch, tmp_path):
    r = client(monkeypatch, tmp_path, "com.upnivo.app", f"{GOOD},oops").get("/.well-known/assetlinks.json")
    assert r.json()[0]["target"]["sha256_cert_fingerprints"] == [GOOD]


def test_manifest_meets_pwa_and_twa_basics():
    m = json.loads((ROOT / "static/manifest.webmanifest").read_text(encoding="utf-8"))
    assert m["start_url"] == "/" and m["scope"] == "/" and m["display"] == "standalone" and m["name"] and m["short_name"]
    assert re.fullmatch(r"#[0-9a-fA-F]{6}", m["theme_color"]) and re.fullmatch(r"#[0-9a-fA-F]{6}", m["background_color"])
    sizes = {(i["sizes"], i["purpose"]) for i in m["icons"]}
    assert {("192x192", "any"), ("512x512", "any"), ("192x192", "maskable"), ("512x512", "maskable")} <= sizes
    for i in m["icons"]:
        assert (ROOT / i["src"].lstrip("/")).is_file()                          # every declared icon exists on disk
    assert all("any maskable" != i["purpose"] for i in m["icons"])


def test_manifest_and_icons_are_served(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    assert c.get("/manifest.webmanifest").status_code == 200
    for path in ("/static/icon-192.png", "/static/icon-512.png", "/sw.js"):
        assert c.get(path).status_code == 200, path


def test_service_worker_basics():
    sw = (ROOT / "static/sw.js").read_text(encoding="utf-8")
    assert "addEventListener(\"fetch\"" in sw and "/api/" in sw                  # API calls are never cached by the worker
    assert "push" in sw and "notificationclick" in sw


def test_android_project_matches_policy_and_package():
    a = ROOT / "android"
    gradle = (a / "app/build.gradle").read_text(encoding="utf-8")
    assert 'applicationId "com.upnivo.app"' in gradle
    assert int(re.search(r"targetSdkVersion\s+(\d+)", gradle).group(1)) >= 36   # Play requires API 36 for new apps/updates from 2026-08-31
    assert 'versionName "1.0.0"' in gradle and "versionCode 1" in gradle
    tm = json.loads((a / "twa-manifest.json").read_text(encoding="utf-8"))
    assert tm["packageId"] == "com.upnivo.app" and tm["host"] == "upnivo-intern.onrender.com" and tm["fingerprints"] == []
    blob = " ".join(p.read_text(encoding="utf-8", errors="ignore") for p in a.rglob("*") if p.suffix in {".json", ".gradle", ".xml", ".properties", ".java"})
    assert not re.search(r"storePassword|keyPassword|BEGIN (RSA |EC )?PRIVATE KEY", blob)  # no secrets
    assert not list(a.rglob("*.keystore")) and not list(a.rglob("*.jks"))
