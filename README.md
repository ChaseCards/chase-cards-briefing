# Tagesbriefing-Automatisierung (Teams)

## Dateien in diesem Paket → wohin im Repo

| Datei hier | Zielort im GitHub-Repo |
|---|---|
| `daily_briefing.py` | Repo-Hauptverzeichnis |
| `requirements.txt` | Repo-Hauptverzeichnis |
| `daily-briefing.yml` | `.github/workflows/daily-briefing.yml` |
| `README.md` | Repo-Hauptverzeichnis (optional) |

## Einrichtung

1. **Repo anlegen** (falls noch nicht geschehen) und die vier Dateien wie oben
   einsortieren.

2. **Teams-Webhook holen** (falls noch nicht erledigt):
   Teams-Channel → „..." → **Workflows** → Vorlage „Post to a channel when a
   webhook request is received" → Channel bestätigen → Webhook-URL kopieren.

3. **Secrets in GitHub hinterlegen**:
   Repo → *Settings* → *Secrets and variables* → *Actions* → *New repository
   secret*
   - `ANTHROPIC_API_KEY` → euer Anthropic-API-Key ([console.anthropic.com](https://console.anthropic.com))
   - `TEAMS_WEBHOOK_URL` → die Webhook-URL aus Schritt 2

4. **Testen**: Im Repo unter *Actions* → Workflow „Tagesbriefing für Teams" →
   *Run workflow* (manueller Trigger über `workflow_dispatch`). Prüfen, ob die
   Nachricht im Teams-Channel ankommt.

5. **Fertig**: Ab jetzt läuft der Workflow automatisch jeden Tag um die im
   Cron-Ausdruck hinterlegte Uhrzeit (Standard: 8:00 Uhr MESZ / 7:00 Uhr MEZ –
   bei Bedarf in `daily-briefing.yml` anpassen).

## Anpassungen

- **Themenliste ändern**: in `daily_briefing.py`, Variable `THEMEN`.
- **Uhrzeit ändern**: in `daily-briefing.yml`, den `cron`-Ausdruck (Achtung:
  GitHub Actions rechnet in UTC).
- **Anderes Nachrichtenformat**: Falls euer Teams-Workflow ein anderes
  JSON-Feld als `text` erwartet (steht in der Beispiel-Payload beim
  Einrichten des Workflows in Teams), das in `post_to_teams()` in
  `daily_briefing.py` anpassen.
