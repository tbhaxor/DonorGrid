import ssl
from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from smtplib import SMTPConnectError, SMTPAuthenticationError
from typing import List
from Donation.models import Donation
from Donor.models import Donor
from Package.models import Package
import requests as r
from .models import SMTPServer, Automation


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

    # shutdown pool
    pool.shutdown()
    pass


def _do_send_webhook_event_on_donor_create(webhook_url: str, donor_details: Donor):
    try:
        r.post(webhook_url, json={
                    'first_name': donor_details.first_name,
                    'last_name': donor_details.last_name,
                    'email': donor_details.last_name,
                    'phone_number': donor_details.phone_number,
                    'is_anonymous': donor_details.is_anonymous,
                    'full_name': donor_details.full_name,
                })
    except Exception:
        pass
    pass


def _do_send_webhook_event_on_payment_success(webhook_url: str, donor_email: Donor, package_name: str, donation_details: Donation):
    try:
        r.post(webhook_url, json={
                    'donor_email': donor_email,
                    'amount': donation_details.amount,
                    'package_name': package_name,
                    'currency': donation_details.currency,
                    'transaction_id': donation_details.txn_id,
                    'on_behalf_of': donation_details.on_behalf_of,
                    'custom_data': donation_details.custom_data,
                    'payment_provider': donation_details.provider
                })
    except Exception:
        pass
    pass


def _do_send_webhook_event_on_payment_fail(webhook_url: str, donor_email: str, package_name: str, donation_details: Donation, fail_reason):
    try:
        r.post(webhook_url, json={
                    'donor_email': donor_email,
                    'amount': donation_details.amount,
                    'package_name': package_name,
                    'currency': donation_details.currency,
                    'transaction_id': donation_details.txn_id,
                    'fail_reason': fail_reason,
                    'on_behalf_of': donation_details.on_behalf_of,
                    'custom_data': donation_details.custom_data,
                    'payment_provider': donation_details.provider
                })
    except Exception:
        pass
    pass


def send_webhook_event(event, package: Package = None, donation: Donation = None, donor: Donor = None, fail_reason: str = None):
    # fetch automation config based on event
    automations: List[Automation] = Automation.objects.filter(event=event).all()

    # create pool
    futures = []
    pool = ThreadPoolExecutor(max_workers=3)

    for automation in automations:
        if automation.event == Automation.EventChoice.ON_DONOR_CREATE:
            futures.append(pool.submit(_do_send_webhook_event_on_donor_create, automation.webhook_url, donor))
        elif automation.event == Automation.EventChoice.ON_PAYMENT_SUCCESS:
            futures.append(pool.submit(_do_send_webhook_event_on_payment_success, automation.webhook_url, donor.email, package.name, donation))
        else:
            futures.append(pool.submit(_do_send_webhook_event_on_payment_fail, automation.webhook_url, donor.email, package.name, donation, fail_reason))
        pass

    # wait for futures to finish
    wait(futures, return_when=ALL_COMPLETED)

    # shutdown pool
    pool.shutdown()
    pass
