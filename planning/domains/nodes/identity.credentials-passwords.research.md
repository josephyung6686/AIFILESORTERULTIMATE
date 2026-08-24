# R1b lab notes — `identity.credentials-passwords`

## Result and node test

**Kept as a template.** It is not a second Identity schema and it does not create a credential
taxonomy. The landed Identity schema is intentionally field-less and contains the broad union of
all Identity safety signals. This row earns a separate node on two differences that matter in the
product:

- its recognition boundary is specific to password exports, recovery-code sets, private key
  material, key-bearing containers and exact credential-vault formats;
- its privacy boundary treats the secret value as useful for protection but useless for every
  organizational output. It is never a fact, candidate label, preview, branch name, excerpt or
  group fact.

The schema and this template both have an empty `dimension_order`; that agreement is required by
D1/PR-6, not evidence that the rows are duplicates. The schema says which broad safety family may
activate. This row says which credential-bearing situation has been observed, which false friends
must be rejected, what can be grouped without copying facts, and how unreadable vault formats
interact with the residual library.

## Authorities read

Local authority and contract material:

- `planning/00-database-agent-product-design.md`, read in full. This is the wording authority.
- the relevant evidence, grouping, tree, residual and privacy renderings in
  `planning/01-product-design-structured.md`;
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, and `planning/domains/CONNECTION-EXAMPLES.md`;
- the stamped roster row, `planning/domains/canonical_fields.json`, and the closed
  `SOURCE_TYPES` in `src/evidence_shape/vocabulary.py`;
- D1, D2 and D6 ratification state in the council decision brief;
- the landed Identity schema and both sibling Identity templates;
- the landed reciprocal neighbors `identity.core-documents`, `code.dotfiles-environment`,
  `finance.crypto-assets`, and `career.credentials-licenses`, including their research notes;
- R2's sensitivity catalogue: detector rules, identifier classes and redaction transforms under
  `planning/deferred-catalogues/08-sensitivity-detector/`.

The current R2 catalogue is important because it already owns the concrete secret-pattern layer.
This node consumes or names its rule families; it does not fork their regexes, label lists,
placeholder vocabulary or injected counts.

## External technical evidence used

These are primary standards or product-owner format documents. They establish recurring file
structure and security properties only. They do not authorize a new fact field, confidence score,
handling class, automatic move, key-validation claim or attempt to decrypt a file.

- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html) distinguishes passwords,
  recovery codes and cryptographic authentication keys as authentication secrets and requires
  exported/synced authentication keys to be strongly protected. It supports the protection
  boundary; this row imports none of NIST's assurance levels or numeric requirements.
- [RFC 7468](https://www.rfc-editor.org/info/rfc7468/) defines textual encodings for PKIX/PKCS
  objects and distinguishes private-key, encrypted-private-key and public-key labels. It supports
  the private/public discriminator already owned by R2's `det-auth-key-material` rule.
- [OpenSSH `PROTOCOL.key`](https://github.com/openssh/openssh-portable/blob/master/PROTOCOL.key)
  documents the OpenSSH private-key container, including its format marker and encrypted private
  key list. It supports exact local parsing; it does not justify reading comments as account facts.
- [RFC 7292](https://www.rfc-editor.org/info/rfc7292/) defines PKCS #12/PFX as a container that may
  carry private keys, shrouded private keys, certificates and miscellaneous secrets. Because the
  container is heterogeneous, PFX structure alone is insufficient; a safely observed key-bag type
  is the discriminator used in the fixture. The current
  [RFC 9879 update](https://www.rfc-editor.org/info/rfc9879/) modernizes password-based integrity
  options; it does not remove the key-versus-certificate bag distinction used here.
- [1Password's export guide](https://support.1password.com/export/) states that desktop 1Password
  exports may be 1PUX or CSV and that exported files are plaintext. Its
  [1PUX format description](https://support.1password.com/1pux-format/) documents a ZIP archive
  containing `export.attributes`, `export.data` and a `files` subtree. That exact manifest layout,
  not the extension, is the node's deterministic archive signal.
- [Bitwarden's export documentation](https://bitwarden.com/help/export-your-data/) documents
  plaintext JSON/CSV, encrypted JSON and ZIP-with-attachments variants. The variety is why a
  `.json`, `.csv` or `.zip` extension cannot decide this template; the structured credential rule
  or a dedicated encrypted-format marker must do the work.
- [KeePass's KDBX format specification](https://keepass.info/help/kb/kdbx.html) identifies KDBX as
  the encrypted database format for usernames, passwords, URLs and related data. KeePass also
  publishes the [database signatures](https://keepass.info/help/base/repair.html) used for exact
  format identification. This supports metadata-only recognition without a master key, while the
  R2 conflict remains a product decision rather than being smoothed over here.
- [GitHub's recovery-method documentation](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication-recovery-methods)
  documents a downloadable recovery-code file whose codes are single-use and should be stored
  securely. It supports the recovery-code fixture and the rule that apparent currentness or usage
  state cannot be inferred from a saved file.

No web source is quoted in the JSON. Product behavior and all design quotations remain grounded in
`00`; external sources only verify the existence and structure of file formats.

## Bottom-up file set

The JSON carries the full observation/fact split. This table records why each concrete file was
kept in the research set.

| Concrete file | Carrier | Why it matters | Inactive outcome |
|---|---|---|---|
| `1Password Export.1pux` | `archive` | exact unencrypted export manifest; members remain unextracted | Protected Records |
| `bitwarden_export_2026.json` | `code_structured` | populated structured login records; filename year means nothing | Protected Records |
| `Passwords.csv` | `spreadsheet` | canonical password-export header/row shape and repeated-service trap | Protected Records |
| `Accounts.xlsx` | `spreadsheet` | hand-maintained credentials are as sensitive as tool exports; bank-name Finance false friend | Protected Records |
| `github-recovery-codes.txt` | `text_document` | explicit recovery heading plus one-time code grid | Protected Records |
| `Screenshot 2026-08-20 at 09.14.33.png` | `ocr` | same recovery material through OCR plus genuine Photos facts | Protected Records |
| `id_ed25519` | `code_structured` | OpenSSH private-key structure; sibling names and directory do not decide it | Protected Records |
| `id_ed25519.pub` | `code_structured` | public-key false friend and no-copy key-pair grouping case | Independent Records |
| `client-auth.p12` | `opaque_binary` | PFX plus observed shrouded-key bag; extension/PFX alone insufficient | Unsupported or Encrypted |
| `Personal.kdbx` | `opaque_binary` | exact known credential-vault format and the R2/roster merge tension | Unsupported or Encrypted |
| `Reset your password.eml` | `email` | native recovery-message shape; the raw reset control remains local | Protected Records |
| `.env.production` | `code_structured` | Code situation with live secrets; schema co-activation but template mutex | Protected Records |
| `recovery phrase backup.jpg` | `image` | wallet-secret seam with Finance and missing R2 mnemonic rule | Protected Records |
| `Exchange Account Statement 2026-Q1.pdf` | `text_document` | reporting-on-assets false friend; no credential structure | Protected Records through Finance |
| `credentials.zip` | `archive` | professional-credential false friend and outer-name ambiguity | Protected Records through Career |
| `Certificate of Naturalization.pdf` | `text_document` | core civil credential versus authentication credential | Protected Records |
| `vault-backup.zip` | `archive` | generic locked archive: encryption and a suggestive name prove nothing | Unsupported or Encrypted |
| `Password Security Policy.pdf` | `text_document` | topic vocabulary without a stored secret or personal account | Reading Inbox |
| `Login page.png` | `ocr` | empty login form and positive screenshot origin; labels are not credentials | Temporary Screenshots |

The set covers every source family this row claims: structured text/data, spreadsheets, native
documents, images, OCR, email, archives and opaque binary. It also covers a protected singleton,
duplicates/versions in the grouping rules, mixed-schema files, neighbor false positives, a readable
manifest, an unreadable archive, public/private material and a model-only ambiguity.

## Field and template analysis — none proposed

The landed Identity schema intentionally contains no field rows. This node therefore has:

```text
fields: []
proposed_fields: []
dimension_order: []
```

The tempting additions were rejected rather than deferred inside the JSON:

- `service`, `site` or `provider` would reveal which accounts the user holds and would turn every
  password-export row into a destination candidate;
- `username`, `account`, `holder` and `email` are person/instrument identifiers, not facts about why
  the file exists;
- `password`, `token`, `recovery_code`, `private_key` and `mnemonic` are raw authentication secrets,
  not fields under any schema;
- `credential_type`, `key_type`, `recovery_method`, `vault`, `expiry`, `validity` and `status` are
  unnecessary for protection and would create a visible sensitive taxonomy before D1 or privacy
  policy permits one.

No existing canonical key can safely stand in for those concepts. `institution` is a Finance
issuer, not a service listed in a credential store. `account_type` describes a financial account,
not an authentication method. `artifact_type` belongs to Research/Code and does not become a secret
kind. `work_type` is Academic. Reusing any of them would be a semantic collision rather than
canonical reuse.

`work_types` in the node are descriptive coverage values only. Because Identity has no equivalent
field, they are not facts and cannot be serialized into a folder level. They help test whether the
node covers the real file situations the roster named.

The recommended tree is intentionally absent. Even a path containing a provider name or a leaf
called Recovery Codes leaks sensitive account information to filesystem views, sync logs and
backups. The current safe flow is:

```text
recognized credential material
  → protect locally before model access
  → attach to an already accepted protected group only on independent evidence
  → otherwise leave in place or represent under redacted Protected Records
```

Time is metadata and version evidence only. Export dates neither identify an account nor prove
which copy is current.

## Recognition ownership and abstention boundary

### Existing R2 families consumed

- `det-credential-password-export` owns credential header/key sets, populated-row evidence and its
  injected row count.
- `det-credential-2fa-backup-codes` owns recovery headings, code-grid shapes and its injected line
  count.
- `det-auth-key-material` owns private-key armor/body recognition and the public/certificate
  negatives.
- `det-env-secret-assignments` owns live-secret detection inside configuration, but a fire from
  that rule raises Identity protection; it does **not** by itself make the configuration this
  template's organizational situation.
- R2's `authentication_secret` identifier class owns locality and full-span dropping. The domain
  node assigns no handling class and defines no alternate redaction procedure.

The JSON names these rule IDs and describes their semantic boundary. It deliberately does not copy
their regexes, label lists, placeholder markers, numeric slots or P7 ceiling vocabulary.

### New structural proposals, and why they are narrow

Three structures are outside current R2:

1. an exact 1PUX archive manifest. This is readable member metadata, not a secret-content scan;
2. exact credential-container formats such as KDBX, identified through a dedicated approved
   metadata-only parser;
3. a wallet recovery-phrase heading plus structured word-list region, whose term vocabulary and
   validation belong in R2 if accepted.

The first can activate from a readable manifest today. The second and third remain explicit merge
questions because current R2 does not produce them. Generic encryption, arbitrary word lists and
filename conventions remain never-alone evidence.

PKCS #12 is deliberately more constrained than KDBX. A PFX may carry a certificate without a
private key, so the node requires a safely observed key-bag type. A PFX wrapper or extension is not
credential evidence. Likewise, a PEM or OpenSSH public key is not a secret; it may join a verified
key set without gaining Identity activation from the group.

### Model boundary

The model is not a secret detector and never opens an encrypted object. Its legitimate questions
are document-role questions after local extraction: handwritten recovery material versus an
ordinary note, a credential inventory versus bookmarks, a reset record versus guidance, or one
mixed manifest versus an unrelated pile. For this row `needs_llm` always means local-model or
explicitly authorized operation after P7. If the answer would require the secret value, full OCR,
an unredacted URL, a private-key body or decrypted container contents, the operation is denied or
abstains.

## Grouping without propagation

The meaningful groups are structural rather than folder-taxonomic:

- one password export and its archive attachments;
- one vault across exact duplicates, safe backups and reviewed export versions;
- one cryptographically verified private/public/certificate key set;
- one recovery kit with independent recovery context on each member;
- one migration event with explicit source, destination and completion evidence;
- one protected singleton;
- one user-confirmed attachment of an unreadable object.

None creates service, account, holder, key type or purpose facts. A session may retrieve candidates
but cannot establish the set. A private-key filename stem does not pull in the public key. An
accepted crypto-account group does not turn a keystore into a Finance record. An accepted code
project does not make all high-entropy files credentials. An unreadable member retains unknown
contents even after manual attachment.

## Collision audit

Four same-kind `collides_with` edges were authored, all reciprocating landed neighbors:

- **`identity.core-documents`** — shared identity/credential/certificate/key vocabulary; civil or
  bearer evidence versus authentication access material.
- **`code.dotfiles-environment`** — secret-bearing configuration versus a file whose whole
  structure is credential material. `.env.production` is the boundary fixture.
- **`finance.crypto-assets`** — holdings/activity records versus wallet recovery and key material.
  The Finance node already identifies this as its sharpest exposure-risk collision.
- **`career.credentials-licenses`** — professional standing versus account access despite the
  shared word credential. `credentials.zip` is the common fixture.

Each edge names one potentially shared evidence item and the structure that discriminates it. None
is a broad topical relation, and no schema id or residual template appears in `collides_with`.

Because this is a template, `also_holds_with` is empty by contract. Real co-activations are carried
by schema edges and per-file `also_schema`: a recovery-code screenshot is both Photos and protected
Identity material; a project configuration can carry Code facts while Identity safety fires; a
wallet-recovery photograph carries Photos facts while Finance is explicitly rejected.

## Neighbors considered but not edged

- **`code.software-project`** — a project-root marker and a secret detector fire on disjoint
  evidence. The project remains structurally preserved while Identity protection applies, so this
  is schema co-activation, not a template mutex. The sharper one-evidence ambiguity is already
  captured against `code.dotfiles-environment`.
- **`code.scratch-prototypes`** — a loose JSON or text file is not a collision once credential
  structure is required. With no populated credential rule and no other anchor it is Review Later;
  source type and Downloads position decide nothing.
- **`finance.personal-records`** — bank names, account labels and usernames occur in access sheets,
  but a Finance record requires statement/account/period/balance or equivalent record structure.
  The concrete self-custody confusion is much sharper and already represented by
  `finance.crypto-assets`.
- **`identity.immigration-visa`** — its landed research correctly treats a visible share code on an
  eVisa/status page as a raw value to redact, not proof that the whole status record is a credential
  store. A separate recovery-code file, password export or key activates this row on its own.
- **`photos.screenshot-captures`** — screen origin and secret content are independent observations.
  The screenshot can retain a Photos fact while protection wins; per-file `also_schema` is the
  correct representation, not a mutex edge that would discard one reading.
- **`applications.purpose-packet`** — a credential file may be a protected member of a migration,
  onboarding or application packet, but packet purpose and member secret structure are disjoint.
  Membership never copies purpose or target facts onto the credential.
- **`Protected Records`, `Unsupported or Encrypted`, `Review Later`, `Reading Inbox`,
  `Temporary Screenshots`, `Independent Records`** — all are residual destinations, not domain
  neighbors. They appear only in `falls_through_to`.

## Files and families considered but rejected

- browser/application credential databases located under generated application-state trees were
  rejected from organization. They may still require local protection, but `00`'s exclusions and
  preservation rules prevent this node from treating an application's internal database as a
  personal filing proposal;
- a free-standing passkey file type was rejected. Passkeys may appear inside a documented vendor
  export, but the research found no stable universal file extension whose existence would justify a
  new carrier or rule;
- authenticator-app backups were not made a deterministic family because vendor formats and
  encryption envelopes vary. An exact documented format can be added through the same dedicated
  metadata-only rule used for KDBX; a generic backup name cannot;
- `.ovpn`, `.mobileconfig`, generic JSON Web Key sets and certificate chains were cut as primary
  examples. They can contain private material, public material or mere references; the existing
  private-key/key-bag detectors already express the honest boundary without extension fishing;
- generic `.gpg`, `.age`, encrypted ZIP, disk image and encrypted PDF files were rejected as
  credential evidence. They belong to Unsupported or Encrypted until an exact format or readable
  content says more;
- contacts and calendars were rejected as carriers for this situation. A contact may contain a
  service address and a calendar event may remind the user to rotate a password, but neither stores
  the authentication material;
- presentations, audio/video and design files were rejected from `file_kinds`. A slide or video can
  discuss credentials, but topic vocabulary is not a credential store; an embedded screenshot is
  routed through image/OCR evidence instead.

## Privacy and handling discipline

The node writes only the catalogue sensitivity value `potentially_sensitive`. It does not write
any of P7's handling classes, even though R2 legitimately uses that vocabulary inside P7's own
catalogue. D2 keeps `ClassificationRecord` authoritative.

The universal `sensitivity_status` fact may be legal after P7 classifies the file. The secret value
itself is never legal. For this node that includes passwords, one-time passwords, recovery codes,
reset tokens, access tokens, private-key material, mnemonic words, usernames tied to secrets and
unredacted reset URLs. The source observations remain local; ordinary summaries show only a
redacted protected count or equivalent safe representation. No secret is retained partially for a
folder name or explanation.

Opaque files are metadata-only unless a dedicated extractor has been explicitly approved. Exact
format identification does not imply validity, ownership, decryptability, integrity or currentness.
The product never tests passphrases, brute-forces, opens a container through an external service or
uses a neighboring export to infer hidden contents.

## NEEDS-JOSEPH

1. **Exact opaque credential format versus unreadable/unclassified.** The roster assigns this row
   `opaque_binary`, but R2 currently says binary P12/PFX and KDBX files with no extracted text do not
   fire its rules. Should exact dedicated metadata-only identification activate Identity protection
   and Protected Records without decrypting the file, or remain Unsupported or Encrypted until
   user confirmation? Recommendation: exact KDBX or key-bag evidence may activate protection;
   generic encryption may not.
2. **Wallet mnemonic ownership in R2.** `finance.crypto-assets` explicitly routes recovery phrases
   here, but R2 has no mnemonic rule. If the product will detect them, R2 must own the vocabulary,
   conjunction, negatives and evidence shape. This row must not smuggle in a regex.
3. **Protected path depth.** May any provider, service, account or credential-type level appear in a
   default filesystem tree when the path itself reveals authentication relationships? This row
   recommends no automatic depth and a redacted Protected Records representation only.
4. **Permitted local-model policy.** May an installed local model inspect ambiguous protected OCR by
   default, or does every model invocation require explicit policy authorization? Default cloud use
   remains closed either way.

None blocks landing the node. The unresolved cases have safe outcomes: exact readable credential
structure is protected; generic unreadable material is represented as Unsupported or Encrypted;
raw secrets remain local; and no folder taxonomy is generated.

## Validation notes

- Both output paths match the stamped assignment, and only those two files were authored.
- Every `facts_legal` key is universal or belongs to the independently active Code, Finance or
  Photos schema. Identity contributes no fields.
- Every example separates source observations from legal facts and explicitly forbids a folder
  path.
- All source types are members of the closed `SOURCE_TYPES` vocabulary.
- All four collision targets are template ids present in the roster; all residuals use the closed
  residual names.
- Extensions, filenames, sessions, encryption, missing EXIF, public certificates, provider names
  and group membership are never-alone signals.
- No confidence score, numeric threshold or P7 handling-class assignment is present.
- Every span quoted from `00` in the JSON was fixed-string verified against the authoritative
  file; external technical sources are paraphrased rather than quoted.
