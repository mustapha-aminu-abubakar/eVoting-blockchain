import smtplib

from .credentials import PASSWORD, SENDER_EMAIL


class MailServer:
    _port = 587  # For starttls
    _smtp_server = "smtp.gmail.com"

    _message = """\
Subject: eVoting System

Your one time password: """

    def send_mail(self, receiver_email, OTP):
        """
        Sends an email containing a one-time password (OTP) to the specified receiver.

        Args:
            receiver_email (str): The recipient's email address.
            OTP (str): The one-time password to be sent.

        Returns:
            dict: The result of the sendmail operation from smtplib.
        """
        receiver_otp = self._message + OTP

        with smtplib.SMTP(self._smtp_server, self._port) as server:
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, PASSWORD)
            ask = server.sendmail(SENDER_EMAIL, receiver_email, receiver_otp)
            server.quit()

            return ask
