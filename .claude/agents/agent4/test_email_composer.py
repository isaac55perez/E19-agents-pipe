"""
Unit tests for email_composer module.
"""

import pytest
from email_composer import EmailComposer


class TestExtractRepoName:
    """Tests for extract_repo_name method."""

    def test_extract_repo_name_https(self):
        """Test extracting repo name from HTTPS URL."""
        url = "https://github.com/user/E18_logistic_regression"
        assert EmailComposer.extract_repo_name(url) == "E18_logistic_regression"

    def test_extract_repo_name_https_with_git_suffix(self):
        """Test extracting repo name from HTTPS URL with .git suffix."""
        url = "https://github.com/user/E18_logistic_regression.git"
        assert EmailComposer.extract_repo_name(url) == "E18_logistic_regression"

    def test_extract_repo_name_http(self):
        """Test extracting repo name from HTTP URL."""
        url = "http://github.com/user/my-repo"
        assert EmailComposer.extract_repo_name(url) == "my-repo"

    def test_extract_repo_name_with_trailing_slash(self):
        """Test extracting repo name from URL with trailing slash."""
        url = "https://github.com/user/repo/"
        assert EmailComposer.extract_repo_name(url) == "repo"

    def test_extract_repo_name_invalid_url(self):
        """Test extracting repo name from invalid URL still parses last segment."""
        url = "not_a_url"
        # The function extracts the last path segment, so "not_a_url" returns "not_a_url"
        assert EmailComposer.extract_repo_name(url) == "not_a_url"

    def test_extract_repo_name_empty_string(self):
        """Test extracting repo name from empty string."""
        url = ""
        assert EmailComposer.extract_repo_name(url) == "Repository"

    def test_extract_repo_name_complex_path(self):
        """Test extracting repo name from complex GitHub path."""
        url = "https://github.com/organization/project-name-123.git"
        assert EmailComposer.extract_repo_name(url) == "project-name-123"


class TestGenerateSubject:
    """Tests for generate_subject method."""

    def test_generate_subject_basic(self):
        """Test generating subject line."""
        subject = EmailComposer.generate_subject("Alice", "https://github.com/user/E18_test")
        assert subject == "Code Review: E18_test"

    def test_generate_subject_with_numbers(self):
        """Test subject generation with numbered repo."""
        subject = EmailComposer.generate_subject("Bob", "https://github.com/user/E42_advanced_ml")
        assert subject == "Code Review: E42_advanced_ml"

    def test_generate_subject_includes_code_review(self):
        """Test that subject includes 'Code Review' prefix."""
        subject = EmailComposer.generate_subject("Charlie", "https://github.com/user/my_project")
        assert "Code Review:" in subject

    def test_generate_subject_different_names(self):
        """Test subject is same regardless of student name."""
        url = "https://github.com/user/project"
        subject1 = EmailComposer.generate_subject("Alice", url)
        subject2 = EmailComposer.generate_subject("Bob", url)
        assert subject1 == subject2


class TestGenerateHtmlBody:
    """Tests for generate_html_body method."""

    def test_generate_html_body_basic(self):
        """Test generating HTML email body."""
        entry = {
            "name": "Alice",
            "greeting": "Great work!",
            "Repo URL": "https://github.com/user/E18_test",
            "grade": "85.50"
        }
        html = EmailComposer.generate_html_body(entry)

        assert "<html>" in html
        assert "Alice" in html
        assert "Great work!" in html
        assert "E18_test" in html
        assert "85.50%" in html

    def test_generate_html_body_includes_repo_url(self):
        """Test that HTML includes clickable repository link."""
        entry = {
            "name": "Bob",
            "greeting": "Excellent code!",
            "Repo URL": "https://github.com/user/E19_project",
            "grade": "92"
        }
        html = EmailComposer.generate_html_body(entry)

        assert "https://github.com/user/E19_project" in html
        assert "<a href=" in html

    def test_generate_html_body_format_grade(self):
        """Test that grade is formatted with 2 decimal places."""
        entry = {
            "name": "Charlie",
            "greeting": "Good work",
            "Repo URL": "https://github.com/user/test",
            "grade": 75
        }
        html = EmailComposer.generate_html_body(entry)

        assert "75.00%" in html

    def test_generate_html_body_missing_grade(self):
        """Test HTML generation with missing grade."""
        entry = {
            "name": "David",
            "greeting": "Nice effort",
            "Repo URL": "https://github.com/user/test",
            "grade": None
        }
        html = EmailComposer.generate_html_body(entry)

        # With None grade, it returns "None" string representation
        assert "None" in html or "N/A" in html
        assert "David" in html

    def test_generate_html_body_includes_header(self):
        """Test that HTML includes proper header."""
        entry = {
            "name": "Eve",
            "greeting": "Great submission!",
            "Repo URL": "https://github.com/user/test",
            "grade": "88"
        }
        html = EmailComposer.generate_html_body(entry)

        assert "Code Submission Feedback" in html
        assert "font-family: Arial" in html

    def test_generate_html_body_default_name(self):
        """Test HTML generation with missing name."""
        entry = {
            "greeting": "Well done!",
            "Repo URL": "https://github.com/user/test",
            "grade": "80"
        }
        html = EmailComposer.generate_html_body(entry)

        assert "Student" in html or "Dear" in html

    def test_generate_html_body_long_greeting(self):
        """Test HTML generation with long greeting message."""
        long_greeting = "This is a very long greeting message that contains multiple sentences. " * 5
        entry = {
            "name": "Frank",
            "greeting": long_greeting,
            "Repo URL": "https://github.com/user/test",
            "grade": "70"
        }
        html = EmailComposer.generate_html_body(entry)

        assert long_greeting in html


class TestGenerateTextBody:
    """Tests for generate_text_body method."""

    def test_generate_text_body_basic(self):
        """Test generating plain text email body."""
        entry = {
            "name": "Alice",
            "greeting": "Great work!",
            "Repo URL": "https://github.com/user/E18_test",
            "grade": "85.50"
        }
        text = EmailComposer.generate_text_body(entry)

        assert "Alice" in text
        assert "Great work!" in text
        assert "E18_test" in text
        assert "85.50%" in text

    def test_generate_text_body_includes_repo_url(self):
        """Test that text body includes repository URL."""
        entry = {
            "name": "Bob",
            "greeting": "Good job!",
            "Repo URL": "https://github.com/user/project",
            "grade": "90"
        }
        text = EmailComposer.generate_text_body(entry)

        assert "https://github.com/user/project" in text

    def test_generate_text_body_no_html_tags(self):
        """Test that plain text body has no HTML tags."""
        entry = {
            "name": "Charlie",
            "greeting": "Nice work",
            "Repo URL": "https://github.com/user/test",
            "grade": "75"
        }
        text = EmailComposer.generate_text_body(entry)

        assert "<" not in text
        assert ">" not in text

    def test_generate_text_body_includes_structure(self):
        """Test that text body has proper structure."""
        entry = {
            "name": "David",
            "greeting": "Excellent!",
            "Repo URL": "https://github.com/user/test",
            "grade": "95"
        }
        text = EmailComposer.generate_text_body(entry)

        assert "Code Submission Feedback" in text
        assert "Submission Details:" in text
        assert "Best regards," in text

    def test_generate_text_body_format_grade(self):
        """Test that grade is formatted with 2 decimal places in text."""
        entry = {
            "name": "Eve",
            "greeting": "Good effort",
            "Repo URL": "https://github.com/user/test",
            "grade": 88.5
        }
        text = EmailComposer.generate_text_body(entry)

        assert "88.50%" in text


class TestComposeEmail:
    """Tests for compose_email method."""

    def test_compose_email_returns_tuple(self):
        """Test that compose_email returns a tuple."""
        entry = {
            "name": "Alice",
            "greeting": "Great work!",
            "Repo URL": "https://github.com/user/test",
            "grade": "85"
        }
        result = EmailComposer.compose_email(entry)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_compose_email_subject_html_text(self):
        """Test that compose_email returns (subject, html, text)."""
        entry = {
            "name": "Bob",
            "greeting": "Good job!",
            "Repo URL": "https://github.com/user/E19_test",
            "grade": "90"
        }
        subject, html, text = EmailComposer.compose_email(entry)

        assert isinstance(subject, str)
        assert isinstance(html, str)
        assert isinstance(text, str)
        assert "Code Review:" in subject
        assert "<html>" in html
        assert "<html>" not in text

    def test_compose_email_all_components(self):
        """Test that all components are present in composed email."""
        entry = {
            "name": "Charlie",
            "greeting": "Excellent submission!",
            "Repo URL": "https://github.com/user/project",
            "grade": "92.75"
        }
        subject, html, text = EmailComposer.compose_email(entry)

        # Check subject
        assert "Code Review:" in subject
        assert "project" in subject

        # Check HTML
        assert "Charlie" in html
        assert "Excellent submission!" in html
        assert "92.75%" in html

        # Check text
        assert "Charlie" in text
        assert "Excellent submission!" in text
        assert "92.75%" in text

    def test_compose_email_different_repos(self):
        """Test compose_email with different repository names."""
        repos = ["E18_ml", "E19_data", "E20_web"]

        for repo in repos:
            entry = {
                "name": "Test",
                "greeting": "Good!",
                "Repo URL": f"https://github.com/user/{repo}",
                "grade": "80"
            }
            subject, html, text = EmailComposer.compose_email(entry)

            assert repo in subject
            assert repo in html
            assert repo in text

    def test_compose_email_missing_optional_fields(self):
        """Test compose_email handles missing optional fields gracefully."""
        entry = {
            "name": "David",
            "greeting": "Nice work",
            "Repo URL": "https://github.com/user/test"
            # Missing grade
        }
        subject, html, text = EmailComposer.compose_email(entry)

        # Should still generate email with N/A for grade
        assert "David" in html
        assert subject is not None
        assert text is not None

    def test_compose_email_long_content(self):
        """Test compose_email with long greeting."""
        long_greeting = "This is an extensive greeting message that spans multiple lines " \
                       "and contains detailed feedback about the submission quality. " * 3
        entry = {
            "name": "Eve",
            "greeting": long_greeting,
            "Repo URL": "https://github.com/user/test",
            "grade": "85"
        }
        subject, html, text = EmailComposer.compose_email(entry)

        assert long_greeting in html
        assert long_greeting in text
