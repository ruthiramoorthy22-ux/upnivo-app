# Digital Asset Links Guide

Digital Asset Links prove that your website and your Android app belong together. Without them the TWA shows a browser address bar.

## Status
| Item | Status |
|---|---|
| Endpoint `GET /.well-known/assetlinks.json` | **IMPLEMENTED and TESTED** locally (7 tests). It is driven by environment variables, so no fingerprint is hard-coded. |
| Input validation | Package name and each fingerprint are format-checked; bad values are dropped with a server warning and the file stays `[]` rather than publishing something broken. |
| Fingerprints | **NONE EXISTS YET.** I did not invent any. They come from your signing key. |
| Deployed on Render / verified by Google | **NOT DONE, NOT VERIFIED** (no deployment authorised; needs your key). |

## What the file looks like (example with a placeholder, not a real value)
```json
[{"relation":["delegate_permission/common.handle_all_urls"],
  "target":{"namespace":"android_app","package_name":"com.upnivo.app",
            "sha256_cert_fingerprints":["AA:BB:...:FF"]}}]
```

## Which fingerprints you need
1. **Upload key** (your own keystore): needed for APKs you sign yourself and install for testing.
2. **Play App Signing key**: when you use Play App Signing (recommended, and the default for new apps) Google re-signs the app you upload with *its* key, and users get that key's signature. Its SHA-256 is shown in Play Console under the app's **App integrity / App signing** page (menu names change; search the console for "App signing key certificate").
List **both**, comma-separated.

## Get the SHA-256 of your own keystore
```powershell
keytool -list -v -keystore .\android.keystore -alias upnivo | Select-String "SHA256"
```
Copy the value in the form `AB:CD:...` (32 pairs).

## Configure on Render (after your approval)
Environment variables:
```
ANDROID_PACKAGE=com.upnivo.app
ANDROID_SHA256=<upload-key SHA-256>,<Play-app-signing SHA-256>
```
Redeploy, then verify.

## Verify (PowerShell)
```powershell
curl.exe -i https://upnivo-intern.onrender.com/.well-known/assetlinks.json
```
Expect HTTP 200, `Content-Type: application/json`, no redirect, the package name and your fingerprints.

Google's own check:
```powershell
curl.exe "https://digitalassetlinks.googleapis.com/v1/statements:list?source.web.site=https://upnivo-intern.onrender.com&relation=delegate_permission/common.handle_all_urls"
```
On a phone with the app installed:
```powershell
adb shell pm get-app-links com.upnivo.app
```
Final proof: launching the app shows **no address bar**.

## Pitfalls
- Domain change = new statements + new app release.
- Uppercase hex with colons only; the server upper-cases for you.
- A redirect (http→https, www→apex) on this path breaks verification.
- Forgetting the Play App Signing fingerprint is the most common reason a Play-installed build shows a bar while your own APK does not.
