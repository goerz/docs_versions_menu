"""Tests for the url_scheme module."""

import pytest

from docs_versions_menu.url_scheme import UrlVersionScheme


class TestParseUrlScheme:
    """Tests for UrlVersionScheme.parse method."""

    def test_parse_no_translations(self):
        """Test parsing 'no-translations' string."""
        result = UrlVersionScheme.parse('no-translations')
        assert result == UrlVersionScheme.NO_TRANSLATIONS

    def test_parse_translations(self):
        """Test parsing 'translations' string."""
        result = UrlVersionScheme.parse('translations')
        assert result == UrlVersionScheme.TRANSLATIONS

    def test_parse_invalid(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            UrlVersionScheme.parse('invalid')

    def test_parse_empty(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            UrlVersionScheme.parse('')
