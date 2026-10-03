# File companion onboarding

The folder-access screen uses a later layout: a Mac window titled File Companion, a top step row (Folders, Profile, Work areas, Categories, Scan, Briefing), the glass companion at the top right, and three folder cards. The primary button stays navy `#364C84`. Documents is not preselected. The other screens keep the left step list and the calm right panel.

## Visual direction

The Mac window keeps the left step list, central question, calm right panel, Back text button, and one primary action. The visual finish now follows the supplied glass-folder and upload-panel references: broad rounded surfaces, white rims, soft light, layered papers, and pill-shaped controls. The companion is a rendered glass folder with two small eyes, rather than a flat CSS illustration.

The folder-access step uses three layered folder surfaces and a separate Another folder row. Work areas use the same material: angled white paper sheets, a translucent periwinkle front, and a shaped tab. Student uses a small paper notebook. The right panel keeps the glass companion with two little eyes.

The foundation token files match the White & Periwinkle style guide. Key surface colors, fields, card and window radii, font family, and interaction duration use these shared values. Folder material shades and translucent shadow recipes remain component-specific.

Folder cards retain native checkboxes. Selection adds a navy inset ring while the checkbox supplies a second visible cue. Keyboard focus highlights both the input and its enclosing folder. Paper movement appears only on pointer hover and stops when reduced motion is requested. Narrow layouts stack folders, preserve readable captions, and keep the inputs above the paper layers.

| Role | Color |
| --- | --- |
| Canvas and cards | `#FFFFFF` |
| Text, links, buttons and focus | `#364C84` |
| Folder | `#95B1EE` |
| Folder gradient start | `#B6CAF4` |
| Selected cards | `#D9E3FA` |
| Tiny Ready and Suggested badges | `#E7F1A8` |
| Supporting text | `#657080` |

Lime is limited to small status badges. Selection uses both a native control and a navy border. There are no preselected folders, profiles, work areas, or categories.

## Screen map

| Screen | Choice or result | Primary action |
| --- | --- | --- |
| Folder access | Documents, Downloads, Desktop, or another folder | Allow folder access |
| Your profile | Student or Start blank | Continue |
| Areas of work | Courses, Applications, Recruiting, Projects, and things to leave alone | Review categories |
| Your categories | Confirm, edit, refuse, or add categories | Save choices & scan |
| Local scan | Read folders, check categories, keep sensitive material held | Pause or resume scan |
| Archive briefing | Found, held, unplaced, left alone, and confirmed categories | Open workspace |

Only Student exposes Courses. Course names, company names, project names, and exclusion names are optional. Continuing without a profile starts blank. Continuing with no work areas is allowed.

## Approval rules

Suggested categories remain pending until the user presses Confirm. Refused and pending categories never enter the confirmed-category list. Renaming a category makes it pending again. Saving an unchanged name preserves its approval. Refused categories can be restored as suggestions.

If every category is refused, setup can still finish. Readable items start unplaced. Sensitive finance, identity, medical, and legal material remains held and must never be sent to a model.

Example filenames in the right panel are explicitly labeled as examples. They are not scan results. Changing folders requires access to be requested again before the scan can start.

## Edge states

- First run: nothing selected; folder access action disabled.
- No folders: continue without folders; add access later.
- Access denied: explain the missing permission and provide a System Settings path.
- Start blank: no Courses card or proposed categories.
- Nothing chosen: continue with items unplaced.
- All categories refused: proceed with no confirmed categories.
- Paused scan: resume without advancing while paused.

## Prototype and native handoff

This prototype works offline. It keeps its state in memory and does not persist personal data. Permission dialogs, scan phases, and the workspace handoff are design previews.

`setupSnapshot()` on the root element returns a proposed answer model. Map this model to the existing engine's answers-file schema; it is not a claimed engine API. Persist the finished answers atomically before invoking the engine. The scan must refuse to start when answers are unfinished or folder access is missing.

The production reader must enforce local folder scope, exclusions, read-only file operations, held-material isolation, and explicit category approval. UI copy alone does not enforce these boundaries.

Result rows must be populated by actual engine output after completion. Do not infer totals from progress phases. Retain undo for changes to the app's metadata structure.

The Other field represents a native folder picker. Use the system permission APIs and the appropriate System Settings destination in the Mac app. Replace the simulated timer with engine progress events. The final workspace is outside this onboarding design.
