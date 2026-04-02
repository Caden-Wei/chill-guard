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
3. Capture `Start / Stop` and `Hold to Mute` hotkeys in `Hotkeys`
4. Fill the apps you want protected in the blacklist
5. Click `Apply Settings`
6. Click `Start Monitoring`

## Main Features

- `Start / Stop hotkey`: quickly starts or stops monitoring
- `Hold to Mute hotkey`: temporarily mutes alerts while held
- `Preview`: shows the live camera frame
- `Alert Sound`: plays a local warning sound when risk is triggered
- `Apps to Hide`: list of apps to switch or hide after risk is detected

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
