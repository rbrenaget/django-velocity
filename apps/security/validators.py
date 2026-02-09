"""
Password Validators - Enhanced password security.

Custom validators for password strength and breach checking.
"""

from __future__ import annotations

import hashlib
import logging
import math
import string
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class PasswordStrengthValidator:
    """
    Validate password strength based on character variety and entropy.

    Configurable via __init__ options or Django settings.
    """

    def __init__(
        self,
        min_length: int = 12,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        min_entropy: float = 30.0,
    ) -> None:
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.min_entropy = min_entropy

    def validate(self, password: str, user: Any = None) -> None:
        """Validate the password meets strength requirements."""
        errors = []

        if len(password) < self.min_length:
            errors.append(
                _("Password must be at least %(min_length)d characters long.")
                % {"min_length": self.min_length}
            )

        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append(_("Password must contain at least one uppercase letter."))

        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append(_("Password must contain at least one lowercase letter."))

        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append(_("Password must contain at least one digit."))

        if self.require_special:
            special_chars = set(string.punctuation)
            if not any(c in special_chars for c in password):
                errors.append(
                    _("Password must contain at least one special character.")
                )

        entropy = self._calculate_entropy(password)
        if entropy < self.min_entropy:
            errors.append(
                _("Password is too weak. Use a more complex combination of characters.")
            )

        if errors:
            raise ValidationError(errors)

    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits."""
        charset_size = 0

        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in string.punctuation for c in password):
            charset_size += 32

        if charset_size == 0:
            return 0.0

        return len(password) * math.log2(charset_size)

    def get_help_text(self) -> str:
        """Return help text for this validator."""
        requirements = [f"at least {self.min_length} characters"]
        if self.require_uppercase:
            requirements.append("one uppercase letter")
        if self.require_lowercase:
            requirements.append("one lowercase letter")
        if self.require_digit:
            requirements.append("one digit")
        if self.require_special:
            requirements.append("one special character")

        return _("Your password must contain: ") + ", ".join(requirements) + "."


class BreachCheckValidator:
    """
    Check if password has been exposed in a data breach.

    Uses Have I Been Pwned API with k-anonymity (only sends first 5 chars of hash).

    Configurable:
    - PASSWORD_BREACH_CHECK_ENABLED: bool (default True)
    - PASSWORD_BREACH_THRESHOLD: int (default 1) - minimum appearances to reject
    """

    def __init__(
        self,
        threshold: int = 1,
        enabled: bool | None = None,
    ) -> None:
        self.threshold = threshold
        self._enabled = enabled

    @property
    def enabled(self) -> bool:
        """Check if breach checking is enabled."""
        if self._enabled is not None:
            return self._enabled
        return getattr(settings, "PASSWORD_BREACH_CHECK_ENABLED", True)

    def validate(self, password: str, user: Any = None) -> None:
        """Check if password appears in breach database."""
        if not self.enabled:
            return

        try:
            breach_count = self._check_password(password)
            threshold = getattr(settings, "PASSWORD_BREACH_THRESHOLD", self.threshold)

            if breach_count >= threshold:
                raise ValidationError(
                    _(
                        "This password has been exposed in a data breach "
                        "and should not be used. Please choose a different password."
                    ),
                    code="password_breached",
                )
        except ValidationError:
            raise
        except Exception as e:
            logger.warning(f"Breach check failed: {e}")

    def _check_password(self, password: str) -> int:
        """
        Check password against Have I Been Pwned API.

        Uses k-anonymity: only sends first 5 chars of SHA-1 hash.

        Returns:
            Number of times password appears in breaches
        """
        import urllib.request

        sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Django-Velocity-PasswordCheck"},
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                body = response.read().decode("utf-8")

            for line in body.splitlines():
                hash_suffix, count = line.split(":")
                if hash_suffix == suffix:
                    return int(count)

            return 0

        except Exception as e:
            logger.warning(f"HIBP API request failed: {e}")
            return 0

    def get_help_text(self) -> str:
        """Return help text for this validator."""
        return _("Your password must not have been exposed in a known data breach.")
