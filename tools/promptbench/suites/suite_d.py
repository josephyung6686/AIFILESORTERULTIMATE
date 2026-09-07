# tools/promptbench/suites/suite_d.py
"""Site D stress cases: one residual file, the approved residual areas, eight actions.

`00`:118-129 governs. The file's OCR, text or metadata is released; every
approved residual area and every branch a return could go to arrives as an
evidence item whose `location` is the area's label chain and what it holds
(`00`:120), the "user-approved residual library" the dossier of `00`:124 names.
A return target is a NODE: the branch that was built from the confirmed group or
accepted packet (`00`:107), because the validator requires a return's target to
exist in the frozen tree (packet §7, G8).

At D every cited item's `location` is the subject ref (packet §7, G5).
"""
from __future__ import annotations

import hashlib

from llm_harness.vocabulary import (
    ABSTAIN, CHOOSE_BROAD_PARENT, CHOOSE_RESIDUAL_DESTINATION, D_RESIDUAL,
    LEAVE_IN_CURRENT_LOCATION, MARK_PROTECTED_OR_UNSUPPORTED, MARK_REVIEW_LATER,
    RETURN_ACCEPTED_PACKET, RETURN_CONFIRMED_GROUP,
)

from tools.promptbench.cases import Case, Item, evidence

PLAN = "plan-bench-1"

AREAS = {
    "r-01": "Photos > Temporary Screenshots | residual area | holds screenshots that look time-sensitive or remind the person of something but belong to no accepted project, trip, application or event",
    "r-02": "Photos > One-Off Images | residual area | holds images with no event, project, reference collection or photo-family association",
    "r-03": "Personal > Reference Clips | residual area | holds saved visual inspiration, product references, quotes, recipes, short article captures and code snippets kept for later retrieval",
    "r-04": "Personal > Independent Records | residual area | holds standalone certificates, notices, confirmations and forms with a durable purpose but no broader group",
    "r-05": "Personal > Receipts and Confirmations | residual area | holds isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts and event tickets",
    "r-06": "Personal > Reading Inbox | residual area | holds papers, articles, reports and saved PDFs that look like reading material with no active research, course or project association",
    "r-07": "Review Later | residual area, review-only, never moves a file | for files whose meaning is partly understood but whose final location needs a future decision",
    "r-08": "Unsupported or Encrypted | residual area, represents without moving | for password-protected archives, unreadable documents, damaged files and unknown formats",
    "r-09": "Personal > Travel > Confirmations | residual area the person defined | holds tickets, boarding passes and reservation records",
    "b-01": "Applications > Columbia > 2026 | branch built from the accepted packet: Columbia application packet | a return sends the file back to the placement engine for this branch",
    "b-02": "Coursework > PHYS1401 | branch built from the confirmed domain group: PHYS1401 course materials | a return sends the file back to the placement engine for this branch",
    "b-03": "Research > PVA-RDP | branch built from the accepted group: PVA/RDP manuscripts and figures | a return sends the file back to the placement engine for this branch",
    "b-04": "Applications | broad parent branch | every application the person has, of any kind",
}


def _areas(*ids: str) -> tuple[Item, ...]:
    return tuple(Item(evidence_ref=node, kind="residual_area" if node.startswith("r-")
                      else "branch", location=AREAS[node]) for node in ids)


def _shuffled(case_id: str, ids) -> tuple[str, ...]:
    """Offered ids in an order that carries no information about the answer.

    Zheng et al. 2023 and Pezeshkpour & Hruschka 2024 measure position bias in
    option lists; an author who lists the right area first would be measuring
    that bias and calling it the prompt's accuracy."""
    return tuple(sorted(ids, key=lambda n: hashlib.sha256(
        f"{case_id}:{n}".encode("utf-8")).hexdigest()))


def _case(case_id, title, persona, traces, subject, items, offered, expect, *,
          should_abstain, conflicts=(), extra_items=(), notes="") -> Case:
    offered = _shuffled(case_id, offered)
    return Case(
        case_id=case_id, site=D_RESIDUAL, title=title, persona=persona,
        traces=tuple(traces), subject_ref=subject,
        allowed_vocabulary=tuple(offered),
        # Every cited item names the subject file (G5).
        evidence=tuple(evidence(subject_ref=subject, location=subject, **item)
                       for item in items),
        items=_areas(*offered) + tuple(extra_items),
        conflicts=tuple(conflicts), plan_version=PLAN,
        authorities={"approved_target_ids": tuple(offered),
                     "frozen_nodes": tuple(AREAS)},
        expect=expect, should_abstain=should_abstain, notes=notes)


CASES = (
    _case(
        "D01", "an admissions confirmation screenshot is not a generic screenshot",
        "multi-life", ("00:125", "00:126"), "file:d01",
        [dict(address="ocr:1", value="Your Columbia University application has been submitted.", zone="ocr"),
         dict(address="ocr:2", value="Confirmation number CU-2026-88213", zone="ocr"),
         dict(address="metadata:1", value="PNG 1170x2532, created 2026-01-02", zone="metadata")],
        ("r-01", "r-03", "b-01"),
        {"action_in": [RETURN_ACCEPTED_PACKET, RETURN_CONFIRMED_GROUP], "target": "b-01"},
        should_abstain=False,
        notes="Returned to the normal group-aware engine, never trapped in a residual folder."),
    _case(
        "D02", "a boarding gate screenshot when a travel confirmations area is approved",
        "multi-life", ("00:125",), "file:d02",
        [dict(address="ocr:1", value="Gate B12 - Boarding at 18:20", zone="ocr"),
         dict(address="ocr:2", value="Flight to Kyoto", zone="ocr"),
         dict(address="metadata:1", value="PNG 1170x2532", zone="metadata")],
        ("r-01", "r-09", "r-05"),
        {"action": CHOOSE_RESIDUAL_DESTINATION, "target": "r-09"},
        should_abstain=False,
        notes="The broad destination, with no specific trip group invented."),
    _case(
        "D03", "the same gate screenshot with no travel area, Temporary Screenshots approved",
        "multi-life", ("00:125",), "file:d03",
        [dict(address="ocr:1", value="Gate B12 - Boarding at 18:20", zone="ocr"),
         dict(address="metadata:1", value="PNG 1170x2532", zone="metadata")],
        ("r-01", "r-03"),
        {"action": CHOOSE_RESIDUAL_DESTINATION, "target": "r-01",
         "also_acceptable": [[LEAVE_IN_CURRENT_LOCATION, None]]},
        should_abstain=False,
        notes="Travel/Flight Gate B12 must not be invented; a gate number is not a trip."),
    _case(
        "D04", "a recipe screenshot", "Tom", ("00:125",), "file:d04",
        [dict(address="ocr:1", value="Ingredients: 2 eggs, 200g flour, a pinch of salt", zone="ocr"),
         dict(address="ocr:2", value="Whisk until smooth and rest for 30 minutes.", zone="ocr")],
        ("r-01", "r-03", "r-02"),
        {"action": CHOOSE_RESIDUAL_DESTINATION, "target": "r-03"},
        should_abstain=False),
    _case(
        "D05", "a screenshot with unreadable OCR and no context", "multi-life",
        ("00:125", "00:239"), "file:d05",
        [dict(address="ocr:1", value="|| .. -- ' .", zone="ocr"),
         dict(address="metadata:1", value="PNG 1170x2532, no EXIF", zone="metadata")],
        ("r-01", "r-03"),
        {"action": LEAVE_IN_CURRENT_LOCATION,
         "also_acceptable": [[CHOOSE_RESIDUAL_DESTINATION, "r-01"]]},
        should_abstain=False,
        notes="Remain in place or enter the approved screenshot area; never a narrative."),
    _case(
        "D06", "an encrypted archive", "Mara", ("00:31", "00:120"), "file:d06",
        [dict(address="manifest:1", value="ZIP archive, password protected; 0 of 14 entries readable", zone="manifest")],
        ("r-08", "r-04"),
        {"action": MARK_PROTECTED_OR_UNSUPPORTED, "target": "unsupported",
         "also_acceptable": [[CHOOSE_RESIDUAL_DESTINATION, "r-08"]]},
        should_abstain=False),
    _case(
        "D07", "a boarding pass with no travel area and Receipts approved", "multi-life",
        ("00:120", "00:125"), "file:d07",
        [dict(address="body:1", value="Boarding pass. Gate B12. Seat 14C. Booking reference Q7XK2L.", zone="body")],
        ("r-05", "r-04", "r-01"),
        {"action": CHOOSE_RESIDUAL_DESTINATION, "target": "r-05"},
        should_abstain=False,
        notes="Transactional documents belong to Receipts and Confirmations."),
    _case(
        "D08", "a figure with a stronger relationship the dossier flags", "multi-life",
        ("00:126", "00:63"), "file:d08",
        [dict(address="heading:1", value="Figure 3 - graft compliance versus time", zone="heading"),
         dict(address="body:1", value="PVA/RDP vascular graft study, cohort B.", zone="body")],
        ("r-06", "r-03", "b-03"),
        {"action_in": [RETURN_ACCEPTED_PACKET, RETURN_CONFIRMED_GROUP], "target": "b-03"},
        should_abstain=False,
        conflicts=(("conflict-stronger-pva", "stronger_relationship"),),
        notes="Measures G1 at D: the shown relationship id cannot be echoed back."),
    _case(
        "D09", "a paper with a DOI and no course or project", "Priya",
        ("00:120",), "file:d09",
        [dict(address="title", value="Attention Is All You Need", zone="title"),
         dict(address="body:1", value="doi:10.48550/arXiv.1706.03762", zone="body"),
         dict(address="body:2", value="Abstract. The dominant sequence transduction models...", zone="body")],
        ("r-06", "r-04", "r-03"),
        {"action": CHOOSE_RESIDUAL_DESTINATION, "target": "r-06"},
        should_abstain=False),
    _case(
        "D10", "a paper the course lists as required reading", "Priya",
        ("00:126",), "file:d10",
        [dict(address="heading:1", value="PHYS 1401 required reading, week 6", zone="heading"),
         dict(address="body:1", value="Feynman, R. The Character of Physical Law, chapter 2.", zone="body")],
        ("r-06", "b-02"),
        {"action_in": [RETURN_CONFIRMED_GROUP, RETURN_ACCEPTED_PACKET], "target": "b-02"},
        should_abstain=False),
    _case(
        "D11", "a spreadsheet whose purpose is unclear", "Tom",
        ("00:122", "00:124"), "file:d11",
        [dict(address="metadata:1", value="XLSX, 1 sheet, 40 rows", zone="metadata"),
         dict(address="table:1", value="Q3 | 1,204 | 980 | 1,411", zone="table")],
        ("r-07", "r-04", "r-05"),
        {"action": MARK_REVIEW_LATER},
        should_abstain=True,
        notes="Partly understood; the final location needs a future decision."),
    _case(
        "D12", "a standalone certificate", "Tom", ("00:120",), "file:d12",
        [dict(address="title", value="Certificate of Completion - Emergency First Aid", zone="title"),
         dict(address="body:1", value="Awarded 12 March 2026. Valid for three years.", zone="body")],
        ("r-04", "r-05", "r-06"),
        {"action": CHOOSE_RESIDUAL_DESTINATION, "target": "r-04"},
        should_abstain=False),
    _case(
        "D13", "a statement whose account number was redacted before release", "Tom",
        ("00:120", "00:185"), "file:d13",
        [dict(address="heading:1", value="Statement for account [redacted]", zone="heading"),
         dict(address="body:1", value="Closing balance and transactions for the period.", zone="body")],
        ("r-04", "r-05"),
        {"action": MARK_PROTECTED_OR_UNSUPPORTED, "target": "protected"},
        should_abstain=False,
        notes="Protected Records: the model marks it; nothing residual claims it."),
    _case(
        "D14", "nothing readable at all", "Mara", ("00:124", "00:126"), "file:d14",
        [dict(address="metadata:1", value="0 bytes readable; format unknown", zone="metadata")],
        ("r-07", "r-08", "r-01"),
        {"action": ABSTAIN, "also_acceptable": [[MARK_PROTECTED_OR_UNSUPPORTED, "unsupported"]]},
        should_abstain=True),
    _case(
        "D15", "a gate screenshot offered an unrelated broad parent", "multi-life",
        ("00:124", "00:125"), "file:d15",
        [dict(address="ocr:1", value="Gate B12 - Boarding at 18:20", zone="ocr"),
         dict(address="metadata:1", value="PNG 1170x2532", zone="metadata")],
        ("b-04", "r-01"),
        {"action": CHOOSE_RESIDUAL_DESTINATION, "target": "r-01",
         "also_acceptable": [[LEAVE_IN_CURRENT_LOCATION, None]]},
        should_abstain=False,
        notes="A broad parent is legal and wrong here; Applications has nothing to do with a gate."),
)
