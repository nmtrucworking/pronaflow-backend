"""
Email Service for sending transactional emails.
Handles verification, password reset, and notification emails.
"""
from typing import Optional, List
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails.
    Currently a stub implementation - should be integrated with an email provider
    (SendGrid, Mailgun, AWS SES, etc.)
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_address: str = "noreply@pronaflow.com"
    ):
        """
        Initialize email service.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_address: From address for emails
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_address = from_address
    
    def send_email_verification(self, to_email: str, verification_token: str) -> bool:
        """
        Send email verification link.
        
        Args:
            to_email: Recipient email
            verification_token: Verification token
            
        Returns:
            True if sent successfully
        """
        verification_link = f"https://pronaflow.com/verify-email?token={verification_token}"
        
        subject = "Verify Your PronaFlow Email"
        body = f"""
        Welcome to PronaFlow!
        
        Please verify your email by clicking the link below:
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you did not create this account, please ignore this email.
        """
        
        return self._send_email(to_email, subject, body)
    
    def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset link.
        
        Args:
            to_email: Recipient email
            reset_token: Reset token
            
        Returns:
            True if sent successfully
        """
        reset_link = f"https://pronaflow.com/reset-password?token={reset_token}"
        
        subject = "Reset Your PronaFlow Password"
        body = f"""
        Password Reset Request
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 15 minutes.
        
        If you did not request a password reset, please ignore this email.
        """
        
        return self._send_email(to_email, subject, body)
    
    def send_password_changed_notification(self, to_email: str) -> bool:
        """
        Send password changed notification.
        
        Args:
            to_email: Recipient email
            
        Returns:
            True if sent successfully
        """
        subject = "Your PronaFlow Password Has Been Changed"
        body = """
        Password Changed Notification
        
        Your password has been successfully changed.
        
        If you did not make this change, please contact support immediately.
        """
        
        return self._send_email(to_email, subject, body)

    def send_workspace_invitation(
        self,
        to_email: str,
        invitation_token: str,
        workspace_name: str,
        inviter_name: Optional[str] = None,
    ) -> bool:
        """
        Send workspace invitation email with magic link.

        Args:
            to_email: Recipient email
            invitation_token: Raw invitation token
            workspace_name: Workspace name
            inviter_name: Optional inviter name

        Returns:
            True if sent successfully
        """
        inviter_label = inviter_name or "A teammate"
        invite_link = (
            f"{settings.FRONTEND_BASE_URL}{settings.WORKSPACE_INVITE_PATH}"
            f"?token={invitation_token}"
        )

        subject = f"You're invited to join {workspace_name} on PronaFlow"
        body = f"""
        {inviter_label} invited you to join the workspace "{workspace_name}" on PronaFlow.

        Accept your invitation here:
        {invite_link}

        This link will expire in 48 hours.

        If you were not expecting this invitation, you can ignore this email.
        """

        return self._send_email(to_email, subject, body)
    
    def send_mfa_enabled_notification(self, to_email: str) -> bool:
        """
        Send MFA enabled notification.
        
        Args:
            to_email: Recipient email
            
        Returns:
            True if sent successfully
        """
        subject = "Two-Factor Authentication Enabled"
        body = """
        Two-Factor Authentication (2FA) Enabled
        
        2FA has been enabled on your PronaFlow account.
        You will now be required to enter a 2FA code when logging in.
        
        If you did not enable this, please contact support immediately.
        """
        
        return self._send_email(to_email, subject, body)
    
    def send_impossible_travel_alert(
        self,
        to_email: str,
        location_1: str,
        location_2: str,
        time_diff_minutes: int
    ) -> bool:
        """
        Send impossible travel detection alert.
        
        Args:
            to_email: Recipient email
            location_1: First login location
            location_2: Second login location
            time_diff_minutes: Time difference in minutes
            
        Returns:
            True if sent successfully
        """
        subject = "Security Alert: Unusual Login Activity Detected"
        body = f"""
        Security Alert: Impossible Travel Detected
        
        We detected two logins from your account in different locations:
        
        Location 1: {location_1}
        Location 2: {location_2}
        Time Difference: {time_diff_minutes} minutes
        
        This is physically impossible and may indicate your account has been compromised.
        
        Please verify this activity in your account settings:
        https://pronaflow.com/security
        
        If this was not you, please:
        1. Reset your password immediately
        2. Review active sessions
        3. Contact support
        """
        
        return self._send_email(to_email, subject, body)
    
    def send_brute_force_alert(self, to_email: str, ip_address: str) -> bool:
        """
        Send brute-force attack alert.
        
        Args:
            to_email: Recipient email
            ip_address: IP address of attack
            
        Returns:
            True if sent successfully
        """
        subject = "Security Alert: Multiple Failed Login Attempts"
        body = f"""
        Security Alert: Brute-Force Attack Detected
        
        We detected multiple failed login attempts on your account from IP: {ip_address}
        
        Your account has been temporarily locked for security purposes.
        You can try logging in again after 15 minutes.
        
        If this was not you, please:
        1. Reset your password immediately
        2. Review active sessions
        3. Enable two-factor authentication
        
        Account Security: https://pronaflow.com/security
        """
        
        return self._send_email(to_email, subject, body)
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """
        Internal method to send email.
        Currently logs the email - should be replaced with actual email provider integration.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            reply_to: Reply-to address
            attachments: List of attachments
            
        Returns:
            True if sent successfully
        """
        try:
            # TODO: Integrate with actual email provider (SendGrid, Mailgun, etc.)
            logger.info(f"Email sent to {to_email}: {subject}")
            logger.debug(f"Body: {body}")
            
            # For now, just log it
            # In production, replace with actual email provider
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
