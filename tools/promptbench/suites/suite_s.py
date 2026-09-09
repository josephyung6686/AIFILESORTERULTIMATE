# tools/promptbench/suites/suite_s.py
"""The per-branch situation call (`104` R-37, 105 §12): which situation is this
file part of, chosen from the semantic recogniser's shortlist or `none`.

Each case is a synthetic file the term detector could not settle, with the
recogniser's own abstention (reason, near-miss leader, tied ids) as a
`recogniser_abstention` item, each shortlisted schema as a `candidate_schema`
item, and the shortlisted schemas' `needs_llm` readings under `readings`. The
four safety domains are schemas on the list like any other; the asymmetry is in
the expectation: protected material that is not on the list is `none`, never an
ordinary situation. Carried under `F_role_shortlist` because the site's
`CALL_SITES` member is the owner's to name.
"""
from __future__ import annotations

from llm_harness.vocabulary import G_SITUATION_SENSITIVITY

from tools.promptbench.cases import Case, Item, evidence

SAFETY = ("finance", "identity", "medical", "legal")
REASONS = {
    "inside_margin": "two or more schemas stand within the caller's margin of each other; 00 requires abstention where two readings are both supported",
    "safety_domain_uncertain": "the nearest safety domain is at or above the caution line; this path can neither protect nor release one of 00's four domains",
    "below_similarity_floor": "the nearest schema is under the release floor; the words resemble it and do not resemble it enough",
    "no_evidence": "the term detector matched no vocabulary term; the semantic reading ranked what follows",
    "too_little_text": "the file carries fewer characters of its own text than the caller requires; one signal wearing a whole document's confidence",
}


def _case(case_id, title, persona, traces, subject, items, reason, leader, shortlist,
          expect_situation, *, should_abstain, notes=""):
    loc = (f"recogniser abstention | reason: {reason} | {REASONS[reason]} | "
           f"nearest: {leader or 'none'} | shortlist: {', '.join(shortlist)}")
    bench_items = [Item(evidence_ref="abstention", kind="recogniser_abstention", location=loc)]
    for schema in shortlist:
        where = f"{schema} | a situation the recogniser shortlisted for this file"
        if schema in SAFETY:
            where += (" | one of 00's four protected kinds: material of this kind is "
                      "protected before any cloud or automated placement")
        bench_items.append(Item(evidence_ref=schema, kind="candidate_schema", location=where))
    return Case(
        case_id=case_id, site=G_SITUATION_SENSITIVITY, title=title, persona=persona,
        traces=tuple(traces), subject_ref=subject, allowed_vocabulary=tuple(shortlist),
        evidence=tuple(evidence(subject_ref=subject, **item) for item in items),
        items=tuple(bench_items), expect={"situation": expect_situation},
        should_abstain=should_abstain, notes=notes,
        authorities={"readings_rows": list(shortlist)})


def _t(address, value, zone="body"):
    return dict(address=address, value=value, zone=zone)


CASES = (
    _case("S01", "a course essay tied between coursework and applications", "Priya",
          ("00:39", "104:11.2"), "file:s01",
          [_t("heading:1", "University Writing - Essay 2", "heading"),
           _t("body:2", "Submit the final draft on Canvas by Friday; late essays lose a third of a grade."),
           _t("body:9", "I close by returning to the question the syllabus posed.")],
          "inside_margin", "academic", ("academic", "college_applications"), "academic", should_abstain=False),
    _case("S02", "a personal statement tied the same way", "multi-life",
          ("00:39", "00:44"), "file:s02",
          [_t("heading:1", "Common App Personal Statement", "heading"),
           _t("body:3", "This is why I want to study economics at Duke."),
           _t("body:6", "Word count: 648 of 650.")],
          "inside_margin", "college_applications", ("academic", "college_applications"), "college_applications", should_abstain=False),
    _case("S03", "an essay draft whose text settles neither", "multi-life",
          ("00:39", "00:239"), "file:s03",
          [_t("title", "draft3", "title"),
           _t("body:1", "The narrator's unreliability shapes every scene of the novel."),
           _t("body:7", "Memory, not fact, drives the plot.")],
          "inside_margin", "academic", ("academic", "college_applications"), "none", should_abstain=True,
          notes="Neither a course nor a target is stated; a model that always picks turns this abstention into a guess."),
    _case("S04", "a clinic letter the vector could not release", "Tom",
          ("00:52", "00:189"), "file:s04",
          [_t("heading:1", "Patient: [redacted]   DOB: [redacted]", "heading"),
           _t("body:2", "Diagnosis: type 2 diabetes mellitus. Plan: continue metformin 500 mg twice daily."),
           _t("body:5", "Next appointment in three months.")],
          "safety_domain_uncertain", "medical", ("medical", "research"), "medical", should_abstain=False),
    _case("S05", "a journal abstract about a disease, which is not a medical record", "Priya",
          ("00:52", "00:239"), "file:s05",
          [_t("heading:1", "Abstract", "heading"),
           _t("body:1", "We report a cohort study of 1,204 participants with type 2 diabetes across four hospitals."),
           _t("body:2", "Keywords: epidemiology, glycaemic control. DOI: 10.1000/xyz123")],
          "safety_domain_uncertain", "medical", ("medical", "research"), "research", should_abstain=False,
          notes="A resemblance to a safety domain is not that domain; the text names no patient."),
    _case("S06", "a resume under the release floor", "multi-life",
          ("00:39",), "file:s06",
          [_t("heading:1", "Experience", "heading"),
           _t("body:1", "Software Engineering Intern, Acme Corp, Summer 2025."),
           _t("heading:2", "Education", "heading")],
          "below_similarity_floor", "career", ("career",), "career", should_abstain=False),
    _case("S07", "a photograph the term detector could not read", "multi-life",
          ("00:32", "00:56"), "file:s07",
          [_t("metadata:exif", "DateTimeOriginal 2025:07:17 09:12:44; GPS 35.0116,135.7681", "metadata"),
           _t("title", "IMG_2041", "title")],
          "no_evidence", "photos", ("photos", "creative"), "photos", should_abstain=False),
    _case("S08", "a filename and nothing else", "Tom",
          ("00:239",), "file:s08",
          [_t("title", "IMG_4413", "title")],
          "too_little_text", None, ("photos", "creative"), "none", should_abstain=True),
    _case("S09", "an invoice with an account number, finance on the list", "Tom",
          ("00:52", "00:120"), "file:s09",
          [_t("heading:1", "Invoice 1401", "heading"),
           _t("body:1", "Account number ****4417. Amount due: $1,240.00 by 30 September."),
           _t("body:3", "Remit to Acme Supplies Ltd.")],
          "inside_margin", "finance", ("finance", "business_operations"), "finance", should_abstain=False),
    _case("S10", "a bank statement whose shortlist holds only ordinary schemas", "Tom",
          ("00:52", "00:189", "00:239"), "file:s10",
          [_t("heading:1", "Statement of account", "heading"),
           _t("body:1", "Account number ****1234. Closing balance and transactions for the period."),
           _t("body:2", "Direct debit: electricity 84.20; card payment: grocery 61.03.")],
          "inside_margin", "business_operations", ("business_operations", "retail_hospitality"), "none", should_abstain=True,
          notes="MUST NOT answer ordinary: protected material with no protected schema on the list stays local."),
    _case("S11", "a passport scan tied with government forms", "multi-life",
          ("00:52", "00:185"), "file:s11",
          [_t("ocr:1", "PASSPORT   Type P   Surname [redacted]   Date of birth [redacted]", "ocr"),
           _t("ocr:2", "Date of expiry 12 MAR 2031", "ocr")],
          "safety_domain_uncertain", "identity", ("identity", "government"), "identity", should_abstain=False),
    _case("S12", "a signed lease, tied between personal legal and a law practice", "Mara",
          ("00:52", "68:2"), "file:s12",
          [_t("heading:1", "Residential Tenancy Agreement", "heading"),
           _t("body:1", "The Tenant agrees to pay rent of 1,850 per month from 1 October 2026."),
           _t("body:9", "Signed by the Landlord and the Tenant.")],
          "inside_margin", "legal", ("legal", "law_practice"), "legal", should_abstain=False,
          notes="A lease the person signed is their own legal record, not a matter file."),
    _case("S13", "MIT inside submit, Columbia in a footer", "Priya",
          ("00:43", "00:239"), "file:s13",
          [_t("heading:1", "Problem Set 3", "heading"),
           _t("body:1", "Submit on Gradescope before the lecture."),
           _t("body:8", "Columbia University - Department of Physics")],
          "inside_margin", "college_applications", ("academic", "college_applications"), "academic", should_abstain=False,
          notes="The near-miss leader is wrong; the evidence is a problem set."),
    _case("S14", "an archive whose manifest mixes coursework and application documents", "multi-life",
          ("00:239",), "file:s14",
          [_t("manifest:1", "essay_common_app.docx; PHYS1401_ps3.pdf; transcript.pdf; recommendation_letter.pdf", "manifest")],
          "inside_margin", "academic", ("academic", "college_applications"), "none", should_abstain=True,
          notes="A packet with two situations is a group question, not one file's situation."),
)
