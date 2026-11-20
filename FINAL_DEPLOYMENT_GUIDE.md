# Final Deployment Guide (Windows PowerShell)

**Nothing in this guide was executed against live services. Do each step yourself, and only when you are ready.** Replace values in `<angle brackets>`. Never paste secrets into chat, reports or git.

## 1. Local project verification
```powershell
cd "C:\Users\Ruthiramoorthy\Downloads\upnivo-intern-v3 (2)\proj"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt pytest httpx
python -m py_compile main.py
python -m pytest -q
```
Expect all tests to pass. Optional PostgreSQL run (needs a local test database you can wipe):
```powershell
$env:TEST_DATABASE_URL = "postgresql://<user>:<password>@localhost:5432/<throwaway_db>"
python -m pytest -q
Remove-Item Env:TEST_DATABASE_URL
```
**The test suite drops the `public` schema of that database each time. Use a throwaway database only.**

## 2. GitHub backup and repository hygiene
```powershell
git status
git check-ignore -v upnivo.db tmp_test.db   # databases must be ignored
git add -A
git status                                  # read the list: no .env, *.db, *.keystore, *.aab
git commit -m "Phases 6-10: payment hardening, accessibility, TWA project, compliance docs"
git push
```
If any secret was ever committed, rotate it; deleting it from the latest commit does not remove it from history.

## 3. Environment variables (Render → your service → Environment)
| Variable | Notes |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | Render PostgreSQL URL (`postgres://` or `postgresql://` both accepted) |
| `SECRET_KEY` | long random value (`python -c "import secrets;print(secrets.token_urlsafe(48))"`). **Required**: otherwise every restart logs everyone out |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | real admin email and a strong password. **Without `ADMIN_PASSWORD` no admin account is created in production** |
| `ALLOWED_ORIGINS` | your exact site origin(s), comma separated |
| `SUPPORT_EMAIL` | real monitored address (replaces the placeholder in policies/help) |
| `UPLOAD_STORAGE_PROVIDER` | `cloudinary` or `s3` (production refuses `local`) + that provider's variables (see `CLOUD_STORAGE_SETUP_GUIDE.md`) |
| `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` | **test** keys first, live only after a successful test-mode run |
| `CERT_FEE`, `UPI_ID`, `UPI_NAME` | as needed |
| `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY` | for web push, if used |
| `ANDROID_PACKAGE`, `ANDROID_SHA256` | later, step 10 |

## 4. PostgreSQL
Create a Render PostgreSQL instance; copy its **internal** connection URL into `DATABASE_URL`. Tables and the Phase 6 columns/indexes are created automatically at startup (additive only). **Back up first** (`POSTGRESQL_BACKUP_RESTORE_GUIDE.md`). Existing production data is never dropped by the app.

## 5. Cloud storage
Follow `CLOUD_STORAGE_SETUP_GUIDE.md`, then upload one screenshot as a test student and confirm the image URL opens. Note: deleting an account removes local files only, not cloud files.

## 6. Razorpay
1. Dashboard (test mode) → Webhooks → URL `https://<your-domain>/api/razorpay-webhook`, secret = `RAZORPAY_WEBHOOK_SECRET`, events `payment.captured`, `order.paid`, `payment.failed`, `refund.processed`.
2. Confirm payment auto-capture.
3. Make **one test-mode payment** with Razorpay's test card; confirm the certificate unlocks via browser callback and (separately) via webhook.
4. Only then switch to live keys. Check `GET /api/admin/settings` shows `razorpay_mode`.

## 7. Render deployment (needs your decision)
Push to the branch Render watches (or deploy manually). Build `pip install -r requirements.txt`; start `uvicorn main:app --host 0.0.0.0 --port $PORT`. Set the health check path to `/api/health`.

## 8. HTTPS verification
```powershell
curl.exe -i https://<your-domain>/api/health
curl.exe -I https://<your-domain>/ | Select-String "strict-transport|x-content-type|x-frame"
```
Expect 200 `{"status":"ok"...}` and the headers.

## 9. PWA verification
Open the site in Chrome on Android → menu → *Install app*; DevTools → Application → Manifest / Service Workers. Turn on airplane mode and reopen: the shell should load.

## 10. Digital Asset Links
See `DIGITAL_ASSET_LINKS_GUIDE.md`: set `ANDROID_PACKAGE` and `ANDROID_SHA256` (upload key **and** Play App Signing key), redeploy, then
```powershell
curl.exe -i https://<your-domain>/.well-known/assetlinks.json
```

## 11. Android build and 12. AAB signing
`ANDROID_TWA_SETUP_GUIDE.md`, `ANDROID_SIGNING_GUIDE.md`, `AAB_BUILD_GUIDE.md`. You create the keystore; keep it and its passwords out of git.

## 13. Play Console preparation
`GOOGLE_PLAY_RELEASE_CHECKLIST.md` and `FINAL_PLAY_STORE_RELEASE_CHECKLIST.md`: resolve the payment-route decision **before** uploading anything.

## Rollback
Keep the previous Render deploy; PostgreSQL changes are additive, so rolling back the code leaves extra columns harmlessly. Restore the database only from your own backup.
