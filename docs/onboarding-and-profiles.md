# Onboarding and the provider step

The order for a folder is:

1. A completed answers file (who the folder is for, which lives it contains, which it refuses).
2. AI provider (`filesorter providers`).
3. The scan: text and OCR, then the deterministic sort, then understanding for files that sort did not place.

A scan refuses until step 1 is done for that folder. Pass `--answers FILE`, or point at a folder that already has a completed record. `confirmed` must be true, and a field that still says TODO is not an answer. The shipped file `profiles/answers.alana.json` is a template. Using it as-is is refused and nothing is scanned.

The adaptive questionnaire in `docs/context-onboarding-plan.md` is still the design for asking those questions in the product. What blocks a scan today is the answers file.

`FILESORTER_ONBOARDING_OPTIONAL=1` is how the test suite skips the refusal. A person's own run does not set it. `--model-dry-run` and `--onboarding-questions` still run without a profile, because neither one sorts the folder.

Lives and refusals in the file are the allow-list the recogniser already reads. Business is not a fallback and is not filled in when a life is missing. The person's name is stored in the plan database and is not put in the model prompt. School, courses, companies, situations, and the declared lives are. Course codes and company names are not a second recogniser: a file the rules do not place is the one the model sees, with that profile beside the dossier.

Step 2 is implemented. `filesorter providers` prints the three lanes and stores the choice in the profile record. The secret, if there is one, stays in the environment or the macOS keychain. Details, flags, and the commands are in `docs/model-providers.md`.

A scan still runs when step 2 has not been answered. In that case DeepSeek is used when `DEEPSEEK_API_KEY` is set, and otherwise the scan stays on what it can decide without a model. Storing lane `none` means this folder asked for no cloud model.
