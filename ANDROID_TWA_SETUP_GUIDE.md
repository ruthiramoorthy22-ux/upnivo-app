# Android TWA Setup Guide (Windows PowerShell)

Prerequisites: Node.js 18+ (`node -v`), internet access, ~5 GB disk. Bubblewrap can download its own JDK 17 and Android SDK on first run.

## 1. Install and check
```powershell
npm install -g @bubblewrap/cli
bubblewrap doctor
```
When asked, let Bubblewrap install the JDK and the Android command-line tools, or give paths to your own JDK 17 and SDK. Settings are stored in `%USERPROFILE%\.bubblewrap\config.json`.

## 2. Decide the domain first
If you will use a custom domain, edit `host`, `webManifestUrl`, `iconUrl`, `maskableIconUrl` and `fullScopeUrl` in `android\twa-manifest.json` **before** building (see ANDROID_TWA_AUDIT.md §3).

## 3. Generate and build from the provided manifest
The repository's `android\` folder was produced without compiling. The reliable way is to let Bubblewrap regenerate it from the manifest in an empty folder:
```powershell
cd $env:USERPROFILE\Desktop
mkdir upnivo-twa; cd upnivo-twa
Copy-Item "<PROJECT>\android\twa-manifest.json" .
bubblewrap update          # regenerates the Android project from twa-manifest.json (fetches the live web manifest + icons)
bubblewrap build           # asks for keystore location/passwords, then builds
```
`<PROJECT>` is your `upnivo-intern-v3 (2)\proj` folder. If `bubblewrap update` is not the right command in your CLI version, run `bubblewrap help`; alternatively run `bubblewrap init --manifest https://upnivo-intern.onrender.com/manifest.webmanifest` and use the values below.

| Prompt | Value |
|---|---|
| Application name | UPNIVO INTERN |
| Short name / launcher name | Upnivo |
| Application ID | com.upnivo.app |
| Start URL | / |
| Display mode | standalone |
| Status/nav/splash colour | #071433 |
| Enable notifications | Yes |
| Signing key | create or choose your own (ANDROID_SIGNING_GUIDE.md) |

## 4. Outputs
`app-release-bundle.aab` (upload to Play) and `app-release-signed.apk` (for installing on a test phone).

## 5. Test on a phone (not done by me)
```powershell
adb install app-release-signed.apk
```
The app must open **without** a browser address bar. A bar means Digital Asset Links failed (DIGITAL_ASSET_LINKS_GUIDE.md).

## 6. Keep in sync
Every change to the host, icons or colours: update `twa-manifest.json`, `bubblewrap update`, **increase `appVersionCode`**, rebuild.
