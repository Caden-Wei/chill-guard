# Chill Guard Installation Guide

[简体中文](INSTALL.zh-CN.md)

## Supported Platform

- Current release supports `macOS`

## macOS Installation

You should receive:

- `Chill Guard-macOS.dmg`

Recommended install flow:

1. Double-click `Chill Guard-macOS.dmg`
2. Drag `Chill Guard.app` into `Applications`
3. Launch `Chill Guard` from Applications

## First Launch Checklist

Confirm these two permissions on first launch:

1. Camera permission
2. Accessibility permission

Accessibility is used for:

- Receiving global hotkeys
- Switching or hiding your configured apps when risk is detected

If global hotkeys do not respond, go to:

- `System Settings -> Privacy & Security -> Accessibility`

Confirm the enabled item is the exact `Chill Guard.app` you are running.

## Basic Workflow

1. Open `Chill Guard`
2. Check the camera and detection settings in `Detection`
3. Capture `Start / Stop` and `Hold to Mute` hotkeys in `Shortcuts & startup`
4. Add applications or their exact process names in `Protected apps`
5. Click `Save changes`
6. Click `Start protection` in Overview

## Main Features

- `Start / Stop hotkey`: quickly starts or stops monitoring
- `Hold to Mute hotkey`: temporarily mutes alerts while held
- `Preview`: shows the live camera frame
- `Alert Sound`: plays a local warning sound when risk is triggered
- `Protected apps`: list of applications to hide when the configured rules trigger

## Inference Backend

Version 1.2 defaults to YOLO26s and Apple Core ML at 1280. Detection offers Apple Core ML, Automatic, and PyTorch compatibility. The local build includes a matching native export. Missing, incompatible or failed native inference switches visibly to PyTorch. Changing the model, engine or size while monitoring reloads the detector. See [Apple inference setup](APPLE_INFERENCE.md).

Overview shows the configured engine before monitoring and the actual engine while running. Chinese/English can be switched using the visible top-right control or Command+Shift+L. Language switching preserves pending edits. App names and recorded keycodes are not translated. Long forms scroll, and Command+1–4 opens each page; Command+S saves changes.

Settings, including trigger frames, model choice, and inference backend, are preserved on restart. Hold to Mute suppresses both sound and hiding while detection continues. Preview keeps the complete camera frame with padding, so people at the edges remain visible.

## Common Issues

### 1. Global hotkeys do not respond

Check:

- Whether you are running the installed app rather than an old copy
- Whether Accessibility is enabled for that exact app
- Whether the hotkey is mapped to a special mouse-driver-only function key

### 2. The camera does not open

Check:

- Whether macOS granted `Chill Guard` camera access
- Whether another app is already using the camera

### 3. Apps are not hidden after risk is detected

Check:

- Whether the app names in the blacklist are correct
- Whether Accessibility permission is enabled

## Distribution Notes

When sending the app to another Mac user, send:

- `Chill Guard-macOS.dmg`
- This installation guide

If macOS shows a security warning:

- Right-click `Chill Guard.app`
- Choose `Open`
- Confirm once more

That is expected for a locally built app that has not been notarized.
