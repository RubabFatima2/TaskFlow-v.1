import html
import re
from typing import Optional, List


class InputSanitizer:
    """Utility class for sanitizing user input to prevent XSS attacks"""

    @staticmethod
    def sanitize_string(text: Optional[str]) -> Optional[str]:
        """
        Sanitize a string by escaping HTML entities and removing dangerous patterns

        Args:
            text: Input string to sanitize

        Returns:
            Sanitized string or None if input is None
        """
        if text is None:
            return None

        # Escape HTML entities
        sanitized = html.escape(text)

        # Remove any remaining script tags (case-insensitive)
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Remove javascript: protocol
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)

        # Remove on* event handlers (onclick, onerror, etc.)
        sanitized = re.sub(r'\bon\w+\s*=', '', sanitized, flags=re.IGNORECASE)

        return sanitized

    @staticmethod
    def sanitize_list(items: Optional[List[str]]) -> Optional[List[str]]:
        """
        Sanitize a list of strings

        Args:
            items: List of strings to sanitize

        Returns:
            List of sanitized strings or None if input is None
        """
        if items is None:
            return None

        return [InputSanitizer.sanitize_string(item) for item in items if item]


# Global sanitizer instance
sanitizer = InputSanitizer()
