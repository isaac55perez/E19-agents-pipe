"""
Gmail API Connector Module

This module handles authentication and communication with Gmail API to fetch emails
from the 'exercises' folder and convert them into EmailData objects for processing.
"""

import logging
import base64
import pickle
from pathlib import Path
from typing import List, Optional, Tuple
from email.mime.text import MIMEText
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery

from extractor import EmailData

logger = logging.getLogger(__name__)

# Gmail API scopes - read-only access to emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailAuthenticator:
    """Handles OAuth authentication with Gmail API."""

    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        """
        Initialize Gmail authenticator.

        Args:
            credentials_file: Path to OAuth credentials JSON file from Google Cloud Console
            token_file: Path to store the OAuth token pickle file
        """
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        logger.info(f"Initializing Gmail authenticator with credentials file: {credentials_file}")

    def authenticate(self) -> Optional[Credentials]:
        """
        Authenticate with Gmail API using OAuth 2.0.

        Returns the Credentials object if successful, None otherwise.
        Uses stored token if available, otherwise initiates OAuth flow.

        Returns:
            Credentials object or None if authentication fails
        """
        creds = None

        # Try to load existing token
        if self.token_file.exists():
            logger.info(f"Loading existing token from {self.token_file}")
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                    logger.debug("Token loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")
                creds = None

        # If no valid token, get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Token expired, refreshing...")
                try:
                    creds.refresh(Request())
                    logger.info("Token refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}")
                    creds = None
            else:
                # Run OAuth flow
                logger.info("Running OAuth flow to get new credentials")
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("OAuth authentication successful")
                except Exception as e:
                    logger.error(f"OAuth flow failed: {e}")
                    return None

            # Save the new token
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                    logger.info(f"Token saved to {self.token_file}")
            except Exception as e:
                logger.warning(f"Failed to save token: {e}")

        return creds


class GmailFetcher:
    """Fetches emails from Gmail using the Gmail API."""

    def __init__(self, credentials: Credentials):
        """
        Initialize Gmail fetcher.

        Args:
            credentials: OAuth2 credentials object
        """
        self.credentials = credentials
        self.service = None
        logger.info("Initializing Gmail fetcher")
        self._initialize_service()

    def _initialize_service(self) -> bool:
        """
        Initialize the Gmail API service.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.service = discovery.build('gmail', 'v1', credentials=self.credentials)
            logger.info("Gmail API service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            return False

    def get_label_id(self, label_name: str) -> Optional[str]:
        """
        Get the label ID for a given label name.

        Args:
            label_name: Name of the label (e.g., 'exercises')

        Returns:
            Label ID if found, None otherwise
        """
        logger.info(f"Looking for label: {label_name}")
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            for label in labels:
                if label['name'].lower() == label_name.lower():
                    logger.info(f"Found label '{label_name}' with ID: {label['id']}")
                    return label['id']

            logger.warning(f"Label '{label_name}' not found")
            return None
        except Exception as e:
            logger.error(f"Failed to get label ID: {e}")
            return None

    def fetch_emails_from_label(self, label_name: str = "exercises", max_results: int = 100) -> List[EmailData]:
        """
        Fetch emails from a specific Gmail label.

        Args:
            label_name: Name of the Gmail label (default: 'exercises')
            max_results: Maximum number of emails to fetch (default: 100)

        Returns:
            List of EmailData objects
        """
        logger.info(f"Fetching emails from label '{label_name}' (max: {max_results})")

        # Get label ID
        label_id = self.get_label_id(label_name)
        if not label_id:
            logger.error(f"Cannot fetch emails: label '{label_name}' not found")
            return []

        emails = []
        try:
            # Get message IDs from label
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[label_id],
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} messages in '{label_name}' label")

            if not messages:
                logger.warning(f"No messages found in '{label_name}' label")
                return []

            # Fetch full message data for each message
            for idx, message in enumerate(messages, 1):
                try:
                    logger.debug(f"Fetching message {idx}/{len(messages)}")
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()

                    email_data = self._parse_message(msg)
                    if email_data:
                        emails.append(email_data)
                        logger.debug(f"Message {idx} parsed successfully: {email_data.subject}")
                    else:
                        logger.warning(f"Failed to parse message {idx}")

                except Exception as e:
                    logger.error(f"Error fetching message {idx}: {e}")

            logger.info(f"Successfully fetched {len(emails)} emails from '{label_name}'")
            return emails

        except Exception as e:
            logger.error(f"Failed to fetch emails from label: {e}")
            return []

    def _parse_message(self, message: dict) -> Optional[EmailData]:
        """
        Parse a Gmail message and extract EmailData.

        Args:
            message: Gmail message object from API

        Returns:
            EmailData object or None if parsing fails
        """
        try:
            headers = message['payload']['headers']

            # Extract date
            date = self._get_header_value(headers, 'Date')
            if not date:
                logger.warning("No date found in message headers")
                date = datetime.now().isoformat()

            # Extract subject
            subject = self._get_header_value(headers, 'Subject')
            if not subject:
                subject = "(No Subject)"

            # Extract body
            body = self._get_message_body(message['payload'])
            if not body:
                body = ""

            logger.debug(f"Parsed email: date={date}, subject={subject}, body_length={len(body)}")

            return EmailData(date=date, subject=subject, body=body)

        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None

    @staticmethod
    def _get_header_value(headers: List[dict], header_name: str) -> Optional[str]:
        """
        Get a specific header value from message headers.

        Args:
            headers: List of header dictionaries
            header_name: Name of the header to find

        Returns:
            Header value or None if not found
        """
        for header in headers:
            if header['name'].lower() == header_name.lower():
                return header['value']
        return None

    @staticmethod
    def _get_message_body(payload: dict) -> Optional[str]:
        """
        Extract message body from Gmail payload.

        Handles both simple messages and multipart messages.

        Args:
            payload: Message payload from Gmail API

        Returns:
            Message body text or None
        """
        try:
            # Simple message with just text
            if 'body' in payload and payload['body'].get('size', 0) > 0:
                data = payload['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')

            # Multipart message - look for text/plain or text/html parts
            if 'parts' in payload:
                for part in payload['parts']:
                    mime_type = part.get('mimeType', '')
                    if mime_type == 'text/plain':
                        if 'body' in part and part['body'].get('size', 0) > 0:
                            data = part['body'].get('data', '')
                            if data:
                                return base64.urlsafe_b64decode(data).decode('utf-8')

                # If no plain text, try HTML
                for part in payload['parts']:
                    mime_type = part.get('mimeType', '')
                    if mime_type == 'text/html':
                        if 'body' in part and part['body'].get('size', 0) > 0:
                            data = part['body'].get('data', '')
                            if data:
                                return base64.urlsafe_b64decode(data).decode('utf-8')

            return None

        except Exception as e:
            logger.error(f"Error extracting message body: {e}")
            return None


class GmailExerciseExtractor:
    """Main class for extracting exercise emails from Gmail."""

    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Initialize Gmail Exercise Extractor.

        Args:
            credentials_file: Path to OAuth credentials file
        """
        self.credentials_file = credentials_file
        self.authenticator = GmailAuthenticator(credentials_file)
        self.fetcher: Optional[GmailFetcher] = None
        logger.info("Initializing GmailExerciseExtractor")

    def setup(self) -> bool:
        """
        Setup the extractor by authenticating with Gmail.

        Returns:
            True if setup successful, False otherwise
        """
        logger.info("Setting up Gmail extractor")
        try:
            creds = self.authenticator.authenticate()
            if not creds:
                logger.error("Failed to authenticate with Gmail")
                return False

            self.fetcher = GmailFetcher(creds)
            logger.info("Gmail extractor setup complete")
            return True

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False

    def extract_exercises(self, label_name: str = "exercises", max_results: int = 100) -> List[EmailData]:
        """
        Extract exercise emails from Gmail.

        Args:
            label_name: Name of the Gmail label containing exercises (default: 'exercises')
            max_results: Maximum number of emails to fetch (default: 100)

        Returns:
            List of EmailData objects from the exercises folder
        """
        logger.info(f"Extracting exercise emails from '{label_name}' label")

        if not self.fetcher:
            logger.error("Gmail extractor not initialized. Call setup() first.")
            return []

        try:
            emails = self.fetcher.fetch_emails_from_label(label_name, max_results)
            logger.info(f"Extracted {len(emails)} exercise emails")
            return emails

        except Exception as e:
            logger.error(f"Failed to extract exercises: {e}")
            return []
