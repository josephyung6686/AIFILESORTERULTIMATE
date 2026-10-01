# Local mail, deadlines, and suggestions

These commands do not call DeepSeek, OpenAI, or Anthropic. They do not open a
network connection. They do not move a file.

## What is real

A JSON fixture on disk is a real import. `filesorter sync gmail` and
`filesorter sync calendar` read that file and store headers in the plan
database as items.

An email item stores the message id, thread id, date, From, To, subject,
attachment filenames, and attachment hashes. A calendar item stores the event
id, calendar id, start, end, title, and status. When an attachment hash matches
`files.content_hash`, the email points at that file and a witnessed
`attached-to` link is stored as `proposed`. It is not approved. A match against
a protected path (a key file, for example) sets the email's `typing_state` to
`held`. A held item contributes no fields to a model request. An attachment
that matches no file stays an email item with no file link.

`filesorter view deadlines` lists each event, the files with a witnessed or
approved link to it, and any file you named with `--expect` that has no such
link. Inferred links are hidden and counted. Unplaced files stay in their own
count. `--html PATH` writes one document with no scripts and no remote assets.

`filesorter suggest` reads course items and future events. A course with no
witnessed or approved `member-of` from an academic file is one printed
warning. `--apply` is refused. The command does not write a row.

The managed provider lane is unchanged: selecting it still refuses. There is
no billing backend.

## What is a stub

Live Gmail and live Calendar are not connected. This repository has no Apple
Mail, EventKit, or Google client. Without `--fixture`, sync prints that no
credentials are configured and stores nothing. OAuth tokens are not a column
in the plan database, and this pass does not write them anywhere else.

Message bodies, raw mail, attachment bytes, and calendar descriptions are not
stored, even when a fixture contains them.

```
filesorter sync gmail --dry-run
filesorter sync calendar --dry-run
filesorter sync gmail --fixture ~/mail.json --database ~/plan.sqlite
filesorter sync calendar --fixture ~/mail.json --database ~/plan.sqlite
filesorter view deadlines --database ~/plan.sqlite --html ~/deadlines.html
filesorter suggest --database ~/plan.sqlite
```

`--dry-run` prints the count and the field names it would store. It does not
create a database.
