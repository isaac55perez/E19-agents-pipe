"""
Unit tests for gmail_client module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from gmail_client import GmailAuthenticator, GmailDraftCreator


class TestGmailAuthenticator:
    """Tests for GmailAuthenticator class."""

    def test_authenticator_init(self):
        """Test GmailAuthenticator initialization."""
        auth = GmailAuthenticator()
        assert auth.service is None
        assert auth.authenticated is False

    def test_authenticator_authenticate(self):
        """Test authentication method."""
        auth = GmailAuthenticator()
        result = auth.authenticate()

        assert result is True
        assert auth.authenticated is True

    def test_authenticator_is_authenticated_before(self):
        """Test is_authenticated before authentication."""
        auth = GmailAuthenticator()
        assert auth.is_authenticated() is False

    def test_authenticator_is_authenticated_after(self):
        """Test is_authenticated after authentication."""
        auth = GmailAuthenticator()
        auth.authenticate()
        assert auth.is_authenticated() is True


class TestGmailDraftCreatorInit:
    """Tests for GmailDraftCreator initialization."""

    def test_draft_creator_init_default(self):
        """Test GmailDraftCreator initialization with default authenticator."""
        creator = GmailDraftCreator()

        assert creator.authenticator is not None
        assert creator.service is None
        assert creator.drafts_created == 0
        assert creator.drafts_failed == 0

    def test_draft_creator_init_custom_authenticator(self):
        """Test GmailDraftCreator initialization with custom authenticator."""
        auth = GmailAuthenticator()
        auth.authenticate()

        creator = GmailDraftCreator(auth)

        assert creator.authenticator is auth
        assert creator.authenticator.is_authenticated() is True

    def test_draft_creator_set_service(self):
        """Test setting Gmail service."""
        creator = GmailDraftCreator()
        mock_service = Mock()

        creator.set_service(mock_service)

        assert creator.service is mock_service


class TestCreateMessage:
    """Tests for create_message method."""

    def test_create_message_basic(self):
        """Test creating a basic MIME message."""
        message = GmailDraftCreator.create_message(
            to_email="user@example.com",
            subject="Test Subject",
            body_html="<html><body>HTML content</body></html>",
            body_text="Plain text content"
        )

        assert isinstance(message, str)
        assert len(message) > 0
        # Message should be base64 encoded, which may have newlines for line wrapping
        # Just verify it's a non-empty string
        import base64
        # Verify it can be decoded (with newlines stripped)
        decoded = base64.urlsafe_b64decode(message.replace('\n', ''))
        assert len(decoded) > 0

    def test_create_message_contains_recipient(self):
        """Test that message contains recipient email."""
        to_email = "alice@example.com"
        message = GmailDraftCreator.create_message(
            to_email=to_email,
            subject="Test",
            body_html="<html></html>",
            body_text="Text"
        )

        # Base64 decode to verify content
        import base64
        # Remove newlines that may be in base64 encoded message
        decoded = base64.urlsafe_b64decode(message.replace('\n', '')).decode('utf-8')
        # Email headers are lowercase in MIME message
        assert to_email in decoded

    def test_create_message_contains_subject(self):
        """Test that message contains subject."""
        subject = "Test Subject Line"
        message = GmailDraftCreator.create_message(
            to_email="user@example.com",
            subject=subject,
            body_html="<html></html>",
            body_text="Text"
        )

        import base64
        # Remove newlines that may be in base64 encoded message
        decoded = base64.urlsafe_b64decode(message.replace('\n', '')).decode('utf-8')
        # Check that subject is in the message (may be lowercase in MIME headers)
        assert subject in decoded

    def test_create_message_contains_html_and_text(self):
        """Test that message contains both HTML and text parts."""
        html_content = "<html><body><h1>Hello</h1></body></html>"
        text_content = "Hello"

        message = GmailDraftCreator.create_message(
            to_email="user@example.com",
            subject="Test",
            body_html=html_content,
            body_text=text_content
        )

        import base64
        decoded = base64.urlsafe_b64decode(message.encode()).decode('utf-8')
        # Should contain multipart structure
        assert "multipart/alternative" in decoded

    def test_create_message_special_characters(self):
        """Test creating message with special characters."""
        message = GmailDraftCreator.create_message(
            to_email="user@example.com",
            subject="Test with émojis and spëcial chars",
            body_html="<html><body>Tëst wîth spëcîâl çhàrs</body></html>",
            body_text="Tëst wîth spëcîâl çhàrs"
        )

        assert isinstance(message, str)
        assert len(message) > 0

    def test_create_message_long_content(self):
        """Test creating message with long content."""
        long_html = "<html><body>" + "<p>Paragraph</p>" * 100 + "</body></html>"
        long_text = "Line\n" * 100

        message = GmailDraftCreator.create_message(
            to_email="user@example.com",
            subject="Long message",
            body_html=long_html,
            body_text=long_text
        )

        assert isinstance(message, str)
        assert len(message) > 1000


class TestCreateDraft:
    """Tests for create_draft method."""

    def test_create_draft_not_authenticated(self):
        """Test creating draft without authentication."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = False

        success, draft_id, message = creator.create_draft(
            to_email="user@example.com",
            subject="Test",
            body_html="<html></html>",
            body_text="Text"
        )

        assert success is False
        assert draft_id is None
        assert "Not authenticated" in message

    def test_create_draft_dry_run(self):
        """Test creating draft in dry-run mode."""
        creator = GmailDraftCreator()

        success, draft_id, message = creator.create_draft(
            to_email="user@example.com",
            subject="Test",
            body_html="<html></html>",
            body_text="Text",
            dry_run=True
        )

        assert success is True
        assert draft_id is not None
        assert "dry_run" in draft_id

    def test_create_draft_authenticated(self):
        """Test creating draft with authentication."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        success, draft_id, message = creator.create_draft(
            to_email="user@example.com",
            subject="Test",
            body_html="<html></html>",
            body_text="Text"
        )

        assert success is True
        assert draft_id is not None
        assert "draft_" in draft_id
        assert creator.drafts_created == 1
        assert creator.drafts_failed == 0

    def test_create_draft_statistics(self):
        """Test that draft creation updates statistics."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        for i in range(3):
            creator.create_draft(
                to_email=f"user{i}@example.com",
                subject="Test",
                body_html="<html></html>",
                body_text="Text"
            )

        assert creator.drafts_created == 3
        assert creator.drafts_failed == 0

    def test_create_draft_returns_email_in_id(self):
        """Test that draft ID contains email address."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        success, draft_id, message = creator.create_draft(
            to_email="alice@example.com",
            subject="Test",
            body_html="<html></html>",
            body_text="Text"
        )

        assert "alice@example.com" in draft_id

    def test_create_draft_multiple_sequential(self):
        """Test creating multiple drafts sequentially."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        for i in range(5):
            success, draft_id, message = creator.create_draft(
                to_email=f"user{i}@example.com",
                subject=f"Test {i}",
                body_html="<html></html>",
                body_text="Text"
            )
            assert success is True

        assert creator.drafts_created == 5


class TestCreateDraftsBatch:
    """Tests for create_drafts_batch method."""

    def test_create_drafts_batch_empty(self):
        """Test batch creation with empty list."""
        creator = GmailDraftCreator()
        results = creator.create_drafts_batch(entries=[])

        assert results['total'] == 0
        assert results['successful'] == 0
        assert results['failed'] == 0
        assert len(results['results']) == 0

    def test_create_drafts_batch_single(self):
        """Test batch creation with single entry."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        entries = [
            {
                "email": "user@example.com",
                "subject": "Test",
                "body_html": "<html></html>",
                "body_text": "Text"
            }
        ]

        results = creator.create_drafts_batch(entries=entries)

        assert results['total'] == 1
        assert results['successful'] == 1
        assert results['failed'] == 0
        assert len(results['results']) == 1

    def test_create_drafts_batch_multiple(self):
        """Test batch creation with multiple entries."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        entries = [
            {
                "email": f"user{i}@example.com",
                "subject": f"Subject {i}",
                "body_html": "<html></html>",
                "body_text": "Text"
            }
            for i in range(5)
        ]

        results = creator.create_drafts_batch(entries=entries)

        assert results['total'] == 5
        assert results['successful'] == 5
        assert results['failed'] == 0

    def test_create_drafts_batch_dry_run(self):
        """Test batch creation in dry-run mode."""
        creator = GmailDraftCreator()

        entries = [
            {
                "email": f"user{i}@example.com",
                "subject": f"Subject {i}",
                "body_html": "<html></html>",
                "body_text": "Text"
            }
            for i in range(3)
        ]

        results = creator.create_drafts_batch(entries=entries, dry_run=True)

        assert results['total'] == 3
        assert results['successful'] == 3
        assert results['failed'] == 0
        # In dry-run, authenticator doesn't need to be authenticated
        assert creator.authenticator.authenticated is False

    def test_create_drafts_batch_result_structure(self):
        """Test that batch results have correct structure."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        entries = [
            {
                "email": "user@example.com",
                "subject": "Test",
                "body_html": "<html></html>",
                "body_text": "Text"
            }
        ]

        results = creator.create_drafts_batch(entries=entries)

        assert "total" in results
        assert "successful" in results
        assert "failed" in results
        assert "results" in results
        assert "errors" in results

        assert len(results['results']) == 1
        assert "email" in results['results'][0]
        assert "success" in results['results'][0]
        assert "draft_id" in results['results'][0]
        assert "message" in results['results'][0]

    def test_create_drafts_batch_missing_fields(self):
        """Test batch handling of entries with missing fields."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        entries = [
            {
                "email": "user1@example.com",
                "subject": "Test",
                "body_html": "<html></html>",
                "body_text": "Text"
            },
            {
                "email": "user2@example.com",
                # Missing subject
                "body_html": "<html></html>",
                "body_text": "Text"
            }
        ]

        results = creator.create_drafts_batch(entries=entries)

        # Should still process both, with defaults for missing fields
        assert results['total'] == 2


class TestGetStatistics:
    """Tests for get_statistics method."""

    def test_get_statistics_initial(self):
        """Test initial statistics."""
        creator = GmailDraftCreator()
        stats = creator.get_statistics()

        assert stats['drafts_created'] == 0
        assert stats['drafts_failed'] == 0
        assert stats['total_attempted'] == 0

    def test_get_statistics_after_creation(self):
        """Test statistics after draft creation."""
        creator = GmailDraftCreator()
        creator.authenticator.authenticated = True

        for i in range(3):
            creator.create_draft(
                to_email=f"user{i}@example.com",
                subject="Test",
                body_html="<html></html>",
                body_text="Text"
            )

        stats = creator.get_statistics()

        assert stats['drafts_created'] == 3
        assert stats['drafts_failed'] == 0
        assert stats['total_attempted'] == 3

    def test_get_statistics_structure(self):
        """Test that statistics have correct structure."""
        creator = GmailDraftCreator()
        stats = creator.get_statistics()

        assert isinstance(stats, dict)
        assert "drafts_created" in stats
        assert "drafts_failed" in stats
        assert "total_attempted" in stats


class TestRetryLogic:
    """Tests for retry logic in create_draft."""

    def test_max_retries_constant(self):
        """Test that MAX_RETRIES constant is set."""
        creator = GmailDraftCreator()
        assert hasattr(creator, 'MAX_RETRIES')
        assert creator.MAX_RETRIES == 3

    def test_retry_delay_constant(self):
        """Test that RETRY_DELAY constant is set."""
        creator = GmailDraftCreator()
        assert hasattr(creator, 'RETRY_DELAY')
        assert creator.RETRY_DELAY == 1

    def test_api_call_delay_constant(self):
        """Test that API_CALL_DELAY constant is set."""
        creator = GmailDraftCreator()
        assert hasattr(creator, 'API_CALL_DELAY')
        assert creator.API_CALL_DELAY == 0.5
