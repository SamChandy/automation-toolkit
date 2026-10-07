"""Scheduled Emailer: sends an email automatically at a set time every day.

Setup:
    1. Copy .env.example to .env and fill in your details.
    2. For Gmail, create an App Password (needs 2-Step Verification on).

Usage:
    python email_scheduler.py --now             # send one test email right away
    python email_scheduler.py --time 09:00      # send every day at 9:00 AM
"""
import argparse
import os
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import schedule

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # fall back to normal environment variables


def build_message(sender, recipient, subject, body, attachment=None) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment:
        path = Path(attachment)
        msg.add_attachment(
            path.read_bytes(),
            maintype="application",
            subtype="octet-stream",
            filename=path.name,
        )
    return msg


def send_email(attachment=None):
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_PASSWORD"]
    recipient = os.environ.get("EMAIL_TO", sender)
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))

    today = datetime.now().strftime("%A, %d %B %Y")
    subject = f"Daily Report - {today}"
    body = f"Hello,\n\nThis is your automated message for {today}.\n\nSent by Automation Toolkit."

    msg = build_message(sender, recipient, subject, body, attachment)
    try:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"[{datetime.now():%H:%M:%S}] Email sent to {recipient}")
    except Exception as exc:  # keep the scheduler alive if one send fails
        print(f"[{datetime.now():%H:%M:%S}] Failed to send email: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Send a scheduled daily email.")
    parser.add_argument("--time", default="09:00", help="Daily send time, 24h HH:MM")
    parser.add_argument("--attach", help="Optional file to attach")
    parser.add_argument("--now", action="store_true", help="Send once immediately and exit")
    args = parser.parse_args()

    if args.now:
        send_email(args.attach)
        return

    schedule.every().day.at(args.time).do(send_email, args.attach)
    print(f"Scheduler running. Email will be sent daily at {args.time}. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
