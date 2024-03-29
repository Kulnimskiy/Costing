import ssl
import smtplib
import logging
from typing import Union
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
from project.file_manager import read_file
from project.credentials import PROJECT_EMAIL_PASSWORD, PROJECT_EMAIL, WORKER_EMAIL
from project.interfaces import Manager, Messanger


class EmailManager(Manager, Messanger):
    SENDER = PROJECT_EMAIL
    SENDER_PASSWORD = PROJECT_EMAIL_PASSWORD

    def __init__(self, email: str):
        self.email = email

    def check(self) -> Union[str, None]:
        """ Checks if the email is valid and returns its value"""
        try:
            v = validate_email(self.email)
            valid_email = v.__dict__["normalized"]
            return valid_email
        except EmailNotValidError as error:
            logging.warning(error)
            return None

    def message(self, text: str, subject: str = "Messager") -> bool:
        """ Sends messages to the email of the class """
        context = ssl.create_default_context()  # Create a secure SSL context
        port = 465  # For SSL
        receiver = self.check()

        if not receiver:
            logging.warning(f"ERROR: THE RECEIVER EMAIL {self.email} ISN'T VALID")
            return False

        try:
            with smtplib.SMTP_SSL("smtp.mail.ru", port, context=context) as server:
                server.login(self.SENDER, self.SENDER_PASSWORD)
                message = MIMEMultipart("alternative")

                # Set the title for the message
                message["Subject"] = subject
                message["From"] = self.SENDER
                message["To"] = receiver

                part = MIMEText(text, "plain")
                message.attach(part)
                server.sendmail(self.SENDER, receiver, message.as_string())
                return True
        except smtplib.SMTPDataError as error:
            logging.warning(f"ERROR SENDING EMAIL TO {receiver}: {error}")
            return False


class EmailTemplates:

    @staticmethod
    def request_connect(current_user, competitor) -> bool:
        """ Send a message to the responsible admin to start working on the given scraper """
        template_path = "./project/request_connect_template.txt"
        subject = f"Connection Request from {current_user.company_name}"

        # replace the placeholders in the email
        text = read_file(template_path)
        text = text.format(USER_ID=current_user.get_id(),
                           USER_INN=current_user.company_inn,
                           USER_NAME=current_user.company_name,
                           COMPETITOR_INN=competitor.competitor_inn,
                           COMPETITOR_NICKNAME=competitor.competitor_nickname,
                           COMPETITOR_WEBSITE=competitor.competitor_website)

        success = EmailManager(WORKER_EMAIL).message(text=text, subject=subject)
        return success
