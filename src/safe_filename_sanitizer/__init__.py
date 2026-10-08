"""Safe Filename Sanitizer.

A small, dependency-free library that rewrites a string into a filename that
is valid on Windows, macOS, and Linux simultaneously.
"""

from .core import sanitize_filename, sanitize_path_segment

__all__ = ["sanitize_filename", "sanitize_path_segment"]
