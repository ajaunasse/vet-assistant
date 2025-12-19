"""Email service for sending verification and notification emails."""
import os
import base64
from pathlib import Path
from typing import Optional
import resend


class EmailService:
    """Service for sending emails via Resend."""

    def __init__(
        self,
        resend_api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        frontend_url: Optional[str] = None,
    ):
        """
        Initialize email service.

        Args:
            resend_api_key: Resend API key
            from_email: From email address
            frontend_url: Frontend URL for links in emails
        """
        self.resend_api_key = resend_api_key or os.getenv("RESEND_API_KEY")
        self.from_email = from_email or os.getenv("FROM_EMAIL", "onboarding@resend.dev")
        self.frontend_url = frontend_url or os.getenv("FRONTEND_URL", "http://localhost:3000")

        # Validate required settings
        if not self.resend_api_key:
            raise ValueError("RESEND_API_KEY must be set")

        # Set Resend API key
        resend.api_key = self.resend_api_key

    def _get_logo_base64(self) -> str:
        """Get logo as base64 encoded string for email embedding."""
        # Try to find the logo in the frontend public directory
        possible_paths = [
            Path(__file__).parent.parent.parent.parent.parent / "frontend" / "public" / "neuro-locus-logo.png",
            Path(__file__).parent / "logo" / "neuro-locus-logo.png",
        ]

        for logo_path in possible_paths:
            if logo_path.exists():
                try:
                    with open(logo_path, "rb") as f:
                        logo_data = f.read()
                    return f"data:image/png;base64,{base64.b64encode(logo_data).decode('utf-8')}"
                except Exception:
                    continue

        # Return empty string if logo not found
        return ""

    async def send_verification_email(
        self, email: str, verification_token: str, first_name: str
    ) -> bool:
        """
        Send email verification email.

        Args:
            email: Recipient email address
            verification_token: Verification token
            first_name: User's first name

        Returns:
            True if email was sent successfully, False otherwise
        """
        subject = "NeuroLocus - Vérifiez votre adresse email"
        verification_url = f"{self.frontend_url}/verify-email?token={verification_token}"

        # Read HTML template
        template_path = Path(__file__).parent / "templates" / "verification_email.html"
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Get logo as base64
            logo_base64 = self._get_logo_base64()

            html_content = html_content.replace("{{first_name}}", first_name)
            html_content = html_content.replace("{{verification_url}}", verification_url)
            html_content = html_content.replace("{{logo_url}}", logo_base64 if logo_base64 else f"{self.frontend_url}/neuro-locus-logo.png")
        else:
            # Fallback to simple HTML
            html_content = f"""
            <html>
                <body>
                    <h2>Bienvenue sur NeuroLocus, {first_name}!</h2>
                    <p>Merci de vous être inscrit. Veuillez cliquer sur le lien ci-dessous pour vérifier votre adresse email:</p>
                    <p><a href="{verification_url}">Vérifier mon email</a></p>
                    <p>Ce lien expirera dans 7 jours.</p>
                    <p>Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.</p>
                    <br>
                    <p>L'équipe NeuroLocus</p>
                </body>
            </html>
            """

        return await self._send_email(email, subject, html_content)

    async def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """
        Send password reset email.

        Args:
            email: Recipient email address
            reset_token: Password reset token

        Returns:
            True if email was sent successfully, False otherwise
        """
        subject = "NeuroLocus - Réinitialisation de votre mot de passe"
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"

        html_content = f"""
        <html>
            <body>
                <h2>Réinitialisation de votre mot de passe</h2>
                <p>Vous avez demandé à réinitialiser votre mot de passe. Cliquez sur le lien ci-dessous pour continuer:</p>
                <p><a href="{reset_url}">Réinitialiser mon mot de passe</a></p>
                <p>Ce lien expirera dans 1 heure.</p>
                <p>Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.</p>
                <br>
                <p>L'équipe NeuroLocus</p>
            </body>
        </html>
        """

        return await self._send_email(email, subject, html_content)

    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send an email via Resend.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            params = {
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": html_content,
            }

            resend.Emails.send(params)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send email to {to_email}: {str(e)}")
            return False
