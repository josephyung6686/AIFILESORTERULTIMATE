# 04 — Personal life, household and media

- **supercategory**: `personal-household`
- **authored**: 2026-08-21
- **entries**: 37
- **contract**: [`_CONTRACT.md`](_CONTRACT.md) · **source of truth**: [`../00-database-agent-product-design.md`](../00-database-agent-product-design.md)
- **consumer**: [`../parts/P6-facts-facets/SPEC.md`](../parts/P6-facts-facets/SPEC.md) — the fact-schema half of every entry lands on P6's deferred *200–300 domain template library* row; the `template` half lands on P10.

Every string between typographic quotes in this file and in the JSON is a **verbatim** fragment of
`00-database-agent-product-design.md`, checked programmatically before either file was written. Prose
outside those marks is this catalogue's own and carries no quotation.

**A note on § numbers.** Section numbers follow the canonical sectioning in
`01-product-design-structured.md`, which `02-segmentation-map.md` names as the design's numbering.
On that numbering the time-first rule and the parent-context rule both sit in **§5.5**
(*Worked example — Academics*), not §5.7, and the photo-branching question sits in **§5.3**, not §5.4.
The brief and `_CONTRACT.md` cite §5.7 and §5.4 for those sentences. The quotes here are verbatim either
way; only the section label differs, and it is set to where the text actually is.

---

## Provenance

| provenance | count | meaning |
|---|---|---|
| `design` | 2 | a design sentence names the domain or its fields |
| `inference` | 14 | extends a design-named domain |
| `proposal` | 21 | new; no design sentence names it |

**design** — `pers.photo-event`, `pers.travel-record`

**inference** — `pers.photo-occasion`, `pers.screenshot`, `pers.scanned-document`, `pers.home-video`, `pers.travel-visa-entry`, `pers.travel-photos`, `pers.household-admin`, `pers.medical-record`, `pers.recipe-meal`, `pers.creative-project`, `pers.correspondence`, `pers.identity-document`, `pers.everyday-finance`, `pers.personal-legal`

**proposal** — `pers.family-photo-archive`, `pers.genealogy`, `pers.utilities`, `pers.insurance`, `pers.vehicle`, `pers.home-tenure`, `pers.moving`, `pers.household-inventory`, `pers.pet`, `pers.dependant-care`, `pers.eldercare`, `pers.fitness-activity`, `pers.hobby-collection`, `pers.music-practice`, `pers.journal`, `pers.gift-occasion`, `pers.estate`, `pers.membership`, `pers.child-school-record`, `pers.volunteering`, `pers.faith-community`

## `template.time_first` — the rule this slice carries

§5.5: “For document and record domains, project, function, or subject usually comes before time
because putting year first scatters related work across calendar folders. Photos and capture-based
media are the major exception: time often belongs first because capture date is a defining aspect of
the material.”

| domain | `time_first` | dimension order | why |
|---|---|---|---|
| `pers.photo-event` | **true** | `capture_year` → `event` | §5.4 states the Photos template literally — “a Photos template may define year → event” — and §5.5 states the reason a capture domain may lead with time: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. Both halves apply here without strain, because the deterministic event is BUILT from capture time, so the parent level is the child's own defining evidence rather than an unrelated calendar imposed on it (§5.5: “a parent dimension should provide the context required to understand the child”). |
| `pers.photo-occasion` | **true** | `capture_year` → `occasion` | §5.4's Photos template is “a Photos template may define year → event”, and §5.5 states the capture exception: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. Year-first also does real work here rather than merely following the rule — occasion labels recur annually, so `Birthday` without a year parent is a colliding branch, which is precisely §5.5's “a parent dimension should provide the context required to understand the child”. |
| `pers.family-photo-archive` | false | `source` → `depicted_period` | This is the capture domain that must NOT lead with time, and the reason is that §5.5's exception is conditional on its own premise — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. Where the capture date is the scan date, leading with it files a nineteen-thirties portrait under the year someone bought a scanner. The available time facts describe the digitising, not the material, so the domain reverts to §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. |
| `pers.screenshot` | false | `captured_subject` | A screenshot is capture-based media by mechanism and a record by meaning, and §5.5's exception is granted for a reason that does not hold here: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. The capture date of a portal screenshot is an accident of when the user pressed the key; §2.7 says what defines it — “a receipt, application portal, conversation, code problem, document, calendar, or research figure”. So this domain takes §5.5's ordinary rule, “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”, and the design's own residual default agrees: §7.3 puts `Temporary Screenshots` in one flat place, not under a year. |
| `pers.scanned-document` | false | `document_type` → `issuer` → `document_date` | The scan is a delivery mechanism, not the subject. §5.5's ordinary rule applies: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Leading with the digitisation date would file a decade of bills under the weekend someone finally scanned them — the exact scattering §5.5 names. |
| `pers.home-video` | **true** | `capture_year` → `event` | §5.5's exception names the category directly — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” — and a home video is capture-based media in exactly that sense: the moment it records is what it is. §5.4's “a Photos template may define year → event” gives the order, and pairing clips with the photographs from the same event keeps one occasion in one place. |
| `pers.genealogy` | false | `ancestor_line` → `subject_person` → `record_type` | A record domain under §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Record year is a search facet here and a poor parent — a marriage, the census that follows it, and the death certificate decades later are one person's file, and year-first scatters exactly that. §5.5's “a parent dimension should provide the context required to understand the child” runs the other way: `birth certificate` is meaningless until the person is known. |
| `pers.travel-record` | false | `trip` → `record_type` | A record domain, so §5.5's ordinary rule applies: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A trip is the function, and its records span the year boundary freely — a December departure and a January return under year-first are two folders for one journey, which is the scattering §5.5 names. The year lives inside the trip label, as §3.12's own value “Japan Trip 2025” already shows. |
| `pers.travel-visa-entry` | false | `holder_role` → `issuing_state` → `permit_type` | A record domain under §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Validity periods overlap and renewals chain, so a year parent splits one continuous permission across folders. §5.5's “a parent dimension should provide the context required to understand the child” puts the holder first because a permit type means nothing until it is known whose it is. |
| `pers.travel-photos` | false | `trip` → `location` | This is the one place in the slice where §5.5's capture exception and §5.5's scattering warning point in opposite directions, and the scattering wins. “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” grants time-first because capture date defines the material; but a trip is itself a bounded time span, so the trip label ALREADY carries the time — §3.12's own value is “Japan Trip 2025”, year included. Putting a year level above it adds nothing and breaks the trips that cross a year boundary, which is literally “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Recorded as an open question because §5.4's Photos template says otherwise. |
| `pers.household-admin` | false | `counterparty` → `matter` | §5.5's ordinary rule for record domains: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A matter that runs across a year boundary is the normal case in household admin, and year-first would split every one of them. §5.5's “a parent dimension should provide the context required to understand the child” puts the counterparty above the matter because matter labels are short and only unique inside a relationship. |
| `pers.utilities` | false | `supply_address` → `utility_type` → `supplier` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The property is the function here, and it is stable while accounts and suppliers change beneath it. Billing period is a strong search facet and a bad parent: year-first would split one supplier relationship across every year it ran. §5.5's “a parent dimension should provide the context required to understand the child” puts the address first because a supplier name means nothing until the property is known in a household with more than one. |
| `pers.insurance` | false | `insured_subject` → `cover_type` → `policy_period` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Policy periods are annual, so year-first looks tempting and is exactly the trap §5.5 names — it separates a claim from the policy year it was made under when the two straddle a renewal. Insured subject first follows “a parent dimension should provide the context required to understand the child”: `renewal notice` means nothing until it is known what was renewed. |
| `pers.vehicle` | false | `vehicle` → `record_type` → `service_date` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The vehicle is the subject and the entire value of the folder is that one vehicle's history sits together — year-first destroys precisely that, which is the scattering §5.5 warns about. §5.5's “a parent dimension should provide the context required to understand the child”: a service invoice is meaningless until the vehicle is known. |
| `pers.home-tenure` | false | `property` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The property is the durable subject; a purchase runs many months and a tenancy many years, so year-first splits single continuous relationships. §5.5's “a parent dimension should provide the context required to understand the child” puts the property above the record type because `notice` and `inventory` are meaningless labels on their own. |
| `pers.moving` | false | `move` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The move is the function, and it is already a bounded time span, so a year parent above it adds a level with one child — which §5.7's validator is told to refuse (“create meaningless one-child levels”). |
| `pers.household-inventory` | false | `item` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A manual is retrieved when the item breaks, which is years after purchase, so the purchase year is the least useful parent available. §5.5's “a parent dimension should provide the context required to understand the child”: `warranty` is meaningless until the item is known. |
| `pers.pet` | false | `animal` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. An animal's history is retrieved as a history — a vaccination schedule and a chronic condition both span years — so year-first scatters exactly what a vet asks to see. §5.5's “a parent dimension should provide the context required to understand the child”: `vaccination record` needs the animal above it. |
| `pers.medical-record` | false | `patient_role` → `body_system_or_specialty` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A condition followed over years is the normal case, and year-first splits one clinical story into calendar fragments — the scattering §5.5 names, at its most harmful. Specialty rather than diagnosis is the deliberate choice for the middle level: §8.4 warns that “a visible list of passport filenames on a shared screen may not be”, and a folder named after a diagnosis is that warning in structural form. |
| `pers.dependant-care` | false | `subject_person_role` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The subject person must be the top dimension or the records merge with the owner's, which is the failure the domain exists to prevent — §5.5's “a parent dimension should provide the context required to understand the child” in its strongest form. Beyond that level the catalogue deliberately stops, because deeper structure states something about the household. |
| `pers.eldercare` | false | `subject_person_role` → `matter` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Care matters run for years and reopen; year-first would break every assessment-to-appeal chain. §5.5's “a parent dimension should provide the context required to understand the child” puts the subject person first because every matter label is meaningless without it. |
| `pers.fitness-activity` | false | `data_source` → `activity_type` → `export_period` | Held at time_first false, and this is the least comfortable of the slice's decisions. A single workout is capture-based and its date is defining, which is exactly §5.5's exception — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. But the material as it actually arrives is a bulk export, one file covering years, and a file cannot sit under a year it spans. Source and activity are the dimensions that describe the file rather than its contents, so §5.5's ordinary rule holds: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A corpus dominated by per-activity track files would justify the opposite order. |
| `pers.recipe-meal` | false | `cuisine_or_category` → `dish` | §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A recipe has no meaningful date at all — the date it was saved is noise — so time is not a candidate dimension here rather than a rejected one. §5.5's “a parent dimension should provide the context required to understand the child” puts category above dish because a dish name is self-describing and a flat list of hundreds is not navigable. |
| `pers.hobby-collection` | false | `pursuit` → `record_type` | §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A collection is retrieved by what is in it, never by when a document about it arrived. §5.5's “a parent dimension should provide the context required to understand the child”: `provenance document` is meaningless until the pursuit and item are known. |
| `pers.music-practice` | false | `instrument_or_voice` → `piece` → `score_type` | §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A piece is returned to for years and a practice recording is retrieved by what it is of, not when it was made. §5.5's “a parent dimension should provide the context required to understand the child”: `part` is a meaningless folder name until the piece and the instrument are known. |
| `pers.creative-project` | false | `project` → `artifact_type` → `stage` | §5.5's ordinary rule, and §5.7 names creative projects among the library's own template subjects: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A creative project runs for years and its drafts are the point, so a year parent would separate a piece from its own revisions. §5.5's “a parent dimension should provide the context required to understand the child”: `draft` needs the artefact above it, which needs the project. |
| `pers.journal` | **true** | `journal` → `entry_date` | time_first is TRUE here, and not by §5.5's capture exception — a journal is not capture-based media. It is true by elimination: the domain has no project, function, or subject dimension, so §5.5's stated harm from leading with time cannot occur. “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” warns that year-first scatters RELATED WORK across calendar folders; in a journal there is no related work to scatter, because the entries are related to each other only by sequence. Where a person keeps more than one journal that name comes first, since §5.5's “a parent dimension should provide the context required to understand the child” makes a date meaningless across two parallel journals. |
| `pers.correspondence` | false | `correspondent_role` → `thread` | §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A correspondence is a relationship that spans years, and year-first cuts every thread that crosses a December. §5.5's “a parent dimension should provide the context required to understand the child” puts the correspondent first because a subject line means nothing without knowing who wrote it. The catalogue deliberately stops at a ROLE rather than proposing a folder per person, for §3.8's reason. |
| `pers.gift-occasion` | false | `occasion` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — planning starts months before and thank-you records land months after, so an occasion routinely straddles a year boundary while the photographs of it do not. This is the sharpest illustration in the slice that ONE real-world event legitimately produces a time-first capture branch and a subject-first record branch, exactly as §5.5's two sentences describe. |
| `pers.estate` | false | `estate` → `estate_role` → `instrument_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Estate documents are separated by decades and belong together; a year parent is the worst available choice, because it puts a will and its codicil in different folders. §5.5's “a parent dimension should provide the context required to understand the child”: `codicil` needs both the estate and the role above it to be readable. |
| `pers.identity-document` | false | `holder_role` → `document_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A credential's validity spans a decade, so year-first is meaningless here; the holder is the only useful first dimension, per §5.5's “a parent dimension should provide the context required to understand the child”. The catalogue stops at two levels deliberately — §8.4 warns that “a visible list of passport filenames on a shared screen may not be”, and deeper structure makes the contents more legible from outside, not less. |
| `pers.membership` | false | `organisation` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A membership is a relationship measured in years, and year-first would fragment one continuous relationship into annual slices — the scattering §5.5 names. §5.5's “a parent dimension should provide the context required to understand the child”: `renewal notice` needs the organisation above it. |
| `pers.everyday-finance` | false | `account_holder_role` → `institution` → `account_type` → `tax_year` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Finance is the domain where year-first is most tempting and §5.5 rules against it: an account relationship runs for years and its documents belong together. Tax year stays as the deepest level, where it is a genuine filing unit rather than a calendar imposed on everything. §5.5's “a parent dimension should provide the context required to understand the child” puts the holder role first because §3.8 requires the owner's money and money managed for another to be distinguishable at the top. |
| `pers.child-school-record` | false | `subject_person_role` → `setting` → `academic_period` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — with a real qualification. School material is genuinely period-structured, so `academic_period` is a strong dimension, but it sits BELOW the setting for exactly §5.5's stated reason: “a parent dimension should provide the context required to understand the child”, and a term label repeats across settings and across children. This mirrors §5.4's Academic template, school → term, without copying its fields. |
| `pers.volunteering` | false | `organisation` → `role` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A volunteering relationship runs for years and its training and clearance records are retrieved as a set. §5.5's “a parent dimension should provide the context required to understand the child”: `hours log` is meaningless without the organisation and role above it. |
| `pers.faith-community` | false | `community` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Participation is a long relationship and its records are retrieved by what they are. The catalogue stops at two levels deliberately: any deeper default would state something about the user's tradition and practice in the shape of their filesystem. |
| `pers.personal-legal` | false | `matter` → `party_role` → `record_type` | §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A matter runs for years and its whole value is that the file sits together; year-first would separate a claim from the order that decided it. §5.5's “a parent dimension should provide the context required to understand the child”: `exhibit` needs the matter above it, and the party role belongs above the documents because it changes what every one of them means. |

**4 of 37 are `true`.** The capture domains that are `false` are the interesting ones: a screenshot,
a scan, an inherited photograph, and a trip photograph are all capture-based media whose capture date
is not what defines them, so §5.5's exception does not reach them.

## Sensitivity

§2.9's phrase `potentially sensitive` is the entire vocabulary used here. **No handling class is
assigned** — those are §8.4's and belong to P7.

| marking | count | domains |
|---|---|---|
| `potentially_sensitive` | 29 | — |
| `none` | 8 | `pers.household-inventory`, `pers.pet`, `pers.recipe-meal`, `pers.hobby-collection`, `pers.music-practice`, `pers.creative-project`, `pers.gift-occasion`, `pers.membership` |

## Open questions — for `NEEDS-JOSEPH.md`

15 of 37 entries carry one. Every one is a place where a default would state something about someone's
real life, or where two design sentences disagree.

### `pers.photo-event`

> Should the deterministic photo event nest under capture year, or stand as a flat list of named events with the year carried inside the label? §5.3 hands this to the user — “whether photographs should branch by year, event, location, or remain mostly flat” — so the order recorded above is a recommendation the tree stage must be able to overturn, not a default the catalogue is entitled to fix.

### `pers.photo-occasion`

> Should occasion photographs branch by the occasion, by the people in them, or stay inside the year? Branching by person makes a folder named after a relative, which is close to the collector pattern §5.7 tells the validator to refuse (“use an author or organization merely as a collector”) and encodes an assumption about whose relationships matter. Joseph's call, not the catalogue's.

### `pers.family-photo-archive`

> Should inherited photographs branch by the person or household they came from, by the period depicted, or by the acquisition event that brought them in? Each encodes a different assumption about whose family this is and how it is reckoned. Joseph's call.

### `pers.screenshot`

> Should the captured subject become a folder level, or stay a search facet with screenshots living flat? §7.3's `Temporary Screenshots` implies flat; §2.7's subject list is exactly the kind of vocabulary that makes good branches. This decides whether a Finder window shows a folder named after what the user screenshots, which is Joseph's call.

### `pers.genealogy`

> Should records concerning living relatives be separated from those concerning the deceased, and if so, does the living branch move under the identity domain's protection? This decides whether a relative's birth certificate sits in a research folder. Joseph's call, and it is a privacy decision as much as a structural one.

### `pers.travel-photos`

> Should trip photographs nest under capture year, as §5.4's “a Photos template may define year → event” prescribes for the Photos template, or under the trip, as the record side does? §5.3 gives the user the choice — “whether photographs should branch by year, event, location, or remain mostly flat” — but the two design sentences pull opposite ways for this domain specifically, and one of them should be named as governing.

### `pers.home-tenure`

> Should owned and rented properties share one branch, or should tenure be the first split? Either choice states something about the household's situation in the shape of their filesystem, and a household that has both is not unusual. Joseph's call — the catalogue records `tenure_type` as a fact and deliberately does not promote it to a folder level.

### `pers.pet`

> Should a multi-animal household get a branch per animal, or one pet branch? A per-animal branch is the right shape for a vet history and the wrong shape for a household with one animal, where it is the one-child level §5.7 tells the validator to refuse (“create meaningless one-child levels”).

### `pers.medical-record`

> Should medical material branch by specialty, by episode, by provider, or stay flat behind one protected node? Each makes some part of a health history legible in a folder name, and §8.4's own example — “a visible list of passport filenames on a shared screen may not be” — says the visibility itself is the risk. Joseph's call, and it should be settled before any default template ships.

### `pers.dependant-care`

> Does a dependant get a named branch of their own, and is it named after them? Both the existence of the branch and its label state something about the household's shape and about a person who did not choose to be in this corpus. Joseph's call; the catalogue deliberately holds the role as a fact and stops short of a default folder.

### `pers.eldercare`

> Is eldercare its own top-level concern, or a branch under the cared-for person alongside their care records? The answer decides whether a filesystem states that someone is being cared for, and by whom. Joseph's call.

### `pers.journal`

> Should journals appear in the proposed tree at all, or be represented without being surfaced? §8.4's own example is that “a visible list of passport filenames on a shared screen may not be”, and a visible `Journals` branch on a shared screen is the same exposure. Joseph's call.

### `pers.everyday-finance`

> §3.11 gives Finance a fact schema while §3.15 makes it a safety domain, “meaning the system detects and protects them before any cloud or automated placement decision is allowed”. P6 SPEC already carries this as an open question. For this slice the unresolved part is narrower: does an ordinary supermarket receipt inherit the whole safety posture because it is a finance record, and if not, what draws the line? Joseph's call.

### `pers.child-school-record`

> Does a child get a named branch, and does the corpus owner's own academic material sit beside it or elsewhere entirely? Both choices encode an assumption about the household, and the label of the branch names a child in a filesystem. Joseph's call; the catalogue holds `subject_person_role` as a fact and proposes no default folder for a person.

### `pers.faith-community`

> Should faith or community life appear as a named top-level branch at all, or only as a facet? A visible branch names a person's tradition on their screen, and §8.4's “a visible list of passport filenames on a shared screen may not be” is the design's own version of that concern. Joseph's call — and it is not a decision this catalogue should make on anyone's behalf.

---

## Entries

### `pers.photo-event` — Photo event

A run of captures that camera identity, capture time, and GPS already show belong to one occasion, before anyone names it.

| | |
|---|---|
| **provenance** | `design` |
| **design cite** | §4.2 “a photo group, it might be a deterministic event created from camera, time, and GPS metadata” · §2.6 “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals” · §3.11 “Photos may use capture year, event, location, people, camera information, and media type” |
| **sensitivity** | `potentially_sensitive` — §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” as material a personal corpus can include; GPS is in that list and is a defining field of this domain. §2.9's phrase “potentially sensitive” is the whole claim made here — the handling class is P7's (§8.4). |
| **work types** | photograph, burst sequence, live photo, raw and jpeg pair, video clip from the same camera, near-duplicate variant |
| **grouping reasons** | • one camera identity across one contiguous stretch of capture time<br>• one GPS locality across one stretch of capture time<br>• a near-duplicate family produced by one exposure<br>• a raw file and its rendered sibling |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `capture_date` | date | `2026-07-17` | `direct` | §3.2 is the worked example for exactly this field: “an EXIF field called DateTimeOriginal is raw metadata”, and “capture date = 2026-07-17” is the file fact derived from it. §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. |
| `capture_year` | year | `2026` | `direct` | §3.11 names `capture_year` as a Photos field: “Photos may use capture year, event, location, people, camera information, and media type”. It is a projection of the direct capture date, not a second observation, so it inherits that ceiling and never outlives it — if capture date is absent, capture year is absent. |
| `event` | string | `Japan Trip 2025` | `validated` | §3.11 names `event`; §4.2 makes it deterministic — “a photo group, it might be a deterministic event created from camera, time, and GPS metadata” — so a rule confirms it and `validated` is earned rather than claimed. §3.12 gives “Japan Trip 2025” as a real value of this field. |
| `location` | string | `Kyoto` | `validated` | §3.11 names `location`. The GPS pair itself is direct EXIF; the place NAME is a gazetteer resolution over it, which is §3.13's “A validated fact was found by a deterministic rule and passed contextual checks”. The coordinate and the label are not the same fact. |
| `camera_information` | string | `Apple iPhone 15 Pro` | `direct` | §3.11 names `camera_information`. EXIF make and model is a labeled metadata slot — §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. |
| `people` | string | — | `user_confirmed` | §3.11 names `people` as a Photos field, and nothing anywhere in the design authorises an automatic producer for it — no face recognition, no contact matching. The only honest ceiling is §3.13's “A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user”. Recorded so the validator legitimises a user-entered value and refuses a model-proposed one. |
| `media_type` | string | `photograph` | `validated` | §3.11 names `media_type`. §2.6's signal hierarchy is a rule, not a guess: “camera EXIF is strong photo evidence”, “capture time, GPS, and sensor-shaped dimensions reinforce it”. Where the bands conflict the field stays unset, because §2.6 requires “conflicting signals should lead to abstention rather than an invented classification”. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • camera make and model EXIF present together with a capture time, on a file whose dimensions reduce to a sensor ratio listed in planning/deferred-catalogues/03-sensor-aspect-ratios.json (list_id `sensor_aspect_ratios`) — §2.6's tier-one band plus its named reinforcement, “camera EXIF is strong photo evidence” and “capture time, GPS, and sensor-shaped dimensions reinforce it”<br>• a run of files sharing one camera identity across contiguous capture times — §4.2's “a photo group, it might be a deterministic event created from camera, time, and GPS metadata”. The window itself is deferred (P6 SPEC, `Photo-event clustering parameters`, G7) and is not set here<br>• a GPS coordinate present in EXIF together with a capture time on the same file, corroborating an already camera-identified run<br>• a filename matching a camera or capture convention in planning/deferred-catalogues/04-camera-filename-patterns.json (list_id `camera_filename_patterns`) together with camera EXIF — the filename alone is never the rule, it is the corroboration<br>• a near-duplicate family established by perceptual hash within one camera-identified run — §2.6: “Exact hashes and perceptual hashes can identify duplicates and near-duplicates” |
| **needs LLM** | • a set of images whose only shared signal is subject matter legible in OCR text, all metadata having been stripped in transit — §2.6 warns that “Messaging platforms and downloaded web images often strip metadata from real photographs”<br>• deciding whether one contiguous capture run is one occasion or two adjacent ones, where the only distinguishing evidence is what is depicted<br>• naming the event in the user's own vocabulary when no folder name, no filename, and no OCR text supplies one |
| **never alone** | • a bare capture date — every file in the corpus has timestamps<br>• a bare GPS coordinate pair with no capture time and no camera identity<br>• a bare place name in a filename<br>• a bare person name<br>• a sensor-shaped aspect ratio on its own — planning/deferred-catalogues/03-sensor-aspect-ratios.json (list_id `sensor_aspect_ratios`) is §2.6's tier-two reinforcement band, not evidence by itself<br>• the ABSENCE of EXIF, in either direction. §2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”. P6 SPEC states the mechanism: absence is never an observation, so no rule may read it |

**Template** — `capture year → event`, `time_first: true`.

> §5.4 states the Photos template literally — “a Photos template may define year → event” — and §5.5 states the reason a capture domain may lead with time: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. Both halves apply here without strain, because the deterministic event is BUILT from capture time, so the parent level is the child's own defining evidence rather than an unrelated calendar imposed on it (§5.5: “a parent dimension should provide the context required to understand the child”).

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.travel-photos` | both are camera captures with GPS. A trip's captures span many days and many localities under one purpose; a photo event is one contiguous capture run. Only the travel case is corroborated by a booking, itinerary, or boarding pass record for the same dates | §4.8 “the model has not invented a date, project, purpose, or membership that the dossier does not support” |
| `pers.screenshot` | the separator is POSITIVE camera evidence, never missing EXIF. A photo event needs camera make and model; a screenshot may be claimed only on §2.6's tier-three band — an exact match in planning/deferred-catalogues/02-screen-resolutions.json (list_id `screen_resolutions`), PNG format, or capture software metadata | §2.6 “the system must not mistake the absence of EXIF for proof that an image is a screenshot” · §2.6 “exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis” |
| `pers.scanned-document` | a photographed page carries real camera EXIF and is therefore a camera capture by every tier-one test, yet it is a document. Dense OCR text does not settle it either way — the separator is whether the depicted content is a document surface, which is an LLM question | §2.6 “receipts, document scans, whiteboards, and photographs of pages can all contain dense text” |

**Open question** — Should the deterministic photo event nest under capture year, or stand as a flat list of named events with the year carried inside the label? §5.3 hands this to the user — “whether photographs should branch by year, event, location, or remain mostly flat” — so the order recorded above is a recommendation the tree stage must be able to overturn, not a default the catalogue is entitled to fix.

---

### `pers.photo-occasion` — Personal photographs of a named occasion

Photographs of a human occasion — a wedding, a graduation, a birthday, a funeral — that the user names, and which may arrive from several cameras and several people.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | Extends the Photos domain of §3.11 (“Photos may use capture year, event, location, people, camera information, and media type”) past the deterministic §4.2 event. No design sentence names an occasion-based photo domain or its fields; the extension is that an occasion is user-named and multi-source where §4.2's event is machine-derived and single-camera. |
| **sensitivity** | `potentially_sensitive` — §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”; GPS is a field of this domain and the depicted people are third parties who never consented to the corpus. §2.9's phrase “potentially sensitive” and no further claim. |
| **work types** | photograph, group portrait, video clip, scanned print contributed by another person, invitation or programme photographed at the occasion, photo-book or album export |
| **grouping reasons** | • one named occasion across every device that captured it<br>• one occasion across captures and the paper artefacts photographed at it<br>• images a participant sent afterwards, joined to the occasion by content rather than metadata |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `occasion` | string | `Graduation` | `user_confirmed` | The occasion label is the domain's reason to exist and cannot be derived from metadata: two cameras at one wedding share nothing but the date. §3.13's “A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user” is the ceiling; an LLM reading OCR'd signage or an invitation may reach `llm_supported` beneath it. |
| `capture_year` | year | `2024` | `direct` | §3.11 names `capture_year`. Where the occasion draws on several devices, the year is the one field every contributor's file agrees on. |
| `event` | string | `Graduation 2024` | `llm_supported` | §3.11's `event` field, reached here through interpretation rather than §4.2's camera, time and GPS rule, because a multi-source occasion breaks the single-camera premise the deterministic rule rests on. |
| `location` | string | `Low Library` | `validated` | §3.11 names `location`. A venue name resolved from GPS or from OCR'd signage against a gazetteer is §3.13's “A validated fact was found by a deterministic rule and passed contextual checks”. |
| `people` | string | — | `user_confirmed` | §3.11 names `people`. Same ceiling and same reason as `pers.photo-event`: the design authorises no automatic producer. |
| `contributor_device` | string | `Canon EOS R6` | `direct` | An occasion assembled from several cameras needs the camera identity kept per file rather than collapsed, or §4.2's event rule silently splits the occasion into one machine event per device. Direct EXIF. |
| `media_type` | string | `photograph` | `validated` | §3.11 names `media_type`; §2.6's signal hierarchy is the rule. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • an existing user-created folder name carrying an occasion word together with camera EXIF on its members — §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal”, and §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent”<br>• several camera identities sharing one capture date and one GPS locality — the multi-device signature the single-camera §4.2 rule cannot produce<br>• a capture run whose OCR text contains an occasion term co-occurring with a date that matches the capture date on the same file |
| **needs LLM** | • naming an occasion from what is depicted when neither folder, filename, nor OCR supplies a label<br>• deciding whether photographs a relative sent by message belong to the same occasion, where the transfer stripped the metadata — §2.6: “Messaging platforms and downloaded web images often strip metadata from real photographs”<br>• separating the occasion itself from the preparation and aftermath captures around it |
| **never alone** | • a bare occasion word in a filename — `wedding.jpg` may be a saved inspiration image, a venue quote, or a meme<br>• a bare date shared by unrelated captures<br>• a bare person name<br>• a bare venue or place name<br>• shared capture date alone across different cameras — two households photographing different things on one afternoon is the common case, not the exception |

**Template** — `capture year → occasion`, `time_first: true`.

> §5.4's Photos template is “a Photos template may define year → event”, and §5.5 states the capture exception: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. Year-first also does real work here rather than merely following the rule — occasion labels recur annually, so `Birthday` without a year parent is a colliding branch, which is precisely §5.5's “a parent dimension should provide the context required to understand the child”.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.photo-event` | one machine event may be a fragment of an occasion, and one occasion may contain many machine events. The deterministic event is evidence FOR the occasion, never a competitor to it — an occasion that contains exactly one camera's contiguous run is the same thing under two names | §4.2 “a photo group, it might be a deterministic event created from camera, time, and GPS metadata” |
| `pers.gift-occasion` | the same occasion generates captures and a record trail — invitations, venue invoices, gift lists. Photographs template time-first; the records do not | §5.5 “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” |
| `pers.family-photo-archive` | an inherited print of an occasion is an archive item whose EXIF is the scan date, not the occasion date; a native capture of the same occasion has a true capture date | §2.6 “the system must not mistake the absence of EXIF for proof that an image is a screenshot” |

**Open question** — Should occasion photographs branch by the occasion, by the people in them, or stay inside the year? Branching by person makes a folder named after a relative, which is close to the collector pattern §5.7 tells the validator to refuse (“use an author or organization merely as a collector”) and encodes an assumption about whose relationships matter. Joseph's call, not the catalogue's.

---

### `pers.family-photo-archive` — Inherited and scanned family photographs

Older photographs that entered the corpus as scans, transfers, or inheritances, where the capture date is unknown, wrong, or the date of scanning.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. §2.6's warning that “Messaging platforms and downloaded web images often strip metadata from real photographs” describes the mechanism, and §3.11's Photos fields supply the vocabulary, but no design sentence names an archival photo domain. Proposed because it is the one capture domain where §5.5's stated reason for time-first — capture date being defining — is exactly what the material lacks. |
| **sensitivity** | `potentially_sensitive` — The people depicted are third parties, frequently including children and frequently deceased, and §8.4's corpus list — “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — covers the identity and record material that arrives in the same inherited box. §2.9's phrase “potentially sensitive” only. |
| **work types** | scanned print, scanned negative or slide, album page scan, photograph of a photograph, digitised home movie frame, restored or retouched copy |
| **grouping reasons** | • one scanning session, evidenced by one scanner signature across contiguous digitisation times<br>• one album or one physical source<br>• one depicted period confirmed by a person<br>• an original scan and its restored copies as a version family |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `depicted_period` | string | `1970s` | `user_confirmed` | The era shown, which is what the material is actually about. It is not the capture date and not the scan date. Nothing in the design authorises deriving it, so §3.13's “A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user” is the ceiling; an LLM reading a handwritten caption may reach `llm_supported`. |
| `digitisation_date` | date | `2019-03-02` | `direct` | The EXIF or filesystem date on an archive scan is the date of DIGITISATION, and recording it under its own name is what stops it being read as the capture date. §3.2's distinction between raw metadata and the fact derived from it is the whole point: “an EXIF field called DateTimeOriginal is raw metadata”. |
| `source` | string | `grandmother's album` | `user_confirmed` | Who or what the material came from is the archive's real organising fact and is only ever supplied by a person. |
| `caption_text` | string | `Summer, Kyoto` | `direct` | Handwriting on a print's reverse, or a caption in an album page scan, recovered by OCR. §2.7 is explicit that OCR is the route into opaque images: “OCR is not merely a rescue tool for scanned PDFs”. The recognised text itself is direct; anything inferred from it is not. |
| `people` | string | — | `user_confirmed` | §3.11 names `people`. Same ceiling as the other photo domains. |
| `media_type` | string | `scanned print` | `validated` | §3.11's `media_type`. A flatbed scan carries scanner software metadata rather than camera EXIF, which §2.6 places outside the tier-one photo band without thereby making it a screenshot. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • scanner software metadata present with no camera make or model — §2.6 puts “exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis” in the weakest band, so this supports `scanned print` only in combination, never alone<br>• a capture-time EXIF value that post-dates the depicted content by an implausible margin, present together with scanner or editing software metadata on the same file<br>• an existing user folder whose name carries an archival or family-album term, over members that share the scanner signature |
| **needs LLM** | • reading a handwritten caption on a print's reverse and deciding whether it names people, a place, or a date<br>• estimating the depicted period from what is shown, which the design permits only as a proposal a person confirms<br>• deciding whether an undated transferred image is an inherited archive item or a recent photograph the sender's platform stripped — §2.6: “Messaging platforms and downloaded web images often strip metadata from real photographs” |
| **never alone** | • absent EXIF — §2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”, and the same refusal applies to reading absence as proof of age<br>• a bare year in a filename<br>• a bare surname<br>• a low pixel count — a small image is as likely to be a thumbnail, an avatar, or a messaging download<br>• sepia or greyscale colour information — a deliberate filter on a recent capture produces the same signal |

**Template** — `source → depicted period`, `time_first: false`.

> This is the capture domain that must NOT lead with time, and the reason is that §5.5's exception is conditional on its own premise — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. Where the capture date is the scan date, leading with it files a nineteen-thirties portrait under the year someone bought a scanner. The available time facts describe the digitising, not the material, so the domain reverts to §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.photo-event` | a scan carries a plausible EXIF timestamp and will satisfy a naive contiguous-capture rule, producing a machine event named after the scanning afternoon. The separator is scanner software metadata against camera make and model | §2.6 “camera EXIF is strong photo evidence” |
| `pers.genealogy` | an inherited photograph and an inherited birth certificate arrive in the same box and the same scanning session. One is a capture, one is a record, and they template in opposite directions | §5.5 “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” |
| `pers.scanned-document` | both are flatbed output with the same scanner signature. The separator is whether the depicted surface is a document, which OCR text density cannot settle — §2.6 lists photographs of pages among the dense-text cases | §2.6 “receipts, document scans, whiteboards, and photographs of pages can all contain dense text” |

**Open question** — Should inherited photographs branch by the person or household they came from, by the period depicted, or by the acquisition event that brought them in? Each encodes a different assumption about whose family this is and how it is reckoned. Joseph's call.

---

### `pers.screenshot` — Screenshots

Captures of a screen, whose meaning is the thing captured rather than the moment of capture.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | Extends §2.6's screenshot hypothesis and §2.7's list of what a screenshot is of — “a receipt, application portal, conversation, code problem, document, calendar, or research figure” — into a domain. §2.1 names the same set for `IMG_4821.png`: “a screenshot of a receipt, application portal, conversation, code error, or research figure”. §7.3's `Temporary Screenshots` is the residual template, not a schema. |
| **sensitivity** | `potentially_sensitive` — The subject is unknown until OCR resolves it, and §2.7's own list includes portals and conversations; §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. A capture of an account page is §8.4's “A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately” case reached through an image. §2.9's phrase “potentially sensitive” and nothing further. |
| **work types** | portal or account status capture, receipt or order confirmation capture, conversation capture, code or error capture, research figure or chart capture, document or form capture, calendar capture, map or directions capture |
| **grouping reasons** | • one captured subject across a session of captures of the same portal or thread<br>• captures that corroborate an accepted group whose other members are records<br>• a repeated capture of one changing status, as a version family |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `captured_subject` | string | `application portal` | `llm_supported` | The field the domain exists for. §2.7 supplies the value set literally: “a receipt, application portal, conversation, code problem, document, calendar, or research figure”. §2.1's list is the same with `code error` for `code problem`. Reaching it requires reading OCR text, which is §3.5's LLM case; the model “can only propose facts that belong to the active domain schema”, so this closed list is the allow-list. |
| `media_type` | string | `screenshot` | `validated` | §3.11's `media_type`. Earned only through §2.6's tier-three band — “Image dimensions, PNG format, software metadata, and known screen resolutions can support a screenshot hypothesis” — with an exact match against planning/deferred-catalogues/02-screen-resolutions.json (list_id `screen_resolutions`). A ratio match from planning/deferred-catalogues/03-sensor-aspect-ratios.json (list_id `sensor_aspect_ratios`) never supports it, and neither does missing EXIF. |
| `capture_date` | date | `2026-07-17` | `direct` | The file's own timestamp. Recorded because §7.3's `Temporary Screenshots` turns on time-sensitivity — “screenshots that appear time-sensitive or remind the user of something but have no accepted project, trip, application, or event relationship” — not because it organises the domain. |
| `source_application` | string | `Safari` | `possible` | Capture software metadata names the capturing tool, and OCR of window chrome may name the application shown. Neither is reliable: the chrome may be cropped and the software string may be a generic editor. §3.13's “A possible fact is a useful but insufficient clue, such as membership in a short download session or a low-confidence semantic match”. |
| `ocr_text` | string | `Application Status: Submitted` | `direct` | The recognised text itself, which §2.7 makes the main route into these files: “OCR is not merely a rescue tool for scanned PDFs”. Direct as recognised output; every conclusion built on it is not. |
| `referenced_record` | string | `order confirmation` | `llm_supported` | A screenshot of a receipt is evidence about a purchase, and this field is what lets it join that group without the image pretending to BE the receipt. §3.6 requires the model to cite the exact OCR region. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • pixel dimensions matching an entry in planning/deferred-catalogues/02-screen-resolutions.json (list_id `screen_resolutions`) exactly, together with PNG format or capture software metadata — §2.6: “Image dimensions, PNG format, software metadata, and known screen resolutions can support a screenshot hypothesis”, and §2.6 keeps the whole band at `may support`<br>• a filename matching a screen-capture convention in planning/deferred-catalogues/04-camera-filename-patterns.json (list_id `camera_filename_patterns`) together with one other tier-three signal. That catalogue records that the English macOS, Windows, and Android defaults are covered and that iOS has NO screenshot filename pattern, because iOS names screenshots exactly as it names camera captures<br>• capture software metadata naming a screen-capture utility, together with the absence of any camera make or model — and the absence is corroboration inside a rule that already fired, never the trigger |
| **needs LLM** | • deciding WHICH of §2.7's subjects a screenshot shows, from OCR text alone<br>• a window grab, a cropped capture, or a downscaled export — planning/deferred-catalogues/02-screen-resolutions.json (list_id `screen_resolutions`) records that an exact-resolution match only fires on a full-screen capture, so these carry arbitrary dimensions and match nothing<br>• a screenshot forwarded through a messaging platform, arriving with dimensions and metadata rewritten<br>• deciding whether the captured subject makes the image part of an accepted group or leaves it residual |
| **never alone** | • missing EXIF. §2.6 is explicit: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”, and “Messaging platforms and downloaded web images often strip metadata from real photographs”<br>• dense OCR text. §2.6: “OCR text density is also not a reliable screenshot detector”, because “receipts, document scans, whiteboards, and photographs of pages can all contain dense text”<br>• PNG format alone — export, download, and design output all produce PNG<br>• a bare capture date<br>• a `Screenshot`-style filename alone, which any user or tool may write on any file<br>• a sensor-shaped ratio from planning/deferred-catalogues/03-sensor-aspect-ratios.json (list_id `sensor_aspect_ratios`) read in reverse as evidence against a screenshot — many panels share a sensor ratio, and planning/deferred-catalogues/02-screen-resolutions.json (list_id `screen_resolutions`) states the arbitration: exact resolution is consulted first and returns at most one signal |

**Template** — `captured_subject`, `time_first: false`.

> A screenshot is capture-based media by mechanism and a record by meaning, and §5.5's exception is granted for a reason that does not hold here: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. The capture date of a portal screenshot is an accident of when the user pressed the key; §2.7 says what defines it — “a receipt, application portal, conversation, code problem, document, calendar, or research figure”. So this domain takes §5.5's ordinary rule, “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”, and the design's own residual default agrees: §7.3 puts `Temporary Screenshots` in one flat place, not under a year.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.photo-event` | a real photograph whose metadata a messaging platform stripped presents as a screenshot to every negative test. The rule must therefore fire on positive tier-three evidence — an exact resolution from planning/deferred-catalogues/02-screen-resolutions.json (list_id `screen_resolutions`) — and never on the absence of camera EXIF | §2.6 “the system must not mistake the absence of EXIF for proof that an image is a screenshot” · §2.6 “Messaging platforms and downloaded web images often strip metadata from real photographs” |
| `pers.scanned-document` | both are dense-text images with no camera EXIF. §2.6 refuses OCR density as the separator; the usable signal is the exact display resolution a scan will not have | §2.6 “OCR text density is also not a reliable screenshot detector” · §2.6 “receipts, document scans, whiteboards, and photographs of pages can all contain dense text” |
| `acad.college-application` | a screenshot of a portal and the portal's own PDF export carry the same OCR text and the same institution name. The PDF is the record; the screenshot is evidence about it. §4.7 treats the portal capture as a purpose clue that helps assemble the packet, not as a second copy of the record | §4.7 “content-incoherent but purpose-coherent” |
| `pers.everyday-finance` | a photographed or captured receipt and a receipt PDF describe one transaction. The image is `captured subject = receipt` with a `referenced_record`; only the PDF carries the issuer's own labeled fields | §7.3 “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” |

**Open question** — Should the captured subject become a folder level, or stay a search facet with screenshots living flat? §7.3's `Temporary Screenshots` implies flat; §2.7's subject list is exactly the kind of vocabulary that makes good branches. This decides whether a Finder window shows a folder named after what the user screenshots, which is Joseph's call.

---

### `pers.scanned-document` — Scanned and photographed documents

A paper document that entered the corpus as an image or an image-only PDF, whose meaning is the document's and not the scan's.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | Extends §2.7's routing rule — “A PDF with no extractable text and evidence of being created from a photographed page can route directly to OCR” — and §2.6's refusal to read dense text as a screenshot signal (“receipts, document scans, whiteboards, and photographs of pages can all contain dense text”) into a domain. No design sentence names a scanned-document domain. |
| **sensitivity** | `potentially_sensitive` — A scan's content is unknown until OCR runs, and §8.4's “A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately” names scanned passports and medical documents specifically. §2.9's phrase “potentially sensitive” only; the class is P7's. |
| **work types** | scanned letter, scanned bill or statement, scanned certificate, photographed form, photographed whiteboard or notebook page, image-only PDF, multi-page scan bundle |
| **grouping reasons** | • one scanning session<br>• one multi-page document across its page images<br>• a scan and the searchable PDF made from it, as a version family |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `document_type` | string | `utility bill` | `llm_supported` | What the scanned page IS, which is the only fact that lets the scan join the group its paper original belongs to. Reached from OCR text, so §3.5's LLM case; the model “can only propose facts that belong to the active domain schema”. |
| `document_date` | date | `2025-11-04` | `validated` | The date printed ON the page, which is not the scan date. §3.10 governs it: “Date extraction should be deliberately narrow” and “The product must not use fuzzy date parsing”. A rule reading a labeled date field beside an issuer name earns §3.13's “A validated fact was found by a deterministic rule and passed contextual checks”. |
| `digitisation_date` | date | `2026-01-09` | `direct` | The scan's own timestamp, named separately so it can never be mistaken for the document date — §3.2's raw-metadata-versus-fact distinction, “an EXIF field called DateTimeOriginal is raw metadata”. |
| `issuer` | string | `City Water Authority` | `validated` | The organisation whose document this is. A gazetteer match under §3.7's “word-boundary matching”, corroborated by a document-structure position rather than a bare mention. |
| `scan_completeness` | string | `ocr complete` | `direct` | §2.7 requires the OCR record to preserve whether extraction was complete or capped. A capped scan is a known-partial fact, not a clean absence, and the difference decides whether an empty field means `not present` or `not read`. |
| `media_type` | string | `scanned document` | `validated` | §3.11's `media_type`. §2.6's hierarchy is the rule, and it must resolve to abstention where bands conflict: “conflicting signals should lead to abstention rather than an invented classification”. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a PDF with no extractable text layer whose page images carry scanner or camera metadata — §2.7: “A PDF with no extractable text and evidence of being created from a photographed page can route directly to OCR”<br>• scanner software metadata together with a page-shaped aspect ratio and OCR output containing a labeled document field such as an account, policy, or invoice label<br>• a multi-page image sequence with contiguous digitisation times and one scanner signature |
| **needs LLM** | • deciding what the scanned page is, from OCR text<br>• a phone photograph of a document, which carries genuine camera EXIF and passes every tier-one photo test — §2.6 lists “receipts, document scans, whiteboards, and photographs of pages can all contain dense text” precisely so this is not settled by text volume<br>• separating one multi-page document from the next inside a single scanning run |
| **never alone** | • dense OCR text — §2.6: “OCR text density is also not a reliable screenshot detector”<br>• missing EXIF — §2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”<br>• a page-shaped aspect ratio, which no entry in planning/deferred-catalogues/03-sensor-aspect-ratios.json (list_id `sensor_aspect_ratios`) claims and which a cropped photograph reproduces freely<br>• a bare date read anywhere on the page<br>• a bare organisation name in OCR text |

**Template** — `document type → issuer → document date`, `time_first: false`.

> The scan is a delivery mechanism, not the subject. §5.5's ordinary rule applies: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Leading with the digitisation date would file a decade of bills under the weekend someone finally scanned them — the exact scattering §5.5 names.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.screenshot` | both are text-dense images with no camera EXIF. §2.6 forbids using text density; the separator is a positive exact-resolution match in planning/deferred-catalogues/02-screen-resolutions.json (list_id `screen_resolutions`) on the screenshot side | §2.6 “OCR text density is also not a reliable screenshot detector” |
| `pers.photo-event` | a photographed page is a camera capture by every tier-one test and will be swept into a contiguous capture run | §2.6 “camera EXIF is strong photo evidence” |
| `pers.medical-record` | a scanned clinic letter is both. The scan facts describe the file; the medical facts describe the content, and §3.1 keeps both — the file is a record of many facts, not one category | §3.11 “target university is not a fact that every file is expected to have” |

---

### `pers.home-video` — Personal video and voice recordings

Video clips and voice memos captured by the household's own devices.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | Extends §2.9's audio and video extractor — “duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present” — and §3.11's Photos fields to moving-image capture. No design sentence names a home-video domain. |
| **sensitivity** | `potentially_sensitive` — §2.9 permits transcripts only “only under an explicit privacy and compute policy”, and §8.4 keeps “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. Speech in a household recording is third-party content. §2.9's phrase “potentially sensitive” only. |
| **work types** | video clip, voice memo, screen recording, live photo motion component, edited compilation, exported render |
| **grouping reasons** | • one camera identity across contiguous capture times<br>• clips belonging to an already-accepted photo event<br>• a source clip and its edited exports, as a version family |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `capture_date` | date | `2026-07-17` | `direct` | §2.9 lists creation time among the fields an audio or video extractor yields; §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field” covers a container metadata slot. |
| `capture_year` | year | `2026` | `direct` | §3.11's `capture_year`, projected from the direct capture date and absent whenever that is. |
| `event` | string | `Japan Trip 2025` | `validated` | §3.11's `event`. A clip sharing camera identity and contiguous capture time with a photo run belongs to the same §4.2 event: “a photo group, it might be a deterministic event created from camera, time, and GPS metadata”. |
| `duration` | duration | — | `direct` | §2.9: “duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present”. Recorded as a fact because it separates a short clip from a long recording without any threshold being set here. |
| `camera_information` | string | `Apple iPhone 15 Pro` | `direct` | §3.11's `camera_information`, from container metadata. |
| `location` | string | `Kyoto` | `validated` | §3.11's `location`, resolved from a GPS track where the container carries one. |
| `transcript` | string | — | `llm_supported` | §2.9 permits speech-to-text “only under an explicit privacy and compute policy”. The permission is conditional in the design and the condition is P7's to enforce, so the field exists but is never populated by default. |
| `media_type` | string | `video` | `validated` | §3.11's `media_type`. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a video or audio container carrying a creation time together with a camera or device make and model<br>• a clip whose camera identity and capture time fall inside an already-established §4.2 photo event<br>• a filename matching a camera video convention in planning/deferred-catalogues/04-camera-filename-patterns.json (list_id `camera_filename_patterns`) together with container camera metadata |
| **needs LLM** | • deciding what a clip is of, where a transcript is permitted and produced<br>• separating a household recording from a downloaded or forwarded video with rewritten metadata |
| **never alone** | • a bare duration<br>• a bare creation time — every container has one, including downloads<br>• a video codec or container format, which says nothing about origin<br>• missing camera metadata, for the reason §2.6 gives: “the system must not mistake the absence of EXIF for proof that an image is a screenshot” |

**Template** — `capture year → event`, `time_first: true`.

> §5.5's exception names the category directly — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” — and a home video is capture-based media in exactly that sense: the moment it records is what it is. §5.4's “a Photos template may define year → event” gives the order, and pairing clips with the photographs from the same event keeps one occasion in one place.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.screenshot` | a screen recording is a video by container and a screen capture by meaning, and it carries no camera metadata. It follows the screenshot domain's rule — a positive display-resolution match from planning/deferred-catalogues/02-screen-resolutions.json (list_id `screen_resolutions`), never absent camera data | §2.6 “the system must not mistake the absence of EXIF for proof that an image is a screenshot” |
| `pers.music-practice` | a practice recording is a voice memo by format. The separator is a piece and instrument context in filename or folder, not the container | §3.5 “can only propose facts that belong to the active domain schema” |

---

### `pers.genealogy` — Family history and genealogy records

Vital records, trees, and research notes about ancestry, assembled deliberately rather than accumulated.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names genealogy. Proposed as a distinct domain because the records arrive with the material in `pers.family-photo-archive` yet template in the opposite direction, and because a birth certificate for a living person is §3.15 identity material while the same document for an ancestor is research. |
| **sensitivity** | `potentially_sensitive` — §8.4's corpus list includes “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”, and genealogical material carries identity documents for living relatives who are not the corpus owner. §2.9's phrase “potentially sensitive” only. |
| **work types** | vital record scan, census extract, family tree export, research log, correspondence with an archive, DNA test result, written family narrative |
| **grouping reasons** | • one ancestral line<br>• one research question across its sources<br>• one archive request and the records it returned |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `record_type` | string | `birth certificate` | `llm_supported` | The kind of vital record. §3.11 already uses `record_type` in the Finance row (“Finance files may use institution, account type, tax year, and record type”); the same field name under a different active schema takes this domain's values, which is what §3.11's per-domain activation is for. |
| `ancestor_line` | string | `maternal` | `user_confirmed` | Which line the record belongs to. Only a person can state it, and stating it is what turns a pile of certificates into a tree. |
| `subject_person` | string | — | `user_confirmed` | Whom the record is about. §3.8's role rule matters here: the subject of a certificate, the informant on it, and the researcher who obtained it are three different roles and must not collapse — “A finance document may mention an account holder and an issuing bank” is the design's own example of the same failure in another domain. |
| `record_year` | year | `1897` | `validated` | The year printed on the record. §3.10 governs it: “Date extraction should be deliberately narrow”. |
| `repository` | string | `national archives` | `validated` | Where the record came from — an archive, a registry, a subscription research service. A gazetteer match under §3.7's “word-boundary matching” corroborated by a reference or citation number on the same page. |
| `research_status` | string | `unverified` | `user_confirmed` | Genealogy's defining discipline is the distinction between a sourced record and a hypothesis, and a system that files them together destroys it. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a genealogy interchange file format, or a research-service export naming a tree, together with person records inside it<br>• OCR text carrying a vital-record heading together with a registry or district identifier on the same page<br>• an existing user folder carrying a family-history term over members that are certificates and tree exports — §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal” |
| **needs LLM** | • deciding whether a scanned certificate concerns a living person or an ancestor, which decides whether it is this domain or `pers.identity-document`<br>• reading an unlabeled handwritten record<br>• separating research notes about an ancestor from correspondence with a living relative |
| **never alone** | • a bare surname — the corpus owner's own surname appears on everything they own<br>• a bare year, especially an early one, which is as likely a course code, a catalogue number, or a scan artefact<br>• a bare place name<br>• the word `family` in a path |

**Template** — `ancestor line → subject person → record type`, `time_first: false`.

> A record domain under §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Record year is a search facet here and a poor parent — a marriage, the census that follows it, and the death certificate decades later are one person's file, and year-first scatters exactly that. §5.5's “a parent dimension should provide the context required to understand the child” runs the other way: `birth certificate` is meaningless until the person is known.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.identity-document` | the same document type — a birth or marriage certificate — is a live identity credential for a living holder and a research source for an ancestor. The separator is whether the subject person is living, which is a fact no rule can read off the page | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `pers.family-photo-archive` | one inherited box yields both, in one scanning session with one scanner signature. Records template subject-first, captures do not | §5.5 “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” |
| `pers.estate` | probate files, wills, and death certificates serve an estate matter while it is live and become genealogy sources afterwards | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |

**Open question** — Should records concerning living relatives be separated from those concerning the deceased, and if so, does the living branch move under the identity domain's protection? This decides whether a relative's birth certificate sits in a research folder. Joseph's call, and it is a privacy decision as much as a structural one.

---

### `pers.travel-record` — Travel records

The paperwork of a trip — bookings, itineraries, confirmations, boarding passes, and receipts — held together by the trip rather than by content type.

| | |
|---|---|
| **provenance** | `design` |
| **design cite** | §3.3 “application essay, research artifact, recruiting document, travel record, or other supported domain” · §5.7 “financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” · §7.3 “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” |
| **sensitivity** | `potentially_sensitive` — Boarding passes and bookings carry passport and identity numbers, and §7.3's `Protected Records` names “passport scans, medical documents, account statements, visas, legal forms, or credentials” with visas among them. §2.9's phrase “potentially sensitive” only. |
| **work types** | itinerary, flight or rail booking, accommodation booking, boarding pass, travel insurance certificate, car hire agreement, tour or activity ticket, expense receipt, packing or planning note |
| **grouping reasons** | • one trip across every record type it produced<br>• one booking reference across confirmation, change, and receipt<br>• an original booking and its amended reissues, as a version family |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `trip` | string | `Japan Trip 2025` | `validated` | The trip is the domain's organising fact, and §3.12 gives “Japan Trip 2025” as a literal example value the system may create: “The system may create new values when it sees a new course, project, company, university, or event”. |
| `travel_dates` | date range | `2025-03-04 to 2025-03-18` | `validated` | Departure and return, read from labeled booking fields. §3.10 governs the parsing: “The product must not use fuzzy date parsing”. A rule reading a labeled date beside a carrier or property name earns “A validated fact was found by a deterministic rule and passed contextual checks”. |
| `destination` | string | `Kyoto` | `validated` | Where the trip goes. A gazetteer match under §3.7's “word-boundary matching”, corroborated by a booking context — the bare place name is refused below. |
| `provider` | string | — | `validated` | The airline, rail operator, hotel, or agency. §3.8's role rule applies: the provider, the traveller, and the payer are three roles, not one entity field — “A finance document may mention an account holder and an issuing bank”. |
| `booking_reference` | string | — | `direct` | A labeled reference on a confirmation is §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field” — a labeled form field. It is also the strongest join between an itinerary, a receipt, and a boarding pass for one trip. |
| `record_type` | string | `boarding pass` | `llm_supported` | §7.3 names the members literally: “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents”. A labeled document may reach `validated`; an unlabeled confirmation email needs interpretation. |
| `traveller_role` | string | `self` | `user_confirmed` | §3.8 requires roles to be separate fields. A booking made for someone else is not the corpus owner's travel record, and only a person can settle it. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a booking reference in a labeled field together with a carrier, property, or agency name and a labeled travel date on the same document<br>• an itinerary structure — paired origin and destination with departure and arrival times — inside one document<br>• a calendar file whose event carries a travel term together with a location, using §2.9's calendar fields: “event title, start and end time, location, organizer, attendees, and recurrence metadata”<br>• an existing user folder named for a trip over members that carry booking references — §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal” |
| **needs LLM** | • a confirmation email whose only travel signal is prose<br>• deciding whether a hotel receipt belongs to a leisure trip, a work trip, or a relocation<br>• assembling a heterogeneous trip packet, which is §4.7's purpose case: “content-incoherent but purpose-coherent” |
| **never alone** | • a bare place name — a destination word appears in news clippings, recipes, and course readings<br>• a bare date or date range<br>• a bare airline or hotel brand name, which appears in advertising, loyalty mail, and unrelated receipts<br>• a bare reference code, which is shaped like an order number, a case number, and a ticket number alike<br>• a bounded download session — §3.9: “It is a purpose clue and a review aid, not a basis for automatic semantic propagation”, and §4.7 repeats it for purpose packets |

**Template** — `trip → record type`, `time_first: false`.

> A record domain, so §5.5's ordinary rule applies: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A trip is the function, and its records span the year boundary freely — a December departure and a January return under year-first are two folders for one journey, which is the scattering §5.5 names. The year lives inside the trip label, as §3.12's own value “Japan Trip 2025” already shows.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.travel-photos` | one trip produces both, and both legitimately carry `trip`. Records carry a booking reference and a provider; captures carry camera identity and capture time. They template in opposite directions, so the trip must be able to hold two differently shaped children | §5.5 “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” |
| `pers.everyday-finance` | a travel expense receipt is both a trip record and a transaction. §7.3's `Receipts and Confirmations` holds the ones with no trip to join | §7.3 “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” |
| `pers.travel-visa-entry` | a visa is trip paperwork and an identity credential. It follows the identity side's protection, not the trip's convenience | §7.3 “passport scans, medical documents, account statements, visas, legal forms, or credentials” |
| `pers.moving` | a one-way flight, a shipping booking, and a temporary hotel stay are indistinguishable from travel until the purpose is known | §3.9 “Purpose must be a first-class facet” |

---

### `pers.travel-visa-entry` — Visas, permits and entry documents

Immigration paperwork — visas, entry and residence permits, sponsorship letters, and the applications behind them.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | Extends §3.15's identity safety domain (“Finance, identity, medical, and legal material should be implemented first as safety domains”) and §7.3's `Protected Records`, which names “passport scans, medical documents, account statements, visas, legal forms, or credentials” with visas listed literally. No design sentence gives it fields. |
| **sensitivity** | `potentially_sensitive` — §7.3's `Protected Records` names visas literally among “passport scans, medical documents, account statements, visas, legal forms, or credentials”, and adds that “it should normally remain local-only and must not cause filenames or content to be exposed in model prompts”. §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §2.9's phrase “potentially sensitive” and no class. |
| **work types** | visa or permit grant, application form, supporting letter, sponsorship document, biometric appointment record, refusal or appeal letter, entry or exit stamp scan |
| **grouping reasons** | • one application from filing to decision<br>• one permit and its renewals, as a version family<br>• one holder across the permits held |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `permit_type` | string | `student visa` | `llm_supported` | The class of permission. §3.5's LLM case, bounded: the model “can only propose facts that belong to the active domain schema”. |
| `issuing_state` | string | — | `validated` | The state or authority granting it — a gazetteer match corroborated by an immigration document structure, per §3.7's “word-boundary matching”. |
| `validity_period` | date range | — | `validated` | Valid-from and valid-to, read from labeled fields. §3.10: “Date extraction should be deliberately narrow”. This is the field that makes an expiry surface possible without any threshold being set here. |
| `application_stage` | string | `granted` | `llm_supported` | Applied, granted, refused, renewed, appealed. A refusal filed beside a grant without this field is a silent error with real consequences. |
| `holder_role` | string | `self` | `user_confirmed` | §3.8 requires roles as separate fields. A sponsor's document and a dependant's document are not the holder's — “It should avoid using authorship or creator identity as a destination dimension” is the same principle applied to placement. |
| `sponsor` | string | — | `llm_supported` | The employer, institution, or person sponsoring. §3.8's role separation again: sponsor and holder are distinct fields. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • OCR text carrying a visa or permit heading together with a labeled validity date and an issuing authority on the same document<br>• a machine-readable-zone structure detected in OCR output together with a document-type label<br>• an immigration case or application reference in a labeled field together with an authority name |
| **needs LLM** | • correspondence about an application whose only signal is prose<br>• deciding whether a document is the grant, the application, or a supporting letter<br>• multilingual immigration documents, which §3.3 names among the cases fixed patterns cannot cover |
| **never alone** | • a bare country name<br>• a bare date range<br>• a bare reference number<br>• a passport-shaped scan, which is the identity domain and not this one until a permit label is present |

**Template** — `holder role → issuing state → permit type`, `time_first: false`.

> A record domain under §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Validity periods overlap and renewals chain, so a year parent splits one continuous permission across folders. §5.5's “a parent dimension should provide the context required to understand the child” puts the holder first because a permit type means nothing until it is known whose it is.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.travel-record` | a visa is obtained for a trip and files naturally beside its bookings, but §7.3 puts visas in `Protected Records` and travel bookings do not carry that constraint | §7.3 “passport scans, medical documents, account statements, visas, legal forms, or credentials” |
| `pers.identity-document` | a passport scan submitted with a visa application is an identity document appearing inside an immigration packet — §3.11's multi-domain case, where both fact sets are kept | §3.11 “target university is not a fact that every file is expected to have” |
| `acad.college-application` | a student visa packet and a university application packet share transcripts, financial evidence, and the institution name. §4.8 requires that a packet not absorb a document with a conflicting target | §4.8 “the model has not invented a date, project, purpose, or membership that the dossier does not support” |

---

### `pers.travel-photos` — Trip photographs

Photographs and clips captured during a trip, which carry both the Photos fields and the trip.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | Extends §3.11's Photos fields (“Photos may use capture year, event, location, people, camera information, and media type”) with the trip that §3.12 already uses as a value — “Japan Trip 2025”. §3.3 names “application essay, research artifact, recruiting document, travel record, or other supported domain”, so the record side is design-named and this is its capture counterpart. |
| **sensitivity** | `potentially_sensitive` — §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and GPS metadata is in it; travel captures are the densest GPS material in a personal corpus. §2.9's phrase “potentially sensitive” only. |
| **work types** | photograph, video clip, panorama, screenshot of a map or ticket taken during the trip, paper ephemera photographed on the trip |
| **grouping reasons** | • one trip across all its captures<br>• one segment or locality inside a trip<br>• captures joined to a booking record by falling inside its travel dates |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `trip` | string | `Japan Trip 2025` | `validated` | Shared with `pers.travel-record`, which is what lets the bookings and the photographs recognise each other. §3.12's own example value. |
| `capture_date` | date | `2025-03-09` | `direct` | §3.2's worked case: “capture date = 2026-07-17” derived from “an EXIF field called DateTimeOriginal is raw metadata”. |
| `capture_year` | year | `2025` | `direct` | §3.11's `capture_year`. |
| `location` | string | `Kyoto` | `validated` | §3.11's `location`, resolved from EXIF GPS against a gazetteer — the coordinate is direct, the label is the rule's output. |
| `event` | string | `Fushimi Inari` | `validated` | §3.11's `event`. A trip contains many §4.2 events: “a photo group, it might be a deterministic event created from camera, time, and GPS metadata”. Keeping both means the trip does not flatten its own internal structure. |
| `camera_information` | string | — | `direct` | §3.11's `camera_information`. |
| `people` | string | — | `user_confirmed` | §3.11's `people`; no automatic producer exists in the design. |
| `media_type` | string | `photograph` | `validated` | §3.11's `media_type`, from §2.6's hierarchy. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • camera EXIF with GPS coordinates falling outside the corpus owner's habitual localities, across capture times that fall inside a travel date range already established by a booking record<br>• a §4.2 photo event whose capture dates lie inside a validated `travel_dates` range on a record in `pers.travel-record`<br>• an existing user folder named for a trip containing camera-EXIF-bearing files — §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent” |
| **needs LLM** | • photographs a companion sent afterwards, arriving stripped — §2.6: “Messaging platforms and downloaded web images often strip metadata from real photographs”<br>• deciding whether captures around the trip's edges belong to the trip or to home<br>• naming the segment a run of captures belongs to, where GPS is absent |
| **never alone** | • a GPS coordinate outside the home locality, on its own — a day out is not a trip<br>• a bare capture date inside a travel range, on a file with no camera evidence<br>• a bare place name in a filename<br>• a bare person name<br>• a folder named for a country, which is as likely a reading list, a language course, or a recipe collection |

**Template** — `trip → location`, `time_first: false`.

> This is the one place in the slice where §5.5's capture exception and §5.5's scattering warning point in opposite directions, and the scattering wins. “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” grants time-first because capture date defines the material; but a trip is itself a bounded time span, so the trip label ALREADY carries the time — §3.12's own value is “Japan Trip 2025”, year included. Putting a year level above it adds nothing and breaks the trips that cross a year boundary, which is literally “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Recorded as an open question because §5.4's Photos template says otherwise.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.travel-record` | same trip, opposite shape. The record side is booking references and providers; this side is camera identity and capture time. §4.8's validator must not let a capture inherit a trip from proximity alone | §4.8 “the model has not invented a date, project, purpose, or membership that the dossier does not support” |
| `pers.photo-event` | every trip capture is also a §4.2 event, and a machine event has no idea it is on a trip. The trip fact must come from a record or a folder name, never from the coordinates alone | §4.2 “a photo group, it might be a deterministic event created from camera, time, and GPS metadata” |
| `pers.photo-occasion` | a wedding abroad is both an occasion and a trip, and both labels are correct. §3.11 keeps both rather than choosing | §3.11 “target university is not a fact that every file is expected to have” |

**Open question** — Should trip photographs nest under capture year, as §5.4's “a Photos template may define year → event” prescribes for the Photos template, or under the trip, as the record side does? §5.3 gives the user the choice — “whether photographs should branch by year, event, location, or remain mostly flat” — but the two design sentences pull opposite ways for this domain specifically, and one of them should be named as governing.

---

### `pers.household-admin` — Household administration

The running correspondence and paperwork of a household that belongs to no single account, property, or policy.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §5.7 names “financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections”, which includes personal administration in the library the product should eventually carry. The name is design-given; the fields are not. |
| **sensitivity** | `potentially_sensitive` — §8.4's corpus list — “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — covers the account and identity material that routine household letters quote. §2.9's phrase “potentially sensitive” only. |
| **work types** | letter, form, confirmation, notice, statement, application, reply or complaint, meeting or call note |
| **grouping reasons** | • one matter from opening to resolution<br>• one counterparty across an ongoing relationship<br>• one reference across the documents that quote it |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `counterparty` | string | `local council` | `validated` | The organisation on the other side. §3.8 requires the role to be its own field rather than a generic organisation mention — “A finance document may mention an account holder and an issuing bank” is the design's example of the same separation. |
| `matter` | string | `council tax banding` | `llm_supported` | What the exchange is about, which is the domain's organising fact and cannot be read from a letterhead. §3.5's LLM case, bounded by “can only propose facts that belong to the active domain schema”. |
| `reference` | string | — | `direct` | An account, case, or customer reference in a labeled field — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. It is the only reliable join between a letter, its reply, and the payment that settled it. |
| `document_date` | date | `2025-09-30` | `validated` | The date printed on the document, parsed under §3.10's “Date extraction should be deliberately narrow”. |
| `record_type` | string | `letter` | `llm_supported` | §7.3's `Independent Records` describes the shape of the residual case — “standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader group” — and this field is what lets a document escape that residual by naming what it is. |
| `action_state` | string | `awaiting reply` | `user_confirmed` | Household admin is defined by whether something is still outstanding, and §7.3's `Review Later` exists for exactly the case of “files whose meaning is partly understood but whose final location requires a future decision”. Only a person settles it. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a labeled account or case reference together with a known institution name in a letterhead position — §3.7's “positional weighting” is what makes the letterhead worth more than a footer mention<br>• a document structure carrying both a labeled reference and a labeled document date, with no policy, tenancy, or utility identifier that would route it to a narrower domain<br>• an existing user folder carrying an administration term over members that share one counterparty |
| **needs LLM** | • deciding what a letter is actually about when the subject line is a reference number<br>• separating a genuine administrative matter from marketing sent by the same counterparty<br>• recognising a matter that spans several counterparties |
| **never alone** | • a bare organisation name<br>• a bare reference number<br>• a bare date<br>• a bare download session — §3.9: “It is a purpose clue and a review aid, not a basis for automatic semantic propagation”<br>• the word `admin` in a path, which is as likely a software directory as a household one |

**Template** — `counterparty → matter`, `time_first: false`.

> §5.5's ordinary rule for record domains: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A matter that runs across a year boundary is the normal case in household admin, and year-first would split every one of them. §5.5's “a parent dimension should provide the context required to understand the child” puts the counterparty above the matter because matter labels are short and only unique inside a relationship.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.utilities` | a utility letter is household admin until a meter or supply identifier appears; that identifier is what earns it the narrower domain | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.correspondence` | a letter from an institution and a letter from a friend are both correspondence. Only the institutional one carries a labeled reference and a counterparty that resolves in a gazetteer | §3.8 “A finance document may mention an account holder and an issuing bank” |
| `pers.personal-legal` | a complaint escalates into a legal matter without any change in file format. The separator is a case or claim number issued by a court or an ombudsman | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |

---

### `pers.utilities` — Utility accounts and supply records

Bills, meter readings, tariffs, and supply correspondence for a service delivered to a property.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. §5.7's personal administration is the nearest design-named slot, and §3.11's Finance row supplies the shape of an account-bearing schema (“Finance files may use institution, account type, tax year, and record type”), but no design sentence names utilities or its fields. |
| **sensitivity** | `potentially_sensitive` — A utility bill is the standard proof-of-address document and carries the account holder's name and home address; §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §2.9's phrase “potentially sensitive” only. |
| **work types** | bill, meter reading record, tariff or price notice, switch confirmation, final statement, supply fault correspondence, annual statement |
| **grouping reasons** | • one account across its billing periods<br>• one property across the utilities serving it<br>• a switch, joining the closing account to the opening one |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `supplier` | string | — | `validated` | The utility company. A gazetteer match under §3.7's “word-boundary matching”, corroborated by a bill structure rather than a bare mention. |
| `utility_type` | string | `electricity` | `llm_supported` | Electricity, gas, water, broadband, refuse, and so on. What makes a supplier switch tractable — the account changes, the utility does not. |
| `supply_address` | string | — | `validated` | The property served. §3.8's role rule: the supply address, the billing address, and the account holder's address are three roles and are not interchangeable. |
| `account_identifier` | string | — | `direct` | The account, meter point, or supply number in a labeled field — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. It survives a tariff change and a supplier rebrand, which no other field does. |
| `billing_period` | date range | — | `validated` | The period the document covers, not the date it was issued. §3.10's “Date extraction should be deliberately narrow” governs the parse. |
| `record_type` | string | `bill` | `llm_supported` | Bill, meter reading, tariff notice, switch confirmation, final statement. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a labeled account or meter identifier together with a supplier name and a labeled billing period on one document<br>• a utility-specific labeled unit — a meter serial, a supply point reference — together with a supply address<br>• a supplier name in a letterhead position together with a labeled billing period, per §3.7's “positional weighting” |
| **needs LLM** | • a switching or tariff letter that quotes no account number<br>• deciding which property a bill serves where a household holds more than one<br>• separating a genuine bill from a marketing comparison sent in the same envelope |
| **never alone** | • a bare supplier name — energy and broadband brands appear in advertising and in unrelated news<br>• a bare address<br>• a bare account-shaped number<br>• a bare month or date range |

**Template** — `supply address → utility type → supplier`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The property is the function here, and it is stable while accounts and suppliers change beneath it. Billing period is a strong search facet and a bad parent: year-first would split one supplier relationship across every year it ran. §5.5's “a parent dimension should provide the context required to understand the child” puts the address first because a supplier name means nothing until the property is known in a household with more than one.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.everyday-finance` | a utility direct-debit line appears on a bank statement and the bill appears in this domain. The statement belongs to the account it is from, not to the utility it mentions | §3.8 “It should avoid using authorship or creator identity as a destination dimension” |
| `pers.home-tenure` | a tenancy pack contains utility set-up documents for the property, and the same property identifier appears in both | §3.9 “Purpose must be a first-class facet” |
| `pers.moving` | final and opening utility statements are generated by a move and belong to it as much as to the account | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |

---

### `pers.insurance` — Insurance policies and claims

Policies, schedules, renewals, and claims for anything insured — property, vehicle, travel, health, life.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names insurance. Proposed because a claim is a purpose-coherent packet in §3.9's sense — policy, evidence photographs, correspondence, and a settlement — that no other domain in this slice can hold together. |
| **sensitivity** | `potentially_sensitive` — Policies carry addresses, dates of birth, and — for health and life cover — medical answers; §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §2.9's phrase “potentially sensitive” only. |
| **work types** | policy schedule, certificate of insurance, renewal notice, quotation, claim form, loss evidence, settlement or decline letter, no-claims proof |
| **grouping reasons** | • one policy across its renewals, as a version family<br>• one claim from notification to settlement<br>• one insured subject across the policies covering it |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `insurer` | string | — | `validated` | The underwriter or provider. §3.8's role rule separates insurer, broker, policyholder, and insured — four roles that a naive organisation field would collapse (“A finance document may mention an account holder and an issuing bank”). |
| `policy_number` | string | — | `direct` | A labeled policy reference is §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field” and is the join between a schedule, a renewal, and a claim. |
| `cover_type` | string | `home contents` | `llm_supported` | What is insured. The field that keeps a travel policy and a home policy apart when both come from one insurer. |
| `policy_period` | date range | — | `validated` | Cover start and end, from labeled fields, parsed under §3.10's “Date extraction should be deliberately narrow”. |
| `insured_subject` | string | — | `llm_supported` | The property, vehicle, trip, or person covered. This is what lets an insurance record join the vehicle or property it belongs to without leaving this domain. |
| `claim_reference` | string | — | `direct` | A labeled claim reference, distinct from the policy number, because a claim is its own matter with its own life. |
| `record_type` | string | `policy schedule` | `llm_supported` | Schedule, certificate, renewal notice, claim form, loss evidence, settlement letter. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a labeled policy number together with an insurer name and a labeled cover period on one document<br>• a labeled claim reference together with an insurer name and a loss or incident date<br>• a certificate structure carrying an insured subject identifier — a vehicle registration, a property address — beside a policy number |
| **needs LLM** | • a quotation that may or may not have become a policy<br>• photographs submitted as loss evidence, which are camera captures with no insurance metadata at all<br>• deciding whether a renewal supersedes a policy or opens a new one |
| **never alone** | • a bare insurer brand name, which saturates advertising and comparison mail<br>• a bare reference number<br>• a bare date range<br>• the word `policy`, which appears in privacy notices, workplace handbooks, and terms of service |

**Template** — `insured subject → cover type → policy period`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Policy periods are annual, so year-first looks tempting and is exactly the trap §5.5 names — it separates a claim from the policy year it was made under when the two straddle a renewal. Insured subject first follows “a parent dimension should provide the context required to understand the child”: `renewal notice` means nothing until it is known what was renewed.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.vehicle` | a motor policy carries the vehicle registration and belongs to both. The registration is the shared value; the policy number is what keeps the insurance record its own thing | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.travel-record` | §7.3 lists travel insurance among trip paperwork, and a single-trip policy genuinely belongs to the trip while an annual multi-trip policy does not | §7.3 “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” |
| `pers.medical-record` | a health insurance claim quotes diagnoses and treatment records, carrying medical content into an insurance file | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `pers.photo-event` | loss-evidence photographs are camera captures and will form a §4.2 event of their own unless the claim can hold them | §4.2 “a photo group, it might be a deterministic event created from camera, time, and GPS metadata” |

---

### `pers.vehicle` — Vehicle ownership and service records

Everything that follows one vehicle — purchase, registration, servicing, tests, tax, and disposal.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names vehicles. Proposed because the vehicle identifier is one of the few genuinely stable, checkable joins in a personal corpus, and because service history is material that must survive a change of owner. |
| **sensitivity** | `potentially_sensitive` — Registration documents carry the keeper's name and home address, and §8.4's corpus list — “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — covers identity material of this kind. §2.9's phrase “potentially sensitive” only. |
| **work types** | purchase or sale record, registration document, service invoice, roadworthiness test certificate, tax or duty record, warranty document, parts receipt, fine or penalty notice |
| **grouping reasons** | • one vehicle across its whole history<br>• one service visit across invoice, report, and receipt<br>• one ownership period |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `vehicle` | string | — | `validated` | The vehicle itself, identified by a registration or chassis identifier. A rule may confirm it because such identifiers have a checkable structure AND appear beside vehicle context — the pattern alone is refused below. |
| `service_date` | date | `2025-06-12` | `validated` | When work was done, from a labeled field on an invoice or record. §3.10's “Date extraction should be deliberately narrow”. |
| `provider` | string | — | `validated` | The garage, dealer, or testing station. §3.8's role rule: provider, owner, and registered keeper are separate fields — “A finance document may mention an account holder and an issuing bank”. |
| `odometer_reading` | string | — | `direct` | A labeled reading on a service or test record, which is what makes a service history verifiable and is a labeled form field under §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. |
| `record_type` | string | `service invoice` | `llm_supported` | Service, roadworthiness test, tax, registration, insurance certificate, purchase, sale. |
| `ownership_period` | date range | — | `user_confirmed` | When the household owned it. Records from before purchase arrive with the vehicle and are genuinely part of its history without being the owner's own transactions. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a registration or chassis identifier co-occurring with vehicle context — a make and model, a garage name, a test or service heading — on the same document. The identifier pattern alone is never sufficient<br>• a labeled odometer reading together with a labeled service or test date<br>• an official vehicle document structure carrying a registered keeper field beside a vehicle identifier |
| **needs LLM** | • a handwritten service book page recovered by OCR<br>• deciding which vehicle a receipt belongs to in a household with more than one<br>• separating a quotation for work from an invoice for work done |
| **never alone** | • a bare registration-shaped string, which collides with reference codes, part numbers, and abbreviations<br>• a bare make or model name, which appears in advertising, hobby material, and photographs<br>• a bare date<br>• a bare garage or dealer name |

**Template** — `vehicle → record type → service date`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The vehicle is the subject and the entire value of the folder is that one vehicle's history sits together — year-first destroys precisely that, which is the scattering §5.5 warns about. §5.5's “a parent dimension should provide the context required to understand the child”: a service invoice is meaningless until the vehicle is known.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.insurance` | a motor certificate carries the registration and is a vehicle record by content and an insurance record by function | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.everyday-finance` | a vehicle purchase is a large transaction and a finance agreement is a credit product; both also belong to the vehicle | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.household-inventory` | a vehicle is the household's most valuable owned item and its manual, warranty, and receipts fit the inventory shape exactly; the registration is what earns it the narrower domain | §5.7 “create meaningless one-child levels” |

---

### `pers.home-tenure` — Home purchase, sale and tenancy

The documents that establish and end a household's occupation of a property, whether owned or rented.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. §5.7's personal administration is the nearest named slot. No design sentence names property tenure or its fields. |
| **sensitivity** | `potentially_sensitive` — Tenure files carry income evidence, identity checks, and the household's address history; §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §2.9's phrase “potentially sensitive” only. |
| **work types** | tenancy or lease agreement, inventory and condition report, deposit record, mortgage offer, survey or valuation, completion statement, title or deed, notice to quit or renewal, estate agent correspondence |
| **grouping reasons** | • one property across the household's occupation of it<br>• one transaction from offer to completion<br>• one tenancy and its renewals, as a version family |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `property` | string | — | `user_confirmed` | The property this is about. An address string is not a reliable identifier — it is written a dozen ways and appears on every letter sent to the household — so the identity of the property is settled by a person. |
| `tenure_type` | string | `tenancy` | `llm_supported` | Owned, rented, shared, sublet, or in transaction. Recorded as a per-property fact so no default about the household's situation is baked into the template. |
| `counterparty` | string | — | `validated` | Landlord, agent, seller, buyer, lender, or conveyancer. §3.8's role rule is load-bearing: these are separate fields, not one organisation field — “A finance document may mention an account holder and an issuing bank”. |
| `agreement_period` | date range | — | `validated` | Term start and end from a labeled field, parsed under §3.10's “Date extraction should be deliberately narrow”. |
| `reference` | string | — | `direct` | A tenancy, mortgage account, or transaction reference in a labeled field — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. |
| `record_type` | string | `tenancy agreement` | `llm_supported` | Agreement, inventory, deposit protection, survey, mortgage offer, completion statement, deed, notice. |
| `transaction_stage` | string | `exchanged` | `llm_supported` | A purchase and a tenancy both run through stages, and a draft filed as though it were executed is a real failure. §3.6's rule applies: insufficient support returns unknown. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a labeled tenancy, mortgage, or transaction reference together with a property address and a counterparty name on one document<br>• an agreement structure carrying labeled term dates beside a named property<br>• a deposit protection or land registration identifier in a labeled field |
| **needs LLM** | • a survey or valuation report whose only property signal is prose<br>• deciding whether a document is a draft, an executed agreement, or a renewal<br>• separating one property's paperwork from another where the household has moved |
| **never alone** | • a bare address — it appears on every piece of post the household receives<br>• a bare person or agency name<br>• a bare date range<br>• a bare reference number |

**Template** — `property → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The property is the durable subject; a purchase runs many months and a tenancy many years, so year-first splits single continuous relationships. §5.5's “a parent dimension should provide the context required to understand the child” puts the property above the record type because `notice` and `inventory` are meaningless labels on their own.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.moving` | the end of one tenure and the start of the next are the move. The tenure documents belong to their properties; the move is a distinct bounded project that touches both | §3.9 “Purpose must be a first-class facet” |
| `pers.utilities` | the same property address identifies both, and a tenancy pack routinely contains utility set-up documents | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.personal-legal` | a conveyance is a legal matter with a solicitor's file reference, and a tenancy dispute becomes one | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |

**Open question** — Should owned and rented properties share one branch, or should tenure be the first split? Either choice states something about the household's situation in the shape of their filesystem, and a household that has both is not unusual. Joseph's call — the catalogue records `tenure_type` as a fact and deliberately does not promote it to a folder level.

---

### `pers.moving` — Moving and relocation

A bounded project that ends one household arrangement and starts another, pulling documents out of half a dozen other domains for its duration.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names moving. Proposed as a §3.9 purpose packet rather than a topic: its members are “content-incoherent but purpose-coherent” in §4.7's exact sense — a removal quote, a final utility bill, an address-change letter, and a floor plan share a workflow and nothing else. |
| **sensitivity** | `potentially_sensitive` — A move packet aggregates address history, identity checks, and financial evidence in one place, which is §8.4's “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §2.9's phrase “potentially sensitive” only. |
| **work types** | removal quotation or booking, packing inventory, storage agreement, address-change confirmation, final and opening utility statements, deposit return record, floor plan or measurement note |
| **grouping reasons** | • one move as a purpose packet<br>• documents whose dates cluster around a confirmed move date AND which name one of the two properties<br>• an origin closing record paired with its destination opening record |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `move` | string | — | `user_confirmed` | The move itself, as a named project. It is the purpose that binds the packet, and §3.9 puts purpose support in a user-created folder name or explicit language: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal”. |
| `origin_property` | string | — | `user_confirmed` | Where the household moved from. §3.8's role separation: origin and destination are two fields, and an address field that holds either is useless for a move. |
| `destination_property` | string | — | `user_confirmed` | Where the household moved to. Separate field, same reason. |
| `move_date` | date | — | `validated` | The date of the move, from a labeled field on a removal booking or a completion statement. §3.10's “Date extraction should be deliberately narrow”. |
| `record_type` | string | `removal quotation` | `llm_supported` | Removal quote or booking, inventory list, address-change confirmation, storage agreement, final utility statement, deposit return. |
| `counterparty` | string | — | `validated` | Removal firm, storage provider, or agent. §3.8's role rule. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a document carrying two distinct property addresses in labeled origin and destination positions<br>• a removal or storage booking reference together with a labeled collection or delivery date and a firm name<br>• an existing user folder named for a move over members drawn from several other domains — §3.9's “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal” and §5.10's “A carefully curated existing folder should be treated as a strong expression of user intent” |
| **needs LLM** | • an address-change letter that names only the new address<br>• deciding whether a final utility statement belongs to the move or stays with the account<br>• assembling the packet itself, which is §4.7's task and requires direct purpose evidence rather than a session |
| **never alone** | • a bare address<br>• a bare date<br>• a bounded download session — §3.9 is explicit that “It is a purpose clue and a review aid, not a basis for automatic semantic propagation”<br>• the word `move` in a path, which is as likely a file operation, a chess note, or a video edit |

**Template** — `move → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The move is the function, and it is already a bounded time span, so a year parent above it adds a level with one child — which §5.7's validator is told to refuse (“create meaningless one-child levels”).

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.home-tenure` | completion statements and tenancy end notices belong to both. The property keeps them long-term; the move borrows them while it is live | §3.14 “A fact such as subject = BUSIB 4300 does not itself dictate one permanent folder path” |
| `pers.travel-record` | a one-way flight, a temporary hotel stay, and a shipping booking are travel records by structure and move records by purpose | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.household-inventory` | a packing inventory and a home inventory are the same list written for different reasons | §3.9 “Purpose must be a first-class facet” |

---

### `pers.household-inventory` — Household inventory, warranties and manuals

What the household owns and the paper that came with it — manuals, warranties, serial numbers, and proof of purchase.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. §7.3's `Independent Records` describes the residual these files fall into today — “standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader group” — which is evidence the slot exists and is unowned, not a design sentence naming the domain. |
| **sensitivity** | `none` — Manuals and warranties carry no identity, account, or health content of their own. Where a proof of purchase carries a card fragment or an address it is the finance record that is sensitive, not the manual, and §3.1's many-facts model keeps them as separate facts on separate files. |
| **work types** | user manual, warranty certificate, proof of purchase, installation or service record, inventory photograph, valuation, disposal or recycling record |
| **grouping reasons** | • one item across its manual, warranty, and receipt<br>• one purchase occasion across its items<br>• an inventory compiled for one purpose, such as a policy or a move |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `item` | string | `washing machine` | `llm_supported` | What the document is about. The domain's organising fact, reached from a manual title or a receipt line. |
| `manufacturer` | string | — | `validated` | A gazetteer match under §3.7's “word-boundary matching”, corroborated by a manual or warranty structure. §3.8 keeps manufacturer, retailer, and installer as separate roles. |
| `model_or_serial` | string | — | `direct` | A labeled model or serial number is §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field” and is the only field that distinguishes two identical items. |
| `purchase_date` | date | — | `validated` | From a labeled receipt field, under §3.10's “Date extraction should be deliberately narrow”. It is what makes a warranty period computable without this catalogue stating one. |
| `warranty_period` | date range | — | `validated` | From labeled cover dates on a warranty document. |
| `record_type` | string | `user manual` | `llm_supported` | Manual, warranty, receipt, installation certificate, valuation, disposal record. |
| `location` | string | `kitchen` | `user_confirmed` | Where the item is. Only useful for an insurance inventory, and only a person can state it. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a document whose title carries a manufacturer name together with a model identifier and a manual or instruction heading<br>• a labeled serial number together with a labeled purchase or installation date<br>• a warranty structure carrying labeled cover dates beside a product identifier |
| **needs LLM** | • a receipt whose line items are the only clue to what was bought<br>• deciding whether a downloaded manual is for an item the household owns or one it was researching<br>• photographs taken as an insurance inventory, which carry no product metadata |
| **never alone** | • a bare brand name<br>• a bare model-shaped string<br>• a bare purchase date<br>• the presence of a PDF manual, which is as often downloaded speculatively as kept for an owned item |

**Template** — `item → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A manual is retrieved when the item breaks, which is years after purchase, so the purchase year is the least useful parent available. §5.5's “a parent dimension should provide the context required to understand the child”: `warranty` is meaningless until the item is known.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.everyday-finance` | the same receipt is proof of purchase here and a transaction there. §7.3's `Receipts and Confirmations` is where it lands when neither claims it — “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” | §7.3 “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” |
| `pers.insurance` | an inventory exists mainly to support a contents policy or a claim, and the valuation document belongs to both | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.hobby-collection` | a collection is an inventory of items with provenance and valuations; the separator is whether the items are used or collected, which is the owner's intent | §3.9 “Purpose must be a first-class facet” |

---

### `pers.pet` — Pet and animal records

Veterinary, licensing, insurance, and care records for an animal in the household's care.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names pets. Proposed because the material is structurally a medical record for a non-person, and folding it into `pers.medical-record` would put an animal under a schema whose fields and protections are built for people. |
| **sensitivity** | `none` — Veterinary records concern an animal, and §8.4's “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” list covers human medical information. The owner's own name, address, and payment details on the same invoice are §3.1 facts about the invoice, and those carry the finance domain's marking rather than importing it here. |
| **work types** | vaccination record, treatment or surgery note, prescription, microchip registration, pet insurance document, pedigree or adoption paper, boarding or grooming agreement, invoice |
| **grouping reasons** | • one animal across its whole record<br>• one course of treatment<br>• one provider relationship |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `animal` | string | — | `user_confirmed` | Which animal. A name is the usual identifier and is not reliable from text alone — a microchip or registration number is, where present. |
| `provider` | string | — | `validated` | The veterinary practice, kennel, groomer, or breeder. §3.8's role rule keeps provider and owner apart — “A finance document may mention an account holder and an issuing bank”. |
| `record_type` | string | `vaccination record` | `llm_supported` | Vaccination, treatment, registration, microchip record, insurance, pedigree, boarding agreement. |
| `record_date` | date | — | `validated` | From a labeled field, under §3.10's “Date extraction should be deliberately narrow”. |
| `identifier` | string | — | `direct` | A labeled microchip, registration, or passport number — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field” — which is the only stable join across providers. |
| `species_or_breed` | string | — | `llm_supported` | Present on nearly every veterinary document and is what most cheaply separates this domain from the human one. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a labeled microchip or animal registration number together with a practice or authority name<br>• a veterinary document structure carrying a species or breed field beside a treatment or vaccination heading<br>• an animal passport or pedigree structure with labeled parentage fields |
| **needs LLM** | • an invoice from a practice that treats both animals and people, or a receipt with no species term<br>• deciding which animal a record belongs to in a multi-animal household<br>• separating pet photographs from the veterinary file they were sent with |
| **never alone** | • a bare animal name, which is also a common human nickname and a common filename<br>• a bare species word<br>• a bare date<br>• a bare practice name |

**Template** — `animal → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. An animal's history is retrieved as a history — a vaccination schedule and a chronic condition both span years — so year-first scatters exactly what a vet asks to see. §5.5's “a parent dimension should provide the context required to understand the child”: `vaccination record` needs the animal above it.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.medical-record` | veterinary and human medical documents have near-identical structure, and a household name appears on both as the payer. Species or breed is usually the only cheap separator | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `pers.insurance` | a pet policy is an insurance record whose insured subject is the animal | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.photo-event` | pet photographs form ordinary camera events and are not this domain; only the record material is | §4.2 “a photo group, it might be a deterministic event created from camera, time, and GPS metadata” |

**Open question** — Should a multi-animal household get a branch per animal, or one pet branch? A per-animal branch is the right shape for a vet history and the wrong shape for a household with one animal, where it is the one-child level §5.7 tells the validator to refuse (“create meaningless one-child levels”).

---

### `pers.medical-record` — Personal medical and health records

The corpus owner's own clinical record — letters, results, prescriptions, referrals, and appointment paperwork.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.15 names medical as one of the domains implemented first as safety domains — “Finance, identity, medical, and legal material should be implemented first as safety domains”, “meaning the system detects and protects them before any cloud or automated placement decision is allowed” — and §8.4 names “A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately”. The design gives the domain and its protection; it states no fields, and P6 SPEC records that gap as deferred. |
| **sensitivity** | `potentially_sensitive` — §8.4 names medical information in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately”. §7.3's `Protected Records` names medical documents in “passport scans, medical documents, account statements, visas, legal forms, or credentials”. §2.9's phrase “potentially sensitive” is the whole marking; the handling class is P7's (§8.4). |
| **work types** | clinic letter, test or imaging result, referral, discharge summary, prescription, appointment notice, consent form, vaccination record, invoice or claim |
| **grouping reasons** | • one episode of care across its documents<br>• one provider relationship<br>• a result and the letter that interprets it |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `provider` | string | — | `validated` | The clinic, hospital, practice, or clinician. §3.8's role rule is critical: the treating clinician, the referring clinician, the patient, and the payer are four roles, and a single organisation field would collapse them — “A finance document may mention an account holder and an issuing bank” is the design's own instance of the same mistake. |
| `record_type` | string | `test result` | `llm_supported` | Letter, result, referral, discharge summary, prescription, appointment notice, consent form. |
| `episode` | string | — | `user_confirmed` | The course of care a document belongs to. It is what makes a referral, a result, and a discharge letter one thing, and it is not written on any of them. Only a person can settle it. |
| `record_date` | date | — | `validated` | From a labeled field on the document, under §3.10's “Date extraction should be deliberately narrow”. Distinct from the appointment date the document may also carry. |
| `patient_role` | string | `self` | `user_confirmed` | §3.8 requires the role as its own field. This is the single field that keeps the corpus owner's record separate from a dependant's, and there is no rule that can read it. |
| `body_system_or_specialty` | string | — | `llm_supported` | The specialty a document belongs to — the least identifying way to group clinical material, and deliberately preferred here over a diagnosis field. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a clinical document structure carrying a labeled patient identifier together with a provider name in a letterhead position — §3.7's “positional weighting”<br>• a result document carrying a labeled specimen or test identifier beside a reporting laboratory name<br>• a prescription structure carrying a labeled prescriber identifier and a dispensing record |
| **needs LLM** | • a clinic letter whose only signal is clinical prose<br>• deciding whose record a document is, where the surname is shared<br>• a photographed or scanned letter, which arrives as an image with no structure at all until OCR runs |
| **never alone** | • a bare clinical term, which appears in coursework, research reading, insurance documents, and news<br>• a bare person name<br>• a bare date<br>• a bare provider name — hospitals are also employers, landlords, and research institutions<br>• a bare identifier-shaped number |

**Template** — `patient role → body system or specialty → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A condition followed over years is the normal case, and year-first splits one clinical story into calendar fragments — the scattering §5.5 names, at its most harmful. Specialty rather than diagnosis is the deliberate choice for the middle level: §8.4 warns that “a visible list of passport filenames on a shared screen may not be”, and a folder named after a diagnosis is that warning in structural form.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.scanned-document` | most medical material enters as a scan or a photograph and carries scan facts as well as clinical ones. §3.1's many-facts model keeps both | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.correspondence` | a scanned clinical letter and a scanned personal letter are the same object to an extractor. The separator is a labeled patient identifier or a provider in a letterhead position, not the fact that it is a letter | §3.7 “positional weighting” |
| `pers.dependant-care` | identical documents differing only in whose name is on them. `patient_role` is the whole separator and no rule produces it | §3.8 “A finance document may mention an account holder and an issuing bank” |
| `pers.insurance` | a health claim carries clinical content into an insurance file | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |

**Open question** — Should medical material branch by specialty, by episode, by provider, or stay flat behind one protected node? Each makes some part of a health history legible in a folder name, and §8.4's own example — “a visible list of passport filenames on a shared screen may not be” — says the visibility itself is the risk. Joseph's call, and it should be settled before any default template ships.

---

### `pers.dependant-care` — Health and care records held for another person

Clinical and care documents the corpus owner holds on someone else's behalf, which are structurally identical to their own and must not merge with them.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. §3.15's medical safety domain covers the material (“Finance, identity, medical, and legal material should be implemented first as safety domains”) but names no fields and no role distinction. Proposed because §3.8's role rule makes the distinction mandatory: the same document type in a different role is a different field. |
| **sensitivity** | `potentially_sensitive` — The material is another person's medical information held in someone else's corpus, and §8.4 names medical information in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” while §7.3's “passport scans, medical documents, account statements, visas, legal forms, or credentials” names medical documents. §2.9's phrase “potentially sensitive” only. |
| **work types** | clinic letter, care or support plan, consent or authority document, prescription, appointment notice, school or setting health form, carer correspondence |
| **grouping reasons** | • one subject person across their record<br>• one episode of care<br>• one authority document and the records it covers |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `subject_person_role` | string | `dependant` | `user_confirmed` | Whose record this is, expressed as a role rather than a relationship, so no assumption about household or family shape is encoded. §3.8: roles are separate fields — “A finance document may mention an account holder and an issuing bank”. |
| `holder_authority` | string | — | `user_confirmed` | The basis on which the corpus owner holds it — a parental role, a power of attorney, a caring arrangement. Documents held without authority are a real category and should not be silently normalised. |
| `provider` | string | — | `validated` | As in `pers.medical-record`; §3.8's role separation applies identically. |
| `record_type` | string | `clinic letter` | `llm_supported` | Same value set as `pers.medical-record`. |
| `record_date` | date | — | `validated` | From a labeled field, under §3.10's “Date extraction should be deliberately narrow”. |
| `care_arrangement` | string | — | `user_confirmed` | School health plan, care package, support plan. The non-clinical half of the material, which has no counterpart in the owner's own medical domain. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a clinical or care document structure carrying a labeled patient identifier that does not match the corpus owner's own confirmed identity value<br>• a care or support plan structure carrying a labeled subject field beside an authority or consent field |
| **needs LLM** | • deciding whether a document concerns the owner or someone else, where names are similar or shared<br>• correspondence written to the holder about the subject person, where both names appear |
| **never alone** | • a person name that differs from the owner's — the corpus is full of other people's names<br>• a bare date of birth<br>• a bare clinical term<br>• a bare provider name<br>• the presence of a child-shaped date of birth, which is an inference about a person and not evidence about a file |

**Template** — `subject person role → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. The subject person must be the top dimension or the records merge with the owner's, which is the failure the domain exists to prevent — §5.5's “a parent dimension should provide the context required to understand the child” in its strongest form. Beyond that level the catalogue deliberately stops, because deeper structure states something about the household.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.medical-record` | identical documents. Only `patient_role` separates them, and §4.8's validator has an exact analogue: a packet must not absorb a document with a conflicting target | §4.8 “the model has not invented a date, project, purpose, or membership that the dossier does not support” |
| `pers.child-school-record` | a school health plan is both a care record and a school record | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.eldercare` | the same person may be both the subject of care records and the subject of an eldercare coordination file; the separator is the material, not the person | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |

**Open question** — Does a dependant get a named branch of their own, and is it named after them? Both the existence of the branch and its label state something about the household's shape and about a person who did not choose to be in this corpus. Joseph's call; the catalogue deliberately holds the role as a fact and stops short of a default folder.

---

### `pers.eldercare` — Eldercare coordination

The administrative file of caring for an older person — assessments, funding, care providers, benefits, and the authority to act.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names eldercare. Proposed because the material is a §3.9 purpose packet that is neither medical nor legal nor financial while drawing documents from all three: “content-incoherent but purpose-coherent” describes it exactly. |
| **sensitivity** | `potentially_sensitive` — The file carries another person's medical, financial, and legal material together, all three of which §8.4 names in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §2.9's phrase “potentially sensitive” only. |
| **work types** | needs assessment, care plan, authority instrument, funding or benefits decision, care provider agreement or invoice, placement correspondence, complaint or appeal, meeting note |
| **grouping reasons** | • one matter from assessment to decision<br>• one care provider relationship<br>• one authority instrument and the acts taken under it |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `subject_person_role` | string | — | `user_confirmed` | Whom the care concerns, as a role. §3.8's separate-fields rule — “A finance document may mention an account holder and an issuing bank” — and the same refusal to encode a relationship as here in `pers.dependant-care`. |
| `authority_instrument` | string | — | `llm_supported` | The power of attorney, deputyship, or appointeeship that permits the holder to act. It is the document everything else depends on and it is worth its own field. |
| `care_provider` | string | — | `validated` | The agency, home, or authority delivering care. §3.8's role rule keeps provider, funder, and assessor apart. |
| `matter` | string | `care needs assessment` | `llm_supported` | The strand this document belongs to — assessment, funding, placement, benefits, complaint. |
| `record_date` | date | — | `validated` | From a labeled field, under §3.10's “Date extraction should be deliberately narrow”. |
| `reference` | string | — | `direct` | A labeled case, client, or claim reference — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • an assessment or care-plan document structure carrying a labeled client reference beside a local authority or agency name<br>• an authority instrument structure — a registered power of attorney or deputyship order — carrying labeled donor and attorney fields<br>• a benefits or funding decision carrying a labeled claim reference and a labeled decision date |
| **needs LLM** | • correspondence about care whose only signal is prose<br>• deciding whether a document concerns the subject person's care or their finances<br>• separating a care provider's invoice from a household service invoice |
| **never alone** | • a bare person name<br>• a bare authority or agency name, which also appears on unrelated council correspondence<br>• a bare date of birth<br>• a bare reference number |

**Template** — `subject person role → matter`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Care matters run for years and reopen; year-first would break every assessment-to-appeal chain. §5.5's “a parent dimension should provide the context required to understand the child” puts the subject person first because every matter label is meaningless without it.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.dependant-care` | clinical documents for the same person belong there; coordination, funding, and authority documents belong here | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.personal-legal` | a power of attorney is a legal instrument and the foundation of an eldercare file | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `pers.estate` | an eldercare file becomes an estate file, and much of it is the same paper read for a different purpose | §3.9 “Purpose must be a first-class facet” |
| `pers.everyday-finance` | managing another person's money under an authority produces statements that are not the corpus owner's own | §3.8 “A finance document may mention an account holder and an issuing bank” |

**Open question** — Is eldercare its own top-level concern, or a branch under the cared-for person alongside their care records? The answer decides whether a filesystem states that someone is being cared for, and by whom. Joseph's call.

---

### `pers.fitness-activity` — Fitness and activity data

Exported workout, training and activity data, and the plans and logs around it.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names fitness. §2.9's structured-data extractor covers the file formats and §2.9's spreadsheet fields (“sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”) cover exported logs, but neither names the domain. |
| **sensitivity** | `potentially_sensitive` — Activity data is health data and carries continuous GPS; §8.4 names both medical information and GPS metadata in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. §2.9's phrase “potentially sensitive” only. |
| **work types** | activity track file, platform data export, workout log spreadsheet, training plan, body measurement record, race entry or result, coaching correspondence |
| **grouping reasons** | • one export as a bundle<br>• one training programme across its activities<br>• one activity across its track, summary, and photographs |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `activity_type` | string | `running` | `llm_supported` | What the activity is. The domain's organising fact, and the one thing a bulk export does not carry in its filename. |
| `data_source` | string | — | `validated` | The platform or device the data came from, identified by an export's own manifest or file structure rather than by a brand name in prose. |
| `activity_date` | date | — | `direct` | A per-activity timestamp inside a track or record file is a labeled field — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. |
| `export_period` | date range | — | `validated` | The span a bulk export covers, read from labeled fields in its manifest. A bulk export has one file date and years of content, and conflating them is the domain's characteristic error. |
| `route` | string | — | `direct` | A GPS track present in the file. Direct as recorded data, and §8.4 requires GPS to stay local: “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. |
| `plan_or_programme` | string | — | `user_confirmed` | A training plan the activities belong to, which is the only thing that gives a year of workouts a shape a person would recognise. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a GPS track file structure carrying labeled trackpoints with timestamps together with an activity or sport field<br>• a platform export manifest naming the exporting service, together with the data files it lists<br>• a workout record structure carrying labeled activity type, duration, and start time fields |
| **needs LLM** | • a spreadsheet log whose column headers are the only clue to what is being recorded<br>• screenshots of workout summaries, which are §2.7's screenshot case and carry no structured data at all<br>• deciding whether a plan document is a training programme or unrelated reading |
| **never alone** | • a bare GPS track, which a mapping hobby, a survey, or a travel log produces identically<br>• a bare date<br>• a bare platform brand name<br>• a health-sounding filename |

**Template** — `data source → activity type → export period`, `time_first: false`.

> Held at time_first false, and this is the least comfortable of the slice's decisions. A single workout is capture-based and its date is defining, which is exactly §5.5's exception — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”. But the material as it actually arrives is a bulk export, one file covering years, and a file cannot sit under a year it spans. Source and activity are the dimensions that describe the file rather than its contents, so §5.5's ordinary rule holds: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A corpus dominated by per-activity track files would justify the opposite order.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.medical-record` | body measurements, heart data, and sleep records sit in fitness exports and are health information wherever they sit | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `pers.travel-photos` | a GPS track from a hike abroad is both an activity file and trip evidence, and both hold the same coordinates | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.screenshot` | much of a fitness corpus is screenshots of summaries, which are `captured_subject` files and not data files | §2.7 “a receipt, application portal, conversation, code problem, document, calendar, or research figure” |

---

### `pers.recipe-meal` — Recipes and meal planning

Collected and written recipes, meal plans, and shopping lists.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §7.3's `Reference Clips` names recipes literally among “saved visual inspiration, product references, quotes, recipes, short article captures, code snippets”, which places the material in the design as residual reference. This entry extends that into a domain with fields; the design gives none. |
| **sensitivity** | `none` — Recipes carry no identity, account, or clinical content. The exception is a `dietary_constraint` value that reveals a medical or religious fact; that is a fact about a person, and §3.1's model keeps it as its own fact rather than making the domain sensitive. |
| **work types** | recipe, meal plan, shopping list, photographed cookbook page, recipe screenshot, restaurant or tasting note, technique reference |
| **grouping reasons** | • one meal plan across its recipes and list<br>• one source collection<br>• one dish across its variants, as a version family |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `dish` | string | — | `llm_supported` | What the recipe makes. The organising fact, and rarely present as a labeled field — a saved web capture's title is as often the site's name. |
| `cuisine_or_category` | string | — | `llm_supported` | The grouping most people actually use when they look for a recipe. |
| `source` | string | — | `validated` | Where it came from — a book, a site, a person. §3.8's role rule keeps the recipe's author and the person who saved it apart, and §3.8 is explicit that “It should avoid using authorship or creator identity as a destination dimension”. |
| `meal_plan_period` | date range | — | `validated` | For plans rather than recipes, read from labeled fields under §3.10's “Date extraction should be deliberately narrow”. |
| `dietary_constraint` | string | — | `llm_supported` | Recorded because it is how recipes are actually retrieved, and flagged here because a constraint may be medical or religious, which makes the field carry more than cooking. |
| `record_type` | string | `recipe` | `llm_supported` | Recipe, meal plan, shopping list, restaurant note, technique reference. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a document structure containing an ingredient list followed by a numbered method section<br>• a recipe interchange or import format from a recipe manager application<br>• an existing user folder carrying a cooking term over members with ingredient-list structure |
| **needs LLM** | • a photographed cookbook page or handwritten card, which is an image until OCR runs<br>• a screenshot of a recipe, which is §2.7's screenshot case<br>• deciding whether a shopping list is meal planning or general household |
| **never alone** | • a bare food word, which appears in travel writing, gardening notes, and photographs<br>• a bare dish name<br>• a bare site or publication name<br>• a bounded download session — §3.9: “It is a purpose clue and a review aid, not a basis for automatic semantic propagation” |

**Template** — `cuisine or category → dish`, `time_first: false`.

> §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A recipe has no meaningful date at all — the date it was saved is noise — so time is not a candidate dimension here rather than a rejected one. §5.5's “a parent dimension should provide the context required to understand the child” puts category above dish because a dish name is self-describing and a flat list of hundreds is not navigable.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.screenshot` | a large share of a recipe collection is screenshots and saved web captures, which §7.3 already routes to `Reference Clips` | §7.3 “saved visual inspiration, product references, quotes, recipes, short article captures, code snippets” |
| `pers.medical-record` | a dietary plan issued by a clinician is clinical material that reads exactly like a meal plan | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `pers.hobby-collection` | serious cooking is a hobby with equipment, notes, and collected references, and the material overlaps almost entirely | §5.7 “create meaningless one-child levels” |

---

### `pers.hobby-collection` — Hobbies and collections

The reference material, records, and provenance of a pursued interest or a deliberately assembled collection.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. §5.7's creative projects and §7.3's `Reference Clips` (“saved visual inspiration, product references, quotes, recipes, short article captures, code snippets”) each touch part of it, but no design sentence names hobbies or collections. |
| **sensitivity** | `none` — Hobby and collection material carries no category §8.4 lists in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. Purchase and valuation records that do are finance and insurance facts on those files, not a property of this domain. |
| **work types** | reference material, instruction or pattern, catalogue or checklist, purchase or auction record, provenance or authentication document, valuation, activity log, club or society correspondence |
| **grouping reasons** | • one pursuit across its material<br>• one item across its provenance chain<br>• one acquisition event |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `pursuit` | string | — | `user_confirmed` | Which hobby or collection this belongs to. The one fact that makes the domain coherent, and it is user vocabulary by nature — §5.1 requires labels to reflect the user's vocabulary rather than a universal taxonomy. |
| `item` | string | — | `llm_supported` | For collections, the specific object a document concerns. |
| `acquisition_date` | date | — | `validated` | From a labeled receipt or certificate field, under §3.10's “Date extraction should be deliberately narrow”. |
| `provenance_record` | string | — | `llm_supported` | Certificates, prior-ownership documents, and authentication papers, which are the collection's real value and have no counterpart in a general inventory. |
| `record_type` | string | `reference material` | `llm_supported` | Reference, instruction, catalogue, purchase record, provenance document, log. |
| `valuation` | string | — | `validated` | A labeled appraised value on a valuation document. Recorded because it is what links a collection to an insurance policy. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • an existing user folder named for a pursuit over members that share a document structure — §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent”<br>• a catalogue or collection-management export naming the collection and listing items<br>• a certificate or authentication structure carrying labeled item and issuer fields |
| **needs LLM** | • reference material whose only signal is its subject matter<br>• deciding whether a purchase is for a collection or for household use<br>• separating a hobby that has become work from one that has not |
| **never alone** | • a bare subject word<br>• a bare item name<br>• a bare purchase date<br>• a bounded download session — §3.9: “It is a purpose clue and a review aid, not a basis for automatic semantic propagation” |

**Template** — `pursuit → record type`, `time_first: false`.

> §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A collection is retrieved by what is in it, never by when a document about it arrived. §5.5's “a parent dimension should provide the context required to understand the child”: `provenance document` is meaningless until the pursuit and item are known.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.creative-project` | a hobby that produces work is also a creative project. The separator is whether the files are references consumed or artefacts produced | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.household-inventory` | both are lists of owned things with receipts; only a collection carries provenance and valuation as first-class material | §3.9 “Purpose must be a first-class facet” |
| `pers.insurance` | a specified-items policy schedule lists the collection and is an insurance record | §3.11 “target university is not a fact that every file is expected to have” |

---

### `pers.music-practice` — Music and instrument practice

Scores, parts, recordings, and practice records for playing an instrument or singing.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names music practice. Proposed because its material — scores, recordings, and lesson records — is otherwise split across three domains that each hold a third of it badly. |
| **sensitivity** | `none` — Scores and practice recordings carry none of the categories §8.4 lists in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. A recording containing a third party's voice is a §2.9 audio fact on that file, not a property of the domain. |
| **work types** | score, part, lead sheet, exercise or method material, practice recording, performance recording, lesson note, programme or exam entry |
| **grouping reasons** | • one piece across its score, parts, and recordings<br>• one performance or examination and everything prepared for it<br>• one teacher or ensemble relationship |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `piece` | string | — | `llm_supported` | The work being played. §3.8's role rule matters unusually here: the composer, the arranger, the performer, and the editor are four roles on one score, and “It should avoid using authorship or creator identity as a destination dimension” means none of them becomes the folder. |
| `instrument_or_voice` | string | — | `llm_supported` | Which part this is for. A score, a part, and a transposition of one piece are different files and only this field separates them. |
| `score_type` | string | `part` | `llm_supported` | Full score, part, lead sheet, exercise, method book, arrangement. |
| `practice_date` | date | — | `direct` | The capture date on a practice recording — a labeled container field, §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field”. |
| `teacher_or_ensemble` | string | — | `validated` | Whose lesson or ensemble the material belongs to. §3.8's role rule keeps this apart from the composer. |
| `performance` | string | — | `user_confirmed` | A concert, exam, or audition the material was prepared for, which is what turns a folder of parts into a project. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a music notation file format, or a PDF whose first page carries a title-and-composer structure with a staff-shaped layout<br>• an audio file whose container metadata carries a title and a performing context together with a household device identity<br>• an existing user folder named for an instrument, ensemble, or examination board over members with score structure |
| **needs LLM** | • a scanned score with no text layer, which is an image until OCR runs<br>• deciding whether a recording is practice, performance, or listening material<br>• separating a piece being learned from a piece merely collected |
| **never alone** | • a bare composer or performer name, which is also a music library, a listening collection, and a reading list<br>• a bare piece title<br>• a bare audio duration<br>• an audio file format, which says nothing about origin |

**Template** — `instrument or voice → piece → score type`, `time_first: false`.

> §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A piece is returned to for years and a practice recording is retrieved by what it is of, not when it was made. §5.5's “a parent dimension should provide the context required to understand the child”: `part` is a meaningless folder name until the piece and the instrument are known.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.home-video` | a practice recording is a voice memo by container. The separator is a piece or ensemble context in the folder or filename | §3.5 “can only propose facts that belong to the active domain schema” |
| `pers.creative-project` | composing and arranging produce artefacts, not practice material, and belong there | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `acad.course-enrollment` | music studied as a course carries a course code and term, which routes it to the academic domain even though the files are scores | §3.5 “can only propose facts that belong to the active domain schema” |

---

### `pers.creative-project` — Personal creative projects

Work the corpus owner is making for its own sake — writing, art, design, film, craft — organised by the project rather than by the file type.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §5.7 names creative projects in the template library the product should eventually carry: “financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections”. The name is design-given; the fields are not. §2.9's design and creative extractor supplies the observable material: “filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text”. |
| **sensitivity** | `none` — Creative artefacts carry none of the categories §8.4 lists in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. Private writing that would be sensitive belongs to `pers.journal`, which carries the marking. |
| **work types** | manuscript or draft, sketch or study, working project file, export or render, reference collection, submission packet, feedback or critique note, exhibition or publication record |
| **grouping reasons** | • one project across every stage and format<br>• one artefact across its drafts, as a version family<br>• one submission and everything sent with it |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `project` | string | — | `user_confirmed` | The work being made. §3.11 already uses `project` in the Research row, and this is the same field under a different active schema. Only a person names a personal project. |
| `stage` | string | `draft` | `llm_supported` | §3.11's Research row also carries `stage`, and creative work has the same shape — sketch, draft, revision, final, exhibited. It is what makes a folder of near-identical files legible. |
| `medium` | string | — | `validated` | Writing, illustration, film, textile, and so on, confirmed from the file formats present rather than asserted from a filename. |
| `artifact_type` | string | `manuscript` | `llm_supported` | §3.11's `artifact_type`, again shared across schemas: manuscript, sketch, working file, export, reference, submission. |
| `collaborator_role` | string | — | `user_confirmed` | §3.8's role separation. Creative work carries editors, collaborators, and commissioners, and “It should avoid using authorship or creator identity as a destination dimension” means none of them becomes the folder level. |
| `submission_target` | string | — | `llm_supported` | Where a finished piece was sent — a publication, a competition, a gallery. It is the field that makes a submission packet a §3.9 purpose group rather than a copy of the work. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a working file format from §2.9's design and creative list present alongside its exports in one directory, sharing a filename stem<br>• a project or scratch file structure naming linked assets — §2.9: “filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text”<br>• an existing user folder named for a project over members that form a version family |
| **needs LLM** | • a manuscript whose only project signal is the prose itself<br>• deciding whether a piece is personal work or coursework, which changes the active schema entirely<br>• separating reference material gathered for a project from the project's own artefacts |
| **never alone** | • a creative file format, which is equally produced by coursework, client work, and hobby use<br>• a bare project-sounding filename<br>• a bare date<br>• a bounded download session — §3.9: “It is a purpose clue and a review aid, not a basis for automatic semantic propagation”<br>• the author or creator metadata string. §2.2 and §2.3 make it supporting evidence only, and §3.8 forbids it as a destination dimension: “Authorship is usually metadata; the document’s purpose, project, subject, or target is more informative for placement” |

**Template** — `project → artifact type → stage`, `time_first: false`.

> §5.5's ordinary rule, and §5.7 names creative projects among the library's own template subjects: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A creative project runs for years and its drafts are the point, so a year parent would separate a piece from its own revisions. §5.5's “a parent dimension should provide the context required to understand the child”: `draft` needs the artefact above it, which needs the project.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.hobby-collection` | the same pursuit produces both reference material and made work. References are consumed, artefacts are produced | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `acad.course-enrollment` | creative coursework is identical in format to personal work and differs only by a course code and term — §3.5's own validated-fact example | §3.5 “can only propose facts that belong to the active domain schema” |
| `pers.journal` | notebooks and journals hold both private writing and project drafting, often in the same file | §3.11 “target university is not a fact that every file is expected to have” |

---

### `pers.journal` — Journals and diaries

Dated personal writing kept for its own sake, where the date is the only structure the material has.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names journals. Proposed separately from `pers.creative-project` because the material is private rather than made, and separately from `pers.correspondence` because it has no counterparty. |
| **sensitivity** | `potentially_sensitive` — Journals are the most private text in a personal corpus and §8.4's “Privacy policy must be enforced before content reaches any model or external connector” is the governing rule for them. §8.4 also requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. §2.9's phrase “potentially sensitive” and nothing more; the class is P7's. |
| **work types** | dated entry, bound volume scan, application export, dream or gratitude log, travel diary, voice diary recording |
| **grouping reasons** | • one journal across its entries<br>• one continuous period of keeping<br>• a handwritten volume and its transcription, as a version family |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `entry_date` | date | `2026-03-04` | `validated` | The date the entry covers, which is usually written in the text and is not the file's timestamp. §3.10 governs it strictly: “Date extraction should be deliberately narrow” and “The product must not use fuzzy date parsing”, because a dated heading is exactly the pattern fuzzy parsing gets wrong. |
| `journal` | string | — | `user_confirmed` | Which journal an entry belongs to, where a person keeps more than one. Only a person can say. |
| `entry_medium` | string | `digital note` | `validated` | Handwritten and scanned, typed, dictated, or in an application export. It decides whether the text is available at all, which no other field records. |
| `period_covered` | date range | — | `validated` | For a bound volume or an application export, the span its entries cover — the field that stops a decade-long export being filed under its export date. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a document containing repeated dated headings in one consistent format across its length<br>• a journalling application export whose manifest names the application and lists dated entries<br>• an existing user folder carrying a journal or diary term over members with dated-heading structure |
| **needs LLM** | • a scanned handwritten notebook, which is images until OCR runs and even then may not resolve<br>• deciding whether an undated personal document is a journal entry, a letter never sent, or project drafting |
| **never alone** | • a bare date in a filename — dated filenames are the most common convention in any corpus<br>• a first-person voice, which appears in essays, applications, and correspondence alike<br>• a notebook-shaped file format<br>• the word `journal` in a path, which is also an academic journal, a ledger, and a logging file |

**Template** — `journal → entry date`, `time_first: true`.

> time_first is TRUE here, and not by §5.5's capture exception — a journal is not capture-based media. It is true by elimination: the domain has no project, function, or subject dimension, so §5.5's stated harm from leading with time cannot occur. “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” warns that year-first scatters RELATED WORK across calendar folders; in a journal there is no related work to scatter, because the entries are related to each other only by sequence. Where a person keeps more than one journal that name comes first, since §5.5's “a parent dimension should provide the context required to understand the child” makes a date meaningless across two parallel journals.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.creative-project` | one notebook holds diary entries and project drafting, sometimes on one page | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.correspondence` | an unsent letter and a journal entry are the same object structurally; only a named recipient separates them | §3.8 “A finance document may mention an account holder and an issuing bank” |
| `pers.travel-record` | a travel diary belongs to the trip and to the journal, and choosing one silently breaks the other sequence | §3.14 “A fact such as subject = BUSIB 4300 does not itself dictate one permanent folder path” |

**Open question** — Should journals appear in the proposed tree at all, or be represented without being surfaced? §8.4's own example is that “a visible list of passport filenames on a shared screen may not be”, and a visible `Journals` branch on a shared screen is the same exposure. Joseph's call.

---

### `pers.correspondence` — Personal correspondence

Letters, messages, and cards exchanged with people rather than institutions.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §8.4 names private correspondence in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”, and §2.9's email extractor states the observable fields: “sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”, “treating addresses and message content as potentially sensitive”. The design names the material and its sensitivity; it names no domain schema. |
| **sensitivity** | `potentially_sensitive` — §2.9 requires “treating addresses and message content as potentially sensitive”, using the design's own phrase “potentially sensitive”, and §8.4 names private correspondence in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. No handling class is assigned here. |
| **work types** | personal letter, greetings card, email thread, message archive export, enclosure or attachment, postcard |
| **grouping reasons** | • one thread across its messages<br>• one correspondent relationship over time<br>• a letter and the enclosures sent with it |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `correspondent_role` | string | — | `user_confirmed` | Who the exchange is with, held as a role rather than an identity, because §3.8 forbids a person becoming a collector dimension — “It should avoid using authorship or creator identity as a destination dimension” — and §5.7's validator refuses a template that would “use an author or organization merely as a collector”. |
| `thread` | string | — | `direct` | §2.9 lists thread identifiers among the fields an email extractor yields; a labeled thread identifier is §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field” and is the only reliable join across a reply chain. |
| `sent_date` | date | — | `direct` | §2.9 lists sent date among the email extractor's fields. |
| `subject` | string | — | `direct` | §2.9 lists subject; direct as a labeled header field, and worth nothing beyond that. |
| `channel` | string | `letter` | `validated` | Email, letter, card, or exported message archive. It decides what evidence exists and therefore what may be claimed. |
| `record_type` | string | `personal letter` | `llm_supported` | Letter, card, message export, enclosure. The field that separates a greetings card from a substantive letter. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • an email or message file whose labeled sender and recipient headers resolve to persons rather than to institutional addresses, together with a thread identifier<br>• a scanned document with a salutation-and-signature structure and no letterhead organisation in the header position — §3.7's “positional weighting”<br>• a message archive export whose manifest names the platform and lists conversations |
| **needs LLM** | • a scanned handwritten letter, which is an image until OCR runs<br>• deciding whether an exchange is personal or institutional where the counterparty is a person at an organisation<br>• separating substantive correspondence from routine notifications in a bulk mailbox export |
| **never alone** | • a bare person name<br>• a bare email address<br>• a bare date<br>• a salutation word, which appears in templates, drafts, and form letters<br>• the author or creator metadata string — §3.8: “Authorship is usually metadata; the document’s purpose, project, subject, or target is more informative for placement” |

**Template** — `correspondent role → thread`, `time_first: false`.

> §5.5's ordinary rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A correspondence is a relationship that spans years, and year-first cuts every thread that crosses a December. §5.5's “a parent dimension should provide the context required to understand the child” puts the correspondent first because a subject line means nothing without knowing who wrote it. The catalogue deliberately stops at a ROLE rather than proposing a folder per person, for §3.8's reason.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.medical-record` | a scanned clinical letter and a scanned personal letter are one object to an extractor. The separator is a labeled patient identifier or an institutional letterhead, never the fact that it is a letter | §3.7 “positional weighting” |
| `pers.household-admin` | institutional correspondence belongs there and carries a labeled reference this domain does not | §3.8 “A finance document may mention an account holder and an issuing bank” |
| `pers.genealogy` | inherited letters are correspondence and family history at once, and their correspondents are dead | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |

---

### `pers.gift-occasion` — Gifts, celebrations and occasion planning

The records around an occasion — invitations, lists, orders, vendor bookings — as distinct from the photographs of it.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names occasions as a record domain. Proposed because §3.9's purpose rule fits it exactly — “content-incoherent but purpose-coherent” — and because the records and the photographs of one occasion template in opposite directions. |
| **sensitivity** | `none` — Occasion planning carries none of the categories §8.4 lists in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. Guest lists carry third-party contact details, which §2.9 handles as contacts material — “should normally be privacy-protected rather than used to create folder proposals” — on those files rather than as a property of this domain. |
| **work types** | invitation, guest or gift list, order or booking confirmation, vendor quotation, seating or running order, thank-you record, card design or print file |
| **grouping reasons** | • one occasion across its records<br>• one vendor booking across quote, confirmation, and invoice<br>• records that name a confirmed occasion date AND its venue or vendor |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `occasion` | string | — | `user_confirmed` | The occasion these records serve. Shared as a value with `pers.photo-occasion`, which is what lets the planning file and the photographs recognise each other. |
| `occasion_date` | date | — | `validated` | From a labeled field on an invitation or booking, under §3.10's “Date extraction should be deliberately narrow”. §2.9's calendar extractor supplies the same fields where an event file exists: “event title, start and end time, location, organizer, attendees, and recurrence metadata”. |
| `recipient_role` | string | — | `user_confirmed` | Whom a gift or occasion is for, as a role. §3.8's separate-fields rule, and the same refusal to name a person as a folder dimension. |
| `vendor` | string | — | `validated` | Venue, caterer, retailer, or supplier. §3.8 keeps vendor, payer, and recipient apart. |
| `record_type` | string | `invitation` | `llm_supported` | Invitation, guest or gift list, order or booking, seating plan, thank-you record. |
| `budget_line` | string | — | `possible` | An occasion routinely has a spending record spread over unrelated receipts. Recorded at §3.13's “A possible fact is a useful but insufficient clue, such as membership in a short download session or a low-confidence semantic match” because attributing a receipt to an occasion is a clue, not a fact, unless the receipt says so. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • an invitation structure carrying a labeled event date and venue together with an occasion term<br>• a calendar file whose event carries an occasion term with a location and attendees — §2.9: “event title, start and end time, location, organizer, attendees, and recurrence metadata”<br>• an existing user folder named for an occasion over members that are orders, lists, and bookings — §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal” |
| **needs LLM** | • an order confirmation that is a gift only because of who it was for<br>• deciding whether a vendor booking serves an occasion or is ordinary household spending<br>• assembling the packet, which is §4.7's task and needs direct occasion evidence rather than a session |
| **never alone** | • a bare occasion word<br>• a bare date<br>• a bare vendor name<br>• a bounded download session — §3.9: “It is a purpose clue and a review aid, not a basis for automatic semantic propagation”<br>• a purchase near a known occasion date, which is the clearest possible case of proximity being read as purpose |

**Template** — `occasion → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — planning starts months before and thank-you records land months after, so an occasion routinely straddles a year boundary while the photographs of it do not. This is the sharpest illustration in the slice that ONE real-world event legitimately produces a time-first capture branch and a subject-first record branch, exactly as §5.5's two sentences describe.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.photo-occasion` | same occasion, opposite template. The occasion value is shared; the records carry vendors and references, the captures carry camera identity | §5.5 “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” |
| `pers.everyday-finance` | occasion spending is ordinary transactions until something attributes it, and §7.3 routes the unattributed ones to `Receipts and Confirmations` | §7.3 “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” |
| `pers.travel-record` | an occasion held away from home generates bookings that are travel records and occasion records at once | §3.9 “Purpose must be a first-class facet” |

---

### `pers.estate` — Wills, estate and end-of-life documents

Instruments and administration for what happens to a person's affairs — wills, probate, executorship, funeral and legacy records.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. §3.15's legal safety domain (“Finance, identity, medical, and legal material should be implemented first as safety domains”) and §7.3's `Protected Records` — “passport scans, medical documents, account statements, visas, legal forms, or credentials” — cover the material's protection. No design sentence names estate matters or their fields. |
| **sensitivity** | `potentially_sensitive` — §7.3's `Protected Records` names legal forms in “passport scans, medical documents, account statements, visas, legal forms, or credentials” and §8.4 names legal records in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The material also concerns third parties who are named beneficiaries. §2.9's phrase “potentially sensitive” only. |
| **work types** | will or codicil, trust deed, grant of probate or administration, letter of wishes, asset schedule, funeral instruction or record, estate account, adviser correspondence |
| **grouping reasons** | • one estate across its administration<br>• one instrument and its supersessions, as a version family<br>• one role the owner holds across the estates they act in |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `estate_role` | string | `executor` | `user_confirmed` | Testator, executor, beneficiary, administrator, attorney. §3.8's role rule is unavoidable here: the same estate file holds documents where the corpus owner occupies different roles, and merging them is a substantive error — “A finance document may mention an account holder and an issuing bank”. |
| `instrument_type` | string | `will` | `llm_supported` | Will, codicil, trust deed, grant of probate, letter of wishes, funeral instruction. |
| `estate` | string | — | `user_confirmed` | Whose estate. The organising fact, and only a person can settle it. |
| `execution_date` | date | — | `validated` | The date an instrument was executed, which is the field that decides which version governs. §3.10's “Date extraction should be deliberately narrow”. |
| `professional_adviser` | string | — | `validated` | The solicitor, notary, or firm holding the file. §3.8 keeps adviser and party apart. |
| `supersession_state` | string | `current` | `user_confirmed` | Whether an instrument is current, superseded, or a draft. A superseded will filed beside the current one is the single most consequential filing error in this slice, and no rule reliably tells them apart. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a will or codicil structure carrying labeled testator, executor, and attestation fields<br>• a grant or court document carrying a labeled case or grant reference beside a registry name<br>• a trust or deed structure carrying labeled parties and an execution date |
| **needs LLM** | • a draft that is textually near-identical to an executed instrument<br>• correspondence about an estate whose only signal is prose<br>• deciding whether a document concerns the owner's own estate or one they administer |
| **never alone** | • the word `will`, which is an ordinary English word and a common given name<br>• a bare person name<br>• a bare date<br>• a bare firm name<br>• a bare reference number |

**Template** — `estate → estate role → instrument type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Estate documents are separated by decades and belong together; a year parent is the worst available choice, because it puts a will and its codicil in different folders. §5.5's “a parent dimension should provide the context required to understand the child”: `codicil` needs both the estate and the role above it to be readable.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.personal-legal` | estate work is legal work with a solicitor's file reference; the separator is whether the matter is contentious or testamentary | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `pers.eldercare` | an eldercare file and an estate file share the authority instruments and often the same correspondence | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.genealogy` | wills and probate records are genealogy's richest sources once the estate is closed | §3.9 “Purpose must be a first-class facet” |
| `pers.everyday-finance` | estate accounts are financial records for money that is not the corpus owner's own | §3.8 “A finance document may mention an account holder and an issuing bank” |

---

### `pers.identity-document` — Identity documents

The credentials that prove who someone is — passports, national identity cards, licences, certificates, and their scans.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.15 names identity among the domains implemented first as safety domains: “Finance, identity, medical, and legal material should be implemented first as safety domains”, “meaning the system detects and protects them before any cloud or automated placement decision is allowed”. §8.4 requires that “A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately” and §7.3 names “passport scans, medical documents, account statements, visas, legal forms, or credentials”. The design gives the domain and its protection and states no fields; P6 SPEC records that gap as deferred. |
| **sensitivity** | `potentially_sensitive` — §8.4 names identity documents first in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately”. §7.3 names passport scans in “passport scans, medical documents, account statements, visas, legal forms, or credentials” and adds that “it should normally remain local-only and must not cause filenames or content to be exposed in model prompts”. §2.9's phrase “potentially sensitive” is the entire marking; the handling class is P7's (§8.4). |
| **work types** | passport or travel document, national identity card, driving licence, birth, marriage or death certificate, residence or right-to-work document, tax or social identifier record, photograph submitted for a credential |
| **grouping reasons** | • one holder across their credentials<br>• one credential across its renewals, as a version family<br>• an application and the credential it produced |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `document_type` | string | `passport` | `llm_supported` | Which credential this is. The field the domain exists for, and the only one safe to surface — §8.4's own example is that “a visible list of passport filenames on a shared screen may not be”. |
| `holder_role` | string | `self` | `user_confirmed` | Whose credential. §3.8's separate-fields rule, and the field that keeps a household's documents from merging into one indistinguishable set. |
| `issuing_authority` | string | — | `validated` | The state, agency, or authority. A gazetteer match under §3.7's “word-boundary matching”, corroborated by a credential structure. |
| `validity_period` | date range | — | `validated` | Issue and expiry from labeled fields, under §3.10's “Date extraction should be deliberately narrow”. It is the only field that gives this domain a reason to be consulted rather than merely stored. |
| `document_status` | string | `current` | `user_confirmed` | Current, expired, replaced, lost. An expired passport filed as current is a real failure and no rule settles it, because an expiry date read from a scan does not say whether a replacement exists. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a machine-readable-zone structure recovered by OCR together with a document-type label on the same image<br>• a credential structure carrying labeled issue and expiry dates beside an issuing authority name<br>• a certificate structure carrying a labeled registration or certificate number beside a registry name |
| **needs LLM** | • a photographed credential at an angle, partially legible<br>• deciding whether a certificate concerns a living holder or is genealogical research material<br>• a foreign-language credential, which §3.3 places among the cases rules cannot cover |
| **never alone** | • a bare person name<br>• a bare date of birth<br>• a bare identifier-shaped number, which collides with references, account numbers, and case numbers<br>• a bare country or authority name<br>• a filename containing an identity word, which is as likely a form, a checklist, or a guide about identity documents |

**Template** — `holder role → document type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A credential's validity spans a decade, so year-first is meaningless here; the holder is the only useful first dimension, per §5.5's “a parent dimension should provide the context required to understand the child”. The catalogue stops at two levels deliberately — §8.4 warns that “a visible list of passport filenames on a shared screen may not be”, and deeper structure makes the contents more legible from outside, not less.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.travel-visa-entry` | a passport scan is submitted inside a visa packet and belongs to both. §3.11 keeps both fact sets rather than choosing | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.genealogy` | the same certificate types serve as live credentials and as research sources; the separator is whether the subject is living | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `acad.college-application` | §3.9's own worked packet contains an identification document alongside a transcript and a resume — the identity document is inside an application packet without ceasing to be an identity document | §3.9 “content-incoherent but purpose-coherent” |
| `pers.scanned-document` | every identity document in a corpus is a scan or a photograph and carries scan facts as well | §2.7 “A PDF with no extractable text and evidence of being created from a photographed page can route directly to OCR” |

---

### `pers.membership` — Memberships and subscriptions

Ongoing paid or joined relationships — clubs, professional bodies, unions, services, and recurring subscriptions.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names memberships. Proposed because the material is defined by a RECURRING relationship rather than by a transaction, which no finance or admin schema in this slice represents. |
| **sensitivity** | `none` — Membership records carry none of the categories §8.4 lists in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” on their own. Where the organisation itself reveals something — a faith body, a political body, a health service — that is a fact about the organisation value, and `pers.faith-community` carries the marking for the case this slice names. |
| **work types** | joining confirmation, membership card or certificate, renewal notice, invoice or receipt, benefits or handbook document, cancellation confirmation, professional registration |
| **grouping reasons** | • one membership across its renewals, as a version family<br>• one organisation relationship<br>• one membership term and everything issued under it |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `organisation` | string | — | `validated` | The body joined or subscribed to. A gazetteer match under §3.7's “word-boundary matching”, corroborated by a membership document structure. |
| `membership_number` | string | — | `direct` | A labeled membership or subscriber identifier — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field” — and the join across years of renewals and a change of address. |
| `membership_type` | string | — | `llm_supported` | The grade or tier, which is what distinguishes a student membership from a full one and changes what the record means. |
| `term` | date range | — | `validated` | The membership year or subscription period, from labeled fields under §3.10's “Date extraction should be deliberately narrow”. |
| `record_type` | string | `renewal notice` | `llm_supported` | Joining confirmation, card, renewal notice, invoice, benefits document, cancellation. |
| `status` | string | `active` | `user_confirmed` | Active, lapsed, cancelled. A cancelled subscription's paperwork looks identical to an active one's and only a person knows which is which. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a labeled membership or subscriber number together with an organisation name and a labeled term<br>• a renewal document structure carrying a labeled expiry or renewal date beside a membership identifier<br>• a professional body certificate carrying a labeled registration number beside the body's name |
| **needs LLM** | • a subscription receipt with no membership identifier<br>• deciding whether a recurring charge is a membership or an ordinary repeat purchase<br>• separating a professional registration, which is closer to a credential, from a club membership |
| **never alone** | • a bare organisation name<br>• a bare identifier-shaped number<br>• a bare renewal date<br>• a recurring charge on a statement, which is a finance fact about the statement and not evidence of a membership document |

**Template** — `organisation → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A membership is a relationship measured in years, and year-first would fragment one continuous relationship into annual slices — the scattering §5.5 names. §5.5's “a parent dimension should provide the context required to understand the child”: `renewal notice` needs the organisation above it.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.everyday-finance` | a subscription invoice is a transaction and a membership record. §7.3's `Receipts and Confirmations` catches the ones no membership claims | §7.3 “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” |
| `pers.faith-community` | membership of a congregation or community body is both, and the community relationship carries meaning the membership schema does not | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.hobby-collection` | club and society membership belongs to the pursuit as much as to the membership file | §3.11 “target university is not a fact that every file is expected to have” |

---

### `pers.everyday-finance` — Day-to-day personal finance

The running financial record of a household — statements, transactions, receipts, payments, and the accounts they belong to.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.11 gives the Finance domain its fields literally: “Finance files may use institution, account type, tax year, and record type”. §3.15 names finance among the safety domains — “Finance, identity, medical, and legal material should be implemented first as safety domains”. This entry is the day-to-day slice of that named domain; the field names below are §3.11's own. |
| **sensitivity** | `potentially_sensitive` — §8.4 names account statements and tax records in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately”. §7.3 names account statements in “passport scans, medical documents, account statements, visas, legal forms, or credentials”. §2.9's phrase “potentially sensitive” only. |
| **work types** | statement, transaction export, receipt, payment or transfer confirmation, tax document, credit agreement, interest or fee notice, budget spreadsheet |
| **grouping reasons** | • one account across its statement periods<br>• one tax year across the documents that evidence it<br>• one transaction across its receipt and confirmation |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `institution` | string | — | `validated` | §3.11's own field name. §3.8's role rule is the design's own example in this domain: “A finance document may mention an account holder and an issuing bank”, so the account holder and the issuing bank are separate fields. |
| `account_type` | string | `current account` | `llm_supported` | §3.11's own field name. |
| `tax_year` | year | — | `validated` | §3.11's own field name. §3.10's “Date extraction should be deliberately narrow” governs it, and a tax year is exactly the case “The product must not use fuzzy date parsing” exists to prevent — it is a labeled span, not a calendar year. |
| `record_type` | string | `statement` | `llm_supported` | §3.11's own field name. Statement, transaction export, receipt, payment confirmation, tax document, agreement. |
| `statement_period` | date range | — | `validated` | The span a statement covers, which is not its issue date. A record domain whose files each cover a period needs the period as a field or the period becomes a guess. |
| `account_holder_role` | string | `self` | `user_confirmed` | §3.8 requires the role as its own field. This is what separates the owner's own money from money managed for someone else under an authority. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a labeled account identifier together with an institution name in a letterhead position and a labeled statement period — §3.7's “positional weighting”<br>• a transaction export whose header row carries labeled date, description, and amount columns — §2.9: “sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”<br>• a tax document structure carrying a labeled tax year and an issuing authority |
| **needs LLM** | • a receipt with no institution and no account, which is §7.3's `Receipts and Confirmations` case: “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents”<br>• deciding which account a payment confirmation belongs to<br>• separating a personal transaction from a business one in a mixed corpus |
| **never alone** | • a bare institution name — banks appear in advertising, employment records, and news<br>• a bare account-shaped number<br>• a bare currency amount<br>• a bare year, which §3.10 warns is as likely a course identifier, a version number, or a build number<br>• a bounded download session — §3.9: “It is a purpose clue and a review aid, not a basis for automatic semantic propagation” |

**Template** — `account holder role → institution → account type → tax year`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Finance is the domain where year-first is most tempting and §5.5 rules against it: an account relationship runs for years and its documents belong together. Tax year stays as the deepest level, where it is a genuine filing unit rather than a calendar imposed on everything. §5.5's “a parent dimension should provide the context required to understand the child” puts the holder role first because §3.8 requires the owner's money and money managed for another to be distinguishable at the top.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.screenshot` | a captured banking page and a statement PDF carry the same account text. The capture is `captured subject = receipt` or a portal capture with a `referenced_record`; only the PDF has the issuer's labeled fields | §2.7 “a receipt, application portal, conversation, code problem, document, calendar, or research figure” |
| `pers.household-inventory` | one receipt is a transaction here and proof of purchase there | §7.3 “isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents” |
| `pers.eldercare` | statements for an account managed under an authority are financial records that are not the corpus owner's own — `account_holder_role` is the whole separator | §3.8 “A finance document may mention an account holder and an issuing bank” |
| `pers.travel-record` | a travel expense receipt belongs to the trip and to the account it was paid from | §3.11 “target university is not a fact that every file is expected to have” |

**Open question** — §3.11 gives Finance a fact schema while §3.15 makes it a safety domain, “meaning the system detects and protects them before any cloud or automated placement decision is allowed”. P6 SPEC already carries this as an open question. For this slice the unresolved part is narrower: does an ordinary supermarket receipt inherit the whole safety posture because it is a finance record, and if not, what draws the line? Joseph's call.

---

### `pers.child-school-record` — A child's school and activity records held by a parent

School, nursery, and activity paperwork about a child, held in an adult's corpus and belonging to the child rather than to the holder.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. §8.4 names educational records in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”, which is the material; no design sentence names this domain or gives it fields. §3.15's launch domains — “academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects” — cover the holder's OWN academic material, not a third party's. |
| **sensitivity** | `potentially_sensitive` — §8.4 names educational records in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”, and this material concerns a child who is not the corpus owner. §2.9's phrase “potentially sensitive” only; the handling class is P7's. |
| **work types** | school report, school letter or newsletter, permission or consent form, assessment or examination result, activity booking or invoice, work sample or artwork, medical or dietary form held by the setting |
| **grouping reasons** | • one child across their record<br>• one academic period at one setting<br>• one activity across its bookings and correspondence |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `subject_person_role` | string | `child` | `user_confirmed` | Whose records these are, as a role. §3.8's separate-fields rule, and the same refusal to encode a relationship as in `pers.dependant-care` — “A finance document may mention an account holder and an issuing bank”. |
| `setting` | string | — | `validated` | The school, nursery, or club. A gazetteer match under §3.7's “word-boundary matching”, corroborated by a report or letter structure rather than a bare mention. |
| `academic_period` | string | — | `validated` | The year or term. §3.10 requires dedicated academic-term patterns rather than generic parsing, and the term vocabulary a school uses is not always the university one. |
| `record_type` | string | `report` | `llm_supported` | Report, letter, permission form, activity booking, assessment, artwork or work sample. |
| `activity` | string | — | `llm_supported` | The club, sport, or lesson an out-of-school record belongs to. |
| `holder_authority` | string | — | `user_confirmed` | The basis on which the adult holds these. Shared with `pers.dependant-care` for the same reason: material held on someone else's behalf should say so. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a school report structure carrying a labeled pupil name and a labeled academic period beside a school name<br>• a permission or consent form structure carrying labeled pupil and guardian fields<br>• a setting name in a letterhead position together with a labeled pupil identifier — §3.7's “positional weighting” |
| **needs LLM** | • a child's own schoolwork, which carries no institutional structure at all<br>• deciding whether coursework belongs to the corpus owner or to a child, which is the collision this domain exists for<br>• photographs of artwork and work samples, which are camera captures with no school metadata |
| **never alone** | • a bare school name, which is also an employer, a venue, and a polling place<br>• a bare person name<br>• a bare term or year<br>• a childlike filename or handwriting, which is an inference about a person and not evidence about a file |

**Template** — `subject person role → setting → academic period`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — with a real qualification. School material is genuinely period-structured, so `academic_period` is a strong dimension, but it sits BELOW the setting for exactly §5.5's stated reason: “a parent dimension should provide the context required to understand the child”, and a term label repeats across settings and across children. This mirrors §5.4's Academic template, school → term, without copying its fields.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | a child's homework and the corpus owner's own coursework are the same kind of artefact in one corpus. The separator is `subject_person_role`, which no rule produces, and §4.8's validator has the exact analogue: a group must not merge material with a conflicting subject | §4.8 “the model has not invented a date, project, purpose, or membership that the dossier does not support” |
| `pers.dependant-care` | a school health or dietary form is both a care record and a school record | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.photo-occasion` | school performances and sports days produce captures that belong to the occasion, not to the school file | §4.2 “a photo group, it might be a deterministic event created from camera, time, and GPS metadata” |

**Open question** — Does a child get a named branch, and does the corpus owner's own academic material sit beside it or elsewhere entirely? Both choices encode an assumption about the household, and the label of the branch names a child in a filesystem. Joseph's call; the catalogue holds `subject_person_role` as a fact and proposes no default folder for a person.

---

### `pers.volunteering` — Volunteering and community service

Unpaid work for an organisation or cause — roles, training, hours, clearances, and the correspondence around them.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names volunteering. Proposed because the material looks like employment material — role descriptions, training records, references — while belonging to no employer, so a career schema would hold it wrongly. |
| **sensitivity** | `potentially_sensitive` — Vetting and clearance records concern criminal-record checks, and §8.4's “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” covers material of that kind through its legal-records entry. §2.9's phrase “potentially sensitive” only. |
| **work types** | volunteer agreement, role description, induction or training record, hours log, clearance or vetting document, expenses claim, reference or testimonial, organisation correspondence |
| **grouping reasons** | • one organisation relationship<br>• one clearance and its renewals, as a version family<br>• one cause across the organisations serving it |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `organisation` | string | — | `validated` | The body volunteered for. A gazetteer match under §3.7's “word-boundary matching”, corroborated by a role or agreement structure. |
| `role` | string | — | `llm_supported` | What the volunteer does, which is the field a reference or an application later needs. |
| `engagement_period` | date range | — | `validated` | From labeled fields, under §3.10's “Date extraction should be deliberately narrow”. |
| `record_type` | string | `training certificate` | `llm_supported` | Agreement, induction or training record, hours log, clearance or vetting document, expenses claim, reference. |
| `clearance` | string | — | `validated` | A background-check or vetting record, held as its own field because it carries a certificate number and an expiry that the rest of the domain does not. |
| `cause` | string | — | `user_confirmed` | The cause served, where a person volunteers across several organisations for one reason. User vocabulary — §5.1 requires labels to reflect it. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a volunteer agreement or role description structure carrying labeled organisation and role fields with no remuneration terms<br>• a vetting or clearance certificate carrying a labeled certificate number beside an issuing body<br>• a training record carrying a labeled course title and completion date beside a charity or community organisation name |
| **needs LLM** | • correspondence whose only signal is prose about unpaid work<br>• deciding whether a role is voluntary or employed, where the document does not say<br>• separating volunteering from a professional membership at the same organisation |
| **never alone** | • a bare organisation name<br>• a bare role title, which is shared with paid employment<br>• a bare date range<br>• the word `volunteer`, which appears in job descriptions, application essays, and research consent forms |

**Template** — `organisation → role → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A volunteering relationship runs for years and its training and clearance records are retrieved as a set. §5.5's “a parent dimension should provide the context required to understand the child”: `hours log` is meaningless without the organisation and role above it.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.faith-community` | volunteering through a congregation is both, and the community relationship carries the more sensitive fact | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.membership` | volunteering usually comes with membership of the same organisation | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.dependant-care` | a clearance obtained for volunteering with children is a vetting record whose subject is the corpus owner, not the children | §3.8 “A finance document may mention an account holder and an issuing bank” |

---

### `pers.faith-community` — Religious and community life

Material from participation in a congregation, faith tradition, or community body — study, rites, roles, and correspondence.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | New. No design sentence names faith or community life. Proposed because the material exists in real corpora and is otherwise scattered across membership, volunteering, and reference clips, each of which loses what it is. |
| **sensitivity** | `potentially_sensitive` — Participation in a faith or community body is a fact about a person that §8.4's default posture — “Privacy policy must be enforced before content reaches any model or external connector” — exists to protect, and §8.4's own interface warning applies: “a visible list of passport filenames on a shared screen may not be”. §2.9's phrase “potentially sensitive” and no class. |
| **work types** | study or teaching material, rite or ceremony certificate, role or office document, contribution or giving record, community correspondence, event or gathering record, photographed ceremony |
| **grouping reasons** | • one community relationship<br>• one rite or observance and its records<br>• one study course or programme |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `community` | string | — | `user_confirmed` | The congregation, group, or body. Held as user vocabulary, per §5.1's requirement that labels reflect the user's own words rather than an imposed taxonomy. |
| `record_type` | string | `study material` | `llm_supported` | Study or teaching material, rite or ceremony record, role or office document, contribution record, correspondence. |
| `rite_or_observance` | string | — | `llm_supported` | The specific rite or observance a record concerns, which is what makes a certificate more than a dated PDF. |
| `record_date` | date | — | `validated` | From a labeled field, under §3.10's “Date extraction should be deliberately narrow”. |
| `role` | string | — | `user_confirmed` | Any office or responsibility held. §3.8's role separation, and it is user-settled because titles vary entirely by tradition. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a certificate structure carrying a labeled rite or ceremony name beside a community or officiant name<br>• an existing user folder named for a community over members that share a document structure — §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent”<br>• a contribution or giving statement carrying a labeled reference beside a community organisation name |
| **needs LLM** | • study or teaching material whose only signal is its subject<br>• deciding whether religious-subject material is participation, academic study, or general reading |
| **never alone** | • a religious term in a filename or text, which appears identically in coursework, history reading, travel material, and art references<br>• a bare organisation name<br>• a bare date<br>• a calendar observance date, which is shared by everyone in a locality regardless of participation |

**Template** — `community → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. Participation is a long relationship and its records are retrieved by what they are. The catalogue stops at two levels deliberately: any deeper default would state something about the user's tradition and practice in the shape of their filesystem.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.membership` | congregation membership is a membership record; only this domain carries what the membership is of | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.volunteering` | service through a community body is volunteering with a community relationship attached | §3.11 “target university is not a fact that every file is expected to have” |
| `acad.course-enrollment` | religious studies coursework carries a course code and term and is academic material regardless of the subject | §3.5 “can only propose facts that belong to the active domain schema” |
| `pers.photo-occasion` | a rite produces captures that belong to the occasion; the certificate belongs here | §5.5 “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material” |

**Open question** — Should faith or community life appear as a named top-level branch at all, or only as a facet? A visible branch names a person's tradition on their screen, and §8.4's “a visible list of passport filenames on a shared screen may not be” is the design's own version of that concern. Joseph's call — and it is not a decision this catalogue should make on anyone's behalf.

---

### `pers.personal-legal` — Personal legal matters

A live legal matter the corpus owner is party to — the case, its parties, its filings, and its advisers.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.15 names legal among the safety domains: “Finance, identity, medical, and legal material should be implemented first as safety domains”, “meaning the system detects and protects them before any cloud or automated placement decision is allowed”. §5.7 names legal matters in the template library: “financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections”. §7.3 names legal forms in “passport scans, medical documents, account statements, visas, legal forms, or credentials”. The design names the domain repeatedly and gives it no fields. |
| **sensitivity** | `potentially_sensitive` — §8.4 names legal records in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and §7.3 names legal forms in “passport scans, medical documents, account statements, visas, legal forms, or credentials”, adding that “it should normally remain local-only and must not cause filenames or content to be exposed in model prompts”. §3.15 makes legal a safety domain. §2.9's phrase “potentially sensitive” only; the class is P7's. |
| **work types** | statement of case or filing, evidence or exhibit bundle, adviser correspondence, court or tribunal order, settlement agreement, fee note or costs schedule, witness statement |
| **grouping reasons** | • one matter from pre-action to conclusion<br>• one case reference across filings from every source<br>• a filing and its exhibits |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling (§3.13) | why |
|---|---|---|---|---|
| `matter` | string | — | `user_confirmed` | The dispute or transaction. The organising fact and the thing a person would name it by. |
| `party_role` | string | — | `user_confirmed` | Claimant, defendant, applicant, respondent, witness, or third party. §3.8's separate-fields rule at its most consequential — “A finance document may mention an account holder and an issuing bank” is the design's own instance of the same distinction. |
| `case_reference` | string | — | `direct` | A labeled court, tribunal, or file reference — §3.13's “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field” — and the only reliable join across filings from different sources. |
| `forum` | string | — | `validated` | The court, tribunal, ombudsman, or authority. A gazetteer match corroborated by a filing structure, per §3.7's “word-boundary matching”. |
| `adviser` | string | — | `validated` | The solicitor or firm. §3.8 keeps adviser, party, and forum apart, and “It should avoid using authorship or creator identity as a destination dimension” forbids the firm becoming the folder. |
| `filing_date` | date | — | `validated` | From a labeled field on a filing, under §3.10's “Date extraction should be deliberately narrow”. |
| `record_type` | string | `statement of case` | `llm_supported` | Filing, exhibit, order, correspondence, fee note. The field that keeps an exhibit bundle from being read as a filing, and it is only ever reached by interpretation. |
| `matter_stage` | string | — | `llm_supported` | Pre-action, filed, heard, decided, appealed, settled. A draft filed as though it were served is a real error, and §3.6's rule applies: insufficient support returns unknown. |

**Recognition** — §3.4's model: a pattern plus corroborating context, never a bare pattern.

| | |
|---|---|
| **deterministic** | • a labeled case or claim reference together with a court, tribunal, or ombudsman name on one document<br>• a filing structure carrying labeled party fields beside a statement of case heading<br>• a letter carrying a solicitor's labeled file reference in a letterhead position — §3.7's “positional weighting” |
| **needs LLM** | • correspondence about a matter that quotes no reference<br>• deciding whether a document is a draft, a served filing, or an exhibit<br>• separating the owner's own matter from one they are a witness in |
| **never alone** | • a bare reference number<br>• a bare firm or court name — law firms and courts appear in employment records, property files, and news<br>• a bare person name<br>• a bare date<br>• legal-sounding language, which appears in terms of service, tenancy agreements, and workplace policies |

**Template** — `matter → party role → record type`, `time_first: false`.

> §5.5's ordinary record rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”. A matter runs for years and its whole value is that the file sits together; year-first would separate a claim from the order that decided it. §5.5's “a parent dimension should provide the context required to understand the child”: `exhibit` needs the matter above it, and the party role belongs above the documents because it changes what every one of them means.

**Collides with**

| domain | signal that separates them | design cite |
|---|---|---|
| `pers.estate` | contentious probate is both; the separator is whether the matter is testamentary or a dispute | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains” |
| `pers.home-tenure` | a conveyance carries a solicitor's file reference and looks exactly like a legal matter | §3.9 “Topic answers what a file is about, while purpose answers what the file was for” |
| `pers.household-admin` | a complaint becomes a legal matter with no change of file format; a court or ombudsman reference is what marks the transition | §3.11 “target university is not a fact that every file is expected to have” |
| `pers.insurance` | a disputed claim generates legal filings and insurance correspondence in one thread | §4.8 “no stronger direct fact conflicts with the conclusion” |

---

