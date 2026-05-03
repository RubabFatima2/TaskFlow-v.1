import pytest
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from datetime import datetime, timezone, timedelta


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password_returns_different_hash(self):
        """Test that hashing the same password twice produces different hashes"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # bcrypt uses random salt
        assert hash1 != password  # hash should not equal plaintext

    def test_verify_password_with_correct_password(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_password_with_empty_string(self):
        """Test hashing empty string"""
        password = ""
        hashed = hash_password(password)

        assert hashed != ""
        assert verify_password(password, hashed) is True

    def test_hash_password_with_special_characters(self):
        """Test hashing password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and verification"""

    def test_create_access_token(self):
        """Test access token creation"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self):
        """Test verifying a valid token"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_invalid_token(self):
        """Test verifying an invalid token"""
        invalid_token = "invalid.token.here"

        payload = verify_token(invalid_token)

        assert payload is None

    def test_verify_tampered_token(self):
        """Test verifying a tampered token"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)

        # Tamper with token
        tampered_token = token[:-10] + "tampered12"

        payload = verify_token(tampered_token)

        assert payload is None

    def test_access_token_contains_expiration(self):
        """Test that access token contains expiration claim"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        payload = verify_token(token)

        assert "exp" in payload
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)

        # Token should expire in the future
        assert exp_datetime > now

    def test_refresh_token_has_longer_expiration(self):
        """Test that refresh token expires later than access token"""
        data = {"user_id": 1, "email": "test@example.com"}

        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        access_payload = verify_token(access_token)
        refresh_payload = verify_token(refresh_token)

        assert refresh_payload["exp"] > access_payload["exp"]

    def test_token_contains_issued_at(self):
        """Test that token contains issued at claim"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        payload = verify_token(token)

        assert "iat" in payload
        iat_timestamp = payload["iat"]
        iat_datetime = datetime.fromtimestamp(iat_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)

        # Token should be issued recently (within last minute)
        assert (now - iat_datetime).total_seconds() < 60

    def test_token_preserves_custom_data(self):
        """Test that custom data is preserved in token"""
        data = {
            "user_id": 123,
            "email": "custom@example.com",
            "custom_field": "custom_value"
        }
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload["user_id"] == 123
        assert payload["email"] == "custom@example.com"
        assert payload["custom_field"] == "custom_value"
