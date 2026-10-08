"""Core implementation for filename sanitisation."""

from __future__ import annotations

import re
import unicodedata

# Characters forbidden by Windows (kernel path rules), plus the ASCII control
# range (0x00-0x1F) which is illegal on every common filesystem. Forward slash
# is reserved as the path separator on POSIX and is also rejected by Windows.
#
# The backslash is intentionally included here: it is a path separator on
# Windows and a regular character on POSIX. Keeping it would produce a name
# that Windows interprets as a directory boundary, which defeats the purpose
# of a single portable filename token. We replace it rather than preserve it.
_INVALID_CHARS = re.compile(r'[<>:\"/\\|?*\x00-\x1f]')

# Windows reserves these names outright, regardless of extension, because they
# map to legacy DOS devices (CON, PR0, NUL, ...). Matching is case-insensitive
# and also catches forms with an extension such as "NUL.txt".
#
# We detect this *before* trimming trailing dots/spaces, so that "CON. " is
# still recognised. The replacement makes the name safe by prefixing it with
# an underscore; we do not strip the original text so the user's intent stays
# visible.
_WINDOWS_RESERVED = re.compile(
    r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?$',
    re.IGNORECASE,
)

# A filename consisting only of dots and/or spaces is legal on POSIX but is
# either reserved ("..", ".") or awkward on Windows. We collapse such names
# to a single underscore rather than returning an empty string.
_DOTS_OR_SPACES = re.compile(r'^[. ]+$')


def _strip_illegal_chars(name: str) -> str:
    return _INVALID_CHARS.sub("_", name)


def _normalise_unicode(name: str) -> str:
    # Apply NFC so that a character with a precomposed form is stored as a
    # single code point where possible. This keeps visually identical names
    # byte-identical, which matters for deduplication and equality checks.
    return unicodedata.normalize("NFC", name)


def _trim_trailing(name: str) -> str:
    # Windows does not allow filenames that end with a space or a dot, because
    # the filesystem layer silently strips them, producing a different name
    # than the caller asked for.
    return name.rstrip(" .")


def _fix_reserved(name: str) -> str:
    if _WINDOWS_RESERVED.match(name):
        return "_" + name
    return name


def _collapse_underscores(name: str) -> str:
    # Multiple illegal characters in a row each became an underscore, which is
    # ugly and can change sort order unexpectedly. Collapse runs to one.
    return re.sub(r'_+', '_', name)


def _final_fallback(name: str) -> str:
    if not name or _DOTS_OR_SPACES.match(name):
        return "_"
    return name


def sanitize_filename(name: str, *, replacement: str = "_") -> str:
    """Return a string that is a valid filename on Windows, macOS, and Linux.

    The input is treated as a *single filename token*, not a path. Any
    character that is a path separator on a supported platform (``/`` or
    ``\\``) is replaced, so the result never contains a directory boundary.

    Steps applied, in order:

    1. Unicode NFC normalisation, so visually identical names are byte-
       identical.
    2. Replacement of every illegal or platform-ambiguous character with
       ``replacement`` (default ``_``).
    3. Collapsing of consecutive replacement characters into one.
    4. Prefixing of Windows-reserved base names (``CON``, ``PRN``, ...).
    5. Stripping of trailing spaces and dots, which Windows drops silently.
    6. Fallback to ``_`` when nothing meaningful remains.

    Parameters
    ----------
    name:
        The raw string to sanitise. ``None`` is rejected with ``TypeError``;
        callers should coerce upstream if they have nullable data.
    replacement:
        Character or short string substituted for each illegal character.
        Must itself be filename-safe; a non-safe value raises ``ValueError``.

    Returns
    -------
    str
        A non-empty filename containing no path separators, no control
        characters, no trailing dots or spaces, and no Windows-reserved stem.
    """
    if name is None:
        raise TypeError("name must be a str, not None")
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    if not isinstance(replacement, str):
        raise TypeError("replacement must be a str")
    if replacement == "":
        raise ValueError("replacement must be non-empty")
    if _INVALID_CHARS.search(replacement) or _DOTS_OR_SPACES.match(replacement):
        raise ValueError("replacement contains illegal or weak characters")

    work = _normalise_unicode(name)
    work = _strip_illegal_chars(work)
    # When the caller picks a custom replacement, we substitute it *after* the
    # initial underscore pass so the collapse regex still sees a single token
    # kind and behaves predictably.
    if replacement != "_":
        work = work.replace("_", replacement)
    work = re.sub(re.escape(replacement) + r'+', replacement, work)
    work = _fix_reserved(work)
    work = _trim_trailing(work)
    work = _final_fallback(work)
    return work


def sanitize_path_segment(name: str, *, replacement: str = "_") -> str:
    """Sanitise a single path *segment*.

    This is identical to :func:`sanitize_filename` but is provided so callers
    can express intent when building paths component by component. It enforces
    the same single-token rule: the result never contains ``/`` or ``\\``.
    """
    return sanitize_filename(name, replacement=replacement)
