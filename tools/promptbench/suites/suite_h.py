# tools/promptbench/suites/suite_h.py
"""The gate (`00` amendment 7(c), site `H_restricted_kind`): is this file a record
of one of `105` §13.3's ten restricted kinds, and which?

Each case is a synthetic file as the gate sees it: a SHORT dossier -- the opening
of a document and its metadata -- and nothing else. There is no shortlist item and
no abstention report, because the gate's options are the same eleven on every file
in every corpus and its template carries them; that is the whole shape of the site
(`model_gate.build_gate_request` says so at length).

**THE ASYMMETRY IS THE SUITE'S SUBJECT AND IT IS THE OWNER'S OWN.** The template
states it: *"A file you call none_of_these wrongly may be sent to a provider. A
file you call one of the ten kinds wrongly stays on this machine and is looked at
by a person."* So the ten record cases here each carry the record's OWN
particulars -- a booking reference, a balance, a patient line, a passport number,
a signature clause -- and the four ordinary cases are the near misses `104` §18.56
measured a model getting wrong in the other direction: a paper ABOUT a disease
called medical, a syllabus that mentions tuition, a flyer that says bring your ID.
Calling any of those a restricted kind costs the person nothing but a review;
calling a real record ordinary is the error this site exists to prevent.

Ten of the fourteen expect a kind. Four expect `none_of_these`, and those are the
`should_abstain` cases: at this site "abstain" is not silence, it is the
clearance, and the bench reads it the same way `cli.gate_kind_named_by_verdict`
does -- the payload says `none_of_these` and the claim carries `unknown`.
"""
from __future__ import annotations

from llm_harness.vocabulary import H_RESTRICTED_KIND

from tools.promptbench.cases import Case, evidence

#: `105` §13.3's ten and the decline, spelled as the identifiers the model answers
#: with. The same eleven on every case, because they are the same eleven on every
#: file: `model_gate.restricted_kind_vocabulary` builds them from the library's own
#: schema at the product, and a case that offered a subset would be measuring a
#: site this product does not have.
VOCABULARY: tuple[str, ...] = (
    "receipt", "order_confirmation", "boarding_pass_or_ticket",
    "own_account_or_message_screenshot", "bank_or_card_notification",
    "identity_document", "medical_record", "financial_statement_or_tax_return",
    "credentials_or_password_vault", "legal_document_naming_the_person",
    "none_of_these",
)


def _case(case_id, title, persona, traces, subject, readings, kind, *, notes=""):
    """One gate case. `kind` is `"none_of_these"` for a file that must be cleared."""
    return Case(
        case_id=case_id, site=H_RESTRICTED_KIND, title=title, persona=persona,
        traces=tuple(traces), subject_ref=subject,
        allowed_vocabulary=VOCABULARY,
        evidence=tuple(evidence(subject_ref=subject, **reading)
                       for reading in readings),
        # NO REFERENCE-ONLY ITEMS. The gate's dossier carries the file's own
        # readings and nothing else; the ten kinds are in the template.
        items=(),
        expect={"restricted_kind": kind},
        should_abstain=(kind == "none_of_these"),
        notes=notes)


def _t(address, value, zone="body"):
    return dict(address=address, value=value, zone=zone)


CASES = (
    # --- the ten kinds, each shown by the record's own particulars ------------
    _case("H01", "a shop receipt", "Tom", ("105:13.3", "00:52"), "file:h01",
          [_t("heading:1", "RECEIPT", "heading"),
           _t("body:1", "Kowloon Stationery Co.   14 Aug 2026   14:22"),
           _t("body:2", "2 x A4 notebook  48.00   1 x pen  12.00   TOTAL 60.00 HKD"),
           _t("body:3", "VISA ****7781   Thank you for your purchase.")],
          "receipt"),
    _case("H02", "an order confirmation email", "multi-life",
          ("105:13.3",), "file:h02",
          [_t("heading:1", "Your order is confirmed", "heading"),
           _t("body:1", "Order number 118-4402517-9930644, placed 3 September 2026."),
           _t("body:2", "Shipping to the address on file. Estimated delivery 8 September."),
           _t("body:3", "Order total 214.90. Manage your order in Your Account.")],
          "order_confirmation"),
    _case("H03", "an e-ticket with a booking reference", "Priya",
          ("105:13.3", "104:18.56"), "file:h03",
          [_t("heading:1", "Electronic ticket - boarding pass", "heading"),
           _t("body:1", "Booking reference 4KQ2ZP   Flight CX255   HKG to LHR"),
           _t("body:2", "Depart 12 Oct 2026 23:55   Seat 41K   Gate closes 30 minutes before departure."),
           _t("body:3", "Present this document with photo identification at the gate.")],
          "boarding_pass_or_ticket",
          notes="§18.56's own case: a correct e-ticket verdict was thrown away by a "
                "retyped citation. The value here is what a copied span must come from."),
    _case("H04", "a screenshot of the person's own inbox", "multi-life",
          ("105:13.3", "00:56"), "file:h04",
          [_t("ocr:1", "Inbox (3)   Primary   Social   Promotions", "ocr"),
           _t("ocr:2", "From: Housing Office   Re: your tenancy - action needed", "ocr"),
           _t("ocr:3", "From: Mum   dinner sunday?   09:41", "ocr"),
           _t("title", "Screenshot 2026-08-02 at 09.41.17", "title")],
          "own_account_or_message_screenshot"),
    _case("H05", "a card notification letter", "Tom", ("105:13.3",), "file:h05",
          [_t("heading:1", "Important notice about your card", "heading"),
           _t("body:1", "We have declined a transaction of 1,204.00 on the card ending 4417."),
           _t("body:2", "If this was you, confirm it in the app. If it was not, call the number on the back of your card."),
           _t("body:3", "This is an automated alert from your bank.")],
          "bank_or_card_notification"),
    _case("H06", "a passport data page", "multi-life",
          ("105:13.3", "00:52"), "file:h06",
          [_t("ocr:1", "PASSPORT   Type P   Code HKG", "ocr"),
           _t("ocr:2", "Passport No. K12345678   Date of birth 04 JUN 2004", "ocr"),
           _t("ocr:3", "Date of expiry 12 MAR 2031   Authority Immigration Department", "ocr")],
          "identity_document"),
    _case("H07", "a health form naming a patient", "Tom",
          ("105:13.3", "00:52", "104:18.56"), "file:h07",
          [_t("heading:1", "Health Authorisation Form", "heading"),
           _t("body:1", "Patient name: Chan Ka Ming   Date of birth: 11/02/2005"),
           _t("body:2", "Known conditions: asthma. Current medication: salbutamol inhaler as needed."),
           _t("body:3", "I authorise the school nurse to administer the medication above.")],
          "medical_record",
          notes="§18.56's worst miss: two forms of exactly this shape carried basis "
                "`detector` with protected 0 and were cloud-eligible on the rules' word."),
    _case("H08", "a bank statement", "Tom", ("105:13.3", "00:52"), "file:h08",
          [_t("heading:1", "Statement of account", "heading"),
           _t("body:1", "Account number ****1234   Period 1 - 31 July 2026"),
           _t("body:2", "Opening balance 8,412.03   Closing balance 6,987.55"),
           _t("body:3", "28 Jul  card payment  grocery  61.03   30 Jul  direct debit  electricity  84.20")],
          "financial_statement_or_tax_return"),
    _case("H09", "a saved credentials file", "multi-life",
          ("105:13.3", "00:239"), "file:h09",
          [_t("title", "keys", "title"),
           _t("body:1", "wifi (home): correct-horse-battery-staple"),
           _t("body:2", "recovery codes: 4f2a-91bc, 7d10-33ee, 0a5c-b721"),
           _t("body:3", "router admin: admin / changeme2026")],
          "credentials_or_password_vault"),
    _case("H10", "a signed tenancy agreement", "Mara",
          ("105:13.3", "68:2"), "file:h10",
          [_t("heading:1", "Residential Tenancy Agreement", "heading"),
           _t("body:1", "Between the Landlord, Wong Property Holdings Ltd, and the Tenant, Mara Oduya."),
           _t("body:2", "The Tenant agrees to pay rent of 1,850 per month from 1 October 2026."),
           _t("body:9", "Signed by the Landlord and the Tenant on 14 September 2026.")],
          "legal_document_naming_the_person"),

    # --- the four ordinary files, each a near miss ---------------------------
    _case("H11", "a course syllabus that mentions tuition", "Priya",
          ("00:239", "104:18.56"), "file:h11",
          [_t("heading:1", "PHYS 1401 Syllabus", "heading"),
           _t("body:1", "Spring 2026. Instructor: Dr. Lee. Credits: 3."),
           _t("body:2", "Tuition and lab fees are billed by the registrar; see the student portal for the schedule of charges."),
           _t("body:3", "Assessment: two midterms and a final.")],
          "none_of_these",
          notes="The template's own counter-example: a syllabus that mentions tuition "
                "is not a financial statement. Calling it one keeps a course file off "
                "the cloud for no reason."),
    _case("H12", "a club flyer that says bring your ID", "multi-life",
          ("00:239",), "file:h12",
          [_t("heading:1", "Photography Society - open shoot", "heading"),
           _t("body:1", "Saturday 20 September, 14:00, meet at the campus gate."),
           _t("body:2", "Bring your student ID to get into the building. Cameras provided if you do not have one."),
           _t("body:3", "Sign up on the noticeboard outside room 3.14.")],
          "none_of_these",
          notes="The template's own counter-example: a flyer that says bring your ID "
                "is not an identity document. It carries no number and names nobody."),
    _case("H13", "a research abstract about a disease", "Priya",
          ("00:52", "00:239", "104:18.56"), "file:h13",
          [_t("heading:1", "Abstract", "heading"),
           _t("body:1", "We report a cohort study of 1,204 participants with type 2 diabetes across four hospitals."),
           _t("body:2", "Glycaemic control improved in the intervention arm over twelve months."),
           _t("body:3", "Keywords: epidemiology, glycaemic control. DOI: 10.1000/xyz123")],
          "none_of_these",
          notes="§18.56 measured this exact error at site G: a journal abstract about a "
                "disease called a medical record. It names no patient."),
    _case("H14", "a photograph with EXIF and nothing else", "multi-life",
          ("00:32", "00:56"), "file:h14",
          [_t("metadata:exif", "DateTimeOriginal 2026:07:17 09:12:44; Model Pixel 8", "metadata"),
           _t("title", "IMG_2041", "title")],
          "none_of_these",
          notes="Nothing here is a record of anything. A gate that named a kind for it "
                "would keep every photograph in a corpus off the cloud."),
)
