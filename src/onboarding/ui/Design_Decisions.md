# File Companion onboarding

The folder-access screen is a Mac window titled File Companion. A top step row reads Folders, Profile, Work areas, Categories, Scan, Briefing. Tuck, in the carry pose, stands on an ember ground. Folder cards use the supplied glass folder icon on solid surface-1. Documents is not preselected. Later screens keep the step list and one Tuck in the side panel.

## Visual direction

The look is the File Companion design system: `tokens.css`, Manrope, JetBrains Mono, and the supplied glass icons. Primary actions use blue-600. Ember is Tuck's ground and the confirmation that removes an empty folder from disk. Cards and lists are solid surface-1. Glass is the icon and Tuck accent.

Folder cards keep native checkboxes. A selected card uses blue-50 with a blue-600 border. Nothing is preselected. Example filenames stay labeled as examples. Tuck is one per screen: carry while choosing folders, idle while waiting, rest when a finished scan has nothing unplaced. Tuck is hidden on errors and is not recolored.

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
