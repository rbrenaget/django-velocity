"""
Tests for security validators.
"""

import pytest
from django.core.exceptions import ValidationError

from apps.security.validators import BreachCheckValidator, PasswordStrengthValidator


class TestPasswordStrengthValidator:
    """Tests for PasswordStrengthValidator."""

    def test_accepts_strong_password(self):
        """Should accept a strong password."""
        validator = PasswordStrengthValidator()
        # Should not raise
        validator.validate("MyStr0ng!Pass")

    def test_rejects_short_password(self):
        """Should reject password shorter than min_length."""
        validator = PasswordStrengthValidator(min_length=10)
        with pytest.raises(ValidationError):
            validator.validate("Short1!")

    def test_rejects_password_without_uppercase(self):
        """Should reject password without uppercase."""
        validator = PasswordStrengthValidator(require_uppercase=True)
        with pytest.raises(ValidationError):
            validator.validate("lowercase1!")

    def test_rejects_password_without_lowercase(self):
        """Should reject password without lowercase."""
        validator = PasswordStrengthValidator(require_lowercase=True)
        with pytest.raises(ValidationError):
            validator.validate("UPPERCASE1!")

    def test_rejects_password_without_digit(self):
        """Should reject password without digit."""
        validator = PasswordStrengthValidator(require_digit=True)
        with pytest.raises(ValidationError):
            validator.validate("NoDigits!")

    def test_rejects_password_without_special(self):
        """Should reject password without special character."""
        validator = PasswordStrengthValidator(require_special=True)
        with pytest.raises(ValidationError):
            validator.validate("NoSpecial123")

    def test_get_help_text(self):
        """Should return help text."""
        validator = PasswordStrengthValidator()
        help_text = validator.get_help_text()
        assert "at least" in help_text


class TestBreachCheckValidator:
    """Tests for BreachCheckValidator."""

    def test_disabled_validator_passes_all(self):
        """Should pass all passwords when disabled."""
        validator = BreachCheckValidator(enabled=False)
        # Should not raise even for common password
        validator.validate("password123")

    def test_get_help_text(self):
        """Should return help text."""
        validator = BreachCheckValidator()
        help_text = validator.get_help_text()
        assert "breach" in help_text.lower()
