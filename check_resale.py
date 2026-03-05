import os
import re
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from typing import List, Tuple

from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
load_dotenv()

import random, time

URL = os.environ.get("CELEBRATIX_URL", "https://shop.celebratix.io/?c=whez5")

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
MAIL_TO   = os.environ["MAIL_TO"]
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER)
ALERT_KEY = os.environ.get("ALERT_KEY", "celebratix-whez5")

def send_email(subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO

    # Stable thread headers for Gmail-ish clients
    msg["Message-ID"] = f"<{ALERT_KEY}@celebratix.local>"
    msg["X-Alert-Key"] = ALERT_KEY

    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
        s.ehlo()
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

def parse_int(text: str) -> int:
    m = re.search(r"\d+", text)
    return int(m.group(0)) if m else 0

def check_resale() -> Tuple[bool, str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="domcontentloaded", timeout=60_000)

        # Click the Resale button
        resale_nav_button = page.locator('button:has(p:has-text("Resale"))').first
        resale_nav_button.wait_for(state="visible", timeout=30_000)
        resale_nav_button.click()

        # Wait for resale panel header
        page.locator('p:has-text("Resale")').first.wait_for(state="visible", timeout=30_000)

        # Ticket-type buttons lookup
        # read: (ticket name, count)
        ticket_buttons = page.locator('div.flex.flex-col.gap-2 >> button')
        n = ticket_buttons.count()

        results: List[Tuple[str, int]] = []
        for i in range(n):
            btn = ticket_buttons.nth(i)

            # first <p> inside button = ticket name (Early Bird, Regular Bird, etc.)
            name = (btn.locator("p").first.text_content() or "").strip()

            # find number of tickets
            count_p = btn.locator("p", has_text=re.compile(r"^\s*\d+\s*$"))
            count_txt = (count_p.first.text_content() or "0").strip() if count_p.count() else "0"
            count = parse_int(count_txt)

            if name:
                results.append((name, count))

        browser.close()

    available = any(c > 0 for _, c in results)
    details = "\n".join([f"- {name}: {count}" for name, count in results]) or "(no ticket buttons found)"
    return available, details

def main() -> None:
    time.sleep(random.uniform(0, 20))

    available, details = check_resale()
    if available:
        send_email(
            subject=f"[{ALERT_KEY}] Celebratix resale tickets available!",
            body=f"Resale tickets seem to be available.\n\nURL: {URL}\n\nCounts:\n{details}\n\nFly you fool."
        )
        print("EMAIL SENT\n", details)
    else:
        print("No resale tickets")

if __name__ == "__main__":
    main()