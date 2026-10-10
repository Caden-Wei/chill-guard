# Chill Guard

<!-- impeccable:product-schema 1 -->

## Platform

macOS desktop, native application lifecycle, app menu and Dock menu, with a Tk interface and AppKit integration.

## Users

The current user wants local protection for private applications while using their Mac. Further audience research is undecided.

## Product Purpose

Analyze camera frames locally for additional people and hide the configured applications when the saved risk rules are met.

## Operating Context

Start and stop from the main window, Dock menu, or saved global shortcut. Hold the saved mute shortcut to temporarily suppress alerts. Camera preview is optional and currently disabled by the user.

## Capabilities and Constraints

- Person detection is not identity recognition. Main-user selection and ignore regions are geometric heuristics.
- Camera images stay local. Native inference must expose the actual backend and any fallback.
- Preserve the user's existing application list, shortcuts, launch-at-login choice, and detection rules during upgrades.
- The user explicitly delegated implementation and requested a complete local upgrade, including newer detection, a more usable modern interface, and switchable Chinese and English.
- Publishing and pushing require explicit user authorization.

## Brand Commitments

Keep the product name Chill Guard. Chinese and English must cover controls, feedback, settings, dialogs, and the menu bar.

## Evidence on Hand

The current implementation, saved user settings, local M4 Pro inference measurements, and the installed application. Sample-image tests are available; representative camera-scene accuracy is undecided.

## Product Principles

- Make monitoring state and the configured protection immediately understandable.
- Keep common controls visible and advanced geometry separate.
- Preserve user choices and show failures with a recovery action.
- Never claim facial identification or guaranteed protection.
