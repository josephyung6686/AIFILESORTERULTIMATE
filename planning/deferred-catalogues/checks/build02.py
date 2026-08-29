import json
from math import gcd
from pathlib import Path

OUT = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues/02-screen-resolutions.json")

# Ratios catalogue 03 treats as sensor-shaped. A resolution whose reduced ratio is
# one of these is flagged: the same two numbers read as a photo shape too.
SENSOR_RATIOS = {"4:3", "3:2", "16:9", "1:1", "5:4"}

SRC_WIKI = "Wikipedia — Display resolution standards"
SRC_APPLE_IOS = "Apple — iOS Device Compatibility Reference, Displays"
SRC_APPLE_SPECS = "Apple — device tech specs (support.apple.com)"
SRC_VESA = "VESA / Club 3D resolutions guide"

# (w, h, family, label, source, note)
ROWS = [
    # --- Desktop and monitor standards -------------------------------------
    (640, 480, "monitor", "VGA", SRC_WIKI, None),
    (800, 600, "monitor", "SVGA", SRC_WIKI, None),
    (1024, 600, "monitor", "WSVGA netbook", SRC_WIKI, None),
    (1024, 768, "monitor", "XGA", SRC_WIKI, None),
    (1152, 864, "monitor", "XGA+", SRC_WIKI, None),
    (1280, 720, "monitor", "HD / 720p", SRC_WIKI, None),
    (1280, 800, "monitor", "WXGA 16:10", SRC_WIKI, None),
    (1280, 1024, "monitor", "SXGA", SRC_WIKI, None),
    (1360, 768, "monitor", "WXGA variant", SRC_WIKI, None),
    (1366, 768, "monitor", "WXGA — the dominant budget-laptop panel", SRC_WIKI, None),
    (1440, 900, "monitor", "WXGA+", SRC_WIKI, None),
    (1600, 900, "monitor", "HD+", SRC_WIKI, None),
    (1600, 1200, "monitor", "UXGA", SRC_WIKI, None),
    (1680, 1050, "monitor", "WSXGA+", SRC_WIKI, None),
    (1920, 1080, "monitor", "FHD / 1080p — the single most common screenshot size", SRC_WIKI, None),
    (1920, 1200, "monitor", "WUXGA", SRC_WIKI, None),
    (2048, 1152, "monitor", "QWXGA", SRC_WIKI, None),
    (2048, 1536, "monitor", "QXGA", SRC_WIKI, None),
    (2560, 1080, "monitor", "UW-FHD ultrawide 21:9", SRC_VESA, None),
    (2560, 1440, "monitor", "QHD / 1440p", SRC_WIKI, None),
    (2560, 1600, "monitor", "WQXGA", SRC_WIKI, None),
    (2880, 1620, "monitor", "3K 16:9", SRC_VESA, None),
    (3440, 1440, "monitor", "UWQHD ultrawide 21:9", SRC_VESA, None),
    (3840, 1080, "monitor", "DFHD dual-FHD ultrawide 32:9", SRC_VESA, None),
    (3840, 1600, "monitor", "UWQHD+ ultrawide 12:5", SRC_VESA, None),
    (3840, 2160, "monitor", "4K UHD", SRC_WIKI, None),
    (4096, 2160, "monitor", "DCI 4K", SRC_VESA, None),
    (5120, 1440, "monitor", "DQHD dual-QHD ultrawide 32:9", SRC_VESA, None),
    (5120, 2880, "monitor", "5K", SRC_WIKI, None),
    (7680, 4320, "monitor", "8K UHD", SRC_WIKI, None),
    # --- Apple Mac built-in and standalone panels ---------------------------
    (2560, 1600, "mac", "MacBook Pro 13-inch Retina / MacBook Air 13-inch Retina", SRC_APPLE_SPECS, "duplicate of WQXGA; one row"),
    (2880, 1800, "mac", "MacBook Pro 15-inch Retina", SRC_APPLE_SPECS, None),
    (2560, 1664, "mac", "MacBook Air 13-inch (M2 and later)", SRC_APPLE_SPECS, None),
    (2880, 1864, "mac", "MacBook Air 15-inch", SRC_APPLE_SPECS, None),
    (3024, 1964, "mac", "MacBook Pro 14-inch (2021 and later)", SRC_APPLE_SPECS, None),
    (3456, 2234, "mac", "MacBook Pro 16-inch (2021 and later)", SRC_APPLE_SPECS, None),
    (2304, 1440, "mac", "MacBook 12-inch Retina", SRC_APPLE_SPECS, None),
    (4096, 2304, "mac", "iMac 21.5-inch 4K Retina", SRC_APPLE_SPECS, None),
    (4480, 2520, "mac", "iMac 24-inch 4.5K Retina", SRC_APPLE_SPECS, None),
    (6016, 3384, "mac", "Pro Display XDR 6K", SRC_APPLE_SPECS, None),
    # --- iPhone native resolutions -----------------------------------------
    (320, 480, "iphone", "iPhone 3G / 3GS", SRC_APPLE_IOS, None),
    (640, 960, "iphone", "iPhone 4 / 4s", SRC_APPLE_IOS, None),
    (640, 1136, "iphone", "iPhone 5 / 5s / SE (1st gen)", SRC_APPLE_IOS, None),
    (750, 1334, "iphone", "iPhone 6 / 6s / 7 / 8 / SE (2nd, 3rd gen)", SRC_APPLE_IOS, None),
    (1080, 1920, "iphone", "iPhone 6 Plus / 6s Plus / 7 Plus / 8 Plus — identical to FHD portrait", SRC_APPLE_IOS, "same pair as the FHD monitor row; one row serves both"),
    (1125, 2436, "iphone", "iPhone X / XS / 11 Pro", SRC_APPLE_IOS, None),
    (828, 1792, "iphone", "iPhone XR / 11", SRC_APPLE_SPECS, None),
    (1242, 2688, "iphone", "iPhone XS Max / 11 Pro Max", SRC_APPLE_SPECS, None),
    (1170, 2532, "iphone", "iPhone 12 / 12 Pro / 13 / 13 Pro / 14", SRC_APPLE_SPECS, None),
    (1080, 2340, "iphone", "iPhone 12 mini / 13 mini", SRC_APPLE_SPECS, None),
    (1284, 2778, "iphone", "iPhone 12 Pro Max / 13 Pro Max / 14 Plus", SRC_APPLE_SPECS, None),
    (1179, 2556, "iphone", "iPhone 14 Pro / 15 / 15 Pro / 16", SRC_APPLE_SPECS, None),
    (1290, 2796, "iphone", "iPhone 14 Pro Max / 15 Plus / 15 Pro Max / 16 Plus", SRC_APPLE_SPECS, None),
    (1206, 2622, "iphone", "iPhone 16 Pro", SRC_APPLE_SPECS, None),
    (1320, 2868, "iphone", "iPhone 16 Pro Max", SRC_APPLE_SPECS, None),
    # --- iPad native resolutions -------------------------------------------
    (768, 1024, "ipad", "iPad 1 / 2 / mini (non-Retina)", SRC_APPLE_IOS, None),
    (1536, 2048, "ipad", "iPad Retina 9.7-inch / iPad mini Retina / iPad Air", SRC_APPLE_IOS, None),
    (1620, 2160, "ipad", "iPad 10.2-inch (7th-9th gen)", SRC_APPLE_SPECS, None),
    (1640, 2360, "ipad", "iPad Air (4th gen and later) / iPad 10th gen", SRC_APPLE_SPECS, None),
    (1668, 2224, "ipad", "iPad Pro 10.5-inch", SRC_APPLE_IOS, None),
    (1668, 2388, "ipad", "iPad Pro 11-inch", SRC_APPLE_SPECS, None),
    (1488, 2266, "ipad", "iPad mini (6th gen and later)", SRC_APPLE_SPECS, None),
    (2048, 2732, "ipad", "iPad Pro 12.9-inch", SRC_APPLE_IOS, None),
    (2064, 2752, "ipad", "iPad Pro 13-inch (M4)", SRC_APPLE_SPECS, None),
    # --- Android / Windows phone families ----------------------------------
    (720, 1280, "android", "HD 720p phone panel", SRC_WIKI, None),
    (1080, 2160, "android", "18:9 FHD+ panel", SRC_VESA, None),
    (1080, 2220, "android", "18.5:9 FHD+ panel", SRC_VESA, None),
    (1080, 2280, "android", "19:9 FHD+ panel", SRC_VESA, None),
    (1080, 2400, "android", "20:9 FHD+ panel — the dominant modern Android size", SRC_VESA, None),
    (1440, 2560, "android", "QHD phone panel", SRC_WIKI, None),
    (1440, 2960, "android", "18.5:9 QHD+ panel", SRC_VESA, None),
    (1440, 3040, "android", "19:9 QHD+ panel", SRC_VESA, None),
    (1440, 3120, "android", "19.5:9 QHD+ panel", SRC_VESA, None),
    (1440, 3200, "android", "20:9 QHD+ panel", SRC_VESA, None),
    (1344, 2992, "android", "Pixel-class 20:9 panel", SRC_VESA, None),
    (1080, 2412, "android", "20.1:9 FHD+ panel", SRC_VESA, None),
]

def ratio(w, h):
    g = gcd(w, h)
    return f"{w // g}:{h // g}"

entries, seen = [], {}
for w, h, family, label, source, note in ROWS:
    lo, hi = min(w, h), max(w, h)
    key = (lo, hi)
    r = ratio(hi, lo)
    if key in seen:
        prev = seen[key]
        prev["rationale"] += f" Also: {label}."
        continue
    overlap = r if r in SENSOR_RATIOS else None
    rat = (f"{label}. §2.6 names \"exact display resolutions\" as a tier-3 signal that "
           f"*may support* a screenshot hypothesis. Matched orientation-insensitively: "
           f"{w}×{h} and {h}×{w} are the same panel.")
    if overlap:
        rat += (f" **Overlap flagged:** the reduced ratio is {overlap}, which catalogue 03 also "
                f"treats as sensor-shaped, so these two numbers are a legitimate photo shape too.")
    e = {
        "id": f"res-{hi}x{lo}",
        "match": f"{hi}x{lo}",
        "also_written": f"{lo}x{hi}",
        "match_kind": "exact",
        "case_sensitive": False,
        "family": family,
        "aspect_ratio": r,
        "overlaps_sensor_ratio": overlap,
        "rationale": rat,
        "design_cite": "§2.6 \"exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis\"",
        "false_positive_risk": "high" if overlap else "low",
        "example_true": f"{w}x{h}",
        "example_true_2": f"{h}x{w}",
        "example_false": "4032x3024",
        "source": source,
    }
    if note:
        e["rationale"] += f" ({note})"
    seen[key] = e
    entries.append(e)

entries.sort(key=lambda e: (int(e["match"].split("x")[1]), int(e["match"].split("x")[0])))

doc = {
  "list_id": "screen_resolutions",
  "title": "02 — Exact display resolutions (P5's `dimension_signal`, tier 3)",
  "version": "1.0",
  "authored": "2026-08-20",
  "owner": "P5 (injected) — the tier it produces is consumed by P6",
  "consumer": "the caller-supplied `dimension_signal(width, height) -> str | None` that P5's `extract_image` requires; a match returns the literal `\"exact display resolution\"`, which P5 maps to `signal_tier: 3`",
  "match_field": "the image's pixel dimensions as an **unordered** pair. Every `match` is written in the conventional landscape form `longer`x`shorter`, and `also_written` gives the portrait form; the matcher compares `(max(w,h), min(w,h))` so both orientations of one panel are one row.",
  "normalization_for_matching": "Integer comparison on the sorted pair. No tolerance, no rounding, no nearest-neighbour: \"exact display resolutions\" is §2.6's own word. `1919x1080` matches nothing.",
  "design_cites": [
    "§2.6: \"Image dimensions, PNG format, software metadata, and known screen resolutions can support a screenshot hypothesis.\"",
    "§2.6: \"exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.\"",
    "P5 SPEC E5 signal table: tier 3 = \"Exact display resolutions, PNG format, software metadata\" — \"**may support** a screenshot hypothesis\".",
    "P5 SPEC Deferred: \"Known screen resolutions / 'exact display resolutions' | §2.6 | That they support a screenshot hypothesis | Which resolutions\" — this file is the missing column.",
    "P5 PLAN Task 15: \"`dimension_signal` and `filename_pattern` are **required keywords with no default**; `dimension_signal` returns at most one of §2.6's two dimension readings and a third name is refused.\""
  ],
  "rules": [
    "**This list never concludes anything.** A match produces one tier-3 observation on the `pixel dimensions` value and nothing else. E5 emits no photo/screenshot conclusion; `media type` is a Photos-domain fact and belongs to P6 (§3.11).",
    "**Absence is not evidence.** Missing EXIF is never a screenshot signal, and OCR text density is never a screenshot signal (§2.6). Nothing in this file may be read as licence for either.",
    "**A tier-3 signal alone must not fill `media type`.** §3.7's minimum-score-and-margin rule is what produces §2.6's abstention, and it is P6's.",
    "**Exact only.** No tolerance band. A tolerance would let sensor sizes drift into this list, and §2.6 says \"exact\".",
    "**Orientation-insensitive.** A screenshot of a rotated tablet, and a landscape phone grab, carry the swapped pair.",
    "**No entry may be a known sensor output size.** `4032x3024` and `4032x2268` belong to catalogue 03 and appear here only as `example_false`."
  ],
  "arbitration_with_catalogue_03": (
    "`dimension_signal` must return **at most one** of `\"sensor-shaped dimensions\"` and "
    "`\"exact display resolution\"`, and P5 refuses any third name. The arbitration is:\n\n"
    "1. If the sorted pair matches an entry in catalogue **02**, return `\"exact display resolution\"` (tier 3).\n"
    "2. Else if the reduced ratio matches an entry in catalogue **03** within its stated tolerance, return `\"sensor-shaped dimensions\"` (tier 2).\n"
    "3. Else return `None` — the dimensions observation is emitted with no `signal_tier` at all.\n\n"
    "**Why exact wins.** Every 16:9 display resolution is also 16:9, so ratio-first would make catalogue 02 "
    "unreachable for its most common members. Nothing is lost by ordering it this way: a real photograph that "
    "happens to be exactly 1920×1080 still carries camera EXIF, which is a **tier-1** observation, and §3.7's "
    "margin rule weighs tier 1 against tier 3 and resolves it. If the EXIF has been stripped, the file "
    "carries one lone tier-3 signal — which §2.6 says *may* support a screenshot hypothesis, and which on its "
    "own must not clear the margin. That is §2.6's abstention, produced by P6's ordinary ranking rather than "
    "by a decision taken inside the signal function."
  ),
  "coverage_note": (
    "v1 covers four families: VESA/common monitor standards, Apple Mac panels, iOS device native "
    "resolutions, and the dominant Android phone panel sizes. It is deliberately **not** a device "
    "database — enumerating every Android panel ever shipped is the \"thousands of obscure phone "
    "models\" case, and each additional row buys less recall than it costs in maintenance.\n\n"
    "**Known coverage limit, stated rather than papered over:** an exact-resolution match only fires on a "
    "**full-screen** capture. A window grab, a cropped screenshot, a Retina capture downscaled on export, and "
    "a browser-viewport screenshot all carry arbitrary dimensions and match nothing here. This is a recall "
    "limit by design: the alternative — a tolerance band or a \"looks like a screen\" heuristic — would "
    "contradict §2.6's word \"exact\" and would start reading absence as evidence."
  ),
  "sources": [
    {"title": SRC_WIKI, "url": "https://en.wikipedia.org/wiki/Display_resolution_standards", "retrieved": "2026-08-20", "note": "Named standards and their exact pixel dimensions: VGA 640×480 4:3, XGA 1024×768 4:3, WXGA 1366×768, SXGA 1280×1024 5:4, WUXGA 1920×1200 16:10, HD 1280×720, FHD 1920×1080, QHD 2560×1440, WQXGA 2560×1600, 4K UHD 3840×2160, 5K 5120×2880, 8K UHD 7680×4320."},
    {"title": SRC_APPLE_IOS, "url": "https://developer.apple.com/library/archive/documentation/DeviceInformation/Reference/iOSDeviceCompatibility/Displays/Displays.html", "retrieved": "2026-08-20", "note": "Apple's own device/native-resolution table through iPhone X: 640×1136, 750×1334, 1080×1920, 1125×2436, 1536×2048, 1668×2224, 2048×2732."},
    {"title": "Apple — iPhone 15 Pro Max tech specs", "url": "https://support.apple.com/en-us/111828", "retrieved": "2026-08-20", "note": "2796-by-1290 at 460 ppi."},
    {"title": "Apple — iPhone 16 Pro Max tech specs", "url": "https://support.apple.com/en-us/121032", "retrieved": "2026-08-20", "note": "Confirms the 15/16 Pro Max panel pair."},
    {"title": "Apple — MacBook Pro 14- and 16-inch tech specs", "url": "https://www.apple.com/macbook-pro-14-and-16/specs/", "retrieved": "2026-08-20", "note": "3024-by-1964 (14-inch) and 3456-by-2234 (16-inch) native, both at 254 ppi."},
    {"title": SRC_VESA, "url": "https://www.club-3d.com/en/technology/24/resolutions_guide/", "retrieved": "2026-08-20", "note": "Ultrawide and DCI entries (2560×1080, 3440×1440, 3840×1600, 5120×1440, 4096×2160)."},
    {"title": "VESA — Display Monitor Timing Standard v1.13", "url": "https://glenwing.github.io/docs/VESA-DMT-1.13.pdf", "retrieved": "2026-08-20", "note": "The standards body's own timing table behind the classic monitor modes."}
  ],
  "injection": (
    "This list is data for the **caller** that constructs `dimension_signal`, not for P5. "
    "`extract_image(..., dimension_signal=make_dimension_signal(load('02-screen-resolutions.json'), "
    "load('03-sensor-aspect-ratios.json')))`. `dimension_signal` is a **required keyword with no default** "
    "(P5 PLAN Task 15) precisely so that no resolution can reach `src/extractors/`: P5 PLAN's Global "
    "Constraints forbid any module-level screen resolution or aspect ratio inside `extractors`, and Task 20 "
    "asserts it by runtime introspection of every module namespace."
  ),
  "entries": entries,
  "uncertain": [
    {"id": "unc-retina-logical-sizes", "match": "logical (point) sizes such as 1440x900 on a 2880x1800 panel", "match_kind": "exact", "case_sensitive": False,
     "rationale": "A macOS screenshot taken with a scaled resolution setting can land on the logical size rather than the native one. Several such sizes (1440×900, 1680×1050, 1280×800) are already in the list as standalone monitor standards, so the common cases are covered by accident rather than by design. Whether to add the remaining Apple scaled-mode sizes needs a real corpus.",
     "design_cite": "§2.6 \"exact display resolutions\"", "false_positive_risk": "medium", "example_true": "1440x900", "example_false": "4032x3024"},
    {"id": "unc-browser-viewport", "match": "browser viewport capture sizes", "match_kind": "exact", "case_sensitive": False,
     "rationale": "A full-page browser screenshot is viewport-width by page-height — an unbounded set. Not enumerable, and any attempt would be a heuristic. Recorded so the gap is visible rather than discovered later.",
     "design_cite": "§2.6", "false_positive_risk": "n/a", "example_true": "—", "example_false": "1920x8412"},
    {"id": "unc-android-long-tail", "match": "Android panel sizes beyond the twelve listed", "match_kind": "exact", "case_sensitive": False,
     "rationale": "The Android panel set is open-ended. v1 covers the dominant 18:9/19:9/19.5:9/20:9 FHD+ and QHD+ families. Adding more should be driven by what Joseph's corpus actually contains, not by a device database.",
     "design_cite": "§2.6", "false_positive_risk": "n/a", "example_true": "—", "example_false": "4032x3024"},
    {"id": "unc-1920x1080-collision", "match": "1920x1080", "match_kind": "exact", "case_sensitive": False,
     "rationale": "The single most overloaded pair in this file: it is FHD portrait, the iPhone 6-8 Plus native panel, **and** exactly 16:9 — which is also a video-still and 16:9-camera-mode shape. It is one row with `false_positive_risk: high`. If Joseph's corpus contains many 16:9-mode camera photos, this row is the first one to reconsider.",
     "design_cite": "§2.6 \"conflicting signals should lead to abstention rather than an invented classification\"", "false_positive_risk": "high", "example_true": "1920x1080", "example_false": "4032x3024"}
  ]
}
OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("entries:", len(entries))
print("has 1920x1080:", any(e["match"] == "1920x1080" for e in entries))
print("has 4032x3024:", any(e["match"] == "4032x3024" for e in entries))
