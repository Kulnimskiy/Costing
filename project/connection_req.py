import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .credentials import password, project_email


def send_connect_request(current_user, competitor):
    # Create a secure SSL context
    context = ssl.create_default_context()
    worker_email = "sergeish2012@yandex.ru"
    port = 465  # For SSL

    with smtplib.SMTP_SSL("smtp.mail.ru", port, context=context) as server:
        server.login(project_email, password)
        receiver_email = worker_email
        sender_email = project_email
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Connection Request from {current_user.company_name}"
        message["From"] = sender_email
        message["To"] = receiver_email
        text = f"""
Hi! This is {current_user.company_name}. Inn: {current_user.company_inn}

We would really like you to connect this organisation to our account
Org: {competitor.competitor_nickname} 
Web: {competitor.competitor_website}
Inn: {competitor.competitor_inn}

Thank, you!!!!
"""
        part = MIMEText(text, "plain")
        message.attach(part)
        server.sendmail(sender_email, receiver_email, message.as_string())
