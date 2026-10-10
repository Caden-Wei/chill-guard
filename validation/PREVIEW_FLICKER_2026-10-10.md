# Camera preview flicker fix — 2026-10-10

The user reported that enabling preview repeatedly showed “Preparing the camera…” over a live image in the installed 1.2.0 application. The same installed application also visibly retained its last camera image behind the “Preview is hidden” placeholder.

## Cause and scoped change

`monitor_loop` cleared `latest_preview` whenever its 120 ms publication limit skipped an inference frame. The UI polls every 80 ms, so it repeatedly received `None` between valid frames and reintroduced the loading placeholder. Separately, CustomTkinter 5.2.2's `CTkLabel.configure(image=None)` leaves the underlying Tk label's previous image drawn.

The loop now retains the latest frame on throttled iterations and clears it only when preview is disabled or monitoring ends. The UI unmaps the image surface on empty/hidden/stopped previews and restores it when a valid frame arrives. Detection rules, model/backend selection, layout, language behavior and stored settings are unchanged.

## Reproduction and verification

- Before the fix, a six-frame simulated camera drove the real monitor loop, runtime and Tk widgets with publication decisions `[True, False, False, True, False, False]`. The five intermediate observations alternated between live preview and loading overlay: `[(True, False), (False, True), (False, True), (True, False), (False, True)]`, where each pair is `(frame available, placeholder mapped)`. The UI clearing assertion also failed on the old image surface. The red log remains local and ignored.
- After the fix, the same five observations were all `(True, False)`. End-of-monitoring showed the placeholder with the image surface unmapped. The existing UI transition test additionally checks that a new frame restores the image after it was cleared.
- All 26 regression tests passed. After the final resume assertion was added, all eight desktop workspace tests passed again. Tests use isolated settings and simulated camera/detector inputs without registering global hotkeys or hiding applications.
- PyInstaller built version 1.2.1, build 20261010.1. The installed bundle's metadata and compiled preview method were checked, and its local signature verified.
- The actual installed application was restarted and its real camera opened successfully with Core ML / CPU + Neural Engine / 1280. Native screenshots showed updating frames without the loading overlay across multiple observations. Activating “Hide preview” then showed a blank preview surface and its placeholder, with no last-frame ghost. These are live preview checks, not a long-duration recording or detection-accuracy acceptance.

## Local delivery

Installed at `~/Applications/Chill Guard.app`, with the same `com.ghostv.chillguard` identifier. The previous app and exact settings were backed up under `~/Library/Application Support/Chill Guard/Backups/20261010-143536/`. Installation preserved settings bytes. Following the live preview check, Chinese and the previous preview-disabled choice were restored; settings bytes matched that backup again. Monitoring was resumed, matching the application's pre-update running state.

The local DMG is refreshed from the installed signed bundle, and `hdiutil verify` confirmed its checksum is valid; the previous 1.2.0 DMG is retained. Raw build/test/install/package records remain in ignored `validation/local/`. Live camera screenshots are not added to Git. No system permissions were changed, and nothing was pushed or released on GitHub.
