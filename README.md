# Safe Filename Sanitizer

Replaces or removes characters that are invalid as a filename on Windows, macOS, or Linux, returning a single portable filename token.

```python
from safe_filename_sanitizer import sanitize_filename, sanitize_path_segment

sanitize_filename("a/b:c?.txt")   # -> "a_b_c_.txt"
sanitize_filename("CON")           # -> "_CON"
sanitize_filename("")              # -> "_"
```

## Why this exists

Cross-platform filename handling is mostly about Windows: POSIX filesystems accept nearly any byte sequence, while Windows forbids a specific set of characters, a set of reserved device names (CON, PRN, NUL, COM1-9, LPT1-9), and trailing dots or spaces. This library applies a single conservative ruleset so one sanitised string works everywhere.

The trade-off is that it is deliberately lossy. Characters that carry meaning on one platform but not another are replaced with `_` rather than preserved, because preservation would require per-platform output. If you need round-trip fidelity, keep the original string separately.

## Edge cases you will hit

The result is treated as a single filename token, not a path. Forward slashes and backslashes are both replaced, so `"a/b"` becomes `"a_b"` rather than a directory plus a file. Build paths segment by segment with `sanitize_path_segment` if that is what you need.

Reserved names are detected before extensions are inspected, so `"CON.txt"` is prefixed to `"_CON.txt"`. The extension is preserved; only the stem is disambiguated.
