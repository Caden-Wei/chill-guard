# Chill Guard 1.2 local desktop upgrade — 2026-10-08

This record distinguishes implementation, local installed-build checks and unaccepted real-world behavior. The user delegated autonomous upgrade and selection of one of five generated UI directions. Nothing was pushed or publicly released.

## Model and inference

- Apple M4 Pro, arm64, macOS 27.0.1, Python 3.12.13, Ultralytics 8.4.174, coremltools 9.0, NumPy 2.3.5.
- Default weights changed to YOLO26s. A verified FP16 raw COCO Core ML export at 1280 is bundled; the loader validates weights SHA-256, input/output shape and manifest contract. PyTorch uses the same one-to-many YOLO26 head and remains a visible fallback.
- Warm wall time includes preprocessing and NMS, excludes camera/tracking/UI/actions. Three warmups and 30 iterations per sample. Core ML p50: bus 34.03 ms, zidane 34.41 ms; PyTorch MPS: 41.52 ms and 32.56 ms. Native p95 approximately 41.16 and 39.39 ms. No native fallback occurred.
- Native and compatibility paths produced four bus boxes and three zidane boxes. Padding differs and boxes differ; these two images do not establish accuracy, scene coverage or uniformly faster inference. Earlier YOLO11 benchmarks are separate evidence.
- Frozen diagnostic: YOLO26s + Core ML / CPU + Neural Engine / 1280, no notice, four bus detections. Deliberately selecting unexported YOLO11n/640 produced PyTorch / MPS with a visible missing-export notice and four detections.

## UI direction and verification

[Five real Imagegen concepts](../design/concepts/EVALUATION.md) were generated. macOS Air was selected by design judgment under the user's explicit delegation. Its pale sidebar, camera/inspector composition, rounded controls and shortcut strip were implemented as working CustomTkinter controls, using real app icons and native SF symbols. Generated inaccurate trigger copy, shortcut modifiers and presets were replaced with product truth. Chinese/English switch applies to pages, dynamic feedback, dialogs, app menus and Dock menus, preserving pending edits and stored keycodes.

Captured the actual installed application at default 1120×760 and minimum 1000×690 content points on DPR 2. Both languages cover all four pages and advanced settings at default size. Minimum captures cover both overview languages and an intentionally scrolled advanced English form with its final field reached by Tab. Native captures are JPEGs reduced by the capture connector to at most 768 pixels high; a purple OS screen-sharing indicator belongs to capture tooling. No web pixel-diff score or whole-platform accessibility acceptance is claimed.

The implementation inspection corrected toolbar occlusion, row clipping, natural field sizing, high-resolution icon rendering and initial navigation/footer state. An independent fresh review requested two fixes: expose the sixth overview row at minimum size and raise text contrast on tinted surfaces. Compact overview row heights and darker text/action variants address these findings. Measured text ratios are 4.96:1 for selected navigation, 5.18:1 on the rail, 5.27:1 on preview, 5.77:1 for the placeholder and 5.98:1 for primary white text. The independent verdict scored both findings resolved, with disposition `ship` at fix-list scope; see [the verdict](../.impeccable/review/finish-verdict.md).

25 regression tests pass. They exercise protection thresholds and target exclusions, mute suppression, settings restart behavior, native contract checks and recovery, bilingual pending-edit preservation, exact shortcuts, drawn mouse/keyboard callbacks, starting versus running states, preview empty/live transitions, advanced field reachability and all six overview rows at minimum size. GUI tests use isolated settings and do not register global hotkeys, open a camera, play sound or hide apps.

## Installed software and preservation

Installed path: `~/Applications/Chill Guard.app`, version 1.2.0, build 20261008.3, bundle identifier `com.ghostv.chillguard`. Prepared/staged bundles were signed locally and verified before replacement. Each replacement backs up the prior app and exact settings under `~/Library/Application Support/Chill Guard/Backups/`; raw installation records remain in ignored `validation/local/`.

The final installed bundle was packaged locally as `dist/Chill Guard-macOS.dmg`. `hdiutil verify` confirmed its checksum is valid. The prior disk image was retained locally; neither package was uploaded.

The authorized detection upgrade selects `yolo26s.pt` and `coreml`, schema 2. The blacklist remains, in exact order: Safari, iPhone Mirroring, WeChat, Telegram, QQ Music, Photos. Exact stored shortcuts remain `<cmd>+<ctrl>+<alt>+<keycode:27>` and `<keycode:99>`. Detection thresholds, camera size/index, preview disabled, sound enabled and login-start choice are retained. The bilingual test temporarily switches language and restores Chinese. Installation itself leaves the settings bytes unchanged.

## Practical limits

macOS's Accessibility check still reports the installed app as unauthorized. The interface exposes recovery steps; global shortcut operation is not accepted. Camera permission, representative live scene accuracy and actual app hiding were not verified in this UI round. The upgrade stays in standby. Offline native inference and mocked protection-rule results cannot establish real camera/Automation behavior. System permissions were not changed.

Generated native model packages, environments, build output and raw reports remain local and ignored. This is a locally signed app, not a notarized public release.
