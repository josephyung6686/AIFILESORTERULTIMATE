# Domain catalogue — time, scheduling and communications

Supercategory: `time-scheduling-communications`
Slice: 14
Entries: 14 — 3 design, 4 inference, 7 proposal
Contract: [`_CONTRACT.md`](_CONTRACT.md) · Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

## Why this slice exists

Thirteen catalogues define 560 domains and not one of them has a calendar entry as its subject. That is not a taste judgement about coverage; it is a hole the product falls into. `src/extractors/router.py` maps `ics` to source type `calendar`, `calendar` is one of P4's fourteen closed `source_type` values, and `src/extractors/long_tail.py` carries `calendar` as one of §2.9's six long-tail families — so a `.ics` file extracts cleanly, emits evidence in the common shape, and then arrives at a fact layer with no schema to resolve into. §3.6 says the validator checks “that the proposed field exists in the relevant domain schema”, and where no schema exists the check cannot pass, so the honest outcome for every calendar file in the corpus today is rejection.

Two authors had already noticed. `03-research-science.json`'s `res.facility-booking` cites `calendar.events`; `06-healthcare-medicine.json`'s `med.practice-administration` cites `personal.calendar`. Neither existed. A third, `08-software-technology.json`'s `soft.helpdesk-ticket`, cites `career.correspondence`, reaching for a working-communication domain that also did not exist — the corpus had `pers.correspondence` for personal letters and `law.matter-correspondence` for legal matters, and nothing for the ordinary case of two people at work sending each other email.

This slice authors the calendar domain under the id one of those two authors already used, so `res.facility-booking`'s reference now resolves. The other two are noted below and are not this slice's to repoint.

## How to read this file

- **Curly double quotes are verbatim quotations** from the source of truth and nothing else. Every one inside the JSON is checked by `check.py`, which normalises whitespace and requires the span to appear in the design; a quotation that does not appear fails the build. Where a claim is mine rather than the design's it is written as plain prose with no quote marks.
- **Single quotes are pattern literals** — tokens a recogniser looks for in a document — following the convention in the contract's own worked example. Backticked spans in the recognition lists are container properties (`DTSTART`, `List-Id`, `BEGIN:VCARD`), which are format facts rather than patterns.
- `reliability_ceiling` uses §3.13's six states only. Every `validated` field in this file has a matching `recognition.deterministic` line that could actually confirm it; where no such rule exists the field is `llm_supported`, `possible` or `user_confirmed` instead, and three fields are deliberately capped below what an optimistic reading would allow.
- `sensitivity` is §2.9's phrase and nothing more. **No handling class is assigned anywhere in this file**; handling classes are P7's (§8.4). This slice makes assigning one more tempting than most — an address book, a mailbox export and a verification code are all in scope — and the temptation is recorded rather than acted on.
- No thresholds, no scores, no counts. Digits appear only inside `example` values.
- Every `collides_with.domain` names a real id from one of the fourteen catalogues. The eight ids referenced outside this file were checked against the merged namespace before they were written.

## Four findings that apply to the whole slice

**1 — §5.5 offers two cases and calendar material is neither, so `time_first` had to be argued rather than looked up.** The rule reads: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders. Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” A calendar entry is time-defined and not capture-based. Both halves therefore half-apply, and they pull opposite ways:

- **The ordinary rule's HARM does not bite.** Its objection to year-first is that it “scatters related work across calendar folders”. For a calendar, scattering across calendar folders is the material's native shape, not damage done to it — a calendar *is* a set of calendar folders.
- **The exception's REASON fits and its CONDITION does not.** Time belongs first, it says, “because capture date is a defining aspect of the material”. A start time is exactly that for a calendar entry. But nothing is captured when someone books a meeting, and the design grants the exception to capture-based media, not to time-defined material in general.

Two entries here are `time_first: true` and twelve are false, and each side is argued from the sentence rather than from the label. `calendar.events` is true on the strength of the exception's reason, with the mismatch in its condition stated in the entry's open question rather than smoothed over. `comms.call-and-voicemail` is true on the exception's *stated terms* — a voicemail is capture-based media, filed by §2.9 in the same audio-and-video bullet as any other capture — and its strain is the opposite one, that a call-detail export in the same domain is a record and wants the ordinary rule. **My reading is that calendar-defined material is a third case the design does not cover**, and I have said so in `calendar.events`' open question rather than legislating it. The other twelve entries are ordinary record domains and §5.5's default applies to them without argument; `calendar.deadline-reminder` is the clearest of them, because a due date is the *content* of a reminder and not its address.

**2 — This slice's two natural anchors are a date and a person's name, and those are the two worst patterns in the corpus.** §3.10 says “Date extraction should be deliberately narrow”, and every file in the corpus carries timestamps as a universal file fact under §3.11. §3.8 says “It should avoid using authorship or creator identity as a destination dimension”, and this is the one slice where every file has a named human on it. The consequence is that recognition here is mostly refusal, and the refusals are load-bearing:

- **A bare date fires nowhere.** Every deterministic rule involving a date requires a phrase governing it — 'due by', 'has been rescheduled', 'your appointment' — which is §3.5's model applied literally: a candidate becomes a fact only “when the engine finds a course-code pattern together with academic context”. A date with no governing phrase is in `never_alone` on all seven scheduling entries.
- **A bare name fires nowhere**, in either direction. Not as a sender, not as an attendee, not as a rota cell, not as an `FN` property. `comms.contact-record` is built so that the one field a contacts domain obviously wants as a folder level is the one field it may never use.
- **Container properties are the only strong evidence this slice has.** `DTSTART` with `SUMMARY`, `Message-ID` with `References`, `BEGIN:VCARD` with `VERSION` and `FN`, `List-Id`, `METHOD:CANCEL`, `Auto-Submitted`. These are §3.13 `direct` because they are labelled slots in self-describing containers, and almost every `validated` field in this file is earned from one of them plus a context check. Where the container is gone — an email printed to PDF, a chat pasted into a document, an invitation designed as an image — the file falls to `needs_llm` or falls out.
- **Format is never a domain signal.** An audio container holds a voicemail, a voice memo, a lecture, a podcast and a music take; a JSON container holds a chat export and everything `soft.*` owns; a spreadsheet holds a rota, a timesheet, a call log, an availability poll and a guest list. §2.9's own instruction is the reason: “The engine should treat the file extension as a routing signal rather than an assumption about meaning”.

**3 — Almost every entry here defers to an older, more specific domain, and the deferrals are the point rather than an embarrassment.** This slice was authored to close a hole, and a hole-closing slice that competes with its neighbours makes the corpus worse. The deferrals, stated plainly: bookings of shared facilities go to `res.facility-booking` and hospitality reservations to `hosp.bookings`, both of which already list a calendar invitation among their own work types; a meeting's agenda, minute and actions stay with `ops.meeting-record`, which is a meeting *record* and not a calendar *entry* — the separator is that an entry with a `DTSTART` and no body is scheduling, while a document carrying attendance, decisions and assigned actions is the record; clinical rotas go to `med.practice-administration`, which already lists an on-call schedule and a rota first among its work types; matter deadlines go to `law.limitation-and-diary`, which already pairs a matter reference with a due date; subscription renewals go to `admin.subscriptions-recurring`; trip disruption goes to `pers.travel-record`; personal letters and messages stay with `pers.correspondence`. Where §3.15 makes a domain a safety domain — “Finance, identity, medical, and legal material should be implemented first as safety domains” — the deferral is a protection and not a tidiness preference, and it is cited as such.

**4 — Sensitivity is marked on what a file contains, and two entries are marked `none` on that basis.** Twelve entries are `potentially_sensitive`; `calendar.deadline-reminder` and `comms.mailing-list-newsletter` are not. The reasoning is the same in both: a bare due date and a published newsletter issue carry nothing §2.9 or §8.4 names, and the genuinely sensitive material that travels with them — a policy number, an account, a national identifier — belongs to the finance, identity and legal domains that already own it and already carry the marking. Marking those two would spread §2.9's phrase across the corpus's most common observation and dilute it where it matters. **The argument against this is real and is recorded in both entries' open questions**: what a *collection* of reminders discloses, and what a *list membership* discloses, are inferences no single file supports. Whether sensitivity is a property of a file or of a collection is one question asked twice, and it is Joseph's.

## Two dangling references this slice does not repoint

`res.facility-booking` cited `calendar.events` before it existed; authoring the domain under that id resolves it, and the checker's cross-file count drops from five problems to four. Two remain and both are edits to other authors' files:

- `06-healthcare-medicine.json` `med.practice-administration` cites `personal.calendar`. The domain it wants is `calendar.events`, or `calendar.appointment` if the intent was the clinical appointment rather than the practice diary. This slice did **not** author a second calendar domain under `personal.calendar` to satisfy it, because two calendar domains would be exactly the duplication the corpus already suffers from.
- `08-software-technology.json` `soft.helpdesk-ticket` cites `career.correspondence`. The domain it wants is `comms.email-thread`, which is written to receive it: that entry's collision row names `soft.helpdesk-ticket` and states the separator, which is that a ticket identifier and a support queue send the file to the software slice.

## Index

| id | name | provenance | sensitivity | time first |
|---|---|---|---|---|
| `calendar.events` | Calendar entries and events | design | sensitive | yes |
| `calendar.appointment` | Appointments with a counterparty | proposal | sensitive | no |
| `calendar.recurring-commitment` | Recurring commitments, rotas and timetables | inference | sensitive | no |
| `calendar.invitation-rsvp` | Invitations and responses | inference | sensitive | no |
| `calendar.availability` | Availability, free/busy and scheduling coordination | proposal | sensitive | no |
| `calendar.deadline-reminder` | Deadlines, due dates and reminders | proposal | none | no |
| `calendar.schedule-change` | Reschedules, cancellations and disruption notices | proposal | sensitive | no |
| `comms.email-thread` | Working email threads | design | sensitive | no |
| `comms.chat-export` | Chat and messaging archives | proposal | sensitive | no |
| `comms.call-and-voicemail` | Calls, voicemail and recordings | inference | sensitive | yes |
| `comms.notification-alert` | Automated notifications and alerts | proposal | sensitive | no |
| `comms.mailing-list-newsletter` | Subscribed mail: newsletters, lists and digests | proposal | none | no |
| `comms.contact-record` | Contact records and address books | design | sensitive | no |
| `comms.mailbox-archive` | Exported mailboxes and message stores | inference | sensitive | no |

---

## `calendar.events` — Calendar entries and events

A dated commitment as the calendar itself records it — a titled entry with a start, an end, a place, an organiser and invited attendees.

**Provenance:** **design** — a design sentence names this domain's fields

**Cite:** §2.9 names this domain's field list outright: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata”. That sentence is the whole schema below, and it is the only one in the design that describes calendar material. §3.15 is why the domain did not exist until now: “Other domains remain placeholders until user demand and corpus evidence justify detailed templates”. The corpus evidence is in this repository — `src/extractors/router.py` maps `ics` to source type `calendar`, `src/extractors/long_tail.py` carries `calendar` as one of the six long-tail families, and two catalogues already cite a calendar domain that no file defined.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `event title` | string | `Design review — autumn roadmap` | `direct` | §2.9 names it first: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata”. A VEVENT SUMMARY property is a labelled slot in a self-describing container, which is §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. |
| `event start` | datetime | `2026-09-03T09:00` | `direct` | §2.9 names “start and end time”. DTSTART is a labelled slot, so the ceiling is §3.13's direct. Note what this does NOT license: §3.10 “Date extraction should be deliberately narrow” still governs every date read from prose, and a start time is direct only when it comes from the container's own property. |
| `event end` | datetime | `2026-09-03T10:30` | `direct` | The other half of §2.9's “start and end time”. DTEND and DURATION are both labelled slots; where neither is present the field is absent rather than inferred, because §3.6 requires that “A model that cannot cite sufficient evidence must return unknown”. |
| `time zone` | string | `Europe/London` | `direct` | §2.9 does not name a time-zone field. It names “start and end time”, and a wall-clock time without its zone is not a time — the TZID parameter and the trailing Z of a UTC stamp are labelled slots the format supplies, so where the container carries one the ceiling is §3.13's direct, and where it does not the field is absent. This is an extension of §2.9's named field rather than a new claim, and it is recorded as its own field because §3.8 requires the product to “separate roles that happen to contain the same entity type” and a local time and an absolute instant are exactly that. |
| `location` | string | `Room 4.02, Kings Place` | `direct` | §2.9 names “location”. LOCATION is a labelled slot. It is metadata here and never a folder level: §5.7 requires that a template not “use an author or organization merely as a collector”, and a room or building name is a collector of exactly that kind. |
| `organiser role` | string | `self as organiser` | `validated` | §2.9 names “organizer”. The raw ORGANIZER value is an address, and §3.8 requires the modelling step this field performs: “The system must separate roles that happen to contain the same entity type” — whether the user convened the meeting or was summoned to it is the fact worth holding, not who the person is. Resolving the address against the user's own identities is a deterministic context check, which is §3.13's “A validated fact was found by a deterministic rule and passed contextual checks”. §3.8 also forbids the obvious misuse: “It should avoid using authorship or creator identity as a destination dimension”. |
| `attendee role` | string | `required attendee` | `direct` | §2.9 names “attendees”. ROLE and PARTSTAT are the format's own labelled parameters on each ATTENDEE line, so the ROLE is direct even though the identity behind it is address-book material §2.9 says should “normally be privacy-protected rather than used to create folder proposals”. The role is kept; the address is held as sensitive and never becomes a dimension. |
| `recurrence` | string | `weekly on Tuesday until 2026-12-15` | `direct` | §2.9 names “recurrence metadata”. RRULE, RDATE and EXDATE are labelled slots. The rule is meaningless without the entry it hangs from, which is why it appears here and is the seed for `calendar.recurring-commitment` rather than a domain of its own. |
| `calendar` | string | `Work` | `direct` | The named calendar a set of entries belongs to. §2.9 does not name it; the container does, as X-WR-CALNAME or as the export's own filename. Recorded because it is the only NON-time dimension a bare `.ics` reliably supplies, which makes it the alternative top level the open question below hands to Joseph. |
| `event kind` | string | `meeting` | `llm_supported` | Whether a titled block is a meeting, a personal appointment, a travel segment, a birthday marker or a held slot. Nothing in the container says so — the same VEVENT shape carries all of them — so this is §3.5's case: “The LLM creates LLM-supported facts only when a file requires language interpretation that rules cannot resolve safely”, bounded by §3.5's limit that “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file”. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a `BEGIN:VCALENDAR` line together with at least one `BEGIN:VEVENT` block carrying a `DTSTART` property — the container declares itself and the block corroborates it, which is the pattern-plus-context shape §3.5 requires when it says a candidate becomes a fact only “when the engine finds a course-code pattern together with academic context”
- a `DTSTART` property co-occurring with a `SUMMARY` property inside one `VEVENT` block — the start alone is a bare date and §3.10 refuses those; the titled pair is the event
- an `RRULE`, `RDATE` or `EXDATE` property inside a `VEVENT` that already carries `DTSTART` and `SUMMARY` — recurrence is readable only once the series' first instance is established
- a `.ics` extension whose content sniff confirms a `VCALENDAR` container — `src/extractors/router.py` already maps `ics` to source type `calendar`, and the sniff is the context check that keeps a mislabelled file out of the domain
- a mail header block carrying a calendar part with `METHOD:REQUEST` together with an `ATTENDEE` property — an emailed meeting invitation, one file that is simultaneously an email and an event
- a `VEVENT` whose `DTSTART` and `DTEND` are both date-valued rather than date-time-valued, together with a `SUMMARY` — the format's own whole-day marker, distinguished by the value type and not by the absence of a time

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- deciding whether a titled block is a working meeting, a personal appointment, a travel segment or a held slot, where the title is a bare noun such as 'Review', 'Dentist' or 'Block'
- an exported day plan or agenda written as prose or a table in a document, with no calendar container anywhere in the file
- reading whether a recurring series is a live commitment or the residue of a job or a class the user has left, which the container cannot say and the last-modified date does not settle
- separating one person's calendar from a shared or subscribed one where the export carries no ownership marker

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a bare date or date-time anywhere in a file — §3.10 “Date extraction should be deliberately narrow”, and every file in the corpus carries timestamps as a universal file fact
- a bare person name in a `From`, `To`, `ORGANIZER` or `ATTENDEE` position — §3.8 “It should avoid using authorship or creator identity as a destination dimension”
- a bare weekday or month name in a filename
- a bare room, building, city or address string — a location appears in letterheads, invoices, itineraries and photographs alike
- the words 'meeting', 'event', 'invite', 'schedule' or 'calendar' in a filename
- a `.ics` extension on its own, with no `VCALENDAR` container confirmed by content
- a time-shaped token such as '09:00' — it appears in logs, transcripts, rotas, timesheets and run sheets across at least six other slices

### Work types

`calendar export (.ics)`, `single event file`, `meeting invitation carried by mail`, `recurring series definition`, `whole-day entry`, `subscribed calendar feed snapshot`, `exported or printed day plan`, `shared or team calendar export`

### Grouping reasons (§4)

- one named calendar across the file or files one export produced
- one recurring series across its instances, exceptions and cancellations, joined by the container's own `UID`
- one event across the invitation, the replies and the attachments that cite the same `UID`
- one working period across the entries whose start times fall inside it

### Template (§5)

`year → calendar → event`

Time first: **yes**

§5.5 offers two cases and this domain is neither of them, so the order is argued from the reasons rather than assumed from the labels. §5.5's ordinary rule is “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — and the named harm does not bite, because a calendar IS calendar folders and the scattering is the material's native shape rather than damage done to it. §5.5's exception is “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” — and its REASON fits exactly, since a start time is what makes a calendar entry the entry it is, while its STATED CONDITION does not, because nothing is captured when someone books a meeting. `time_first` is recorded true on the strength of the reason, with the mismatch stated rather than hidden, and the open question below hands the call to Joseph. `calendar` sits second rather than first because §5.7 warns against a template that would “create meaningless one-child levels”, and most corpora hold exactly one calendar.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `ops.meeting-record` | a meeting RECORD is what a meeting produced — an agenda, a minute, an action log; a calendar entry is the reservation of the time before anything was produced. `ops.meeting-record` already lists a calendar invitation among its work types, so one invitation file satisfies both schemas at once. The separator is what the file contains, not what it is about: an entry with a `DTSTART` and no body is scheduling; a document carrying attendance, decisions and assigned actions is the record | §4.8 requires the validator to confirm “that each fact or label belongs to an allowed domain schema” — which it cannot arbitrate when the facts belong to two allowed schemas, so the pair is written down here rather than left latent |
| `res.facility-booking` | a facility booking is a calendar entry with a facility, an instrument and a charge code attached. Where those are present the research slice is the more specific home and this domain defers. `res.facility-booking` already lists a calendar invite among its work types and already cited this domain by name before it existed | §3.11 “It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible” — the facility and charge-code facts are what make the more specific schema plausible |
| `hosp.bookings` | the venue's reservation record, held on the provider's side with a party size, a channel and a booking reference; a calendar entry is the guest's own dated block with none of those. `hosp.bookings` also lists a calendar invitation among its work types, so the discriminating facts are the provider-side ones and their absence is what keeps a file here | §3.8 “The system must separate roles that happen to contain the same entity type” — the venue and the guest hold the same booking from opposite sides |
| `pers.travel-record` | a flight or hotel confirmation is a trip record even when it arrives as an `.ics` attachment, because the trip is the organising reason and `pers.travel-record` already models it that way. Where a booking reference resolves to a known trip, that domain wins | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” — the entry's topic is a time; its purpose is the trip |
| `calendar.appointment` | an appointment is a time reserved with a named counterparty and is usually delivered as a letter, a confirmation or a portal page rather than as a container; a calendar entry is the container. A file that is both — an `.ics` attached to a confirmation — carries both schemas and neither absorbs the other | §3.12 “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically” |

### Sensitivity

`potentially_sensitive` — §2.9 attaches its sensitivity phrase to Email and to Contacts, not to Calendar, so this marking is an inference and is written as one. The inference is short: a VEVENT's ATTENDEE lines hold email addresses, and §2.9 says of exactly those values that the engine should be “treating addresses and message content as potentially sensitive”; §8.4 names “private correspondence” among what the corpus can include, and an attendee list read across a year is a social graph. §2.9's phrase is the whole claim made here. No handling class is assigned — that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> §5.5 offers two cases and a calendar entry is neither, so `time_first` above is a reasoned guess and not a reading. Its ordinary rule names a harm — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — that does not bite here, because a calendar is calendar folders by nature. Its exception gives the right reason — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” — but grants it only to capture-based media, and nothing is captured when someone books a meeting. Three things follow that only Joseph can settle: whether calendar-defined material is a third case the design does not cover; whether the top level should be the year or the named calendar ('Work', 'Personal', 'Family'); and whether a calendar belongs in the destination tree at all, given that most people keep an `.ics` only as a backup. §5.3 hands the equivalent photograph question to the user — “then decide whether photographs should branch by year, event, location, or remain mostly flat” — and this one is not more decidable than that one.

---

## `calendar.appointment` — Appointments with a counterparty

A time reserved with a named other party — the confirmation, the reminder and the letter that fix it.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names appointments. §7.3's residual library is the nearest thing the design has, and it is a residual destination rather than a domain: “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents”. That sentence is the design saying where a confirmation goes when NO domain claims it, which is an argument for authoring one. §5.7 is what permits the addition: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `counterparty` | string | `Whitfield Dental Practice` | `validated` | The organisation the time is reserved with. §3.8 is what makes this legitimate where an author field would not be: “Authorship is usually metadata”, and the counterparty is the document's target rather than its writer. Reading a letterhead or a `From` organisation and confirming it against an appointment phrase in the same document is a context check, which is §3.13's “A validated fact was found by a deterministic rule and passed contextual checks”. |
| `appointment purpose` | string | `six-month check-up` | `llm_supported` | §3.9 “Purpose must be a first-class facet” and “Topic answers what a file is about, while purpose answers what the file was for”. A confirmation rarely labels its own purpose in a parseable slot, so the ceiling is the model route under §3.6's validation, and the field stays unset where the model cannot cite. |
| `appointment date` | datetime | `2026-09-17T14:20` | `validated` | §3.10 governs this field completely: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching”. The date is `validated` and not `direct` because a letter has no labelled date slot — it earns the ceiling only from the appointment phrase governing it, which is exactly what the first deterministic rule below requires. |
| `appointment reference` | string | `APT-4471-C` | `direct` | An explicit reference label followed by its identifier is §3.13's “labeled form field”. It is the strongest evidence this domain has and the only fact that reliably joins a confirmation to its reminder and its outcome. |
| `appointment status` | string | `confirmed` | `validated` | Confirmed, rescheduled, attended, missed or cancelled. A status vocabulary appearing beside an appointment reference passes a context check; a status word on its own does not, which is why 'cancelled' sits in `never_alone` on `calendar.schedule-change` rather than here. |
| `attendee role` | string | `patient` | `llm_supported` | Whose appointment it is — the user's own, a dependant's, a client's. §3.8 requires it: “The system must separate roles that happen to contain the same entity type”, and a parent's corpus holds their own and their child's appointment letters in identical shapes. Nothing deterministic separates them, so the ceiling is the model route. |
| `location` | string | `Level 2, Whitfield House` | `direct` | Where to turn up. Metadata only, never a folder level — §5.7 requires that a template not “use an author or organization merely as a collector”. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a low-frequency appointment phrase — 'your appointment', 'appointment confirmation', 'appointment reminder', 'we look forward to seeing you on' — governing an explicit date-time pattern in the same sentence. §3.10's narrow-date rule supplies the date half and the phrase supplies the context half
- an explicit reference label — 'appointment ref', 'booking reference', 'confirmation number' — immediately followed by an identifier token, in a document that also carries a date-time pattern
- a confirmation phrase co-occurring with a named organisation in a letterhead or `From` position and a date-time in the body — §3.7 “It should use positional weighting because a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference”
- a `VEVENT` whose `SUMMARY` carries an appointment phrase and whose `ORGANIZER` resolves to an organisation rather than to the user's own identities
- an arrival instruction ('please arrive', 'bring the following', 'check in at') co-occurring with a date-time and a named organisation

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- what the appointment is for, where the confirmation names only a service code or a practitioner
- whose appointment it is in a household corpus that holds several people's letters in the same template
- separating a first appointment from a follow-up in a run of near-identical letters from one provider
- deciding whether a booked slot is an appointment or a hospitality reservation where the counterparty is a business that does both

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a bare date — §3.10 “Date extraction should be deliberately narrow”
- the word 'appointment' — it names a job appointment, a board appointment, a consular appointment and an appointment of trustees in four other slices
- a clinic, salon, garage or surgery name on its own — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”, and the same reading problem holds for any organisation name
- a bare reference-shaped token
- a time of day
- the phrase 'we look forward to' with no date beside it

### Work types

`appointment confirmation`, `appointment letter`, `appointment reminder`, `check-in or arrival instruction`, `pre-appointment form or preparation instruction`, `calendar attachment issued with the appointment`, `outcome or discharge summary naming the appointment`, `missed-appointment notice`

### Grouping reasons (§4)

- one appointment across its confirmation, its reminder and its outcome, joined by an appointment reference
- one counterparty across a run of appointments held with them
- one referral or course of treatment across every appointment it generated
- one dependant across the appointments held on their behalf

### Template (§5)

`counterparty → appointment purpose → year`

Time first: **no**

§5.5's ordinary record rule applies without strain here, unlike on `calendar.events`: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A dentist's reminder filed under the month it arrived is separated from the dentist, and the counterparty is what makes the date legible at all — §5.5 “a parent dimension should provide the context required to understand the child”. The year is last and optional; where a counterparty is seen once, §5.7's warning against templates that “create meaningless one-child levels” collapses it.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `med.referral-received` | a hospital or clinic appointment letter is the visible half of a referral, and the medicine slice already models the referral as the organising reason. Where a referral reference, a specialty or a clinician is named, that domain is the more specific home and this one defers; what stays here is the appointment with a non-clinical counterparty | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” — routing clinical appointments into a general scheduling branch would defeat that ordering |
| `hosp.bookings` | the same reserved slot seen from the business's side, with a party size and a channel. A restaurant's own reservation record is `hosp.bookings`; the diner's confirmation email is an appointment-shaped file with none of the provider-side facts | §3.8 “The system must separate roles that happen to contain the same entity type” |
| `pers.household-admin` | a boiler service visit, a meter reading appointment or a delivery slot is household administration with a time attached, and `pers.household-admin` is the older and broader home. The separator is whether the file's subject is the reserved time or the household matter it serves | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `calendar.events` | an appointment delivered as an `.ics` attachment is both. The container's facts belong to `calendar.events`; the letter's counterparty, reference and purpose belong here. Neither absorbs the other and the file carries both | §4.9 “A file may validly belong to more than one accepted group” |

### Sensitivity

`potentially_sensitive` — An appointment discloses who someone is dealing with and when, which is often more revealing than the appointment's own content. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” among what the corpus can include, and a clinic, solicitor, lender or clinic-adjacent counterparty is the schedule-shaped face of four of those. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Two things are unresolved. First, whether clinical appointments belong here at all or route wholesale to the medicine slice — `med.practice-administration` already cites a domain it calls `personal.calendar`, which no catalogue defines and which this slice has NOT authored under that id, so that dangling reference needs repointing to `calendar.events` or to this entry by whoever owns file 06. Second, whether an appointment with a counterparty is a scheduling record at all, or whether every appointment should simply live inside whatever domain owns the relationship — the dentist under health, the solicitor under legal, the viewing under property — leaving this domain to hold only the residue. §5.3's branch-by-branch process is where that gets decided: “This branch-by-branch design reflects the real way people organize files”.

---

## `calendar.recurring-commitment` — Recurring commitments, rotas and timetables

A commitment that repeats — the rota, timetable or standing series that says who is on, and when, week after week.

**Provenance:** **inference** — extends a family the design names

**Cite:** Extends a field the design names rather than a domain it names. §2.9's calendar bullet ends with “recurrence metadata”, and a rota, a timetable and a standing series are what that metadata describes once it is published as a document instead of carried as an RRULE. §5.7 permits the extension: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `commitment` | string | `Tuesday orchestra rehearsal` | `llm_supported` | What repeats. A `SUMMARY` supplies it directly where the material is a container, but a published rota names shifts and people and never names the commitment itself, so the honest ceiling across the domain is the model route under §3.6's validation. §3.6 also bounds what happens when the model cannot cite: “A model output that is useful but too weak to establish a fact may remain a possible clue for review; it must not quietly become a folder proposal or an asserted file property”. |
| `recurrence` | string | `weekly, term-time only` | `direct` | §2.9 names “recurrence metadata” as a field calendar formats should yield, and RRULE is a labelled slot — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. Where the material is a spreadsheet rota rather than a container the field falls to `validated` on the weekday-sequence rule below, and where neither holds it is absent. |
| `effective period` | string | `autumn term 2026` | `validated` | The stretch a published rota covers. §3.10 is the constraint and the warning: “Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing” — a term, a quarter, a roster cycle and a school half-term each need their own pattern, and a bare year token is refused below. |
| `participant role` | string | `on-call second` | `validated` | The slot a person occupies, not the person. §3.8 is the whole reason the field is shaped this way: “The system must separate roles that happen to contain the same entity type” and “It should avoid using authorship or creator identity as a destination dimension”. A role vocabulary appearing as a column header beside a weekday sequence passes a context check; a name in a cell does not. |
| `slot` | string | `Tuesday 19:00-21:00` | `validated` | The repeating position within the cycle. Earned from the weekday-plus-time pairing below, never from a time token on its own — §3.10 “Date extraction should be deliberately narrow”. |
| `issuing body` | string | `Whitfield Sinfonia` | `validated` | Who publishes the rota. Held as a joining fact rather than a folder level; §3.8 “A folder should not become a collection point for everything produced by the same person or organization”. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an `RRULE` property inside a `VEVENT` that already carries `DTSTART` and `SUMMARY` — §2.9 names “recurrence metadata” and RRULE is its explicit slot; the entry is the corroborating context the rule alone lacks
- a spreadsheet whose column headers form a weekday sequence together with a name-, role- or shift-bearing column — §2.9 says spreadsheets should yield “sheet names, column headers, visible cell values, table-like regions”, and it is the pairing of the two header kinds, not either alone, that identifies a rota
- a low-frequency rota word — 'rota', 'roster', 'shift pattern', 'on-call schedule', 'duty schedule', 'timetable' — co-occurring with a weekday sequence in the same document
- a repeating time-of-day value appearing against every row of a weekday-headed table, together with an effective-period label in a title position — §3.7 “It should use positional weighting because a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference”
- a cover or swap phrase ('covering for', 'swap request', 'shift exchange') co-occurring with a named slot and a date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- reading whether a repeating block is a live commitment, a placeholder or an abandoned series
- a timetable published as an image or a scanned wall chart, where OCR yields a grid with no headers the rules can key on
- separating one person's own commitments from a whole team's rota published in the same grid
- deciding whether an academic timetable belongs to the course or to the person's week, which is the collision recorded below and is a judgement about the corpus rather than about the file

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a weekday name
- a bare time of day
- the word 'schedule' — a project schedule, a payment schedule, a schedule to a contract, a depreciation schedule and a maintenance schedule are five other domains' material
- a grid or table shape on its own — §2.9 says every spreadsheet should yield “table-like regions”, so the shape is universal and carries no domain information
- a bare person name in a cell — §3.8 “It should avoid using authorship or creator identity as a destination dimension”
- a bare year token — §3.10 warns that documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”

### Work types

`rota or roster`, `shift pattern`, `class or lecture timetable`, `on-call or duty schedule`, `recurring series definition`, `cover request or shift swap`, `training, rehearsal or fixture schedule`, `standing-order or recurring-payment schedule`

### Grouping reasons (§4)

- one commitment across the successive periods it was published for
- one issuing body across its run of rotas
- one recurring series across its exceptions, cancellations and covers
- one effective period across every rota published for it

### Template (§5)

`commitment → effective period`

Time first: **no**

§5.5's ordinary rule states this case almost literally: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A rota's whole value is the run — this term's beside last term's — and a period-first order guarantees the run is broken. The commitment is also what makes a given week's grid readable at all, which is §5.5's other half: “a parent dimension should provide the context required to understand the child”. This entry is deliberately the mirror of `calendar.events`: the same slice reaches opposite conclusions because the material differs, not because the rule does.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `med.practice-administration` | an on-call schedule and a rota are already the first two work types of `med.practice-administration`, so a clinical rota belongs there and this domain defers wherever a practice, a service line or a clinician is named. What stays here is the rota with no clinical counterparty — the volunteer rota, the rehearsal schedule, the parish roster | §3.11 “It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible” |
| `trade.timesheet` | a timesheet records hours WORKED and a rota assigns hours to be worked; the two look identical as grids and are opposite in tense. The separator is whether the cells are commitments or claims — a signature, a total, or a pay reference makes it a timesheet | §3.8 “The system must separate roles that happen to contain the same entity type” |
| `acad.course-enrollment` | a lecture timetable is course material by every fact it carries — school, term, course code — and the education slice already owns those. Where a course-code pattern validates under §3.5's context test the academic domain wins outright | §3.5 a candidate becomes “a course fact only when the engine finds a course-code pattern together with academic context” |
| `calendar.events` | a recurring series held inside an `.ics` is a `calendar.events` entry carrying an `RRULE`; this domain begins where the series has been PUBLISHED as a document that no longer carries the container. A file that is both is both | §4.9 “A file may validly belong to more than one accepted group” |

### Sensitivity

`potentially_sensitive` — A rota names individuals against times and, read across a run, discloses a person's working pattern, their absences and their seniority. §8.4 names “employment materials” among what the corpus can include, and a published rota is employment material about several people at once rather than about the corpus owner alone. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Is a rota scheduling material or employment material? The facts point both ways — it is time-shaped like this slice and people-shaped like `hr.workforce-analytics` — and the answer decides whether it appears in a Calendar branch, a Work branch, or under whichever organisation issued it. The sharper version of the question is one this catalogue cannot answer at all: a rota the user RECEIVES and a rota the user PUBLISHES are the same document seen from opposite sides, and §3.8's role separation makes that expressible without making it readable. §5.1 leaves the branch itself open — the labels should be drawn “rather than a universal corporate taxonomy”.

---

## `calendar.invitation-rsvp` — Invitations and responses

The asking and the answering — an invitation issued for a dated occasion, and the acceptances, declines and tentatives it collected.

**Provenance:** **inference** — extends a family the design names

**Cite:** Extends the two slots §2.9 names rather than a domain the design names. §2.9's calendar bullet yields “event title, start and end time, location, organizer, attendees, and recurrence metadata”, and an invitation with its replies is the transaction BETWEEN the organiser and the attendees those two slots hold. §5.7 permits the extension: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `occasion` | string | `Rowan and Priya's wedding` | `validated` | What is being invited to. Earned from an invitation phrase governing a titled occasion in a title position — §3.7 “It should use positional weighting because a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference”. Where the occasion is unnamed the field is absent and the file falls to `needs_llm`. |
| `occasion date` | datetime | `2026-06-20T13:00` | `validated` | §3.10 governs it: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching”. Kept distinct from the response date below because §3.8 requires it: “The system must separate roles that happen to contain the same entity type” — an invitation carries two dates that mean opposite things. |
| `record type` | string | `reply` | `validated` | Invitation, reply, response list or reminder. `METHOD:REQUEST` and `METHOD:REPLY` are labelled slots where a container exists; a document earns the field from the invitation or RSVP vocabulary below. This is the field the template branches on, because it is the only one that distinguishes files that otherwise share every fact. |
| `response` | string | `accepted` | `direct` | A `PARTSTAT` parameter on an `ATTENDEE` line is the format's own labelled answer — §3.13's “labeled form field”. In a response list it falls to `validated`, earned from an accept/decline vocabulary filling a column whose header is a name column. |
| `response deadline` | date | `2026-05-01` | `validated` | The by-when of an RSVP, earned only from an explicit respond-by phrase governing a date. §3.10 “Date extraction should be deliberately narrow” refuses it otherwise, and a bare second date on an invitation is exactly the over-firing case. |
| `invitation role` | string | `invited guest` | `llm_supported` | Whether the corpus owner is the host or the invited. §3.8 makes the distinction mandatory — “The system must separate roles that happen to contain the same entity type” — and nothing in an invitation states it, because both sides keep the identical file. The model route is the honest ceiling and the field stays unset where it cannot cite. |
| `host` | string | `Whitfield Sinfonia` | `validated` | Who is inviting. Metadata only. §3.8 “A folder should not become a collection point for everything produced by the same person or organization”, so this never becomes a level. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a `METHOD:REQUEST` or `METHOD:REPLY` property inside a `VCALENDAR` container together with an `ATTENDEE` property carrying a `PARTSTAT` value — the format's own invitation and reply verbs, corroborated by the slot that answers them
- an explicit RSVP token — 'RSVP', 'please respond by', 'regrets only', 'let us know by' — co-occurring with an explicit date pattern in the same document
- an invitation phrase — 'you are invited', 'invitation to', 'save the date', 'requests the pleasure' — co-occurring with a date-time and a venue string
- an accept/decline vocabulary ('accepted', 'declined', 'tentative', 'attending', 'not attending') filling the values of a column whose header column holds names or addresses, in a table that also carries an occasion title — §2.9 says spreadsheets should yield “sheet names, column headers, visible cell values, table-like regions”
- an `RSVP=TRUE` parameter on an `ATTENDEE` line inside a `VEVENT` that already carries `DTSTART` and `SUMMARY`

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- whether the corpus owner hosted the occasion or was invited to it, which both sides' files state identically
- an invitation designed as an image or a card, where OCR yields ornamental text with no parseable slots
- separating a social invitation from a commercial one addressed in social language
- reading a reply written as prose — 'we would love to, but we are away that weekend' — into an accept or a decline

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- the word 'invitation' — an invitation to tender, an invitation to interview and an invitation to a party belong to three different slices, and `ops.sourcing-rfp` and `career.interview-cycle` own two of them
- a bare guest or invitee name — §3.8 “It should avoid using authorship or creator identity as a destination dimension”
- a bare 'yes' or 'no' cell
- a bare date — §3.10 “Date extraction should be deliberately narrow”
- a venue name on its own
- an ornamental or card-shaped layout

### Work types

`invitation`, `save-the-date`, `meeting request`, `RSVP reply`, `guest or attendance response list`, `seating or table plan`, `declination or regrets note`, `reminder to respond`

### Grouping reasons (§4)

- one occasion across the invitation and every reply to it, joined by the container's `UID` where one exists
- one invitee across the occasions they were invited to
- one invitation across its issue, its reminder and its final response list
- one host across the occasions they convened

### Template (§5)

`occasion → record type`

Time first: **no**

§5.5 “a parent dimension should provide the context required to understand the child” is the whole argument: a reply says 'accepted' and nothing else, and it is meaningless anywhere except beneath what it answers. Filing a reply by its own send date is the arrangement that guarantees it lands nowhere near the invitation, which is §5.5's ordinary harm — “putting year first scatters related work across calendar folders” — at the scale of a single occasion. `record type` is second because it is the only fact that separates files sharing every other one.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `event.production` | a guest list is already a work type of `event.production`, and where a brief, a budget, a run sheet or a supplier appears the file is production material rather than an invitation record. The separator is which side of the occasion the corpus sits on — the producer holds the plan, the invitee holds the card | §3.8 “The system must separate roles that happen to contain the same entity type” |
| `pers.gift-occasion` | a wedding, a christening or a milestone birthday is a personal occasion the household slice already owns, and its invitation is one artifact of it. Where the occasion is a named personal event this domain holds only the RSVP mechanics and defers the occasion itself | §3.9 “Purpose must be a first-class facet” |
| `ops.meeting-record` | a meeting request and its accept/decline replies are invitation-shaped, and `ops.meeting-record` already lists a calendar invitation among its work types. Where the file also carries an agenda, attendance and decisions it is the meeting's record and belongs there | §4.8 the validator must confirm “that each fact or label belongs to an allowed domain schema”, which cannot arbitrate a file whose facts belong to two |
| `calendar.events` | an invitation IS a `VEVENT` plus a `METHOD`. The container's facts belong to `calendar.events`; the transaction — who was asked, who answered, by when — belongs here, and a single `.ics` invitation carries both | §4.9 “A file may validly belong to more than one accepted group” |

### Sensitivity

`potentially_sensitive` — A guest list is a list of named people with addresses, and §2.9 says of exactly that material that it should “normally be privacy-protected rather than used to create folder proposals”. A reply additionally discloses one person's whereabouts on one date, and the reasons given in declines are frequently medical or financial. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Should an invitation live in a scheduling branch at all, or beneath whatever domain owns the occasion — the wedding under the household slice, the conference under research, the interview under career? The design's own instinct is the second: §5.3 has the user “decide whether application files should branch first by target institution, admissions cycle, document type, or a purpose-defined packet”, and a purpose-defined packet is exactly what an occasion is. This catalogue has authored the domain because the RSVP mechanics are real and recur, and records that the placement question is Joseph's.

---

## `calendar.availability` — Availability, free/busy and scheduling coordination

The negotiation before the entry exists — published free/busy, scheduling-link pages, poll results, and the exchange that converged on a time.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names availability sharing. §2.9's calendar bullet names the settled entry's slots — “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata” — and free/busy is what precedes those, not one of them. §5.7 is what permits the addition: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `scheduling subject` | string | `kick-off with Aldermore` | `llm_supported` | What is being scheduled. Almost never stated in a slot — a free/busy publication carries no subject at all by design — so the model route is the honest ceiling, bounded by §3.6: “A model that cannot cite sufficient evidence must return unknown”. |
| `counterparty` | string | `Aldermore Bank` | `validated` | Who the time is being found with. §3.8 permits it where an author field would not be permitted: “Authorship is usually metadata”, and the counterparty is the target of the coordination. Earned from an address domain or a named organisation corroborated by a scheduling phrase in the same document. |
| `proposed slots` | string | `Tue 10:00, Wed 14:00, Thu 09:30` | `validated` | The candidate times. Earned only from a run of date-time candidates governed by a scheduling phrase — a single date-time is refused, because §3.10 “Date extraction should be deliberately narrow” and one date in a document is the corpus's most common observation. |
| `availability window` | string | `week of 2026-09-07` | `validated` | The stretch the publication covers. A `VFREEBUSY` component carries `DTSTART` and `DTEND` as labelled slots; a document earns the field from an explicit window phrase. §3.10 governs the parsing. |
| `time zone` | string | `America/New_York` | `direct` | The zone the proposal is stated in. A TZID parameter is a labelled slot — §3.13's “labeled form field”. It is recorded here rather than left implicit because a zone appearing beside every proposed time is the tell that the coordination crossed zones, which is the deterministic rule below, and because a proposal read in the wrong zone is a wrong fact rather than a missing one. |
| `coordination outcome` | string | `agreed` | `llm_supported` | Whether the negotiation settled, lapsed or was abandoned. Nothing states it; the settled case is usually visible only as a later `calendar.events` entry, which is a corpus-level inference and not a file-level fact. §3.6's “possible clue for review” is the right destination for a weak reading here. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a `FREEBUSY` property inside a `VFREEBUSY` component in a `VCALENDAR` container — the format's own availability object, which is not a `VEVENT` and must not be read as one
- a `METHOD:REQUEST` calendar part whose component is `VFREEBUSY` rather than `VEVENT` — a request for availability rather than for attendance
- a scheduling-service phrase — 'book a time with', 'schedule a meeting', 'pick a time that works', 'here is my availability' — co-occurring with a run of distinct date-time candidates in one document
- a poll export whose column headers are date-time values and whose cells carry an availability vocabulary ('yes', 'no', 'if need be') — §2.9 says spreadsheets should yield “sheet names, column headers, visible cell values, table-like regions”, and it is date-valued HEADERS that make this a poll rather than a table
- a time-zone identifier appearing beside each member of a run of proposed times — the repetition is the context check a single zone token cannot supply
- an absence phrase ('out of office', 'on annual leave', 'away from', 'back on') governing a date range in the same sentence

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- reading a proposal buried in a message thread whose subject is something else entirely
- deciding whether a run of times is a proposal, an itinerary, a rota or a set of opening hours
- whether a coordination succeeded, where the only evidence is the absence of further messages
- separating the user's own availability from a colleague's forwarded into the same corpus

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a bare list of dates — §3.10 “Date extraction should be deliberately narrow”, and a list of dates is a rota, an itinerary, a fixture list and a payment schedule as readily as a proposal
- a bare time-zone identifier — every calendar container carries one
- the word 'available' or 'availability' — a stock availability report, a rental availability calendar and a system availability metric belong to three other slices
- a scheduling-service URL on its own
- a bare counterparty name
- an out-of-office string with no date range governed by it

### Work types

`free/busy publication`, `scheduling-link page capture`, `availability poll or its result export`, `proposed-times message`, `coordination exchange`, `out-of-office or absence notice`, `opening-hours or bookable-window statement`, `time-zone comparison sheet`

### Grouping reasons (§4)

- one scheduling attempt across its proposal, its poll and the confirmation that ended it
- one counterparty across repeated coordination with them
- one absence period across every notice that announces it
- one poll across its invitation and its result export

### Template (§5)

`counterparty → scheduling subject`

Time first: **no**

§5.5 “a parent dimension should provide the context required to understand the child” decides this: a bare run of times means nothing until you know what was being scheduled and with whom, and the counterparty is the fact this domain can actually validate while the subject usually needs the model. Time is not offered as a level at all — a negotiation that straddles a month boundary would be split by §5.5's named harm, “putting year first scatters related work across calendar folders”, and the material is short-lived enough that a year level would be §5.7's “meaningless one-child levels” in most corpora.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `calendar.events` | a successful coordination ENDS in a calendar entry, and the confirmation message carries both the proposal it settles and the entry it creates. The separator is tense: candidate times that were never fixed belong here, a fixed `DTSTART` belongs there | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `comms.email-thread` | most coordination lives inside a thread and has no artifact of its own. The separator is whether the file's SUBJECT is the time — a thread whose reply chain happens to contain three proposed slots is a thread, not an availability record | §3.6 “A model output that is useful but too weak to establish a fact may remain a possible clue for review; it must not quietly become a folder proposal or an asserted file property” |
| `calendar.schedule-change` | a reschedule negotiation is coordination about a commitment that already exists. Where a prior fixed time is named, the change domain is the more specific home; where no commitment exists yet, this one is | §4.8 the validator must confirm “that the model has not invented a date, project, purpose, or membership that the dossier does not support” |
| `hr.interview-panel` | finding a slot for an interview panel is the commonest scheduling coordination in a working corpus, and it carries a requisition or candidate reference that the HR slice already owns. Where such a reference resolves, that domain wins and this one holds nothing; the candidate's own side of the same exchange belongs to `career.interview-cycle` | §3.11 “It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible” |

### Sensitivity

`potentially_sensitive` — A free/busy publication discloses a person's entire working pattern without disclosing a single event title, and an absence notice states that a home is empty between two dates. The files themselves arrive by mail carrying addresses, which §2.9 says to treat as “potentially sensitive”, and §8.4 names “private correspondence” among what the corpus can include. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Is this material worth keeping at all? A settled negotiation is superseded by the entry it produced, and an unsettled one is noise — which makes the honest destination §7.3's residual library rather than a domain: “Review Later may hold files whose meaning is partly understood but whose final location requires a future decision”. This catalogue has authored the domain because the schema is needed to RECOGNISE the material (an availability poll misread as a rota or an itinerary is a real misfiling), while taking no position on whether the tree should ever show it. §7.3's lifecycle rule is the relevant constraint on whatever Joseph decides, and it is a constraint against deletion rather than for retention.

---

## `calendar.deadline-reminder` — Deadlines, due dates and reminders

A date something must happen by, and the notice that says so — due dates, renewal warnings, key-date schedules and reminder exports.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** The design's only sentence about reminders puts them in the RESIDUAL library, which is the design saying that a reminder with no home is residue: §7.3 “Temporary Screenshots may live under Photos/Temporary Screenshots and hold screenshots that appear time-sensitive or remind the user of something but have no accepted project, trip, application, or event relationship”. That is an argument for a domain rather than against one — the residual template exists precisely because the material recurs and nothing claims it. §5.7 permits the addition: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `obligation` | string | `passport renewal` | `llm_supported` | What must be done. A notice states the consequence and the date and very often leaves the obligation implicit, so the model route is the honest ceiling; §3.6 bounds it — “A model that cannot cite sufficient evidence must return unknown”. Where the notice names a policy, an account or a matter reference the obligation is carried by that reference instead, and the more specific domain named in the collisions below owns it. |
| `due date` | date | `2026-11-30` | `validated` | The defining field, and the one §3.10 constrains hardest: “Date extraction should be deliberately narrow”, and “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”. It is `validated` and never `direct` outside a `VTODO` container, because a due date in prose earns its meaning only from the deadline phrase governing it. |
| `notice type` | string | `final reminder` | `validated` | First notice, reminder, final notice, expiry warning. A notice vocabulary in a title position passes a context check — §3.7 “It should use positional weighting because a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference”. This is the field that orders a run of otherwise identical letters. |
| `issuing party` | string | `HM Passport Office` | `validated` | Who is imposing the date. Earned from a letterhead or `From` organisation corroborated by the deadline phrase. Held as a joining fact and offered as a template level only beneath the obligation, because §3.8 warns that “A folder should not become a collection point for everything produced by the same person or organization”. |
| `consequence` | string | `cover lapses` | `llm_supported` | What happens if the date passes. This is the fact that makes a deadline worth surfacing at all, and it is always prose. §3.9's distinction is the reason it is a field rather than a note: “Topic answers what a file is about, while purpose answers what the file was for”. |
| `obligation status` | string | `outstanding` | `user_confirmed` | Whether the thing was done. No file states it — the discharging document is a different file, often in a different domain, and matching them is a corpus-level inference. §3.13's “A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user” is the only honest ceiling, and the field is recorded so the validator legitimises a user-entered value and refuses a model-proposed one. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a deadline phrase — 'due by', 'must be received by', 'expires on', 'last day to', 'no later than' — immediately governing an explicit date pattern in the same sentence. §3.10 supplies the date half and the governing phrase supplies the context half; neither fires alone
- a renewal phrase — 'renewal notice', 'your policy expires', 'time to renew', 'your subscription ends' — co-occurring with a named issuing organisation and an explicit date
- a `VTODO` component inside a `VCALENDAR` container carrying a `DUE` property — the calendar format's own task object, which is not a `VEVENT` and must not be read as one
- a `VALARM` component inside a `VCALENDAR` container — the format's own reminder slot, readable only against the entry it hangs from
- a task-list export whose column headers include a due-date column together with a status column — §2.9 says spreadsheets should yield “sheet names, column headers, visible cell values, table-like regions”, and the pairing of the two headers is the check either alone lacks
- a key-dates phrase ('key dates', 'important dates', 'milestone schedule') in a title position over a table whose rows pair a label with a date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- what the obligation actually is, where the notice names only a scheme, a reference or a product code
- whether a stated date is a deadline, a start date, an effective date or an expiry — four readings of one date pattern that the surrounding prose distinguishes and no rule can
- deciding whether a deadline is live or long discharged, where the corpus holds the notice but not the receipt
- a reminder captured as a screenshot or a photographed letter, which §7.3 already contemplates as residual material

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a bare future date — §3.10 “Date extraction should be deliberately narrow”, and a future date appears in every contract, warranty, rota, insurance schedule and passport in the corpus
- the words 'deadline', 'due' or 'reminder' in a filename
- a bare issuing-organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”
- typographic emphasis — bold, red text, a warning glyph
- the word 'urgent' or 'action required', which is the most common subject line in an unfiltered mailbox
- a date range with no phrase governing either end

### Work types

`reminder notice`, `renewal notice`, `expiry or lapse warning`, `final notice`, `key-dates or milestone schedule`, `task export carrying due dates`, `diarised alarm entry`, `countdown or checklist with dates`

### Grouping reasons (§4)

- one obligation across its first notice, its reminder and its final notice
- one issuing party across the obligations it tracks
- one renewal cycle across the notice and the payment or submission that discharged it
- one key-dates schedule across its successive republications

### Template (§5)

`obligation → issuing party → year`

Time first: **no**

§5.5's ordinary rule bites here harder than anywhere else in this slice: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The due date is the CONTENT of a reminder, not its address — a renewal notice belongs beside the policy it renews, and filing by the notice's own year is the one arrangement that guarantees this year's reminder sits nowhere near last year's. `time_first` is false, and this entry is the clearest case in the slice for it, which is why it is stated rather than assumed. The year is last and collapsible under §5.7's warning against templates that “create meaningless one-child levels”.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `law.limitation-and-diary` | the legal-practice version of this domain already exists and already models a matter reference beside a due date and a deadline type. Where a matter reference resolves, that domain is the more specific home and this one defers entirely; what stays here is the deadline with no matter — a passport, a warranty, a tax filing, a school form | §3.11 “It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible” |
| `admin.subscriptions-recurring` | a renewal notice is already the first work type of `admin.subscriptions-recurring`, which models a vendor, a billing period and a renewal date. Where a subscription identifier or a payment method appears the administration slice wins; a renewal notice with neither is a bare deadline and stays here | §4.8 the validator must confirm “that each fact or label belongs to an allowed domain schema” — and here it belongs to two, so the pair is recorded rather than left latent |
| `fin.insurance` | a policy renewal notice carries a policy number and a premium, and the finance slice owns both. §3.15 additionally makes finance a safety domain, so the deferral is not merely a tidiness preference | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” |
| `calendar.events` | a `VTODO` and a `VEVENT` arrive in the same container and are different objects. A deadline occupies no span and has no attendees; an event does. The container states which, and a rule that reads a `DUE` property as a `DTSTART` produces a fact of the wrong kind rather than a missing one | §3.2 “Raw evidence is not yet a fact” |

### Sensitivity

`none` — Neither §2.9 nor §8.4 attaches a sensitivity phrase to a due date, and this catalogue declines to invent one. What a specific notice carries alongside the date — a policy number, an account, a national identifier, a matter reference — is genuinely sensitive, and it belongs to the finance, identity, medical and legal domains named in the collisions above, which §3.15 already makes safety domains: “Finance, identity, medical, and legal material should be implemented first as safety domains”. Marking the bare deadline sensitive would spread the phrase across the corpus's single most common observation and dilute it where it matters. The open question below records the case against this call rather than hiding it. No handling class is assigned — that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Two calls here are Joseph's. First, the sensitivity marking above is `none`, and the argument against it is real: a run of reminders read together discloses what someone owes, to whom, and whether they are keeping up — an inference no single notice supports. If Joseph wants domains marked on what a COLLECTION discloses rather than on what one file contains, this entry flips and so do several others across the corpus. Second, whether a discharged reminder should be kept at all. §7.3's residual lifecycle is the only guidance the design offers and it constrains deletion rather than retention: “Review Later may hold files whose meaning is partly understood but whose final location requires a future decision”.

---

## `calendar.schedule-change` — Reschedules, cancellations and disruption notices

The notice that a fixed time moved — a reschedule, a cancellation, a delay or a travel disruption, and the commitment it amends.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names schedule changes. §2.9's calendar field list — “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata” — describes the entry, not its amendment. The design's provenance rule is why the amendment must be its own record rather than an overwrite: “The product must never overwrite the evidence record merely because a later extractor or model produces a different answer. A newer result should supersede an earlier result while retaining the old observation and the reason it was superseded”. §4.8 depends on the same thing — the validator must be able to see “that the model has not invented a date, project, purpose, or membership that the dossier does not support”, which it cannot do once the new time has silently replaced the old.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `changed commitment` | string | `BA1476 LHR-EDI, 12 Sept` | `validated` | What moved. Earned from a change phrase governing a named commitment, or directly from a `UID` that matches a stored entry. Without it there is no domain — a change notice that cannot name what changed is §3.6's “possible clue for review” and nothing more. |
| `original time` | datetime | `2026-09-12T07:35` | `validated` | The time being replaced. §3.8 is why it is a separate field rather than a superseded value of one time field: “The system must separate roles that happen to contain the same entity type” — a change notice carries two date-times that mean opposite things, and collapsing them destroys the only fact the domain exists to hold. |
| `new time` | datetime | `2026-09-12T11:10` | `validated` | The replacement. Both times are `validated` rather than `direct` because in prose neither is labelled — they are told apart by the change phrase between them, which is exactly the context check §3.5 describes when a candidate becomes a fact only “when the engine finds a course-code pattern together with academic context”. Where the container supplies them as `RECURRENCE-ID` and `DTSTART` the pairing is labelled and the ceiling would be direct. |
| `change type` | string | `rescheduled` | `validated` | Rescheduled, cancelled, delayed, postponed, diverted. `METHOD:CANCEL` is a labelled slot; prose earns the field from the disruption vocabulary below. This is the field the template branches on because it is what a person searches for. |
| `change reason` | string | `crew shortage` | `llm_supported` | Always prose, often euphemistic, and worth holding because it is what a compensation claim later cites. §3.6 bounds it: “A model that cannot cite sufficient evidence must return unknown”. |
| `notifying party` | string | `British Airways` | `validated` | Who moved it. Metadata and a joining fact, never a level — §3.8 “A folder should not become a collection point for everything produced by the same person or organization”. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a change phrase — 'has been rescheduled', 'this event has been cancelled', 'your appointment has moved', 'is delayed by', 'has been postponed' — co-occurring with two distinct date-time patterns in one document, which is the pairing no single date can supply
- a `METHOD:CANCEL` property inside a `VCALENDAR` container — the format's own cancellation verb
- a `VEVENT` sharing one `UID` with an entry already stored but carrying a later `SEQUENCE` value — the format's own amendment marker, readable only against the earlier version and therefore a corpus-level rule rather than a file-level one
- a `RECURRENCE-ID` property on a `VEVENT` — the format's marker for one altered instance of a series, meaningless without the series it belongs to
- a disruption vocabulary ('cancelled', 'delayed', 'diverted', 'postponed') co-occurring with a named carrier, venue or provider AND a service or booking identifier in the same document
- a `STATUS:CANCELLED` property inside a `VEVENT` that already carries `DTSTART` and `SUMMARY`

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- reading which of two dates in a notice is the original and which the replacement, where no phrase governs either
- deciding whether a cancellation ended the commitment or preceded a rebooking held elsewhere in the corpus
- an apology letter that describes a disruption without naming a booking, a service or a date
- separating a change to the user's own commitment from a general service advisory sent to everybody

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- the word 'cancelled' — a cancelled cheque, a cancelled order, a cancelled subscription and a cancelled contract belong to four other slices
- a bare pair of dates — §3.10 “Date extraction should be deliberately narrow”, and two dates in a document is the ordinary case, not the exceptional one
- a strikethrough or a struck-out time
- a bare flight, train or service number — §3.10 warns that documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and a service number is exactly such a token
- the word 'update' or 'change' in a subject line
- an apology phrase on its own

### Work types

`reschedule notice`, `cancellation notice`, `delay or disruption alert`, `amended itinerary or revised confirmation`, `updated calendar entry carrying a later sequence or a cancel method`, `recurring-series exception`, `apology and rebooking offer`, `service advisory naming a specific booking`

### Grouping reasons (§4)

- one commitment across its original entry and every amendment to it, joined by the container's `UID` or by a booking reference
- one disruption across every notice it generated
- one recurring series across its exceptions
- one rebooking across the cancellation and the replacement confirmation

### Template (§5)

`changed commitment → change type`

Time first: **no**

§5.5 “a parent dimension should provide the context required to understand the child” is decisive: a reschedule notice says only that something moved, and it is legible nowhere except beneath the thing that moved. A date-first order is the single arrangement that guarantees the amendment lands nowhere near the original — §5.5's “putting year first scatters related work across calendar folders” describes it exactly, and here the scattered pair is the pair that has to be read together. A per-notice date level would additionally be §5.7's “meaningless one-child levels”, since notices arrive one at a time.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `calendar.events` | an amended `.ics` IS a calendar entry — same `UID`, later `SEQUENCE`. The two domains describe one file from opposite ends, and the question of whether the amendment is a new file or a new version of the old one is raised as an open question rather than settled here | §3.11 names “version family” among the universal file facts, which is the mechanism the question turns on |
| `pers.travel-record` | a flight cancellation belongs to the trip, and `pers.travel-record` already models the trip as the organising reason with a booking reference to join on. Where the reference resolves to a known trip that domain is the more specific home and this one defers | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `calendar.appointment` | a rescheduled appointment letter carries an appointment reference and a counterparty, which are the appointment domain's fields. The separator is what the file is FOR: a letter that confirms a new time is an appointment record, a letter whose subject is the disruption itself is a change record | §3.9 “Purpose must be a first-class facet” |
| `comms.notification-alert` | most disruption alerts are machine-sent and carry every marker of an automated notification. The separator is whether the notice names a SPECIFIC commitment of the user's — a general service advisory is a notification, an advisory quoting the user's own booking reference is a change record | §4.9 “It should not form a supported group when there is no valid anchor” — the booking reference is the anchor, and without it the file is not this domain's |

### Sensitivity

`potentially_sensitive` — A disruption notice states where someone was going, when, and that they were not at home. It arrives by mail carrying addresses, which §2.9 says to treat as “potentially sensitive”, and §8.4 names “private correspondence” and “GPS metadata” among what the corpus can include — a travel change notice is the itinerary-shaped form of the second. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Is an amendment a file of its own or a new version of the file it amends? §3.11 makes “version family” a universal file fact, and an updated `.ics` carrying the same `UID` and a later `SEQUENCE` is a version family by every structural test — which would put the amendment inside `calendar.events` and delete this domain. The argument against is that a version family is normally one document redrafted, whereas a reschedule notice is a NEW communication about an old commitment, frequently from a different sender in a different format. This catalogue has authored the domain and flagged the collision rather than resolving it, because the answer changes how the tree looks for anyone whose corpus is mostly travel and appointments. It is Joseph's.

---

## `comms.email-thread` — Working email threads

One conversation carried by email — the messages, their reply chain, and what was attached to them.

**Provenance:** **design** — a design sentence names this domain's fields

**Cite:** §2.9 names the formats, every field and the handling: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context, while treating addresses and message content as potentially sensitive”. That single sentence is this entry's schema, its grouping reason (“thread identifiers” and “reply-chain context”) and its sensitivity marking. `src/extractors/router.py` already maps `eml`, `mbox` and `msg` to source type `email`, and `src/extractors/long_tail.py` already marks addresses and body zones sensitive at emission — the fact layer had no schema for any of it to resolve into.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `thread` | string | `Aldermore kick-off` | `direct` | §2.9 names “thread identifiers” as a field email should yield. `Message-ID`, `In-Reply-To` and `References` are labelled header slots, which is §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. The thread is the identifier's family, not the subject line — the subject changes mid-thread and the `References` chain does not. |
| `subject` | string | `Re: Aldermore kick-off` | `direct` | §2.9 names “subject”. A `Subject` header is a labelled slot. It is held as a display fact and is explicitly NOT the joining fact — 'Re: Update' is the most common string in a real mailbox, and §4.9's warning applies to it exactly: a group must not form “when one high-frequency entity acts as the only bridge”. |
| `first message date` | datetime | `2026-04-14T08:52` | `direct` | §2.9 names “sent date”. The `Date` header is a labelled slot, and the earliest such date across a resolved thread is a projection of direct facts rather than a second observation, so it inherits the ceiling and never outlives it. Held separately from the last message date because §3.8 requires it: “The system must separate roles that happen to contain the same entity type”. |
| `last message date` | datetime | `2026-06-02T17:20` | `direct` | The other end of the span. The pair is what makes a thread a duration rather than an instant, and it is the only fact that distinguishes a live exchange from a dead one without reading the body. |
| `participant role` | string | `external counterparty` | `validated` | §2.9 names “sender” and “recipients”; §3.8 requires the modelling this field performs: “The system must separate roles that happen to contain the same entity type”, since the same address appears as sender, recipient, copied party and quoted signature within one thread. Resolving an address against the user's own identities and against a known-counterparty list is a deterministic context check — §3.13's “A validated fact was found by a deterministic rule and passed contextual checks”. §3.8 also forbids the obvious misuse: “It should avoid using authorship or creator identity as a destination dimension”. |
| `correspondent organisation` | string | `Aldermore Bank` | `validated` | The organisation on the other side, taken from the address domain and confirmed against a gazetteer. §3.7 constrains the match: “It should use word-boundary matching rather than substring matching” and “It should rank candidate matches instead of accepting the first match”. This is the only field in the entry offered as a folder level, and the open question below records that §3.8 has a real objection to even that. |
| `attachment name` | string | `kickoff-agenda.pdf` | `direct` | §2.9 names “attachment names” explicitly. The name is a labelled slot in the MIME part. It matters beyond search: an attachment extracted from a thread is a file whose parent-folder context is a mailbox, and §2.9 lists “parent-folder context” among what every file receives, so the thread is the only context that attachment will ever have. |
| `thread subject matter` | string | `supplier onboarding` | `llm_supported` | What the conversation is actually about, which the subject line frequently misstates and often contradicts by the tenth reply. §3.5 is the licence and the limit: the model may act “only when a file requires language interpretation that rules cannot resolve safely”, and “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file”. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an RFC-5322 header block carrying `Message-ID` together with `In-Reply-To` or `References` — §2.9 names “thread identifiers” as a field email should yield, and the pairing of an identity header with a chain header is what makes it a thread rather than a message
- a `From`, `To` and `Subject` header triple present in one header block, in a file the router already sent to source type `email` — `src/extractors/router.py` maps `eml`, `mbox` and `msg`, and the header triple is the content check that confirms the extension
- a `Subject` value whose reply and forward prefixes have been stripped matching the stripped subject of another message in the corpus WHERE both also share a participant address — the subject alone is refused below and only the pairing fires
- an `mbox` `From ` separator line at the start of a message block together with a `Date` header inside that block
- a quoted-reply structure — a run of lines prefixed with a quote marker beneath an attribution line naming a sender and a date — appearing inside a body §2.9 already treats as sensitive

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an email saved as a PDF or a print, where the headers survive as body text and the reply chain survives as indentation
- what the thread is actually about, once the subject line has stopped describing it
- whether an exchange is working correspondence or personal correspondence, where the address is a personal one used for work
- separating a genuine conversation from a one-to-one marketing message written in conversational voice

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a bare email address — §2.9 requires the engine be “treating addresses and message content as potentially sensitive” before it treats them as evidence, and an address appears in signatures, letterheads, footers, invoices and CVs in every slice of this corpus
- a `Subject` value alone — §4.9 refuses a group formed “when one high-frequency entity acts as the only bridge”
- a bare person name — §3.8 “It should avoid using authorship or creator identity as a destination dimension”
- a `.eml` or `.msg` extension with no header block confirmed by content
- the presence of an `@` character
- a signature block — it is a contact card in prose, and `comms.contact-record` does not claim it either

### Work types

`single message (.eml/.msg)`, `thread export`, `forwarded chain`, `message saved as PDF or print`, `attachment carried by the thread`, `auto-reply or bounce within the thread`, `message with an embedded calendar part`

### Grouping reasons (§4)

- one thread across its messages, replies and forwards, joined by `References` rather than by subject
- one correspondent organisation across the threads it appears in
- one message and the attachments it carried
- one exchange that changed its subject line but kept its reply chain

### Template (§5)

`correspondent organisation → thread`

Time first: **no**

§5.5's ordinary record rule — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — rules time out immediately, since a thread spanning a year-end would be split down the middle. The first level is the harder call. §3.8 says “Authorship is usually metadata” and warns that “A folder should not become a collection point for everything produced by the same person or organization”, which is an objection to a per-correspondent level; the answer taken here is that an organisation on the other side of an exchange is the target rather than the author, which is the reading §3.8 itself endorses when it names “our_firm and client” as distinct facets. The objection is real enough to be raised in the open question below rather than argued away.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `pers.correspondence` | an email thread and a message archive export are already work types of `pers.correspondence`, so the two domains overlap by construction. The separator is the correspondent's role, not the format: a person writing as a person belongs there, an organisation or a working counterparty belongs here, and a personal address used for work satisfies both | §3.8 “The system must separate roles that happen to contain the same entity type” |
| `law.matter-correspondence` | correspondence on a legal matter is already modelled with a client and a matter reference. Where a matter reference resolves, the law slice is the more specific home and this domain defers; §3.15 makes that deferral a safety property rather than a preference | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” |
| `ops.internal-comms` | a broadcast to an organisation's own people is not a thread — it has no reply chain and no counterparty, which is exactly the structural absence that separates them. `ops.internal-comms` owns the producing side | §2.9 names “reply-chain context” as a field email should yield, and its absence is what disqualifies a broadcast here |
| `soft.helpdesk-ticket` | a support thread with a queue and a ticket identifier belongs to the software slice, which already models both. This is a deliberate resolution: `soft.helpdesk-ticket` currently cites a domain called `career.correspondence` that no catalogue defines, and this entry is the working-communication domain that citation was reaching for | §4.9 “It should not form a supported group when there is no valid anchor” — the ticket identifier is the anchor, and its presence sends the file there rather than here |

### Sensitivity

`potentially_sensitive` — §2.9 states it directly of this material and no inference is needed: email should be handled “while treating addresses and message content as potentially sensitive”. §8.4 independently names “private correspondence” among what the corpus can include. `src/extractors/long_tail.py` already emits the signal on address-kind header values and on body and link zones. §2.9's phrase is the whole claim made here — the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Should a mailbox branch by correspondent at all? §3.8's warning is aimed at exactly this shape — “A folder should not become a collection point for everything produced by the same person or organization” — and a `Correspondence/Aldermore Bank/` tree is a collector by any reading, however the counterparty/author distinction is drawn. The alternative is to branch by the MATTER a thread concerns, which is what `law.matter-correspondence` does and what §3.8 recommends when it says the “purpose, project, subject, or target is more informative for placement”; the cost is that the matter is `llm_supported` here and a validated reference there. Joseph's call, and it decides whether working email is a branch of its own or is dispersed into the projects it discusses.

---

## `comms.chat-export` — Chat and messaging archives

A conversation carried by a messaging platform and exported as a file — channel logs, direct-message histories, and the attachments inside them.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names chat or messaging. §2.9's long-tail list runs from email through calendar and contacts to code, media and archives and never reaches messaging platforms; the nearest sentence routes a chat export by its container rather than by its meaning — “Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure”. §2.6 is the only place the design mentions these platforms at all, and it mentions them as a source of damage: “Messaging platforms and downloaded web images often strip metadata from real photographs”. §5.7 permits the addition: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `workspace or service` | string | `Slack - Aldermore` | `validated` | Which platform and which tenant. Earned from an export manifest at the archive root, or from the container's own schema keys — §2.9 says structured data should yield “readable text plus format-specific structure”, and the schema keys ARE the format-specific structure. `direct` is refused because no labelled slot names the workspace in most exports; it is read from the file layout. |
| `channel or conversation` | string | `#kickoff` | `direct` | The addressable conversation. Where an export carries a channel name as a manifest key or a directory name it is a labelled slot — §3.13's “labeled form field”. This is the domain's joining fact and the level the template branches on. |
| `participant role` | string | `external guest` | `validated` | §3.8 “The system must separate roles that happen to contain the same entity type” — a workspace holds the user, colleagues, guests and bots behind one author key. Resolving the key against a users manifest is a context check; naming the person is neither necessary nor permitted as a dimension under §3.8's “It should avoid using authorship or creator identity as a destination dimension”. |
| `conversation period` | string | `2026-04 to 2026-09` | `validated` | The span the export covers, taken from the earliest and latest message timestamps rather than from the export's own filename. §3.10 “Date extraction should be deliberately narrow” refuses a period read from a filename token. |
| `export format` | string | `platform JSON export` | `direct` | Which shape the archive is in, which decides what can be read from it at all. §2.9's closing requirement is why the field is worth holding: “Every extractor must emit the same evidence shape”, and a chat export that is an archive is read through its manifest rather than its contents. |
| `attachment name` | string | `floorplan-v3.png` | `direct` | Files carried inside the conversation. Held for the same reason as on `comms.email-thread`: an image pulled out of a chat export has no parent-folder context of its own, and §2.6 warns what has already happened to it — “Messaging platforms and downloaded web images often strip metadata from real photographs”, so the conversation is the only provenance it retains. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a JSON array of objects each carrying a message-shaped key triple — an author key, a text key and a timestamp key — repeating through the file, in a container that also names a channel or conversation. §2.9 says structured data should yield “readable text plus format-specific structure”, and it is the repeated triple, not any one key, that identifies the structure
- a platform export manifest at an archive root (a channels list beside a users list) read from the manifest alone — §2.5 “Archives should be inspected without being unpacked to disk”
- a chat transcript line shape — a bracketed or trailing timestamp followed by a name and a colon — repeating line after line through a text file, which is the repetition no single line supplies
- an export header phrase — 'chat history with', 'messages exported', 'conversation export' — co-occurring with a participant name and a date range in the same file
- a directory of media files sitting beside a message container that names them, inside one archive manifest

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- whether an exchange is working or personal, which the platform does not record and the channel name rarely settles
- a conversation pasted into a document, where the line shape survives but the container does not
- reading what a channel was for once its name has stopped describing it
- separating a real conversation from a bot or integration feed posting into the same channel

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a bare timestamp column
- a bare participant name — §3.8 “It should avoid using authorship or creator identity as a destination dimension”
- a name followed by a colon — every screenplay, interview transcript, deposition and qualitative-coding file has the identical shape, and `write.screenplay`, `law.depositions` and `res.qualitative-coding` own those
- the word 'chat', 'messages' or 'export' in a filename
- a JSON container on its own — §2.9 routes JSON to structured data and `src/extractors/router.py` maps `json` to source type `code_structured`, so the container is evidence of a format and not of a domain
- an emoji or reaction token

### Work types

`channel export`, `direct-message export`, `group-chat export`, `message archive in platform JSON or HTML`, `exported attachment set`, `chat transcript pasted into a document`, `screenshot of a conversation`

### Grouping reasons (§4)

- one channel or conversation across the period exported
- one export run across every file it produced, joined by the archive manifest
- one conversation and the attachments carried inside it
- one workspace across its channels

### Template (§5)

`workspace or service → channel or conversation → conversation period`

Time first: **no**

§5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — a channel exported twice must not split across two year folders, and the channel is the function. The period is last and only appears where a channel has been exported more than once; where it has not, §5.7's warning against templates that “create meaningless one-child levels” collapses it. The workspace leads because §5.5 also requires that “a parent dimension should provide the context required to understand the child”, and `#general` means nothing until you know whose `#general`.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `pers.correspondence` | a message archive export is already a work type of `pers.correspondence`, so personal messaging defers there. The separator is the correspondent's role rather than the platform — the same application carries both, often in adjacent conversations of one export | §3.8 “The system must separate roles that happen to contain the same entity type” |
| `comms.email-thread` | both are threaded working conversation and the same exchange frequently crosses between them. The separator is the container: an RFC-5322 header block is email, a platform export is chat, and a chat notification delivered BY email is email carrying a chat | §2.9 “The engine should treat the file extension as a routing signal rather than an assumption about meaning” |
| `pers.screenshot` | a screenshotted conversation is a capture by every §2.6 test and a conversation by its content, and the two readings do not resolve from metadata. §7.3 already anticipates where such a file goes when nothing claims it | §7.3 “Temporary Screenshots may live under Photos/Temporary Screenshots and hold screenshots that appear time-sensitive or remind the user of something but have no accepted project, trip, application, or event relationship” |
| `law.ediscovery-production` | a chat export collected for a matter carries a custodian and a production reference, and the law slice owns both. Where those resolve, that domain wins outright and the export must not be re-filed by workspace | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” |

### Sensitivity

`potentially_sensitive` — §2.9 attaches its phrase to email rather than to chat, so this marking is an inference and is written as one: a chat export is message content and participant addresses in a different container, and §8.4 names “private correspondence” among what the corpus can include without naming a transport. The volume is what sharpens it — one export holds years of unguarded conversation about people who never consented to being in the user's corpus. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Is a chat export one file or a corpus? A platform export is an archive containing hundreds of conversations and thousands of messages, and the design's only rule for that shape is §2.5's “Archives should be inspected without being unpacked to disk” — which means the engine sees the manifest and not the conversation, so every schema field above is read from structure rather than from content. Whether such a file should be placed as a single opaque object, unpacked into per-channel groups, or held back entirely under §7.3's Protected Records is Joseph's; the same question is raised in a different form on `comms.mailbox-archive`, and the two should be answered together.

---

## `comms.call-and-voicemail` — Calls, voicemail and recordings

Spoken communication as a file — a call log, a voicemail, a recorded call or meeting, and the transcript or captions made from it.

**Provenance:** **inference** — extends a family the design names

**Cite:** Extends a family §2.9 names rather than a domain it names. §2.9's audio bullet gives the field list: “Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present”, and the transcript half of that sentence is conditional in the design's own words — it is available “only under an explicit privacy and compute policy”, which `src/extractors/long_tail.py` already implements as an injected predicate with no default. This entry therefore treats a speech-derived transcript as unavailable unless P7 has authorised it, and captions as unconditionally available. §5.7 permits the domain: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `counterparty role` | string | `external caller` | `validated` | Who was on the other end, as a role rather than as a person. §3.8 requires the shape: “The system must separate roles that happen to contain the same entity type”, and forbids the alternative — “It should avoid using authorship or creator identity as a destination dimension”. Earned from a caller-id slot or a log column resolved against known identities, which is a context check. |
| `call direction` | string | `inbound` | `direct` | Inbound, outbound or missed. A direction column in a call-detail export and a caller-id tag on a voicemail are both labelled slots — §3.13's “labeled form field”. It is the cheapest fact in the domain and the one that separates a voicemail left FOR the user from a recording made BY them. |
| `call date` | datetime | `2026-05-08T16:41` | `direct` | §2.9 names “creation time” among what audio should yield, and a container's creation timestamp is a labelled metadata slot. This is the field that makes the template decision below, because for the recording half of this domain it is the material's defining aspect rather than an incidental stamp. |
| `duration` | string | `00:03:41` | `direct` | §2.9 names “duration” first in its audio field list. Held for search and for triage rather than for placement — a two-second file and a ninety-minute file are different kinds of thing, and neither is a folder level. |
| `recording type` | string | `voicemail` | `validated` | Voicemail, call recording, meeting recording, voice memo. §2.9 names “embedded tags” as a field audio should yield, and a recorder application's tag corroborated by a filename convention is a context check — §3.13's “A validated fact was found by a deterministic rule and passed contextual checks”. Without a tag the file falls to `needs_llm`, because the container is identical across all four. |
| `transcript availability` | string | `captions present` | `direct` | Whether text exists for this audio and where it came from. The distinction is a privacy boundary rather than a convenience: §2.9 makes captions unconditional — “subtitles or captions where present” — and speech-to-text available “only under an explicit privacy and compute policy”. Recording which one a file has is what lets the validator refuse a transcript that arrived without authorisation. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an audio container whose embedded tags carry a voicemail vocabulary or a caller-id slot together with a creation time — §2.9 names “embedded tags” and “creation time” as fields audio should yield, and it is the pairing that fires
- a call-log export whose column headers include a direction column, a number-shaped column and a duration column together — §2.9 says spreadsheets should yield “sheet names, column headers, visible cell values, table-like regions”, and it is the header triple, not any one column, that identifies a call log
- a sidecar caption or subtitle file sharing a basename with an audio or video file in the same directory — §2.9's “subtitles or captions where present” is the unconditional half of the transcript sentence and needs no policy
- an audio filename matching a telephony or recorder capture convention together with an embedded tag naming the recording application
- a conferencing platform's recording filename convention together with a container whose duration and codec metadata match a long-form capture rather than a media file

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- separating a voicemail from a voice memo, a lecture capture, a field recording and a music take, which share one container and frequently one tag set
- reading what a call was about, where a transcript exists under P7's policy and the audio is otherwise opaque
- deciding whether a meeting recording belongs to the meeting's own record or stands alone
- an audio file whose tags were stripped in transit, which §2.6 already establishes as the ordinary outcome of passing through a platform

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a bare audio file — a voice memo, a music track, a podcast episode, a lecture recording and a field recording share one container, and `audio.music-session`, `audio.podcast-episode` and `res.field-work` own three of those
- a bare phone-number-shaped token — §3.10 warns that documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and §2.9 additionally treats phone numbers as address-book material that “should normally be privacy-protected rather than used to create folder proposals”
- a bare duration
- the word 'recording', 'call' or 'audio' in a filename
- a speech-to-text transcript produced without P7's policy — §2.9 permits it “only under an explicit privacy and compute policy”, so absent that authorisation the transcript is not weak evidence, it does not exist
- the ABSENCE of embedded tags, in either direction — §2.6 establishes that stripping is routine, and P5 already refuses to read an absence as an observation

### Work types

`voicemail message`, `call recording`, `meeting or conference recording`, `call log or call-detail export`, `caption or subtitle sidecar`, `authorised speech-to-text transcript`, `voice memo`, `missed-call notice`

### Grouping reasons (§4)

- one call across its recording, its transcript or captions, and its row in a log
- one counterparty across the calls exchanged with them
- one meeting across its recording and the minute that cites it
- one export run across the log rows and media files it produced together

### Template (§5)

`year → recording type`

Time first: **yes**

This is the one entry in the slice that meets §5.5's exception on its stated terms rather than by argument: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. A voicemail and a call recording ARE capture-based media — §2.9 files them in the same audio-and-video bullet as any other capture, and their creation time is what identifies them, since nothing else about the container differs. The strain is the log half: a call-detail export is a record and not a capture, and §5.5's ordinary rule would put the counterparty first. `time_first` is recorded true for the capture majority with the tension stated in the open question, and `recording type` is second because it is the only fact that separates files sharing a container.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `audio.podcast-episode` | a produced episode is published work with an edit, a run order and a release; a recorded call is communication with none of those. The separator is the presence of production artifacts beside the audio, not anything inside it | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `ops.meeting-record` | a meeting recording and the minute made from it describe one meeting from two directions — the minute is the record, the audio is the capture. `ops.meeting-record` already models the meeting series and date, and where a minute exists it is the more legible home for the pair | §4.9 “A file may validly belong to more than one accepted group” |
| `res.qualitative-coding` | a research interview recording belongs to the study, and the research slice already models the participant identifier and the protocol. Where those resolve, that domain wins; §3.15's safety ordering makes the deferral matter, since a consented recording is governed material | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” |
| `pers.correspondence` | a voicemail from a family member is personal correspondence in an audio container, and the household slice already claims letters, cards and message archives. The separator is the counterparty's role, exactly as it is between `comms.email-thread` and the same domain | §3.8 “The system must separate roles that happen to contain the same entity type” |

### Sensitivity

`potentially_sensitive` — §8.4 names “private correspondence” among what the corpus can include, and spoken correspondence is the least guarded form of it. §2.9 marks phone numbers as address-book material that “should normally be privacy-protected rather than used to create folder proposals”, and a call log is nothing but phone numbers. The transcript route is itself a privacy gate in the design's own words — speech-to-text runs “only under an explicit privacy and compute policy” — which is the design saying this material is sensitive without using the phrase. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Does §5.5's capture exception cover a voicemail? The entry claims it does, on the ground that §2.9 files voicemail in the same audio-and-video family as any other capture and that creation time is what identifies it. Two things make that less than settled and both are Joseph's. First, this domain mixes captures with records — a call-detail export is a spreadsheet, and §5.5's ordinary rule would put the counterparty above the year for it, so a single template serves the two halves badly whichever way it points. Second, whether an authorised transcript is a file fact of the audio or a derived document of its own: §3.11 makes “version family” a universal file fact and a transcript is not a version, yet §3.2 requires that “the product must preserve both the original evidence and the conclusion built from it”, which is the relationship a transcript has to its audio.

---

## `comms.notification-alert` — Automated notifications and alerts

Machine-sent messages that report a state change — service, security, delivery and account notices nobody wrote by hand.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names notifications. §7.3 is where they land by default, in two of its residual templates: “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” covers the confirmation half, and “Review Later may hold files whose meaning is partly understood but whose final location requires a future decision” covers the rest. A domain exists here because the material is recognisable even when it is not worth keeping, and misrecognising it is expensive: a security alert misread as correspondence carries a verification code into a model prompt. §5.7 permits the addition: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `service` | string | `Aldermore Bank` | `validated` | Which system sent it. Earned from a sender domain or a letterhead corroborated by an automated-message marker in the same file. §3.7 constrains the match: “It should use word-boundary matching rather than substring matching”, which matters here because service names are short and generic. |
| `notification class` | string | `security alert` | `validated` | Security, delivery, payment, terms change, service status. This is the field the domain exists for, because the classes differ in how they must be HANDLED and not merely in what they say. Earned from the class vocabularies in the deterministic rules below, each of which requires a corroborating fact. |
| `event reported` | string | `new sign-in from a new device` | `llm_supported` | What actually happened. Always prose and frequently deliberately vague. §3.6 bounds it: “A model that cannot cite sufficient evidence must return unknown”, and a notification whose event cannot be read is still a notification. |
| `notification date` | datetime | `2026-07-02T03:14` | `direct` | The `Date` header is a labelled slot — §2.9 names “sent date” for email and this material arrives as email. Note what it is NOT: the time of the event reported, which is a different fact carried in the body, and §3.8 requires them kept apart — “The system must separate roles that happen to contain the same entity type”. |
| `actionability` | string | `no action required` | `llm_supported` | Whether the recipient must do something. It is the only fact that decides whether a notification is worth surfacing, and it is stated in prose or not at all. §3.9's distinction is why it is a field: “Topic answers what a file is about, while purpose answers what the file was for”. |
| `reference` | string | `TRK-88213` | `direct` | A tracking, transaction or case identifier where the notice carries one, taken from its explicit label — §3.13's “labeled form field”. It is what joins a notification to the order, payment or ticket it reports on, and its absence is what keeps a general advisory out of `calendar.schedule-change`. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a no-reply sender pattern in a `From` header ('no-reply@', 'donotreply@', 'notifications@') together with an automated-message phrase in the body ('this is an automated message', 'do not reply to this email') — the sender alone is refused below
- an `Auto-Submitted` header whose value is not 'no' — RFC 3834's own automatic-message marker — present in a header block that also carries a `From` address in a no-reply position
- a security vocabulary ('new sign-in', 'your password was changed', 'verification code', 'unusual activity') co-occurring with a named service and a timestamp in the same document
- a delivery vocabulary ('your parcel', 'out for delivery', 'has been delivered') together with a labelled tracking reference and a named carrier
- a payment or transaction vocabulary co-occurring with a labelled transaction reference and a named institution — which is also the point at which the file stops being this domain's and becomes the finance slice's
- a terms-change phrase ('we are updating our terms', 'changes to your agreement') together with an effective date governed by an explicit phrase, per §3.10

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- whether a notification still matters, which depends on whether the state it reported has since changed
- separating a genuine service alert from a phishing message written to imitate one, which is a judgement about tone and inconsistency rather than about any parseable slot
- reading a notification rendered entirely as an image, where OCR yields the body and none of the headers
- deciding whether an alert is the user's own or was forwarded to them about somebody else

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a no-reply address alone — a real person's message is frequently sent from a shared or system mailbox
- the word 'notification' or 'alert' in a filename — `soft.monitoring-log-export` and `hse.incident-record` own the operational senses and both are more specific
- a bare timestamp — §3.10 “Date extraction should be deliberately narrow”
- a tracking-shaped or reference-shaped token on its own
- the words 'urgent' or 'action required'
- an unsubscribe link — it appears on transactional mail, on newsletters and on one-to-one marketing alike, and it is `comms.mailing-list-newsletter` that needs a list header rather than a link

### Work types

`service or account notification`, `security or sign-in alert`, `delivery or shipping notification`, `payment or transaction alert`, `terms-change or policy-update notice`, `system or platform status notice`, `digest of alerts`, `verification or one-time-code message`

### Grouping reasons (§4)

- one service across the notifications it sent
- one reported event across the alert, the follow-up and the resolution, joined by a reference
- one order, payment or ticket across every notification about it
- one export or capture run across a batch saved together

### Template (§5)

`service → notification class`

Time first: **no**

§5.5 “a parent dimension should provide the context required to understand the child”: a notification is legible only once you know which system sent it, and the class is what makes a run of them navigable. Time is offered as no level at all — §5.7 forbids a template that would “create meaningless one-child levels”, and a per-notification date level is a one-child level by construction, since notifications arrive one at a time and each carries its own instant. This is also the entry where a template is least likely to be wanted; the open question below is about whether the branch should exist rather than about how to order it.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `soft.monitoring-log-export` | an operational alert from a monitoring system is software material and the software slice already owns it. The separator is the recipient's role — an operator acting on an alert is doing engineering work, a person receiving one about their own account is not | §3.8 “The system must separate roles that happen to contain the same entity type” |
| `fin.receipts-expenses` | a payment alert carrying an amount and a merchant is a transaction record, and the finance slice owns it. §3.15 additionally makes finance a safety domain, so the deferral protects rather than merely tidies | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” |
| `admin.subscriptions-recurring` | a terms-update notice is already a work type of `admin.subscriptions-recurring`, which models the vendor, the plan and the billing period. Where a subscription identifier resolves that domain is the more specific home | §3.11 “It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible” |
| `comms.mailing-list-newsletter` | both are machine-sent and neither is a conversation. The separator is structural rather than semantic: a list header marks material the recipient subscribed to, an auto-submitted header marks material a system sent about the recipient's own state | §2.9 “Every extractor must emit the same evidence shape”, which is what makes a header-level separator usable at all |

### Sensitivity

`potentially_sensitive` — A verification code and a sign-in alert are credential-bearing, and §8.4 names “credentials” among what the corpus can include; §8.4 also states the consequence for this product specifically — “Privacy policy must be enforced before content reaches any model or external connector”. The marking here is therefore about what the class can carry rather than about what a typical file contains: a delivery notice is anodyne and a one-time code in the same shape is not, and the recogniser cannot tell which it holds before it reads it. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Should this material reach the tree at all? Every argument for a domain here is a recognition argument, not a placement one — the schema exists so that a security alert is not misread as correspondence and carried into a model prompt, which §8.4 forbids: “Privacy policy must be enforced before content reaches any model or external connector”. Whether the tree should then show a Notifications branch, hold the material in §7.3's Review Later, or surface it only for deletion review under the residual lifecycle is Joseph's, and this catalogue takes no position. §7.3's own instinct is that this is residue: “Review Later may hold files whose meaning is partly understood but whose final location requires a future decision”.

---

## `comms.mailing-list-newsletter` — Subscribed mail: newsletters, lists and digests

Mail a person receives because they subscribed rather than because someone wrote to them — newsletters, list traffic and digests.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names mailing lists. §2.9's email field list — “sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context” — fits a newsletter exactly without describing what makes it different, which is that the recipient never entered the conversation. §7.3's nearest destination is a residual one: “Reading Inbox may hold papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association”. §5.7 permits the addition: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `publication` | string | `The Long View` | `validated` | The masthead. Earned from a title-position name corroborated by a list header or an unsubscribe phrase — §3.7 “It should use positional weighting because a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference”. This is the domain's joining fact and its only folder level. |
| `issue` | string | `No. 214` | `validated` | Which instalment. Earned from an issue label governing an identifier, never from a bare number — §3.10 warns that documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and an issue number is exactly such a token when it stands alone. |
| `list identifier` | string | `longview.example.com` | `direct` | A `List-Id` or `List-Unsubscribe` header is a labelled slot — §3.13's “labeled form field” — and it is the strongest evidence this domain has, because it is the format stating the recipient's non-participation rather than the content implying it. |
| `publication cadence` | string | `weekday` | `llm_supported` | Daily, weekly, occasional. Read across a run of issues rather than from any one file, which makes it a corpus-level inference and not a file fact; §3.6's “A model output that is useful but too weak to establish a fact may remain a possible clue for review” is where a weak reading belongs. |
| `subscription status` | string | `subscribed` | `validated` | Subscribed, lapsed or unsubscribed. Earned from a confirmation or cancellation message rather than from an issue, which is why those are separate work types below. |
| `topic` | string | `monetary policy` | `llm_supported` | What the publication is about, held for search rather than for placement. §3.9 “Topic answers what a file is about, while purpose answers what the file was for” — and the purpose of a subscribed issue is reading, which is what makes §7.3's Reading Inbox its natural rival. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a `List-Unsubscribe` or `List-Id` header present in a message header block — RFC 2369's own list markers, and their presence is the recipient's non-participation stated by the format rather than inferred from the prose
- an unsubscribe phrase ('unsubscribe', 'manage your preferences', 'you are receiving this because') co-occurring with a publication name in a masthead or title position, which is §3.7's positional weighting supplying the context the footer phrase alone cannot
- an issue label ('Issue', 'No.', 'Vol.') governing an identifier, together with a publication name in a title position and a `Date` header
- a digest phrase ('daily digest', 'weekly roundup', 'this week in') together with a list header in the same message
- a subscription-confirmation phrase ('you are now subscribed', 'confirm your subscription') co-occurring with a named publication

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- separating a newsletter from a one-to-one marketing message written in a personal voice, where both carry an unsubscribe link and neither carries a list header
- an issue saved as a PDF or a web capture, where the headers are gone and only the masthead survives
- deciding whether an internal all-hands newsletter is this domain's or `ops.internal-comms`'s, which depends on whose organisation it is
- reading what a publication is about, where the masthead is a made-up word

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- an unsubscribe link alone — transactional mail and one-to-one marketing carry one too, and this is the single most over-firing signal in the domain
- a publication name — it appears in citations, reading lists, bibliographies and `res.reference-library` entries
- the word 'newsletter' — `ops.internal-comms` publishes one, `media.content-marketing` writes one, and `npo.fundraising-donor` sends one
- a bare send date — §3.10 “Date extraction should be deliberately narrow”
- a bare issue number
- an HTML email template shape, which is shared by every commercial sender in the corpus

### Work types

`newsletter issue`, `mailing-list message`, `list digest`, `subscription confirmation`, `unsubscribe confirmation`, `archived issue saved as PDF or HTML`, `welcome or onboarding sequence message`, `list announcement or moderator notice`

### Grouping reasons (§4)

- one publication across its issues
- one list across the traffic captured from it, joined by a `List-Id`
- one subscription across its confirmation, its issues and its cancellation
- one saved-for-reading batch across the issues captured together

### Template (§5)

`publication → year`

Time first: **no**

§5.5's ordinary rule states this case literally: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A publication's run IS the related work, and a year-first order breaks it every December. The year is second and collapsible — most subscriptions produce a handful of kept issues, and §5.7 warns against templates that “create meaningless one-child levels”. No issue level is offered, because an issue is a file and not a folder.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `ops.internal-comms` | a newsletter issue is already a work type of `ops.internal-comms`, which owns the producing side — an organisation telling its own people something. The separator is whose organisation it is, which §3.8 makes expressible and does not make readable | §3.8 “The system must separate roles that happen to contain the same entity type” |
| `media.content-marketing` | a newsletter written to market something belongs to the creative slice on the authoring side. The same file exists in the writer's corpus as a deliverable and in the reader's as received mail, and only the corpus tells them apart | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pub.periodical-issue` | a published periodical issue is publishing work with a production process behind it; a subscribed issue is the same artifact after delivery. Where production artifacts sit beside it — proofs, a schedule, contributor material — the publishing slice wins | §3.11 “It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible” |
| `comms.notification-alert` | both are machine-sent. The separator is structural: a list header marks material the recipient subscribed to, an auto-submitted header marks material a system sent about the recipient's own state, and a message carrying both is a service digest | §2.9 “The engine should treat the file extension as a routing signal rather than an assumption about meaning” — and a header is the same kind of routing signal, read from content rather than from the name |

### Sensitivity

`none` — A subscribed issue is published material: its body was written for an audience, and §2.9's phrase attaches to “addresses and message content” in correspondence rather than to a broadcast. The recipient's own address sits in the header, but every email in the corpus carries one, so it is not this domain's distinguishing fact and marking the domain on it would say nothing. The open question below records the serious argument against this call rather than burying it. No handling class is assigned — that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> The sensitivity marking above is `none` and it may well be wrong. What a subscription discloses is not its content but its MEMBERSHIP — a list about a diagnosis, a faith, a political campaign or a job search says something about the subscriber that no issue says about anyone, and §8.4's list of what the corpus can include names “medical information” and “employment materials” among the things such a membership implies. This catalogue has marked the domain on what a file contains, consistent with the rest of the corpus, and flags that a membership-based reading would flip this entry and would also flip `calendar.deadline-reminder`. Whether sensitivity is a property of a file or of a collection is Joseph's, and it is the same question raised there.

---

## `comms.contact-record` — Contact records and address books

The address book itself — cards holding names, organisations, numbers and addresses, which the design says must not become folders.

**Provenance:** **design** — a design sentence names this domain's fields

**Cite:** §2.9 names the format, the fields AND the handling in one sentence: “Contact formats such as VCF should yield names, organizations, email addresses, phone numbers, and address-book metadata, but should normally be privacy-protected rather than used to create folder proposals”. The clause after the comma is unusual in the design — it is the only place a long-tail family is given a field list and then told not to act on it — and it is why this entry's template offers one dimension where every other entry in the slice offers two or three. `src/extractors/router.py` maps `vcf` to source type `contacts` and `src/extractors/long_tail.py` already emits every value of a VCF as potentially sensitive with no exception to enumerate.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `address book` | string | `iCloud - Personal` | `validated` | Which book the cards came from. This is the ONLY field the entry offers as a folder level, because it is a fact about the container rather than about any person, and §2.9 forbids folder proposals built from the rest. Earned from an export filename or a directory corroborated by a confirmed `VCARD` container. |
| `contact name` | string | *(left blank deliberately)* | `direct` | §2.9 names “names” first. An `FN` property is a labelled slot, so the ceiling is §3.13's direct — but the field is metadata-only and never a dimension, on two independent grounds: §2.9's own “rather than used to create folder proposals”, and §3.8's “It should avoid using authorship or creator identity as a destination dimension”. The example is left blank deliberately; a catalogue that ships a specimen person's name has already done the thing this entry exists to prevent. |
| `organisation` | string | *(left blank deliberately)* | `direct` | §2.9 names “organizations”. An `ORG` property is a labelled slot. Metadata only — §3.8 “A folder should not become a collection point for everything produced by the same person or organization”, and §4.9 adds the reading problem: an organisation name in a card is an employer, a client, a supplier and a former employer at once. |
| `email address` | string | *(left blank deliberately)* | `direct` | §2.9 names “email addresses”. Labelled `EMAIL` slot, metadata only, and marked sensitive at emission by `src/extractors/long_tail.py` before it reaches the fact layer. Held so that a thread's participants can be resolved to a role, never so that a folder can be named after someone. |
| `phone number` | string | *(left blank deliberately)* | `direct` | §2.9 names “phone numbers”. Labelled `TEL` slot. §3.10's warning applies to any number-shaped token found OUTSIDE such a slot: documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, so a phone-shaped run in prose is not this field. |
| `postal address` | string | *(left blank deliberately)* | `direct` | An `ADR` property is a labelled slot. §8.4 is why it is worth naming separately from the rest: it names “GPS metadata” among what the corpus can include, and a home address is the same disclosure arrived at by a different route. |
| `address-book metadata` | string | `card revision, group membership, photograph present` | `direct` | §2.9 names “address-book metadata” as its own field. `REV`, `CATEGORIES` and the presence of a `PHOTO` are labelled slots, and they are what let the engine describe a card without reading who it is about — which is the only way this domain can be surfaced in a review interface at all. |
| `export scope` | string | `full export` | `validated` | Whether the file is one shared card or a whole book. It is the difference between a person forwarding a business card and a person's entire social graph sitting in Downloads, and §4.9 makes the second case a protected one: such files “may be surfaced as protected records even when they do not meet a normal group-size threshold”. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a `BEGIN:VCARD` line together with a `VERSION` property and an `FN` property inside the same card — the container declares itself and the two required properties corroborate it
- a repeated `BEGIN:VCARD` / `END:VCARD` pairing through one file — a multi-card export rather than a single shared card, which is the `export scope` field's whole evidence
- a CSV whose column headers match an address-book export header set (a given-name column beside a family-name column beside an email or telephone column) — §2.9 says spreadsheets should yield “sheet names, column headers, visible cell values, table-like regions”, and it is the header SET, not any one header, that identifies the export
- a `.vcf` extension whose content sniff confirms a `VCARD` container — `src/extractors/router.py` maps `vcf` to source type `contacts`, and the sniff is the check that keeps a mislabelled file out of a domain the design wants protected
- a `CATEGORIES` or group property repeated across a run of cards in one file — the format's own distribution-list marker

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- whether an address book is the user's own, a shared team directory, or somebody else's forwarded to them
- a contact list rendered as a document or a scanned page, where OCR yields names and numbers with no container
- deciding whether a card attached to a message is a signature, an introduction or a deliberate transfer of a directory
- reading a bare export with no filename convention and no manifest to say which book produced it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a bare person name — §3.8 “It should avoid using authorship or creator identity as a destination dimension”, and this is the single field the domain must never act on
- a bare email address or phone number
- a `.vcf` extension alone, with no `VCARD` container confirmed by content
- a column header called 'Name' or 'Email' — every export, form response, roster and mailing list in the corpus has one
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”
- a signature block in a message body, which is a contact card in prose and belongs to no domain

### Work types

`single contact card (.vcf)`, `multi-card address-book export`, `address-book CSV export`, `contact group or distribution list`, `shared or forwarded card`, `address-book backup`, `directory or roster document`

### Grouping reasons (§4)

- one address book across the files one export produced
- one export run across the cards it wrote
- one card across its successive revisions, joined by `UID` or `REV`
- one distribution list across the cards that carry its category

### Template (§5)

`address book`

Time first: **no**

§2.9 forbids the obvious template outright — contacts “should normally be privacy-protected rather than used to create folder proposals” — so the only dimension offered is the book the cards came from, which is a fact about a container and not about a person. No per-contact, per-organisation or per-address-domain level appears anywhere in this entry, and §3.8 independently forbids the first two: “A folder should not become a collection point for everything produced by the same person or organization”. §5.5's ordering rule is never reached, because with one level there is nothing to order; `time_first` is false because there is no time dimension to place, not because time lost an argument.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `pers.identity-document` | a card carrying a passport number, a national identifier or a date of birth has stopped being an address book and become an identity record, and the household slice already treats those as protected. The presence of an identifier-shaped labelled property is the separator | §4.9 “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold” |
| `career.networking-and-referrals` | a networking contact list is a working list ABOUT a job search, with notes, dates and next steps beside the names; an address book is a container with none of those. The separator is whether the file carries state about the relationship or only the means of reaching someone | §3.9 “Purpose must be a first-class facet” |
| `comms.email-thread` | a signature block is a contact card in prose and this domain does not claim it — it has no container, no labelled slots and no export scope. It is listed here so that the absence is deliberate rather than an oversight | §3.2 “Raw evidence is not yet a fact” |
| `calendar.events` | an `ATTENDEE` line carries the same values a card carries, and resolving one against the other is exactly the folder proposal §2.9 forbids. The attendee ROLE may be used; the identity behind it may not, in either direction | §2.9 contacts “should normally be privacy-protected rather than used to create folder proposals” |

### Sensitivity

`potentially_sensitive` — §2.9 states the handling itself rather than merely the phrase: contacts “should normally be privacy-protected rather than used to create folder proposals”. `src/extractors/long_tail.py` already implements the whole-file reading — every value of a VCF carries the signal, with no exception to enumerate. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” among what the corpus can include, and a complete address book is the index to most of that list. §2.9's phrase is the whole claim made here — the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> §2.9 says contacts should “normally be privacy-protected rather than used to create folder proposals”, and the word doing the work is `normally`. A user who deliberately keeps a `Contacts/` folder has made the proposal themselves; a user with a stray export in Downloads has not, and the file is identical. Two things follow for Joseph. Whether the exception to `normally` is user-initiated only — the tree may hold contacts if the user puts them there, and may never propose it. And whether an address book should be surfaced in the tree canvas at all or held back the way §7.3's Protected Records are: “it should normally remain local-only and must not cause filenames or content to be exposed in model prompts”. This entry has been written so that either answer works, by offering exactly one dimension that names no person.

---

## `comms.mailbox-archive` — Exported mailboxes and message stores

A whole message store as one file — an mbox, a PST or a platform takeout, which is a corpus wearing a filename.

**Provenance:** **inference** — extends a family the design names

**Cite:** Extends a format §2.9 names. Its email bullet covers “EML, MBOX, MSG, and exported mail archives”, and this entry exists because the last of those four is not the same kind of thing as the first three: a store is not a message, and reading one as a message produces a single file fact where there should be thousands. §2.5's rule for the analogous case is the model this entry follows — “Archives should be inspected without being unpacked to disk”. §5.7 permits the addition: “expand the library as recurring user needs and corpus evidence justify additional coverage”.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `mailbox` | string | `work - archive` | `validated` | Which store this is. Earned from an export filename or manifest corroborated by a confirmed store container; `direct` is refused because most stores carry no labelled name for themselves. |
| `account` | string | *(left blank deliberately)* | `validated` | Whose mailbox it is, resolved against the user's own identities rather than named from a header — §3.8 “The system must separate roles that happen to contain the same entity type”, because a store may be the user's, a shared team box, or somebody else's handed over. The example is blank for the same reason it is blank on `comms.contact-record`. |
| `export date` | date | `2026-06-30` | `direct` | When the export was taken, from the manifest or the container's own creation stamp. It is emphatically NOT the date of the material, which is the trap the template note below turns on. |
| `coverage period` | string | `2019-01 to 2024-06` | `possible` | The span the store actually holds. It cannot be read without unpacking, which §2.5 forbids — “Archives should be inspected without being unpacked to disk” — so where a manifest does not state it the value is §3.13's “A possible fact is a useful but insufficient clue, such as membership in a short download session or a low-confidence semantic match”, and it must not become a folder level. |
| `export scope` | string | `all mail including archive` | `validated` | What was included — one folder, all mail, mail plus attachments. Earned from an export report or manifest. It is the fact that decides whether this store duplicates material already loose in the corpus, which is a §3.11 duplicate-family question rather than a placement one. |
| `store format` | string | `mbox` | `direct` | Which container. §2.9's closing requirement is why it is worth a field of its own: “Every extractor must emit the same evidence shape”, and a store's shape decides whether anything beyond its manifest can be emitted at all. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an `mbox` `From ` separator line occurring repeatedly through one file — a single separator is one message, a repeating one is a store, and the repetition is the context check the separator alone cannot supply
- a PST or OST file signature confirmed by content sniff rather than by extension — §2.9 “The engine should treat the file extension as a routing signal rather than an assumption about meaning”
- a takeout or export manifest at an archive root naming a mail directory, read from the manifest alone — §2.5 “Archives should be inspected without being unpacked to disk”
- an export-report file ('archive summary', 'export complete', a manifest listing message counts) sharing a directory with a store-shaped file
- a directory tree whose folder names reproduce a mail hierarchy (an inbox folder beside a sent folder beside an archive folder) inside one archive manifest

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- whose mailbox a store holds, where the export carries no account name
- whether a store duplicates loose messages already in the corpus, which needs the contents and is therefore blocked by §2.5's own rule
- deciding whether an old store is a working archive or an abandoned backup
- reading an export report written as prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- a large file size — size is a universal file fact under §3.11 and says nothing about a domain
- an `.mbox` or `.pst` extension alone, with no container confirmed by content
- the word 'archive' — `res.repository-deposit`, `gov.archives-recordkeeping` and an ordinary compressed archive are three other readings, and §2.9 gives compressed archives their own handling
- a mail-shaped filename
- a single `From ` line — it is one message, which is `comms.email-thread`'s
- an old modification date

### Work types

`mbox export`, `PST or OST store`, `platform takeout archive`, `mailbox backup`, `export manifest or report`, `extracted message set from a store`, `per-folder store fragment`

### Grouping reasons (§4)

- one mailbox across the files one export produced
- one export run across its store, its manifest and its report
- one account across successive exports of it
- one store and the loose messages later extracted from it

### Template (§5)

`account → export date`

Time first: **no**

§5.5's ordinary rule puts function above time — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — and the account is the function. The export date is second and carries a warning that no other entry in this slice needs: it is not the material's date. A store exported in 2026 holds mail from 2019, so a year level built from the export stamp would file a decade of correspondence under a year in which none of it was written, which is worse than scattering. `coverage period` would be the honest time dimension and it is `possible` at best under §2.5's no-unpacking rule, so no time level is offered from it.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| `comms.email-thread` | the store CONTAINS threads, so every fact of that domain is inside every file of this one. The separator is the container: a file the engine can only read through a manifest is a store, a file whose headers it can read is a message. Extracting the store turns one file into thousands and is a decision, not an extraction step | §2.5 “Archives should be inspected without being unpacked to disk” |
| `law.ediscovery-production` | a mailbox collected for a matter carries a custodian and a production reference, and the law slice owns both. Where those resolve, that domain wins outright and the store must not be re-filed by account | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” |
| `pers.correspondence` | a personal mailbox export is a store of personal letters, and the household slice already lists a message archive export among its work types. The separator is the account's role rather than the container, exactly as it is between `comms.email-thread` and that domain | §3.8 “The system must separate roles that happen to contain the same entity type” |
| `comms.chat-export` | structurally the same problem in a different transport — a container whose contents the engine may not unpack, whose schema fields are therefore read from layout rather than from content. The two entries raise the same open question and should be answered together | §2.9 “Every extractor must emit the same evidence shape” |

### Sensitivity

`potentially_sensitive` — §2.9 states it of the material this file contains: email is to be handled “while treating addresses and message content as potentially sensitive”, and a store is that material in bulk. §8.4 names “private correspondence” among what the corpus can include. The bulk is what sharpens it — a single message exposes one exchange, a store exposes every exchange the account ever had, including material about people who are not the corpus owner. §2.9's phrase is the whole claim; the handling class is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Is a store one file or a corpus? The design has no sentence for a file that contains a corpus. §2.5's “Archives should be inspected without being unpacked to disk” is the nearest analogue and it does not fit cleanly, because an archive has a manifest and an mbox does not — so for the commonest store format the engine can either read nothing or read everything, with no middle setting. Three consequences are Joseph's: whether a store is placed as one opaque object or unpacked into per-thread groups; whether unpacking is a user action rather than an engine one; and whether the loose messages that result are duplicates of the store under §3.11's “duplicate family”, which decides whether both can safely exist in the tree at once.

---
