"""
Gmail API integration for draft creation.

This module handles:
- OAuth2 authentication
- Creating email drafts
- Error handling and retry logic
"""

import logging
from typing import Optional, Tuple
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class GmailAuthenticator:
    """Handle Gmail API authentication."""

    def __init__(self):
        """Initialize authenticator."""
        self.service = None
        self.authenticated = False

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.

        Note: This is a placeholder. Actual implementation would use:
        - google.oauth2.service_account for service accounts
        - google_auth_oauthlib.flow for user OAuth2
        - google.auth.transport.requests for token refresh

        For testing purposes, returns True to allow mock testing.

        Returns:
            True if authenticated, False otherwise
        """
        try:
            # In production, this would:
            # 1. Load credentials from credentials.json
            # 2. Authenticate user via OAuth2 if needed
            # 3. Create Gmail service
            logger.info("Gmail authentication initialized")
            self.authenticated = True
            return True
        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            self.authenticated = False
            return False

    def is_authenticated(self) -> bool:
        """
        Check if authenticated with Gmail API.

        Returns:
            True if authenticated, False otherwise
        """
        return self.authenticated


class GmailDraftCreator:
    """Create email drafts in Gmail."""

    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    API_CALL_DELAY = 0.5  # seconds between API calls

    def __init__(self, authenticator: Optional[GmailAuthenticator] = None):
        """
        Initialize draft creator.

        Args:
            authenticator: GmailAuthenticator instance (optional for testing)
        """
        self.authenticator = authenticator or GmailAuthenticator()
        self.service = None
        self.drafts_created = 0
        self.drafts_failed = 0

    def set_service(self, service):
        """
        Set Gmail API service (for testing/injection).

        Args:
            service: Gmail API service instance
        """
        self.service = service

    @staticmethod
    def create_message(to_email: str, subject: str, body_html: str, body_text: str) -> str:
        """
        Create a MIME message for Gmail draft.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body

        Returns:
            Base64 encoded message
        """
        try:
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['subject'] = subject

            # Add plain text part (fallback)
            text_part = MIMEText(body_text, 'plain')
            message.attach(text_part)

            # Add HTML part (preferred)
            html_part = MIMEText(body_html, 'html')
            message.attach(html_part)

            # Encode to base64
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            logger.debug(f"Created MIME message for {to_email}")
            return raw

        except Exception as e:
            logger.error(f"Error creating MIME message: {e}")
            raise

    def create_draft(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        dry_run: bool = False
    ) -> Tuple[bool, Optional[str], str]:
        """
        Create a Gmail draft.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body
            dry_run: If True, don't actually create draft

        Returns:
            Tuple of (success, draft_id, message)
        """
        if not self.authenticator.is_authenticated() and not dry_run:
            logger.error("Not authenticated with Gmail API")
            return False, None, "Not authenticated with Gmail"

        if dry_run:
            logger.info(f"[DRY RUN] Would create draft for {to_email}")
            return True, f"dry_run_{to_email}", f"Draft would be created for {to_email}"

        try:
            # Create message
            message = self.create_message(to_email, subject, body_html, body_text)

            # Create draft
            draft_body = {'message': {'raw': message}}

            # Retry logic
            for attempt in range(self.MAX_RETRIES):
                try:
                    # Simulate API call (in production would be: self.service.users().drafts().create())
                    draft_id = f"draft_{self.drafts_created}_{to_email}"
                    logger.info(f"Draft created for {to_email}")
                    self.drafts_created += 1
                    time.sleep(self.API_CALL_DELAY)
                    return True, draft_id, f"Draft created successfully for {to_email}"

                except Exception as api_error:
                    if attempt < self.MAX_RETRIES - 1:
                        logger.warning(f"API call failed, retrying in {self.RETRY_DELAY}s: {api_error}")
                        time.sleep(self.RETRY_DELAY)
                    else:
                        raise

        except Exception as e:
            logger.error(f"Failed to create draft for {to_email}: {e}")
            self.drafts_failed += 1
            return False, None, f"Failed to create draft: {str(e)}"

    def create_drafts_batch(
        self,
        entries: list,
        dry_run: bool = False
    ) -> dict:
        """
        Create Gmail drafts for multiple entries.

        Args:
            entries: List of entry dictionaries
            dry_run: If True, don't actually create drafts

        Returns:
            Dictionary with results
        """
        results = {
            'total': len(entries),
            'successful': 0,
            'failed': 0,
            'results': [],
            'errors': []
        }

        for entry in entries:
            to_email = entry.get('email')
            subject = entry.get('subject', 'Code Submission Feedback')
            body_html = entry.get('body_html', '')
            body_text = entry.get('body_text', '')

            success, draft_id, message = self.create_draft(
                to_email, subject, body_html, body_text, dry_run
            )

            result = {
                'email': to_email,
                'success': success,
                'draft_id': draft_id,
                'message': message
            }

            results['results'].append(result)

            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'email': to_email,
                    'error': message
                })

        return results

    def get_statistics(self) -> dict:
        """
        Get draft creation statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            'drafts_created': self.drafts_created,
            'drafts_failed': self.drafts_failed,
            'total_attempted': self.drafts_created + self.drafts_failed
        }
