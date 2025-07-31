import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SMTP_SERVER_HOST = "localhost"
SMTP_SERVER_PORT = 1025
SENDER_ADDRESS = "test@donotreply.in"   # any fake sender works
SENDER_PASSWORD = ""  # not needed for MailHog

def send_email(to_address, subject, message, content="html", attachment_file=None):
    msg = MIMEMultipart()
    msg['From'] = SENDER_ADDRESS
    msg['To'] = to_address
    msg['Subject'] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    msg.attach(MIMEText(message, "html"))

    with smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT) as s:
        s.send_message(msg)

    print(f"✅ Email sent to {to_address}")
    return True
