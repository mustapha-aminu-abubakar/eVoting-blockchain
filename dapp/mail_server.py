import smtplib

from .credentials import PASSWORD, SENDER_EMAIL


class MailServer:
    _port = 587  # For starttls
    _smtp_server = "smtp.gmail.com"

    _otp_message = """\
Subject: eVoting System - Your OTP

Your one time password: """

    _vote_confirmation_message = """\
Subject: Vote Confirmation - eVoting System

Dear Voter,

This email confirms that your vote has been successfully recorded in the blockchain.

Vote Details:
{details}

Thank you for participating in the election.

Best regards,
eVoting System"""

    def send_mail(self, receiver_email, OTP):
        """
        Sends an email containing a one-time password (OTP) to the specified receiver.

        Args:
            receiver_email (str): The recipient's email address.
            OTP (str): The one-time password to be sent.

        Returns:
            dict: The result of the sendmail operation from smtplib.
        """
        receiver_otp = self._otp_message + OTP

        with smtplib.SMTP(self._smtp_server, self._port) as server:
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, PASSWORD)
            ask = server.sendmail(SENDER_EMAIL, receiver_email, receiver_otp)
            server.quit()

            return ask

    def send_vote_confirmation(self, receiver_email, vote_details):
        """
        Sends a confirmation email for a submitted vote.

        Args:
            receiver_email (str): The voter's email address.
            vote_details (list): List of dictionaries containing position and candidate details.

        Returns:
            dict: The result of the sendmail operation from smtplib.
        """
        # Format vote details
        details_text = "\n".join([
            f"Position: {detail['position']}\n"
            f"Selected Candidate: {detail['candidate']}\n"
            for detail in vote_details
        ])
        
        message = self._vote_confirmation_message.format(details=details_text)

        with smtplib.SMTP(self._smtp_server, self._port) as server:
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, PASSWORD)
            result = server.sendmail(SENDER_EMAIL, receiver_email, message)
            server.quit()

            return result
