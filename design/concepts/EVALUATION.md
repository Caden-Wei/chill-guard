# Five image-led desktop directions

The user rejected the first code-led interface and explicitly requested five image-model directions, autonomous evaluation/selection, and implementation against the selected image. All five references were generated with the built-in Imagegen tool; exact prompts are in prompts.json.

Scores are design judgments, not user research. Each axis is out of five.

| Direction | Visual craft | Workflow clarity | Desktop usability | Fidelity feasibility | Judgment |
| --- | --- | --- | --- | --- | --- |
| [01 macOS Air](01-macos-air.png) | 5 | 5 | 5 | 4 | Selected: clear hierarchy, familiar controls, balanced preview and inspector |
| [02 Graphite Pro](02-graphite-pro.png) | 5 | 4 | 4 | 4 | Beautiful but dense and duplicates several summaries/actions |
| [03 Soft Mint](03-soft-mint.png) | 4 | 4 | 4 | 4 | Friendly; the headline incorrectly claims protection while in standby |
| [04 Midnight Console](04-midnight-console.png) | 4 | 4 | 3 | 4 | Strong composition; large preview and dark instrument styling dominate everyday settings |
| [05 Editorial Workbench](05-editorial-workbench.png) | 4 | 4 | 4 | 4 | Good grid; broader configuration layout and orange action feel less native |

## Selected authority

01-macos-air.png controls proportion, color, radii, density, camera empty state, inspector layout, protected-app rows/icons and the language control. All other pages inherit this system. Rebuild the widget presentation with CustomTkinter so rounded buttons, fields, and panels are real working controls.

## Required factual corrections to the reference

- Replace the generated claim about hiding applications when nobody is present with the actual rule: eligible people exceed the saved limit for the saved consecutive-frame threshold.
- Use the exact saved Cmd + Ctrl + Option + minus shortcut, not the image's incorrect Shift modifier.
- Replace invented sensitivity presets with the actual allowed-people and trigger-frame settings.
- Keep actual native window chrome, installed application icons, current version, and translated feedback.
- Show configured inference in standby and actual inference only after the detector loads.

## Verification scope

Inspect Chinese and English at default and minimum window sizes, all four pages, basic/advanced settings, keyboard focus, language changes with pending edits, saved keycodes/list, and native/fallback inference in the final package. Compare the running UI directly with the selected image; the reference is not used as a background or a fake clickable screenshot.
