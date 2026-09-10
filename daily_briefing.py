"""
Tagesbriefing für Chase Cards Streams
--------------------------------------
Generiert per Anthropic API (mit Websuche) ein tägliches Kurz+Lang-Briefing zu
NFL, NBA, MLB, UEFA, WWE, Tennis, Marvel und Disney und schickt es per E-Mail
(über Resend) an die Teams-Kanal-E-Mail-Adresse (kommt dort automatisch als
Beitrag an).

Benötigte Umgebungsvariablen (als GitHub Secrets hinterlegen):
  ANTHROPIC_API_KEY     -> euer Anthropic API Key
  RESEND_API_KEY        -> API-Key von resend.com
  TEAMS_CHANNEL_EMAIL   -> die E-Mail-Adresse des Teams-Kanals
  SENDER_EMAIL          -> Absenderadresse auf eurer verifizierten Domain,
                            z.B. briefing@chase-cards.de
"""

import os
import sys
from datetime import datetime

import anthropic
import requests
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

    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n\n".join(text_parts).strip()


def send_email_to_teams(briefing_markdown: str) -> None:
    api_key = os.environ["RESEND_API_KEY"]
    sender = os.environ["SENDER_EMAIL"]
    recipient = os.environ["TEAMS_CHANNEL_EMAIL"]

    html_body = md_lib.markdown(briefing_markdown, extensions=["tables"])

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": sender,
            "to": [recipient],
            "subject": f"Tagesbriefing {datetime.now().strftime('%d.%m.%Y')}",
            "html": html_body,
        },
        timeout=30,
    )
    resp.raise_for_status()


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
