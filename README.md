"""
Tagesbriefing für Chase Cards Streams
--------------------------------------
Generiert per Anthropic API (mit Websuche) ein tägliches Kurz+Lang-Briefing zu
NFL, NBA, MLB, UEFA, WWE, Tennis, Marvel und Disney und schickt es per E-Mail
an die Teams-Kanal-E-Mail-Adresse (kommt dort automatisch als Beitrag an).

Benötigte Umgebungsvariablen (als GitHub Secrets hinterlegen):
  ANTHROPIC_API_KEY     -> euer Anthropic API Key
  TEAMS_CHANNEL_EMAIL   -> die E-Mail-Adresse des Teams-Kanals
  SENDER_EMAIL          -> das Absender-Postfach (Microsoft 365)
  SENDER_APP_PASSWORD   -> App-Passwort für das Absender-Postfach
"""

import os
import sys
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import anthropic
import markdown as md_lib

MODEL = "claude-sonnet-5"

THEMEN = ["NFL", "NBA", "MLB", "UEFA Champions League", "WWE", "Tennis", "Marvel", "Disney"]

PROMPT = f"""Erstelle ein Tagesbriefing (Datum: {datetime.now().strftime('%d.%m.%Y')}) für die \
Stream-Vorbereitung eines Sammelkarten-Livestream-Unternehmens (Chase Cards). \
Recherchiere aktuell per Websuche die wichtigsten News von heute zu: {", ".join(THEMEN)}.

Format exakt so:
1. Eine kompakte Tabelle (Bereich | wichtigste News heute) - so kurz, dass sie auf eine \
DIN-A4-Seite passt.
2. Danach pro Bereich einen etwas längeren Absatz (3-5 Sätze) mit mehr Kontext.

Schreibe auf Deutsch, sachlich, ohne Floskeln. Nutze Markdown (##-Überschriften, |-Tabelle).
Wenn es zu einem Bereich heute keine relevanten News gibt, schreibe das kurz und ehrlich \
statt etwas zu erfinden."""


def generate_briefing() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": PROMPT}],
    )

    # Alle Text-Blöcke der Antwort zusammensetzen (Websuche kann mehrere Blöcke erzeugen)
    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n\n".join(text_parts).strip()


def send_email_to_teams(briefing_markdown: str) -> None:
    sender = os.environ["SENDER_EMAIL"]
    app_password = os.environ["SENDER_APP_PASSWORD"]
    recipient = os.environ["TEAMS_CHANNEL_EMAIL"]

    html_body = md_lib.markdown(briefing_markdown, extensions=["tables"])

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = f"Tagesbriefing {datetime.now().strftime('%d.%m.%Y')}"
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(sender, app_password)
        server.sendmail(sender, [recipient], msg.as_string())


def main() -> None:
    try:
        briefing = generate_briefing()
    except Exception as exc:  # noqa: BLE001
        print(f"Fehler bei der Briefing-Generierung: {exc}", file=sys.stderr)
        sys.exit(1)

    if not briefing:
        print("Leeres Briefing erhalten - breche ab, ohne zu posten.", file=sys.stderr)
        sys.exit(1)

    try:
        send_email_to_teams(briefing)
    except Exception as exc:  # noqa: BLE001
        print(f"Fehler beim E-Mail-Versand an Teams: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Briefing erfolgreich generiert und per E-Mail an Teams gesendet.")


if __name__ == "__main__":
    main()
