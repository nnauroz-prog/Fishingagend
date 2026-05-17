# Hugging Face Spaces — 100 % gratis, ohne Karte

## Schnellster Weg (auf dem Handy machbar)

Diese 5 Schritte musst du **einmal** machen. Danach läuft jeder GitHub-Commit
automatisch in dein Space.

### 1. Hugging-Face-Account anlegen
<https://huggingface.co/join> — Email + Passwort, **keine Karte**.

### 2. Leeres Space erstellen
<https://huggingface.co/new-space>

| Feld | Wert |
|------|------|
| Owner | dein HF-Nutzername |
| Space name | `fishingagend` |
| License | `agpl-3.0` |
| SDK | **Docker → Blank** |
| Hardware | `CPU basic — FREE` |
| Public/Private | Public |

Klick **Create Space**. Das Space ist erst mal leer — das ist OK.

### 3. HF-Access-Token erstellen
<https://huggingface.co/settings/tokens> → **"New token"**:

| Feld | Wert |
|------|------|
| Name | `github-sync` |
| Type | **Write** |

Token kopieren — du brauchst ihn gleich.

### 4. Zwei GitHub-Secrets setzen
Auf <https://github.com/nnauroz-prog/fishingagend/settings/secrets/actions>:

| Name | Wert |
|------|------|
| `HF_USER` | dein HF-Nutzername aus Schritt 2 |
| `HF_TOKEN` | das Token aus Schritt 3 |

### 5. Sync auslösen
Auf <https://github.com/nnauroz-prog/fishingagend/actions/workflows/hf-sync.yml>
→ **"Run workflow"** → Branch `claude/general-session-utthR` → **"Run"**.

Nach ~30 Sekunden ist dein Space gefüllt. Ab jetzt synct jeder
zukünftige GitHub-Push automatisch.

## Deine URL

<https://huggingface.co/spaces/DEIN_USERNAME/fishingagend>

Der erste Build dauert ~5 min (Docker baut Frontend + Backend),
spätere Builds nur ~2 min. Im Space siehst du das Logs-Tab mit Live-Output.

## Optional: echtes Claude statt Mock-LLM

Im Space → **Settings** → **Repository secrets** → "New secret":

| Name | Wert |
|------|------|
| `ANTHROPIC_API_KEY` | dein Anthropic-Key |

Space restartet automatisch.

## Wenn was nicht klappt

- **Action grün, aber Space-Build fehlschlägt** → Logs-Tab im Space, meist
  Tippfehler in env-Vars.
- **Action selbst fehlschlägt** → Logs-Link in GitHub-Actions-Run.
  Häufigste Ursache: HF_TOKEN nicht "Write"-Permission.
- **Space schläft ein** → Free-Tier wacht beim ersten Request automatisch
  wieder auf (~30 s).
