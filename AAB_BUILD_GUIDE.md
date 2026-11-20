# AAB Build Guide

**Status: no AAB has been built.** Building needs the Android SDK/Gradle (blocked in the sandbox) and a signing key that only you should hold.

## Build
Follow ANDROID_TWA_SETUP_GUIDE.md, then:
```powershell
bubblewrap build
```
Output in the project folder: `app-release-bundle.aab`.

## Versioning
Play rejects an upload whose `versionCode` is not higher than every earlier upload. In `twa-manifest.json` raise `appVersionCode` (1, 2, 3 …) and optionally `appVersion` ("1.0.1"), run `bubblewrap update`, rebuild.

## Check before upload (optional but useful)
```powershell
# bundletool: https://github.com/google/bundletool/releases
java -jar bundletool.jar validate --bundle=app-release-bundle.aab
java -jar bundletool.jar dump manifest --bundle=app-release-bundle.aab | Select-String "package|targetSdk|versionCode|uses-permission"
```
Expect package `com.upnivo.app`, targetSdkVersion 36, versionCode as set.

## Test order
1. Install the signed APK on a phone (`adb install`) and confirm no address bar, login, task submit, offline start, notifications.
2. Upload the AAB to **Internal testing** in Play Console.
3. Add the Play App Signing fingerprint (DIGITAL_ASSET_LINKS_GUIDE.md) and retest from the Play-installed build.
4. If your personal developer account was created after 2023-11-13, run a **closed test with at least 12 testers opted in for 14 continuous days** before applying for production (Play Console Help, "App testing requirements for new personal developer accounts").

Never upload to production until GOOGLE_PLAY_RELEASE_CHECKLIST.md is complete and you approve.
