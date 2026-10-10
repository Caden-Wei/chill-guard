# Detection dropdowns and trackpad scrolling — 2026-10-10

The reported screen was the English Detection settings page in the installed 1.2.2 app. Native desktop automation reproduced a scroll with no movement; Camera and Feedback remained below the viewport.

The bundled runtime uses Tk 9.0.3 on Aqua. An isolated workspace captured a `TouchpadScroll` event delivered to the toplevel, while CustomTkinter 5.2.2's scrollable frame only binds `MouseWheel`. Tk 9 encodes signed x/y deltas in this separate event, as specified in [Tk TIP 684](https://core.tcl-lang.org/tips/doc/main/tip/684.md).

`WorkspaceScrollFrame` handles precise vertical pixel deltas and resolves toplevel delivery using the pointer's widget. Only the visible containing scroll area moves. Existing CTk mouse-wheel handling remains; the new binding is removed on destruction. Horizontal-only gestures do not move these vertical forms. All existing workspace scroll areas use the same adapter.

The model and engine selectors retain CTk's menus, value mappings and keyboard activation. Their arrows are now 8 × 4 point gray chevrons with a 1.4 point round stroke, on a unified field background. The app icon, page layout, translations and detection settings remain intact. DESIGN.md and its token metadata reflect the new surfaces.

The precise-event regression failed before the change over the body, menu label, entry and scrollbar. It passed afterward, including reverse movement and reaching the lower settings at the 1000 × 690 minimum window size. Additional checks cover single-pixel deltas, toplevel delivery, visible-page isolation, horizontal-only gestures, menu mouse/keyboard activation, actual menu commands, and preserving pending choices across language switches. All 29 tests passed.

Native automation on the isolated workspace confirmed that the same down/up scroll input now reveals Camera, Feedback and Restore defaults, then returns to the selectors. This verifies generated native precise-scroll events; a physical trackpad gesture was not operated by the agent. Raw diagnostic and test records are kept in ignored `validation/local/`.

PyInstaller built version 1.2.3, build 20261010.3. The installed `~/Applications/Chill Guard.app` passes strict signature verification. Native inspection of that installed version confirmed both new arrows, scrolling to Feedback and Restore defaults, returning to the selectors, and scrolling downward with the pointer over an entry. The user's current English configuration, protected-app list and shortcuts are byte-identical before and after installation and UI verification. The prior app and settings are backed up under `~/Library/Application Support/Chill Guard/Backups/20261010-153002/`. The refreshed local DMG passes `hdiutil verify`; the 1.2.2 DMG is retained separately. Local binaries, settings and diagnostic records remain ignored.
