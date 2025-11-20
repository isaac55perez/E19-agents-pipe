"""
Email composition and formatting.

This module generates professional email content from entry data:
- HTML and plain text versions
- Subject line generation
- Professional formatting
"""

import logging
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class EmailComposer:
    """Generate professional email content from entry data."""

    @staticmethod
    def extract_repo_name(repo_url: str) -> str:
        """
        Extract repository name from GitHub URL.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Repository name (e.g., "E18_logistic_regression")
        """
        try:
            # Handle URLs like https://github.com/user/repo.git or https://github.com/user/repo
            path = urlparse(repo_url).path
            # Remove leading/trailing slashes and .git suffix
            repo_name = path.strip("/").split("/")[-1].replace(".git", "")
            return repo_name if repo_name else "Repository"
        except Exception:
            logger.warning(f"Could not extract repo name from {repo_url}")
            return "Repository"

    @staticmethod
    def generate_subject(name: str, repo_url: str) -> str:
        """
        Generate email subject line.

        Args:
            name: Student name
            repo_url: Repository URL

        Returns:
            Subject line for email
        """
        repo_name = EmailComposer.extract_repo_name(repo_url)
        subject = f"Code Review: {repo_name}"
        logger.debug(f"Generated subject: {subject}")
        return subject

    @staticmethod
    def generate_html_body(entry: Dict) -> str:
        """
        Generate HTML email body.

        Args:
            entry: Dictionary with entry data including:
                - name: Student name (optional, falls back to Subject)
                - greeting: Personalized greeting message
                - Repo URL: Repository URL
                - grade: Code quality grade

        Returns:
            HTML-formatted email body
        """
        try:
            # Get name from 'name' field, or fall back to 'Subject'
            name = entry.get("name")
            if not name:
                subject = entry.get("Subject", "Student")
                name = subject if subject else "Student"

            greeting = entry.get("greeting", "")
            repo_url = entry.get("Repo URL", "")
            grade = entry.get("grade", "N/A")
            repo_name = EmailComposer.extract_repo_name(repo_url)

            # Format grade as percentage with 2 decimals
            try:
                grade_float = float(grade)
                grade_str = f"{grade_float:.2f}%"
            except (ValueError, TypeError):
                grade_str = str(grade)

            # Create HTML email
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto;">
                        <!-- Header -->
                        <div style="border-bottom: 2px solid #4472C4; padding-bottom: 10px; margin-bottom: 20px;">
                            <h2 style="color: #4472C4; margin: 0;">Code Submission Feedback</h2>
                        </div>

                        <!-- Greeting Section -->
                        <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #4472C4; margin-bottom: 20px;">
                            <p style="font-size: 16px; font-weight: bold; margin-top: 0;">Dear {name},</p>
                            <p style="font-size: 15px; line-height: 1.8; margin-bottom: 0;">
                                {greeting}
                            </p>
                        </div>

                        <!-- Details Section -->
                        <div style="background-color: #ffffff; padding: 15px; border: 1px solid #e0e0e0; margin-bottom: 20px;">
                            <h3 style="color: #333; margin-top: 0;">Submission Details</h3>

                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #e0e0e0; font-weight: bold; width: 30%;">Repository:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">
                                        <a href="{repo_url}" style="color: #4472C4; text-decoration: none;">{repo_name}</a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #e0e0e0; font-weight: bold;">Grade:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{grade_str}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">URL:</td>
                                    <td style="padding: 8px; word-break: break-all; font-size: 12px;">
                                        <a href="{repo_url}" style="color: #4472C4; text-decoration: none;">{repo_url}</a>
                                    </td>
                                </tr>
                            </table>
                        </div>

                        <!-- Footer -->
                        <div style="border-top: 1px solid #e0e0e0; padding-top: 15px; color: #666; font-size: 12px;">
                            <p style="margin: 5px 0;">Best regards,<br/>Code Review Team</p>
                            <p style="margin: 5px 0; color: #999;">
                                This is an automated message from the Exercise Submission System
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
            logger.debug(f"Generated HTML body for {name}")
            return html.strip()

        except Exception as e:
            logger.error(f"Error generating HTML body: {e}")
            raise

    @staticmethod
    def generate_text_body(entry: Dict) -> str:
        """
        Generate plain text email body.

        Args:
            entry: Dictionary with entry data

        Returns:
            Plain text email body
        """
        try:
            # Get name from 'name' field, or fall back to 'Subject'
            name = entry.get("name")
            if not name:
                subject = entry.get("Subject", "Student")
                name = subject if subject else "Student"

            greeting = entry.get("greeting", "")
            repo_url = entry.get("Repo URL", "")
            grade = entry.get("grade", "N/A")
            repo_name = EmailComposer.extract_repo_name(repo_url)

            # Format grade
            try:
                grade_float = float(grade)
                grade_str = f"{grade_float:.2f}%"
            except (ValueError, TypeError):
                grade_str = str(grade)

            # Create plain text email
            text = f"""
Code Submission Feedback

Dear {name},

{greeting}

Submission Details:
-------------------
Repository: {repo_name}
Grade: {grade_str}
URL: {repo_url}

Best regards,
Code Review Team

This is an automated message from the Exercise Submission System
            """.strip()

            logger.debug(f"Generated text body for {name}")
            return text

        except Exception as e:
            logger.error(f"Error generating text body: {e}")
            raise

    @staticmethod
    def compose_email(entry: Dict) -> Tuple[str, str, str]:
        """
        Compose complete email from entry.

        Args:
            entry: Dictionary with entry data

        Returns:
            Tuple of (subject, html_body, text_body)
        """
        try:
            repo_url = entry.get("Repo URL", "")
            name = entry.get("name", "Student")

            subject = EmailComposer.generate_subject(name, repo_url)
            html_body = EmailComposer.generate_html_body(entry)
            text_body = EmailComposer.generate_text_body(entry)

            logger.info(f"Composed email for {name}")
            return subject, html_body, text_body

        except Exception as e:
            logger.error(f"Error composing email: {e}")
            raise
