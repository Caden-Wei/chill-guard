# App Icon reuse — 2026-10-10

The user requested the current macOS App Icon in the upper-left brand area and authorized pushing the completed upgrade to GitHub.

The installed app's decoded 1024 × 1024 ICNS pixels matched `assets/app_icon_1024.png`. The navigation rail now displays that same PNG at 40 × 40, replacing the blue camera badge. The packaged app explicitly includes the source PNG for the UI. Other layout, typography, controls and detection behavior are retained; design documentation reflects the new brand asset.

All 26 existing regressions passed. PyInstaller built version 1.2.2, build 20261010.2. The installed bundle's PNG bytes match the source asset, its local signature passes verification, and the updated local DMG passes `hdiutil verify`. Native inspection confirmed the actual brand icon and alignment beside Chill Guard.

Installed at `~/Applications/Chill Guard.app`. The prior app and settings were backed up under `~/Library/Application Support/Chill Guard/Backups/20261010-144513/`; settings bytes remain identical. Monitoring was resumed with preview disabled. The first camera start failed, while the retry connected successfully and returned to Running. No camera-code change or system permission change was made; the transient failure's cause is not established.

Raw build/test/install/package records remain in ignored `validation/local/`. The current source, bilingual workspace, YOLO26/Core ML upgrade and preview fix are included in this authorized GitHub synchronization. Local DMGs and native model exports remain ignored build artifacts.
