# Chill Guard

[简体中文](README.zh-CN.md)

Chill Guard is a small macOS app for covering your screen when you are slacking off at work. It watches the local camera feed, counts how many people are in view, and hides selected apps when too many people show up.

Current status:

- macOS only
- local desktop app, not a cloud service
- built with `tkinter`, `OpenCV`, `PyObjC`, `ultralytics`, and `PyInstaller`

## What it does

- Monitors the built-in or external camera in real time
- Treats one person as the primary user and counts additional people in frame
- Triggers the hide flow when visible people exceed the configured limit
- Plays a local alert sound
- Hides configured apps through macOS accessibility automation
- Supports global start/stop and hold-to-mute hotkeys
- Supports launch at login

## What it does not do

- It does not perform identity recognition
- It does not upload camera frames to a remote server
- It does not currently support Windows

## How it works

The app uses a YOLO person-detection model to detect `person` boxes only. A heuristic then picks the main user box and counts everyone else in frame. If `visible_people > max_allowed_people`, Chill Guard plays an alert and tries to hide the apps in your list.

## Repository layout

- `chill_guard_app.py`: main application
- `Chill Guard.spec`: PyInstaller spec for macOS packaging
- `packaging/build_macos_release.sh`: release build script
- `docs/INSTALL.md`: end-user macOS install guide
- `docs/INSTALL.zh-CN.md`: Chinese install guide
- `yolo11s.pt`: default model file used by the packaged app
- `yolo11n.pt`: lighter optional model file

## Requirements

- macOS
- Python `3.12`
- Camera permission
- Accessibility permission
- A local Python environment with the dependencies in `requirements.txt`

## Run from source

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python chill_guard_app.py
```

If `tkinter` is missing on your machine, install the Homebrew Python/Tk stack first.

## Build the macOS app

```bash
./packaging/build_macos_release.sh
```

The script produces a DMG release in `dist/`.

## Permissions

Chill Guard needs:

- Camera access: to inspect the local camera feed
- Accessibility access: to receive global hotkeys and hide configured apps
- Apple Events automation: to hide configured apps and manage login items

## Open source and licensing

This repository is published under `AGPL-3.0-or-later`.

The reason is practical: the project currently depends on `ultralytics`, whose official licensing model is AGPL-3.0 or commercial enterprise licensing. If you plan to reuse this code in a closed-source product, review the upstream licensing terms carefully before doing so.

See:

- [Ultralytics licensing overview](https://docs.ultralytics.com/license/)
- [GNU AGPL v3](https://www.gnu.org/licenses/agpl-3.0.txt)

## Known limitations

- The app is tightly coupled to macOS system APIs through `PyObjC`
- Global hotkeys depend on macOS input and accessibility behavior
- Hiding third-party apps relies on AppleScript/System Events and may vary by target app
- Person counting is heuristic-based and can be affected by framing, lighting, and duplicate detections

## Development notes

- Do not commit `dist/`, `build/`, `.venv/`, or runtime logs
- Validate syntax with:

```bash
python -m py_compile chill_guard_app.py
```

- For user-facing behavior changes, update `docs/INSTALL.md` and `docs/INSTALL.zh-CN.md`
