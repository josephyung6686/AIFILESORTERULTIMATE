# src/readers/perceptual_hash.py
"""`98`'s perceptual hash and its distance, as the owner ruled them on 11 Sep 2026.

`98` was ratified as written (`00`, Amendments of 2026-09-11, item 4) and as written
it named neither half: §3.1 records that `00` "names no algorithm", §3.2 that the
threshold "is a judgement about the owner's tolerance, not a technical constant ...
the number is the owner's". The owner then ruled, in session on 11 Sep 2026:

    A difference hash (dHash) of 64 bits over an 8x9 greyscale thumbnail, decoded
    through the same Quartz ImageIO the reader already uses. Two images are
    near-duplicates at a Hamming distance of at most 5 of 64.

**THE HASH AND THE DISTANCE ARE IN ONE MODULE BECAUSE `98` §3.1 REQUIRES IT.** "The
distance is only meaningful against the hash the reader actually produces. Whatever
ships must be stated together with the hash it assumes." So the producer, the metric,
the threshold and the blocking key are one file, and `facts.families` still holds
none of them -- `near_match` stays an injected predicate with no default and P6 still
states no distance of its own. The composition root binds `near_duplicate` here.

**A RENDERED VALUE NAMES ITS OWN ALGORITHM.** `HASH_ALGORITHM` prefixes every value
this module emits, and `distance` refuses a pair whose prefixes are not both it.
Without that a hash from some future algorithm and a hash from this one would be
compared bit for bit and the answer would be a number about nothing.

**WHY THE READER NOW DECODES PIXELS, FOR THIS ONE PURPOSE ONLY.**
`readers/image_headers.py` reads "Properties only, never
`CGImageSourceCreateImageAtIndex`. The metadata sits in the container's header;
decoding the pixels to read a camera's `Make` would spend a 50-megapixel decode on a
string, on every image in a corpus." That argument is untouched and still governs
every other slot: EXIF, colour, software and orientation are still read out of the
container. A perceptual hash is the one §2.6 slot that is ABOUT the pixels and cannot
be read from a header at all, and the route taken here is the cheap one --
`CGImageSourceCreateThumbnailAtIndex` with a maximum pixel size of the nine columns
the hash needs, so ImageIO decodes at a reduced scale and never materialises the full
raster. No dependency is added: Quartz is the same framework `image_headers.py` and
`ocr_vision.py` already import, and it is imported inside the call for the reason
that module states at length -- Apple's frameworks cost about 4.6s warm and a person
typing `--list-situations` must not pay it.

**A REFUSAL IS `None` AND NEVER A ZERO HASH.** Bytes ImageIO will not decode, a
thumbnail it will not build, a raster it returns short: each returns `None`, so
`extract_image` emits no observation and `_near_families` simply has one fewer
carrier. An all-zero hash would be a value nothing measured, and -- worse than
useless -- every such image would be within distance 0 of every other.
"""
from __future__ import annotations

import sys
from pathlib import Path

#: The owner's ruling of 11 Sep 2026, answering `98` §3.1 ("`00` names no
#: algorithm"). The name is the value's own prefix, so a stored hash states the
#: algorithm it was computed under and can never be silently compared against
#: another.
HASH_ALGORITHM: str = "dhash64"

#: The owner's ruling of 11 Sep 2026, answering `98` §3.1. Sixty-four bits, which is
#: also what the thumbnail below yields: one comparison between each adjacent pair of
#: columns, on every row.
NEAR_DUPLICATE_HASH_BITS: int = 64

#: The owner's ruling of 11 Sep 2026, answering `98` §3.2 -- the decision `98` says
#: "is a judgement about the owner's tolerance, not a technical constant", trading
#: two errors that are not symmetric: "too loose -> two different photographs are
#: called near-duplicates, and the review screen invites the owner to delete one of
#: them; too tight -> a resized or re-exported copy of one photo is treated as two
#: files."
NEAR_DUPLICATE_MAX_DISTANCE: int = 5

#: The owner's ruling of 11 Sep 2026: "an 8x9 greyscale thumbnail". Eight rows of
#: nine columns, compared left to right, is the difference hash's own shape.
NEAR_DUPLICATE_THUMBNAIL_ROWS: int = 8
NEAR_DUPLICATE_THUMBNAIL_COLUMNS: int = 9

#: Not a number from the ruling: CoreGraphics' required sample depth for an
#: eight-bit grey bitmap context, spelled here so it is never mistaken for the row
#: count it happens to equal.
_GREY_BITS_PER_COMPONENT: int = 8

#: The three ruled numbers are not independent, and this is where that is said. A
#: ruling that changed the thumbnail without changing the bit count would otherwise
#: produce a hash of the wrong width in silence.
assert (NEAR_DUPLICATE_THUMBNAIL_ROWS
        * (NEAR_DUPLICATE_THUMBNAIL_COLUMNS - 1)) == NEAR_DUPLICATE_HASH_BITS

#: `98`'s own sub-quadratic key, and the ONLY one of the three candidates that is a
#: necessary condition of the ruled metric. Splitting the hash into
#: `NEAR_DUPLICATE_MAX_DISTANCE + 1` bands makes the pigeonhole argument exact: two
#: hashes differing in at most `NEAR_DUPLICATE_MAX_DISTANCE` bits cannot differ
#: inside every one of that many-plus-one disjoint bands, so a near-duplicate pair
#: always agrees on at least one band and blocking loses no family. It is not a
#: chosen number -- it is the threshold plus one.
#:
#: The two keys the brief offered were considered and are not used, with the reason
#: recorded because both look right: the hash's LEADING BITS are not necessary (a
#: re-encode may differ in exactly those bits and still be within 5 of 64), and the
#: SAME DIRECTORY is not necessary either (a re-saved export is most often somewhere
#: else, which is `98` §4's whole example). Either would have been cheap and would
#: have lost families silently.
NEAR_DUPLICATE_BANDS: int = NEAR_DUPLICATE_MAX_DISTANCE + 1


def _thumbnail_rows(path: Path) -> tuple[bytes, int] | None:
    """The 8x9 grey raster and its stride, or `None` where nothing could be read."""
    if sys.platform != "darwin":
        return None
    import Quartz                                # noqa: PLC0415 -- see the docstring
    from Foundation import NSURL                 # noqa: PLC0415

    source = Quartz.CGImageSourceCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), None)
    if source is None or Quartz.CGImageSourceGetType(source) is None:
        return None
    # THE SMALLEST DECODE THAT ANSWERS. The maximum pixel size is the column count
    # the hash needs, so ImageIO decodes at a reduced scale rather than building the
    # full raster and throwing it away. `FromImageAlways` is required because an
    # embedded camera thumbnail is a DIFFERENT PICTURE from the one in the file --
    # cropped, rotated, sometimes stale -- and hashing it would compare two images
    # neither of which is the file.
    thumbnail = Quartz.CGImageSourceCreateThumbnailAtIndex(source, 0, {
        Quartz.kCGImageSourceCreateThumbnailFromImageAlways: True,
        Quartz.kCGImageSourceThumbnailMaxPixelSize: NEAR_DUPLICATE_THUMBNAIL_COLUMNS,
    })
    if thumbnail is None:
        return None

    context = Quartz.CGBitmapContextCreate(
        None, NEAR_DUPLICATE_THUMBNAIL_COLUMNS, NEAR_DUPLICATE_THUMBNAIL_ROWS,
        _GREY_BITS_PER_COMPONENT, 0, Quartz.CGColorSpaceCreateDeviceGray(),
        Quartz.kCGImageAlphaNone)
    if context is None:
        return None
    # Drawn to the exact ruled shape whatever the source's aspect ratio. A hash whose
    # grid depended on the picture's proportions would put a photograph and its own
    # letterboxed export in different spaces.
    Quartz.CGContextDrawImage(
        context, Quartz.CGRectMake(0, 0, NEAR_DUPLICATE_THUMBNAIL_COLUMNS,
                                   NEAR_DUPLICATE_THUMBNAIL_ROWS), thumbnail)
    rendered = Quartz.CGBitmapContextCreateImage(context)
    if rendered is None:
        return None
    data = Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(rendered))
    if data is None:
        return None
    # The stride is READ BACK and never assumed to be the column count: CoreGraphics
    # pads a row to its own alignment, and a hash computed against an assumed stride
    # would read the neighbouring row's first pixels as this row's last.
    stride = int(Quartz.CGImageGetBytesPerRow(rendered))
    raster = bytes(data)
    if stride < NEAR_DUPLICATE_THUMBNAIL_COLUMNS or len(
            raster) < stride * NEAR_DUPLICATE_THUMBNAIL_ROWS:
        return None
    return raster, stride


def perceptual_hash(path: Path) -> str | None:
    """`98`'s difference hash: 64 bits, one per adjacent column pair, per row.

    Each bit says whether a cell is DARKER than the cell to its right. That is what
    makes it a difference hash rather than an average one, and what makes it survive
    the material `98` §4 names -- "resized exports, screenshots of screenshots, and
    messaging-app re-encodes" -- none of which changes which of two neighbouring
    regions is the brighter.

    Rendered most-significant bit first as hexadecimal, behind the algorithm's own
    name, so the value states what it is.
    """
    read = _thumbnail_rows(path)
    if read is None:
        return None
    raster, stride = read
    bits = 0
    for row in range(NEAR_DUPLICATE_THUMBNAIL_ROWS):
        base = row * stride
        for column in range(NEAR_DUPLICATE_THUMBNAIL_COLUMNS - 1):
            bits <<= 1
            if raster[base + column] < raster[base + column + 1]:
                bits |= 1
    return f"{HASH_ALGORITHM}:{bits:0{NEAR_DUPLICATE_HASH_BITS // 4}x}"


def _bits(rendered: str) -> int | None:
    """The integer behind a rendered value, or `None` if it is not one of ours."""
    name, _, digits = rendered.partition(":")
    if name != HASH_ALGORITHM or len(digits) != NEAR_DUPLICATE_HASH_BITS // 4:
        return None
    try:
        return int(digits, 16)
    except ValueError:
        return None


def distance(left: str, right: str) -> int | None:
    """The Hamming distance between two of this algorithm's hashes.

    `None` when either value is not one of this algorithm's: a distance between a
    `dhash64` and something else is a number about nothing, and returning one would
    let a future hash be compared against this one bit for bit.
    """
    left_bits, right_bits = _bits(left), _bits(right)
    if left_bits is None or right_bits is None:
        return None
    return (left_bits ^ right_bits).bit_count()


def near_duplicate(left: str, right: str) -> bool:
    """`98`'s `near_match`, at the owner's threshold. False when either is unreadable.

    False rather than an exception on an unparseable value, and the asymmetry is the
    point: this predicate's False means "not shown to the owner as a near-duplicate",
    which is `98` §3.2's safe side. An exception here would stop a scan over one
    unreadable photograph.
    """
    apart = distance(left, right)
    return apart is not None and apart <= NEAR_DUPLICATE_MAX_DISTANCE


def near_block_keys(rendered: str) -> tuple[str, ...]:
    """The banded blocking keys for one hash: agree on one band, or never compare.

    `NEAR_DUPLICATE_BANDS` disjoint bands over the 64 bits. Two hashes within
    `NEAR_DUPLICATE_MAX_DISTANCE` differ in at most that many bits, and there are
    more bands than that, so at least one band is bit-identical -- the pigeonhole
    bound, which is what makes this key a NECESSARY CONDITION of `near_duplicate`
    and therefore safe to block on. A value this algorithm did not produce gets no
    key at all and is compared against nothing.

    The bands are contiguous and their widths differ by at most one bit, because 64
    is not a multiple of six; both facts are properties of the ruled numbers rather
    than choices.
    """
    bits = _bits(rendered)
    if bits is None:
        return ()
    keys: list[str] = []
    start = 0
    for band in range(NEAR_DUPLICATE_BANDS):
        end = (NEAR_DUPLICATE_HASH_BITS * (band + 1)) // NEAR_DUPLICATE_BANDS
        width = end - start
        window = (bits >> (NEAR_DUPLICATE_HASH_BITS - end)) & ((1 << width) - 1)
        keys.append(f"{band}:{window:x}")
        start = end
    return tuple(keys)
