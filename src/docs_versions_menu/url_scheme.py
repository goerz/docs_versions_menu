"""URL version scheme enumeration."""

from __future__ import annotations

from enum import Enum


class UrlVersionScheme(str, Enum):
    """Defines the URL structure for versioned documentation.

    NO_TRANSLATIONS uses /<version>/<filename> (current default behavior).
    TRANSLATIONS uses /<language>/<version>/<filename> (Read the Docs style).
    """

    NO_TRANSLATIONS = "no-translations"
    TRANSLATIONS = "translations"

    def __str__(self):
        return self.value

    def __format__(self, format_spec):
        return self.value.__format__(format_spec)

    @staticmethod
    def parse(value: str) -> UrlVersionScheme:
        for member in UrlVersionScheme:
            if member.value == value:
                return member
        raise ValueError(
            f"{value!r} is not a valid UrlVersionScheme. "
            f"Valid values are: {[m.value for m in UrlVersionScheme]}"
        )
