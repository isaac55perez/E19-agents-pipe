"""
Unit tests for Gmail connector module.

Tests cover authentication, email fetching, parsing, and error handling.
"""

import sys
from pathlib import Path

# Add the agent1 directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import pytest
import pickle
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

from gmail_connector import (
    GmailAuthenticator,
    GmailFetcher,
    GmailExerciseExtractor
)
from extractor import EmailData


class TestGmailAuthenticator:
    """Tests for GmailAuthenticator class."""

    @pytest.fixture
    def authenticator(self):
        """Create authenticator instance with test files."""
        creds_file = "test_credentials.json"
        token_file = "test_token.pickle"
        return GmailAuthenticator(creds_file, token_file)

    def test_authenticator_initialization(self, authenticator):
        """Test authenticator initializes correctly."""
        assert authenticator.credentials_file == Path("test_credentials.json")
        assert authenticator.token_file == Path("test_token.pickle")

    @patch('gmail_connector.InstalledAppFlow.from_client_secrets_file')
    @patch('gmail_connector.Path.exists')
    def test_authenticate_no_token_new_flow(self, mock_exists, mock_flow, authenticator):
        """Test authentication with no existing token."""
        mock_exists.return_value = False
        mock_creds = Mock()
        mock_creds.valid = True
        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.return_value = mock_flow_instance

        with patch('builtins.open', create=True):
            result = authenticator.authenticate()

        assert result == mock_creds
        mock_flow.assert_called_once()

    @patch('gmail_connector.Path.exists')
    def test_authenticate_with_valid_token(self, mock_exists, authenticator):
        """Test authentication with existing valid token."""
        mock_creds = Mock()
        mock_creds.valid = True

        # Mock the file operations
        with patch('builtins.open', create=True):
            with patch('pickle.load', return_value=mock_creds):
                with patch('gmail_connector.Path.exists', return_value=True):
                    result = authenticator.authenticate()

        assert result is not None

    @patch('gmail_connector.Path.exists')
    def test_authenticate_refresh_expired_token(self, mock_exists, authenticator):
        """Test token refresh when token is expired."""
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "some_token"

        # Mock file and refresh operations
        with patch('builtins.open', create=True):
            with patch('pickle.load', return_value=mock_creds):
                with patch('gmail_connector.Path.exists', return_value=True):
                    with patch('gmail_connector.Request'):
                        result = authenticator.authenticate()

        # Token refresh should have been attempted
        assert mock_creds.refresh.called


class TestGmailFetcher:
    """Tests for GmailFetcher class."""

    @pytest.fixture
    def mock_credentials(self):
        """Create mock credentials."""
        return Mock()

    @pytest.fixture
    def fetcher(self, mock_credentials):
        """Create fetcher instance with mock credentials."""
        with patch('gmail_connector.discovery.build'):
            return GmailFetcher(mock_credentials)

    def test_fetcher_initialization(self, fetcher):
        """Test fetcher initializes correctly."""
        assert fetcher.credentials is not None
        assert fetcher.service is not None

    @patch('gmail_connector.discovery.build')
    def test_initialize_service_success(self, mock_build, mock_credentials):
        """Test successful Gmail service initialization."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        fetcher = GmailFetcher(mock_credentials)
        result = fetcher._initialize_service()

        assert result is True
        assert fetcher.service == mock_service

    @patch('gmail_connector.discovery.build')
    def test_initialize_service_failure(self, mock_build, mock_credentials):
        """Test Gmail service initialization failure."""
        mock_build.side_effect = Exception("Service error")

        with patch('gmail_connector.logger'):
            fetcher = GmailFetcher.__new__(GmailFetcher)
            fetcher.credentials = mock_credentials
            fetcher.service = None

            result = fetcher._initialize_service()

        assert result is False

    def test_get_label_id_found(self, fetcher):
        """Test getting label ID when label exists."""
        mock_response = {
            'labels': [
                {'id': '123', 'name': 'exercises'},
                {'id': '456', 'name': 'archives'}
            ]
        }

        fetcher.service.users().labels().list().execute.return_value = mock_response

        result = fetcher.get_label_id('exercises')
        assert result == '123'

    def test_get_label_id_not_found(self, fetcher):
        """Test getting label ID when label doesn't exist."""
        mock_response = {'labels': []}
        fetcher.service.users().labels().list().execute.return_value = mock_response

        result = fetcher.get_label_id('nonexistent')
        assert result is None

    def test_get_label_id_case_insensitive(self, fetcher):
        """Test label ID lookup is case-insensitive."""
        mock_response = {
            'labels': [
                {'id': '123', 'name': 'Exercises'}
            ]
        }

        fetcher.service.users().labels().list().execute.return_value = mock_response

        result = fetcher.get_label_id('EXERCISES')
        assert result == '123'

    def test_fetch_emails_from_label_success(self, fetcher):
        """Test successful email fetching from label."""
        fetcher.get_label_id = Mock(return_value='123')

        mock_messages = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'}
            ]
        }

        mock_msg1 = {
            'payload': {
                'headers': [
                    {'name': 'Date', 'value': 'Mon, 15 Nov 2021 10:30:00 +0000'},
                    {'name': 'Subject', 'value': 'Exercise 1'}
                ],
                'body': {'data': ''}
            }
        }

        mock_msg2 = {
            'payload': {
                'headers': [
                    {'name': 'Date', 'value': 'Tue, 16 Nov 2021 11:00:00 +0000'},
                    {'name': 'Subject', 'value': 'Exercise 2'}
                ],
                'body': {'data': ''}
            }
        }

        # Setup proper mock chaining
        mock_list_result = Mock()
        mock_list_result.execute.return_value = mock_messages
        mock_messages_api = Mock()
        mock_messages_api.list.return_value = mock_list_result

        mock_get_result_1 = Mock()
        mock_get_result_1.execute.return_value = mock_msg1
        mock_get_result_2 = Mock()
        mock_get_result_2.execute.return_value = mock_msg2
        mock_messages_api.get.side_effect = [mock_get_result_1, mock_get_result_2]

        mock_users_api = Mock()
        mock_users_api.messages.return_value = mock_messages_api
        fetcher.service.users.return_value = mock_users_api

        results = fetcher.fetch_emails_from_label('exercises', max_results=10)

        assert len(results) == 2
        assert all(isinstance(r, EmailData) for r in results)

    def test_fetch_emails_label_not_found(self, fetcher):
        """Test email fetching when label is not found."""
        fetcher.get_label_id = Mock(return_value=None)

        results = fetcher.fetch_emails_from_label('exercises')

        assert results == []

    def test_fetch_emails_no_messages(self, fetcher):
        """Test email fetching when label has no messages."""
        fetcher.get_label_id = Mock(return_value='123')

        mock_response = {'messages': []}
        fetcher.service.users().messages().list().execute.return_value = mock_response

        results = fetcher.fetch_emails_from_label('exercises')

        assert results == []

    def test_get_header_value_found(self):
        """Test extracting header value when present."""
        headers = [
            {'name': 'From', 'value': 'sender@example.com'},
            {'name': 'Subject', 'value': 'Test Subject'},
            {'name': 'Date', 'value': '2021-11-15'}
        ]

        result = GmailFetcher._get_header_value(headers, 'Subject')
        assert result == 'Test Subject'

    def test_get_header_value_not_found(self):
        """Test extracting header value when not present."""
        headers = [
            {'name': 'From', 'value': 'sender@example.com'}
        ]

        result = GmailFetcher._get_header_value(headers, 'Subject')
        assert result is None

    def test_get_header_value_case_insensitive(self):
        """Test header lookup is case-insensitive."""
        headers = [
            {'name': 'Subject', 'value': 'Test Subject'}
        ]

        result = GmailFetcher._get_header_value(headers, 'subject')
        assert result == 'Test Subject'

    def test_get_message_body_simple(self):
        """Test extracting body from simple message."""
        import base64

        body_text = "This is the email body"
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        payload = {
            'body': {
                'size': 22,
                'data': encoded_body
            }
        }

        result = GmailFetcher._get_message_body(payload)
        assert result == body_text

    def test_get_message_body_multipart_plain(self):
        """Test extracting plain text from multipart message."""
        import base64

        body_text = "This is the plain text body"
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        payload = {
            'body': {'size': 0, 'data': ''},
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {
                        'size': len(body_text),
                        'data': encoded_body
                    }
                }
            ]
        }

        result = GmailFetcher._get_message_body(payload)
        assert result == body_text

    def test_get_message_body_empty(self):
        """Test extracting body when message is empty."""
        payload = {
            'body': {'size': 0, 'data': ''}
        }

        result = GmailFetcher._get_message_body(payload)
        assert result is None

    def test_parse_message_success(self, fetcher):
        """Test successful message parsing."""
        import base64

        body_text = "Check out https://github.com/user/repo"
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        message = {
            'payload': {
                'headers': [
                    {'name': 'Date', 'value': 'Mon, 15 Nov 2021 10:30:00 +0000'},
                    {'name': 'Subject', 'value': 'Exercise 1'}
                ],
                'body': {
                    'size': len(body_text),
                    'data': encoded_body
                }
            }
        }

        result = fetcher._parse_message(message)

        assert isinstance(result, EmailData)
        assert result.subject == 'Exercise 1'
        assert 'github.com' in result.body

    def test_parse_message_missing_subject(self, fetcher):
        """Test parsing message without subject."""
        message = {
            'payload': {
                'headers': [
                    {'name': 'Date', 'value': 'Mon, 15 Nov 2021 10:30:00 +0000'}
                ],
                'body': {'size': 0, 'data': ''}
            }
        }

        result = fetcher._parse_message(message)

        assert isinstance(result, EmailData)
        assert result.subject == "(No Subject)"

    def test_parse_message_error(self, fetcher):
        """Test parsing message with error."""
        fetcher.service = None
        message = None

        result = fetcher._parse_message(message)
        assert result is None


class TestGmailExerciseExtractor:
    """Tests for GmailExerciseExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        with patch('gmail_connector.GmailAuthenticator'):
            return GmailExerciseExtractor()

    def test_extractor_initialization(self, extractor):
        """Test extractor initializes correctly."""
        assert extractor.credentials_file == "credentials.json"
        assert extractor.authenticator is not None
        assert extractor.fetcher is None

    @patch('gmail_connector.GmailAuthenticator')
    @patch('gmail_connector.GmailFetcher')
    def test_setup_success(self, mock_fetcher_class, mock_auth_class, extractor):
        """Test successful setup."""
        mock_creds = Mock()
        extractor.authenticator.authenticate.return_value = mock_creds
        mock_fetcher_instance = Mock()
        mock_fetcher_class.return_value = mock_fetcher_instance

        result = extractor.setup()

        assert result is True
        assert extractor.fetcher == mock_fetcher_instance

    @patch('gmail_connector.GmailAuthenticator')
    def test_setup_auth_failure(self, mock_auth_class, extractor):
        """Test setup with authentication failure."""
        extractor.authenticator.authenticate.return_value = None

        result = extractor.setup()

        assert result is False

    @patch('gmail_connector.GmailAuthenticator')
    def test_extract_exercises_not_initialized(self, mock_auth_class, extractor):
        """Test extract before setup."""
        extractor.fetcher = None

        result = extractor.extract_exercises()

        assert result == []

    @patch('gmail_connector.GmailAuthenticator')
    @patch('gmail_connector.GmailFetcher')
    def test_extract_exercises_success(self, mock_fetcher_class, mock_auth_class, extractor):
        """Test successful exercise extraction."""
        mock_fetcher = Mock()
        extractor.fetcher = mock_fetcher

        mock_emails = [
            EmailData(date='2021-11-15', subject='Exercise 1', body='https://github.com/user1/repo1'),
            EmailData(date='2021-11-16', subject='Exercise 2', body='https://github.com/user2/repo2')
        ]
        mock_fetcher.fetch_emails_from_label.return_value = mock_emails

        result = extractor.extract_exercises(label_name='exercises', max_results=100)

        assert len(result) == 2
        assert all(isinstance(e, EmailData) for e in result)
        mock_fetcher.fetch_emails_from_label.assert_called_once_with('exercises', 100)

    @patch('gmail_connector.GmailAuthenticator')
    def test_extract_exercises_error(self, mock_auth_class, extractor):
        """Test exercise extraction with error."""
        extractor.fetcher = Mock()
        extractor.fetcher.fetch_emails_from_label.side_effect = Exception("API error")

        result = extractor.extract_exercises()

        assert result == []


class TestGmailIntegration:
    """Integration tests for Gmail components."""

    @patch('gmail_connector.GmailAuthenticator')
    @patch('gmail_connector.GmailFetcher')
    def test_full_workflow_mock(self, mock_fetcher_class, mock_auth_class):
        """Test full workflow with mocked Gmail API."""
        # Setup authenticator
        mock_creds = Mock()
        mock_auth = Mock()
        mock_auth.authenticate.return_value = mock_creds
        mock_auth_class.return_value = mock_auth

        # Setup fetcher
        mock_emails = [
            EmailData(
                date='Mon, 15 Nov 2021 10:30:00 +0000',
                subject='Exercise 1',
                body='Solution: https://github.com/student/exercise1'
            )
        ]
        mock_fetcher = Mock()
        mock_fetcher.fetch_emails_from_label.return_value = mock_emails
        mock_fetcher_class.return_value = mock_fetcher

        # Run extraction
        extractor = GmailExerciseExtractor()
        assert extractor.setup() is True

        emails = extractor.extract_exercises()
        assert len(emails) == 1
        assert emails[0].subject == 'Exercise 1'
        assert 'github.com' in emails[0].body
