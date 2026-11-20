# Android Signing Guide

**No signing key was created, and none exists in this project.** A key must be created and kept by you. Never put it, or its passwords, in the repository, in chat, or in a report.

## 1. Use Play App Signing
In Play Console, new apps use Play App Signing: you sign uploads with an **upload key**, Google signs what users receive with the **app signing key** it holds. If you lose the upload key you can ask Google to reset it; if you lose a self-managed signing key the app can never be updated.

## 2. Create the upload keystore (PowerShell)
```powershell
keytool -genkeypair -v -keystore upnivo-upload.keystore -alias upnivo -keyalg RSA -keysize 2048 -validity 10000
```
You will be asked for two passwords and your name/organisation. Use long unique passwords from a password manager.

## 3. Back it up
- Store the `.keystore` file and passwords in at least two private places (password manager + encrypted drive).
- Do **not** commit: `.gitignore` already excludes `*.keystore`, `*.jks`, `keystore.properties`, `*.aab`, `*.apk`.

## 4. Use it
`bubblewrap build` asks for the keystore path, alias and both passwords at build time. Do not store them in `twa-manifest.json` (it only holds path and alias).

## 5. Get the fingerprint
See DIGITAL_ASSET_LINKS_GUIDE.md.

## 6. Checklist
- [ ] Keystore created by you  - [ ] Two backups  - [ ] Passwords in a password manager
- [ ] Upload key SHA-256 added to `ANDROID_SHA256`  - [ ] Play App Signing SHA-256 added after first upload
