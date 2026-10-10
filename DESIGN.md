---
name: Chill Guard — macOS Air
description: A quiet native macOS utility with clear protection state and bilingual controls.
colors:
  blue: '#005FCC'
  blue-hover: '#0562D9'
  selected: '#DDEBFF'
  white: '#FFFFFF'
  rail: '#EFF3F8'
  ink: '#17202D'
  muted: '#58677B'
  line: '#DFE5EE'
  preview: '#F1F5FA'
  secondary: '#F2F5F9'
  secondary-hover: '#E4EBF4'
  language-track: '#F1F3F7'
  status-surface: '#F6F8FB'
  app-row: '#F8FAFC'
  readonly: '#F7F9FC'
  shortcut: '#F0F3F7'
  switch-off: '#D0D7E2'
  switch-thumb-hover: '#DCE6F5'
  menu-button: '#E8EDF5'
  menu-button-hover: '#DCE5F2'
  menu-item-hover: '#E4EEFF'
  scrollbar: '#D5DDE8'
  scrollbar-hover: '#AEBBCB'
  running: '#21835A'
  muted-state: '#886016'
  error: '#BC3D42'
typography:
  headline:
    fontFamily: SF Pro Text
    fontSize: 25px
    fontWeight: 700
  brand:
    fontFamily: SF Pro Text
    fontSize: 18px
    fontWeight: 700
  empty-state:
    fontFamily: SF Pro Text
    fontSize: 17px
    fontWeight: 700
  section-title:
    fontFamily: SF Pro Text
    fontSize: 14px
    fontWeight: 700
  body:
    fontFamily: SF Pro Text
    fontSize: 13px
    fontWeight: 400
  action:
    fontFamily: SF Pro Text
    fontSize: 13px
    fontWeight: 700
  caption:
    fontFamily: SF Pro Text
    fontSize: 12px
    fontWeight: 400
  status:
    fontFamily: SF Pro Text
    fontSize: 12px
    fontWeight: 700
  label:
    fontFamily: SF Pro Text
    fontSize: 11px
    fontWeight: 400
  fine-print:
    fontFamily: SF Pro Text
    fontSize: 10px
    fontWeight: 400
  keycap:
    fontFamily: SF Pro Text
    fontSize: 16px
    fontWeight: 400
rounded:
  compact: 6px
  field: 7px
  row: 8px
  button: 9px
  panel: 12px
spacing:
  compact: 2px
  tight: 3px
  small: 5px
  control: 8px
  icon: 9px
  row: 10px
  item: 12px
  group: 13px
  column: 14px
  panel: 16px
  section: 18px
  page: 22px
components:
  button-primary:
    backgroundColor: '{colors.blue}'
    textColor: '{colors.white}'
    typography: '{typography.action}'
    rounded: '{rounded.button}'
    height: 34px
  button-primary-hover:
    backgroundColor: '{colors.blue-hover}'
    textColor: '{colors.white}'
    typography: '{typography.action}'
    rounded: '{rounded.button}'
    height: 34px
  button-secondary:
    backgroundColor: '{colors.secondary}'
    textColor: '{colors.ink}'
    typography: '{typography.body}'
    rounded: '{rounded.button}'
    height: 34px
  button-secondary-hover:
    backgroundColor: '{colors.secondary-hover}'
    textColor: '{colors.ink}'
    typography: '{typography.body}'
    rounded: '{rounded.button}'
    height: 34px
  input:
    backgroundColor: '{colors.white}'
    textColor: '{colors.ink}'
    typography: '{typography.body}'
    rounded: '{rounded.field}'
    height: 32px
    width: 148px
  input-readonly:
    backgroundColor: '{colors.readonly}'
    textColor: '{colors.ink}'
    typography: '{typography.body}'
    rounded: '{rounded.field}'
    height: 34px
    width: 200px
  option-menu:
    backgroundColor: '{colors.secondary}'
    textColor: '{colors.ink}'
    typography: '{typography.caption}'
    rounded: '{rounded.field}'
    height: 32px
    width: 247px
  navigation:
    backgroundColor: '{colors.rail}'
    textColor: '{colors.ink}'
    typography: '{typography.body}'
    rounded: '{rounded.button}'
    height: 42px
    width: 172px
  navigation-active:
    backgroundColor: '{colors.selected}'
    textColor: '{colors.blue}'
    typography: '{typography.body}'
    rounded: '{rounded.button}'
    height: 42px
    width: 172px
  language-group:
    backgroundColor: '{colors.language-track}'
    rounded: '{rounded.row}'
    height: 28px
    width: 118px
  language-selected:
    backgroundColor: '{colors.white}'
    textColor: '{colors.blue}'
    typography: '{typography.body}'
    rounded: '{rounded.compact}'
    height: 24px
    width: 55px
  language-unselected:
    backgroundColor: '{colors.language-track}'
    textColor: '{colors.muted}'
    typography: '{typography.body}'
    rounded: '{rounded.compact}'
    height: 24px
    width: 55px
  panel:
    backgroundColor: '{colors.white}'
    rounded: '{rounded.panel}'
  preview-panel:
    backgroundColor: '{colors.preview}'
    rounded: '{rounded.panel}'
  app-row-editor:
    backgroundColor: '{colors.app-row}'
    textColor: '{colors.ink}'
    typography: '{typography.body}'
    rounded: '{rounded.row}'
  app-row-overview:
    backgroundColor: '{colors.white}'
    textColor: '{colors.ink}'
    typography: '{typography.caption}'
    rounded: '{rounded.row}'
  status:
    backgroundColor: '{colors.status-surface}'
    textColor: '{colors.muted}'
    typography: '{typography.status}'
    rounded: '{rounded.panel}'
  shortcut-keycap:
    backgroundColor: '{colors.shortcut}'
    textColor: '{colors.ink}'
    typography: '{typography.keycap}'
    rounded: '{rounded.field}'
  switch-track:
    backgroundColor: '{colors.switch-off}'
    height: 20px
    width: 36px
---

# Design System: Chill Guard — macOS Air

## Overview

**Creative North Star: "macOS Air"**

A quiet, legible macOS camera utility. Pale gray navigation, white working surfaces, a restrained blue action color, and rounded hairline panels make protection state and the next action easy to read. The interface stays compact without hiding the configured applications or mixing advanced geometry into the overview.

This is a native desktop system implemented with CustomTkinter controls and AppKit integration. SF Pro Text, native window chrome, platform symbol assets, and authentic installed application icons adapt the selected image to macOS. The upper-left brand uses the existing packaged App Icon at 40 × 40; preview camera symbols remain platform assets.

**Key Characteristics:**
- Fixed pale navigation rail and flexible white content.
- One dominant camera area, a compact inspector, and a short shortcut strip on the overview.
- Textual state paired with semantic color; explicit save feedback for forms.
- Visible Chinese/EN switching with stable app identities and stored keycodes.

### Authority and evidence

This session replaced the first code-led interface after the user rejected it and requested five Imagegen directions, autonomous evaluation and selection, then real-code recreation. `design/concepts/01-macos-air.png` is the selected visual authority. The prior private-workspace direction is superseded. This records this session's chosen workflow only.

Normative tokens below come from `chill_guard_ui.py`; the direction contract and selected image provide context. Five final native captures were inspected: Chinese and English overview at default and minimum sizes, and English Protected apps at default size. A fresh independent reviewer found minimum-size Photos clipping and text contrast; the reported verdict pass resolved those two findings and returned `ship` at fix-list scope only. The final blue and muted tokens reflect those fixes.

The handoff reports offline native/fallback diagnostics and 25 tests passing. System Accessibility permission remains unauthorized; global shortcut operation and a representative live camera/app-hiding scene remain unaccepted. These files do not claim full accessibility or operational protection acceptance. The native screenshot connector scales output to a maximum height of 768 pixels; the inspected window uses DPR 2. Capture dimensions are not native layout dimensions, and the purple sharing indicator belongs to OS capture tooling. No web detector or numerical comp-diff score applies.

## Colors

The palette is cool, pale, and deliberately quiet. The frontmatter is the normative source for exact values; roles below explain their use.

### Primary

- **Clear Action Blue** (`blue`) marks the primary action, current navigation item, active language, enabled switch track, and explicit button focus border. `blue-hover` is the primary-button hover state.
- **Pale Selection Blue** (`selected`) gives the current navigation item a broad, readable background.

### Neutral

- **Clean White** (`white`) is the working surface, panel interior, button text on blue, and switch thumb.
- **Air Rail** (`rail`) separates navigation from content. **Camera Air** (`preview`) gives the camera area a quiet tonal field.
- **Deep Ink** (`ink`) carries main text. **Slate Secondary** (`muted`) carries supporting copy, labels, standby state, and inactive language labels.
- **Hairline** (`line`) defines panels and fields without heavy outlines.
- **Quiet Control** (`secondary`, `secondary-hover`) gives secondary actions a soft fill and hover response.
- `language-track`, `status-surface`, `app-row`, `readonly`, and `shortcut` are subtle surface variants for their named controls, not extra accents.
- `menu-button`, `menu-button-hover`, and `menu-item-hover` distinguish the option-menu arrow and menu choice hover. `switch-off` and `switch-thumb-hover` describe switch affordances. `scrollbar` and `scrollbar-hover` keep intentional scrolling visible.

### Semantic states

- **Running Green** (`running`) labels active monitoring. **Muted Amber** (`muted-state`) labels paused alerts. **Error Red** (`error`) labels error or alert. Starting uses the primary blue; standby uses muted text.

**The State Before Color Rule.** Always show the protection state in words with its supporting note. Color supplements the words and never establishes protection by itself.

## Typography

**Display and body family:** SF Pro Text, requested by the native toolkit. Chinese glyph fallback is supplied by the installed macOS/Tk font system; no separate Chinese font is embedded or asserted here.

The type is compact and familiar to a macOS utility. Positive source font sizes are CustomTkinter size values; the portable frontmatter expresses those values with `px`. Native window dimensions below are documented in points. Browser samples in the sidecar illustrate roles rather than certifying native font metrics.

### Hierarchy

- **Headline:** bold page title, source size 25.
- **Brand:** bold product name, source size 18.
- **Empty state:** bold camera title, source size 17.
- **Section title:** bold group and inspector titles, source size 14.
- **Body / Action:** regular controls and form labels, or bold primary-action labels, source size 13.
- **Caption / Status:** regular supporting copy and compact app rows, or bold status title, source size 12.
- **Label:** metadata, model values, save feedback, and helper copy, source size 11.
- **Fine print:** local-processing footer and status note, source size 10.
- **Keycap:** shortcut display, source size 16.

No authored line-height or tracking scale exists in the native source. Do not infer either from a resized capture.

**The Native Type Rule.** Use the compact platform typography and Chinese system glyph fallback. Keep the brand name, application names, and shortcut identity intact across languages.

## Layout

Default content size is 1120 × 760 points; minimum is 1000 × 690 points. The rail is fixed at 204 logical units. Content expands horizontally with 22-unit page insets and a 44-unit toolbar. The language group stays at upper right. There is no mobile layout or web breakpoint system in this build.

The overview has a flexible camera region on the left, a fixed 292-unit inspector on the right, and a 14-unit gap. The inspector stacks model/rules and protected apps. The full-width shortcut panel sits below, after textual feedback. The camera empty state is centered near 47% of the camera area's height; its single primary action is 156 × 38 units. The live camera frame is padded to fit, retaining all edges.

The overview currently exposes all six saved applications: Safari, iPhone Mirroring, WeChat, Telegram, QQ Music, and Photos. Compact overview rows use 23-unit icons, 12-size text, and tight vertical spacing. The source shows the first six saved rows and a manage action when more exist; this is a presentation limit, not a limit on the stored list. The editable list uses larger 27-unit icons and 13-size text, with intentional scrolling. Default and minimum captures show Photos completely.

Detection has basic and advanced scrollable forms. Protected apps and Shortcuts & startup also use deliberate scrolling. Source focus handling reveals an offscreen detection field when it receives focus. The form footer remains outside the scroll area; Overview hides that save footer. Use the actual spacing steps in frontmatter rather than imposing a new uniform grid.

**The Complete Frame Rule.** Fit the whole camera frame into the preview using padding. Edge entrants must remain visible rather than being cropped for composition.

## Elevation & Depth

The app uses flat tonal layering and one-unit hairline borders. There are no authored in-app shadows, glass effects, gradients, or custom motion/easing tokens. macOS owns the window chrome and its exterior depth. State changes and language changes update directly; the delayed native-appearance setup is scheduling, not a motion token.

**The Hairline Depth Rule.** Separate panels with a light stroke and tonal surfaces. Reserve actual window elevation for macOS window chrome.

## Shapes

Bordered panels use gently rounded corners (12 source units) with a one-unit hairline. Buttons use a compact curve (9); app rows and the language container use 8; fields and shortcut keycaps use 7; language segments use 6. The App Icon retains its own artwork and corners without an extra blue badge. Flat page and rail wrappers have square corners. Keep radius tied to the component role rather than rounding every nested wrapper.

Platform symbols are image assets, not text glyph substitutes for interface icons. The upper-left brand shares `assets/app_icon_1024.png` with the packaged macOS App Icon; camera symbols serve preview states. Native title chrome and authentic installed application icons are intentional macOS adaptations. Modifier glyphs in shortcut keycaps and the dot beside a written status are functional notation.

## Components

### Buttons

Restrained, compact actions. Default height is 34 source units with a 9-unit radius. Primary buttons use Clear Action Blue and white bold labels; secondary buttons use Quiet Control and regular ink labels. Hover uses the recorded variant fills. The native drawn buttons explicitly accept keyboard focus, Return, and Space; focus adds a two-unit blue border. The camera action is the larger 156 × 38 variant; the save action is 128 × 34. Do not infer complete accessibility from these bindings.

### Fields and option menus

Plain white, hairline fields use a 7-unit radius. Numeric fields are 148 × 32 and right aligned. The manual process-name field is 34 high and expands in its row. Readonly shortcut fields use the subtle readonly surface, 200 × 34. Model/engine option menus are 247 × 32 with a filled arrow region and light hover fill. Native toolkit field focus appearance is not established as a separate authored token.

### Navigation

Four native pages share 172 × 42 buttons in the fixed rail. Regular 13-size text and 20-unit platform symbols keep labels legible. Active state uses the pale selection surface, blue text, and blue asset variant; inactive state uses the rail and ink. Command–1 through Command–4 select pages.

### Chinese / EN control

The toolbar holds a 118 × 28 rounded group containing 55 × 24 segments with two-unit inset spacing. The selected segment is white with blue text; the other uses the track surface and muted text. Switching is immediate and persisted, updates controls, feedback, dialogs and menus, and preserves pending form edits. Command–Shift–L also switches language. Application/process names and underlying shortcut keycodes remain unchanged by translation.

### Panels and camera

White inspector and settings panels use the shared hairline and panel curve. Inspector content uses 16-unit side insets; settings sections use 18. The pale camera panel has nine-unit inner frame padding. Standby shows camera-off text and Start protection; a hidden preview explains that detection continues. The toolbar is present only for applicable running controls. Standby shows configured inference; actual inference is presented only after loading.

### Status

The rounded status card pairs a bold 12-size title with a 10-size note. State words carry meaning; green, amber, red, blue, or muted text supplements them. The supporting feedback line remains available below the overview panels. This badge is feedback, not an action.

### Application rows

Real installed icons accompany exact app/process names. Overview rows navigate to management; editable rows use a trailing remove action on a pale row surface. Add application resolves the declared executable when available; manual entry asks for the exact process name. Edits take effect after Save changes, and unsaved feedback remains visible.

### Switches and shortcut strip

Switch tracks are 36 × 20, with blue progress, a white thumb, and a gray off track. The overview shortcut strip combines a platform keyboard symbol, short explanation, a neutral keycap, and Change shortcut. The saved start/stop chord is Cmd + Ctrl + Option + minus; the generated reference's Shift modifier is superseded. This visual notation does not establish global-listener acceptance.

### Save behavior

Detection parameters, application-list edits, and shortcuts require explicit Save changes. Language, preview, and launch-at-login preferences persist immediately. The save footer pairs a muted saved/unsaved label with the blue action; Command–S saves. Keep these different persistence semantics visible in the copy.

## Do's and Don'ts

### Do:
- **Do** keep the Chinese/EN control visible in the upper-right toolbar on every page.
- **Do** preserve the actual six saved app identities and keycode data; display labels may change with language.
- **Do** retain complete app rows at the minimum window size and use intentional scrolling for long forms.
- **Do** distinguish configured inference in standby from the backend that actually loads while running.
- **Do** show saved versus unsaved form state and provide a visible recovery action when permission or runtime feedback requires it.
- **Do** inherit the selected macOS Air palette, compact native type, rounded controls, and hairline panels on new pages.

### Don't:
- **Don't** restore the rejected code-led private-workspace direction or combine it with this chosen system.
- **Don't** turn this session's five-image exploration and delegated selection into a permanent user workflow preference.
- **Don't** infer active protection from standby, hidden preview, or a static screenshot.
- **Don't** replace real app names, keycodes, saved numeric rules, or backend state with generated presets or claims.
- **Don't** use a screenshot as a working interface or crop camera edges to imitate the concept.
- **Don't** add in-app decorative shadows, promotional display typography, or invented telemetry to this native utility.
