# Onboarding and the provider step

The order for a folder is:

1. A completed profile (who the folder is for, which lives it contains, which it refuses).
2. AI provider (`filesorter providers`).
3. The scan: text and OCR, then the deterministic sort, then understanding for files that sort did not place.

A scan refuses until step 1 is done for that folder. Two ways finish that step. `--answers FILE` reads a JSON file the person already filled in. `filesorter onboard` asks the same questions in the terminal and stores the record, so no pre-filled file is required. `confirmed` must be true, and a field that still says TODO is not an answer. The shipped file `profiles/answers.alana.json` is a template. Using it as-is is refused and nothing is scanned.

`filesorter onboard` asks, in order: name, lives, lives to refuse, a situation for each life, school, courses, companies, names to leave alone, wording to keep on this computer, and private areas. The name and the wording stay in the plan database. They are not printed back and they are not put in the model prompt. Type `skip` and the command refuses, unless `FILESORTER_ONBOARDING_OPTIONAL=1`, which is how the test suite skips the refusal. A person's own run does not set it. Typing `yes` at the end stores the profile. The database must sit outside the folder.

```
filesorter onboard \
  --folder ~/star-sorter-test/dl \
  --database ~/star-sorter-test/dl-plan.sqlite \
  --write ~/star-sorter-test/answers.json
```

When that command finishes it prints the next step. If no provider is stored, that step is `filesorter providers`. Then the scan. A later scan of the same folder can omit `--answers`, because the record is already stored. `--answers FILE` remains the path that does not ask questions.

`--model-dry-run` and `--onboarding-questions` still run without a profile, because neither one sorts the folder. `--model-dry-run` does not open a network connection.

The longer adaptive questionnaire in `docs/context-onboarding-plan.md` is still the design for questions that follow a scan. The command above is the required profile before the first scan.

Lives and refusals in the file are the allow-list the recogniser already reads. Business is not a fallback and is not filled in when a life is missing. The person's name is stored in the plan database and is not put in the model prompt. School, courses, companies, situations, and the declared lives are. Course codes and company names are not a second recogniser: a file the rules do not place is the one the model sees, with that profile beside the dossier.

Step 2 is implemented. `filesorter providers` prints the three lanes and stores the choice in the profile record. The secret, if there is one, stays in the environment or the macOS keychain. Details, flags, and the commands are in `docs/model-providers.md`.

Understanding is part of the scan. `filesorter onboard` stores the profile and the fact that dossier text may go to the provider. It does not ask whether to use a model. A scan with a stored provider, or with `DEEPSEEK_API_KEY` and `DEEPSEEK_MODEL_FAST`, runs the understanding pass after the rules. A scan with no provider stops before any file is read and says to set up a model provider. The sentence names `filesorter onboard` and `filesorter providers`. Nothing is sent. Storing lane `none` is the same as no provider. `filesorter providers status` prints the stored lane and whether each key is present. It does not print the key, and it sends nothing.

Developers skip the pass with `--no-understand` or `FILESORTER_SKIP_UNDERSTANDING=1`. A person's run does not set that name, and a person does not pass a flag to turn understanding on.
