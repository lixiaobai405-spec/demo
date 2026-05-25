from __future__ import annotations

import argparse
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings


def mask(value: str) -> str:
    if not value:
        return "<empty>"
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}***{value[-2:]}"


def collect_config_errors() -> list[str]:
    errors: list[str] = []
    if not settings.smtp_enabled:
        errors.append("SMTP_ENABLED is false")
    if not settings.smtp_host:
        errors.append("SMTP_HOST is empty")
    if not settings.smtp_from_email:
        errors.append("SMTP_FROM_EMAIL is empty")
    if settings.smtp_username and not settings.smtp_password:
        errors.append("SMTP_PASSWORD is empty while SMTP_USERNAME is set")
    if settings.smtp_password and not settings.smtp_username:
        errors.append("SMTP_USERNAME is empty while SMTP_PASSWORD is set")
    if settings.smtp_use_ssl and settings.smtp_use_tls:
        errors.append("SMTP_USE_SSL and SMTP_USE_TLS cannot both be true")
    return errors


def build_test_message(recipient: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = "SMTP connectivity test"
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message.set_content(
        "\n".join(
            [
                "This is a test email from the local SMTP checker.",
                "",
                f"Host: {settings.smtp_host}",
                f"Port: {settings.smtp_port}",
            ]
        )
    )
    return message


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SMTP connectivity for password reset email.",
    )
    parser.add_argument(
        "--send-to",
        help="Optional recipient email for a live send test. Without this flag, only connect/auth is tested.",
    )
    args = parser.parse_args()

    print("SMTP configuration summary")
    print(f"  enabled: {settings.smtp_enabled}")
    print(f"  host: {settings.smtp_host or '<empty>'}")
    print(f"  port: {settings.smtp_port}")
    print(f"  username: {mask(settings.smtp_username)}")
    print(f"  password set: {bool(settings.smtp_password)}")
    print(f"  from email: {settings.smtp_from_email or '<empty>'}")
    print(f"  use TLS: {settings.smtp_use_tls}")
    print(f"  use SSL: {settings.smtp_use_ssl}")

    errors = collect_config_errors()
    if errors:
        print("")
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    smtp_client = smtplib.SMTP_SSL if settings.smtp_use_ssl else smtplib.SMTP
    try:
        print("")
        print(f"Connecting to {settings.smtp_host}:{settings.smtp_port} ...")
        with smtp_client(settings.smtp_host, settings.smtp_port, timeout=30) as client:
            client.ehlo()
            if not settings.smtp_use_ssl and settings.smtp_use_tls:
                print("Starting TLS ...")
                client.starttls()
                client.ehlo()
            if settings.smtp_username:
                print(f"Logging in as {mask(settings.smtp_username)} ...")
                client.login(settings.smtp_username, settings.smtp_password)
            else:
                print("Skipping login because SMTP_USERNAME is empty.")

            if args.send_to:
                print(f"Sending test email to {args.send_to} ...")
                client.send_message(build_test_message(args.send_to))

        if args.send_to:
            print("SMTP check passed and test email was accepted by the server.")
        else:
            print("SMTP check passed.")
        return 0
    except (smtplib.SMTPException, OSError) as exc:
        print("")
        print(f"SMTP check failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
