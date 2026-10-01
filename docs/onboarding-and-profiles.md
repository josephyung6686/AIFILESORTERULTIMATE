# Onboarding and the provider step

The order for a folder is:

1. Profile questions (who the folder is for, which lives it contains, which it refuses).
2. AI provider (`filesorter providers`).
3. The first scan.

Step 2 is implemented. `filesorter providers` prints the three lanes and stores the choice in the profile record. The secret, if there is one, stays in the environment or the macOS keychain. Details, flags, and the commands are in `docs/model-providers.md`.

A scan still runs when step 2 has not been answered. In that case DeepSeek is used when `DEEPSEEK_API_KEY` is set, and otherwise the scan stays on what it can decide without a model. Storing lane `none` means this folder asked for no cloud model.

Step 1 is the questionnaire in `docs/context-onboarding-plan.md`. This page does not replace that design. It records where the provider step sits in it: after those questions, before the scan.
