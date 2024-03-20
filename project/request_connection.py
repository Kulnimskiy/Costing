import ssl
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from project.credentials import PASSWORD, PROJECT_EMAIL, WORKER_EMAIL
from project.file_manager import read_file


def send_connect_request(current_user, competitor) -> bool:
    """ Send a message to the responsible admin to start working on the given scraper """
    context = ssl.create_default_context()  # Create a secure SSL context
    port = 465  # For SSL
    try:
        with smtplib.SMTP_SSL("smtp.mail.ru", port, context=context) as server:
            server.login(PROJECT_EMAIL, PASSWORD)
            receiver_email = WORKER_EMAIL
            sender_email = PROJECT_EMAIL
            message = MIMEMultipart("alternative")

            # set the title for the message
            message["Subject"] = f"Connection Request from {current_user.company_name}"
            message["From"] = sender_email
            message["To"] = receiver_email

            # get the email template and replace the placeholders
            text = read_file("./project/request_email_template.txt")
            text = text.replace("USER_ID", str(current_user.get_id()))
            text = text.replace("USER_INN", str(current_user.company_inn))
            text = text.replace("USER_NAME", current_user.company_name)
            text = text.replace("COMPETITOR_INN", str(competitor.competitor_inn))
            text = text.replace("COMPETITOR_NICKNAME", competitor.competitor_nickname)
            text = text.replace("COMPETITOR_WEBSITE", competitor.competitor_website)
            part = MIMEText(text, "plain")
            message.attach(part)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except smtplib.SMTPDataError as error:
        logging.warning(f"ERROR SENDING CONNECTION REQUEST: {error}")
