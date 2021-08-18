import ssl
from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from smtplib import SMTPConnectError, SMTPAuthenticationError
from typing import List
from .models import SMTPServer


def _do_send_email(server: SMTPServer, email: str):
    # instantiate smtp based on port
    if server.port == 25:
        smtp = SMTP(host=server.host, port=server.port)
    else:
        ssl_context = ssl.create_default_context()
        smtp = SMTP_SSL(host=server.host, port=server.port, context=ssl_context)
        if server.port == 587:
            smtp.starttls(context=ssl_context)

    try:
        # create message payload
        message = MIMEMultipart('alternative')
        message["Subject"] = "multipart test"
        message["From"] = "%s <%s>" % (server.from_name, server.from_email)
        message["To"] = email

        payload = "<html><body>%s</body></html>" % server.template

        message.attach(payload=MIMEText(payload))

        # login to smtp and sendmail
        smtp.login(server.username, server.password)
        smtp.sendmail(from_addr=message["From"], to_addrs=message["To"], msg=message.as_string())
    except (SMTPConnectError, SMTPAuthenticationError):
        pass
    finally:
        smtp.quit()
    pass


def send_email(email, event):
    # fetch server_configs for
    server_configs: List[SMTPServer] = SMTPServer.objects.filter(event=event).all()

    # create executor context
    pool = ThreadPoolExecutor(max_workers=3)
    fut = []

    # submit sendmail jobs
    for server_config in server_configs:
        fut.append(pool.submit(_do_send_email, server_config, email))

    # wait for completion
    wait(fut, return_when=ALL_COMPLETED)
    pass
