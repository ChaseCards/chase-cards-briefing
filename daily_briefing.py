"""
Tagesbriefing für Chase Cards Streams
--------------------------------------
Generiert per Anthropic API (mit Websuche) ein tägliches Kurz+Lang-Briefing zu
NFL, NBA, MLB, UEFA, WWE, Tennis, Marvel und Disney und postet es in einen
Microsoft-Teams-Channel (per Workflows-Webhook).

Benötigte Umgebungsvariablen (als GitHub Secrets hinterlegen):
  ANTHROPIC_API_KEY   -> euer Anthropic API Key
  TEAMS_WEBHOOK_URL   -> die Webhook-URL aus dem Teams-Workflow (Schritt 1 der Anleitung)
"""

import os
import sys
import json
from datetime import datetime

import anthropic
import requests

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


def post_to_teams(webhook_url: str, message: str) -> None:
    # Standard-Payload für den Teams-"Workflows"-Webhook (Vorlage "Post to a channel
    # when a webhook request is received"). Falls euer Flow ein anderes Feld als
    # "text" erwartet, hier den Feldnamen anpassen (siehe Beispiel-Payload beim
    # Einrichten des Workflows in Teams).
    payload = {"text": message}

    resp = requests.post(
        webhook_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
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
        post_to_teams(os.environ["TEAMS_WEBHOOK_URL"], briefing)
    except Exception as exc:  # noqa: BLE001
        print(f"Fehler beim Posten in Teams: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Briefing erfolgreich generiert und in Teams gepostet.")


if __name__ == "__main__":
    main()
