# 03 — Sensor-shaped aspect ratios (P5's `dimension_signal`, tier 2)

- **list_id**: sensor_aspect_ratios
- **version**: 1.0
- **authored**: 2026-08-20
- **owner**: P5 (injected) — the tier it produces is consumed by P6
- **consumer**: the caller-supplied `dimension_signal(width, height) -> str | None` that P5's `extract_image` requires; a match returns the literal `"sensor-shaped dimensions"`, which P5 maps to `signal_tier: 2`
- **match_field**: the image's pixel dimensions reduced to lowest terms as `longer:shorter`. `4032x3024` reduces to `4:3`; `3024x4032` reduces to the same thing, because the pair is unordered.
- **normalization for matching**: Reduce `(max(w,h), min(w,h))` by their GCD and compare the resulting `a:b` string exactly. If no exact reduction matches, fall back to a numeric comparison: a ratio matches when `abs(w/h - target) / target <= tolerance`. Both steps are needed — most sensors reduce exactly, but a few real sensor sizes (Pixel-class `4080x3072`) are 0.4 % off nominal and would otherwise be missed.

## Design basis

- §2.6: "camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it".
- P5 SPEC E5 signal table: tier 2 = "Capture time, GPS, sensor-shaped dimensions" — "reinforce photo".
- P5 SPEC Deferred: "'Sensor-shaped dimensions' | §2.6 | That they reinforce photo evidence | Which aspect ratios qualify" — this file is the missing column.
- P5 PLAN Task 15: `DIMENSION_SIGNALS == ("sensor-shaped dimensions", "exact display resolution")` and a third name raises `UnknownSignal`.

## Rules this list obeys

1. **Reinforcement, never proof.** §2.6 puts this band at tier 2: it *reinforces* photo evidence. A tier-2 signal on its own is not a photograph verdict, and E5 emits no verdict at all.
2. **Absence is not evidence.** A ratio that matches nothing here is not a screenshot signal; it produces a dimensions observation with **no** `signal_tier`. §2.6's trap 1 is that missing metadata proves nothing, and the same discipline applies to a missing ratio match.
3. **Ratios only, no device table.** The contract value is the shape. Concrete sensor output sizes appear below as cited anchors that demonstrate each ratio, not as an enumerable set to match against.
4. **Display-only ratios are refused.** 16:10, 21:9, 32:9 and 5:3 are panel shapes, not sensor shapes; admitting them would make catalogue 02 and catalogue 03 fight over the same numbers.
5. **Tight tolerance.** 0.5 % relative. That is wide enough for real sensor readouts and far too narrow to let 4:3 (1.3333) reach 5:4 (1.25) or 3:2 (1.5).

## Arbitration with catalogue 02

`dimension_signal` returns **at most one** signal name. Catalogue 02 is consulted first: an exact display-resolution match returns `"exact display resolution"` (tier 3); otherwise this file is consulted and a ratio match returns `"sensor-shaped dimensions"` (tier 2); otherwise `None`. The full reasoning — and why exact-beats-ratio does not lose the photo case — is written out under *Arbitration with catalogue 03* in `02-screen-resolutions.md`. The short form: a real photograph that happens to be exactly `1920x1080` still carries camera EXIF at tier 1, and §3.7's margin rule is what resolves tier 1 against tier 3. Resolution belongs to P6, never to this function.

## Injection

Same injection point as catalogue 02, and the same prohibition: `make_dimension_signal(resolutions, ratios)` is built by P5's **caller** and passed as the required `dimension_signal` keyword. P5 PLAN's Global Constraints forbid any module-level aspect ratio inside `src/extractors/` — "no module-level gazetteer, regex, screen resolution, producer string, or language tag" — and Task 20 asserts it by runtime introspection, so nothing in this file may become an `extractors` constant.

## Coverage note

Five ratios, and that is the whole contract. Every consumer camera in wide use produces one of them: 4:3 (Micro Four Thirds, medium format, virtually every phone, most compacts), 3:2 (35 mm full frame and APS-C, the dominant interchangeable-lens shape), 16:9 (video mode and video stills), 1:1 (square capture mode), 5:4 (large-format and medium-format crops). Panorama shapes are deliberately excluded — a panorama is an arbitrary stitched width, so no ratio describes it, and the honest record is the `uncertain` row rather than a guessed band.

## Entries

5 entries.

| id | match | match_kind | case sensitive | overlaps display resolutions | decimal | tolerance | rationale | design cite | FP risk | example true | example false (must NOT match) | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ratio-4-3` | `4:3` | exact | no | — | 1.333333 | 0.005 | The dominant sensor shape by file count in a personal corpus: every iPhone and virtually every Android main camera writes 4:3 at full resolution, as do Micro Four Thirds bodies, medium format, and most compacts. Photography Life: "4:3 is used by medium format, Micro Four Thirds, most smartphones and some point-and-shoot cameras." | §2.6 "capture time, GPS, and sensor-shaped dimensions reinforce it" | medium | `4032x3024` | `1920x1080` | Apple iOS Camera reference; Photography Life |
| `ratio-3-2` | `3:2` | exact | no | — | 1.5 | 0.005 | The 35 mm shape, inherited by full-frame and APS-C interchangeable-lens cameras. Photography Life: "The 3:2 aspect ratio was popularized by 35mm film and it is the most common one in photography today. With full frame and APS-C cameras, this aspect ratio is 3:2." | §2.6 "sensor-shaped dimensions reinforce it" | low | `6000x4000` | `4032x3024` | Photography Life; Canon CNA |
| `ratio-16-9` | `16:9` | exact | no | yes — every 16:9 entry in catalogue 02 reduces to this ratio | 1.777778 | 0.005 | In-camera 16:9 crop mode and video stills. **This is the contested ratio**, and it is why the arbitration order exists: HD, FHD, QHD, 4K UHD, 5K and 8K all reduce to 16:9, so a ratio-first arbitration would swallow catalogue 02 entirely. Catalogue 02 is therefore consulted first, and a 16:9 image whose exact size is a known panel reads as tier 3, not tier 2. A 16:9 photograph that is *not* a panel size (a video still at `4032x2268`, a 16:9 crop at `5472x3078`) still reads as tier 2 here. | §2.6 "sensor-shaped dimensions reinforce it" vs "exact display resolutions … may support a screenshot hypothesis" | high | `4032x2268` | `4032x3024` | Photography Life: 16:9 is "the most common video format today … some cameras provide it as a cropping option" |
| `ratio-1-1` | `1:1` | exact | no | — | 1.0 | 0.005 | In-camera square capture mode, offered by iPhone, Canon, Fujifilm and others. Square is a weak reinforcement — social-media exports and generated graphics are also square — so it sits at tier 2 with everything else in this band and never concludes anything on its own. | §2.6 "sensor-shaped dimensions reinforce it" | high | `3024x3024` | `4032x3024` | Canon CNA aspect-ratio guide |
| `ratio-5-4` | `5:4` | exact | no | — | 1.25 | 0.005 | The large-format and 8×10 print shape, offered as an in-camera crop on medium-format and some mirrorless bodies. Note the collision to be aware of: SXGA `1280x1024` is also 5:4 — which is exactly why catalogue 02 is consulted first. | §2.6 "sensor-shaped dimensions reinforce it" | medium | `5000x4000` | `1280x1024` | Canon CNA aspect-ratio guide |

## Sensor output sizes — cited anchors demonstrating each ratio (not a match set)

12 entries.

| id | match | match_kind | case sensitive | aspect ratio | rationale | design cite | FP risk | example true | example false (must NOT match) | source |
|---|---|---|---|---|---|---|---|---|---|---|
| `anchor-4032x3024` | `4032x3024` | exact | no | 4:3 | The iPhone 12 MP main-camera output, confirmed by Apple. **This is a camera output size and is catalogued here, not in catalogue 02.** It is not a screenshot size: no shipping iPhone has a 4032×3024 display, and the file makes no claim that it is unique to any one device — several Android 12 MP cameras produce the same pair. It appears in catalogue 02 only as an `example_false`. | §2.6 "sensor-shaped dimensions" | low | `4032x3024` | `1920x1080` | Apple Developer Forums thread 738418 |
| `anchor-8064x6048` | `8064x6048` | exact | no | 4:3 | iPhone 48 MP ProRAW / HEIF Max output, confirmed by Apple. | §2.6 | low | `8064x6048` | `7680x4320` | Apple Developer Forums thread 738418 |
| `anchor-4032x2268` | `4032x2268` | exact | no | 16:9 | The iPhone 16:9 crop of the 12 MP sensor. Worth naming because it is the concrete case that makes the 16:9 arbitration matter: it is a photograph, it is exactly 16:9, and it is not any display panel. | §2.6 | low | `4032x2268` | `3840x2160` | — |
| `anchor-3264x2448` | `3264x2448` | exact | no | 4:3 | The 8 MP output of older iPhones and a very large number of Android phones. Common in an archive of older photos. | §2.6 | low | `3264x2448` | `3200x2400` | — |
| `anchor-6000x4000` | `6000x4000` | exact | no | 3:2 | The 24 MP full-frame output shared by many Sony, Nikon and Canon bodies. | §2.6 | low | `6000x4000` | `6000x4500` | — |
| `anchor-6720x4480` | `6720x4480` | exact | no | 3:2 | The 30 MP full-frame output of the Canon EOS 5D Mark IV class. | §2.6 | low | `6720x4480` | `6720x5040` | — |
| `anchor-8256x5504` | `8256x5504` | exact | no | 3:2 | The 45.7 MP full-frame output of the Nikon D850 class. | §2.6 | low | `8256x5504` | `8256x6192` | — |
| `anchor-5472x3648` | `5472x3648` | exact | no | 3:2 | The 20 MP APS-C and 1-inch-compact output. | §2.6 | low | `5472x3648` | `5472x4104` | — |
| `anchor-5184x3888` | `5184x3888` | exact | no | 4:3 | The 20 MP Micro Four Thirds output — the 4:3 native shape of a 17.3 × 13 mm sensor. | §2.6 | low | `5184x3888` | `5184x3456` | Wikipedia — Panasonic Lumix DC-GH5S (sensor dimensions) |
| `anchor-4608x3456` | `4608x3456` | exact | no | 4:3 | The 16 MP 4:3 output common to Micro Four Thirds bodies and many Android phones. | §2.6 | low | `4608x3456` | `4608x2592` | — |
| `anchor-4000x3000` | `4000x3000` | exact | no | 4:3 | The 12 MP 4:3 output of GoPro action cameras and many Android phones. | §2.6 | low | `4000x3000` | `4000x2250` | — |
| `anchor-3024x3024` | `3024x3024` | exact | no | 1:1 | The iPhone square capture mode — the 12 MP sensor cropped to its short side. | §2.6 | medium | `3024x3024` | `3024x4032` | — |

## Refused — deliberately NOT matched

3 entries.

| id | match | match_kind | case sensitive | rationale | design cite | FP risk | example true | example false (must NOT match) |
|---|---|---|---|---|---|---|---|---|
| `ref-16-10` | `16:10` | exact | no | A panel shape, not a sensor shape. WXGA 1280×800, WXGA+ 1440×900, WSXGA+ 1680×1050, WUXGA 1920×1200 and WQXGA 2560×1600 are all 16:10 and all live in catalogue 02. No camera produces 16:10 natively. Admitting it would make the two catalogues contradict each other on the same numbers. | §2.6 distinguishes "sensor-shaped dimensions" from "exact display resolutions" | would be high | `—` | `2560x1600` |
| `ref-21-9` | `21:9 and 32:9 ultrawide` | exact | no | Monitor shapes. `2560x1080`, `3440x1440`, `3840x1600`, `5120x1440` are catalogue 02 rows. A camera never reads out at these shapes; a stitched panorama might land near them, and that is handled as an `uncertain` row rather than by borrowing a monitor ratio. | §2.6 | would be high | `—` | `3440x1440` |
| `ref-5-3` | `5:3` | exact | no | WVGA/FWVGA panel shape. Same reasoning as 16:10. | §2.6 | would be medium | `—` | `800x480` |

## Uncertain — needs Joseph

5 entries.

| id | match | match_kind | case sensitive | rationale | design cite | FP risk | example true | example false (must NOT match) |
|---|---|---|---|---|---|---|---|---|
| `unc-panorama` | `panorama shapes` | regex | no | An iPhone or Android panorama is an arbitrary stitched width — anywhere from roughly 2:1 to 12:1 — so no ratio describes the class and no honest entry can be written. A width-to-height threshold (say, longer/shorter > 2.5) would be a heuristic, and §2.6's discipline is that a signal must be a reading, not an inference. Recorded so the gap is visible. If Joseph wants panoramas recognised, the right lever is the EXIF and the filename pattern, not the shape. | §2.6 "conflicting signals should lead to abstention rather than an invented classification" | high | `10240x2560` | `3440x1440` |
| `unc-pixel-4080x3072` | `4080x3072` | exact | no | The Pixel-class 12.5 MP binned output. Its ratio is 1.3281, which is 0.39 % off nominal 4:3 — inside the 0.5 % tolerance, and the concrete case that motivates the tolerance existing at all. Community-reported rather than vendor-documented, so it is recorded here rather than promoted to an anchor. Confirming it against one real Pixel photo would settle both this row and the tolerance value. | §2.6 | low | `4080x3072` | `1280x1024` |
| `unc-tolerance-value` | `the 0.5 % tolerance itself` | exact | no | 0.005 is chosen to clear the widest real sensor deviation found (0.39 %) with margin, while staying far inside the 6.7 % gap between 4:3 and 5:4. It has not been measured against a real corpus. It is a number, so it must not live inside `src/extractors/` either — it travels with this file. | P5 PLAN Global Constraints: "no module-level number anywhere in `extractors`" | unknown | `—` | `—` |
| `unc-crop-shapes` | `4:5 and 9:16 social crops` | exact | no | `4:5` is the Instagram portrait crop and `9:16` the story crop. Both are the unordered form of 5:4 and 16:9 respectively, so they already match — which is arguably wrong, since a social-media crop is not a sensor readout. Whether to distinguish them needs the orientation information the unordered pair deliberately discards. Flagged rather than acted on: fixing it would mean making the match orientation-sensitive, which breaks the rotated-photo case. | §2.6 | medium | `1080x1350` | `—` |
| `unc-near-miss-fallthrough` | `near-miss display resolutions falling through to a ratio match` | exact | no | A consequence of the arbitration order that is worth naming because it is not obvious. `1919x1080` — a screenshot cropped by one pixel — misses catalogue 02 exactly (as §2.6's word "exact" requires) and then lands inside the 0.5 % band around 16:9, so it is emitted as tier 2, *reinforcing photo*, when it is in fact a screenshot. The signal is wrong in direction, not merely absent. It is left as-is for v1 for two reasons: a tier-2 signal on its own must not clear §3.7's margin, so no fact is produced from it; and the alternative — widening catalogue 02 with a tolerance — is what §2.6 forbids. Joseph should know it exists before the first eval run, because it will show up in P2's replay diffs. | §2.6 "exact display resolutions" vs "sensor-shaped dimensions" | medium | `1919x1080` | `1920x1080` |

## Sources

- [Apple — iOS Device Compatibility Reference, Cameras](https://developer.apple.com/library/archive/documentation/DeviceInformation/Reference/iOSDeviceCompatibility/Cameras/Cameras.html) — retrieved 2026-08-20 — Apple's own per-device still-image capture dimensions — the source for the 4:3 iPhone output sizes.
- [Apple Developer Forums — 24MP capture for iPhone 15 / 15 Pro](https://developer.apple.com/forums/thread/738418) — retrieved 2026-08-20 — Confirms iPhone 15 Pro supported photo dimensions `4032x3024` (12 MP) and `8064x6048` (48 MP), both 4:3.
- [Photography Life — Aspect Ratio](https://photographylife.com/aspect-ratio) — retrieved 2026-08-20 — "With full frame and APS-C cameras, this aspect ratio is 3:2"; "4:3 is used by medium format, Micro Four Thirds, most smartphones and some point-and-shoot cameras"; 16:9 is "the most common video format today and not a common format in photography, but some cameras provide it as a cropping option."
- [Canon — How to choose the right aspect ratios in photography](https://en.canon-cna.com/get-inspired/tips-and-techniques/how-to-choose-the-right-aspect-ratios-in-photography/) — retrieved 2026-08-20 — Vendor confirmation of 3:2, 4:3, 16:9 and 1:1 as the in-camera capture ratios Canon bodies offer.
- [Wikipedia — Panasonic Lumix DC-GH5S](https://en.wikipedia.org/wiki/Panasonic_Lumix_DC-GH5S) — retrieved 2026-08-20 — Micro Four Thirds body; 17.3 × 13 mm sensor is 4:3 by construction.

---

_Generated from the JSON beside this file by `render.py`. Do not hand-edit: edit the JSON and re-run._
