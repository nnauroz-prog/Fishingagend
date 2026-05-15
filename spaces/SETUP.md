# Hugging Face Spaces — Deploy in 4 Schritten

100 % gratis, ohne Kreditkarte. Geht auf dem Handy.

## 1. Account anlegen

<https://huggingface.co/join> — Email + Passwort, **keine Karte gefragt**.

## 2. Neues Space anlegen

<https://huggingface.co/new-space>

| Feld | Wert |
|------|------|
| Owner | dein Nutzername |
| Space name | `fishingagend` |
| License | `agpl-3.0` |
| Select the Space SDK | **Docker → Blank** |
| Space hardware | `CPU basic · 2 vCPU · 16 GB · FREE` |
| Public/Private | Public (für gratis) |

Klick **Create Space**.

## 3. Code in das Space schaufeln

Im neuen Space klick auf **"Files"** → oben rechts **"⋮"** → **"Upload files"**.

Es ist auf dem Handy unhandlich, alle Dateien per Hand hochzuladen.
Drei Wege, je nach deiner Lust:

### 3a. Per Action automatisch synchronisieren (einmaliges Setup)

Wenn du das Setup einmal auf einem Desktop machst, läuft danach jedes
GitHub-Push automatisch in das HF-Space. Anleitung:
<https://huggingface.co/docs/hub/spaces-github-actions>

### 3b. Klone das GitHub-Repo lokal und pushe es zum Space (3 Befehle)

```bash
git clone https://github.com/nnauroz-prog/fishingagend.git
cd fishingagend
git checkout claude/general-session-utthR
# Dein HF-Space als zusätzlichen Remote hinzufügen:
git remote add space https://huggingface.co/spaces/DEIN_USERNAME/fishingagend
# README für HF (mit YAML-Frontmatter) an die Wurzel kopieren:
cp spaces/README.md README.md
git add README.md && git commit -m "HF-Spaces-Header"
git push space claude/general-session-utthR:main
```

### 3c. Manuell auf dem Handy hochladen

In der Space-Files-UI:

1. Lade `Dockerfile` aus dem GitHub-Repo hoch (Wurzel).
2. Lade `spaces/README.md` als `README.md` hoch.
3. Lade den Ordner `backend/` hoch (Files-UI unterstützt Drag&Drop).
4. Lade den Ordner `frontend/` hoch.

(Das ist mühsam. 3a oder 3b sind einfacher.)

## 4. Geheimnisse setzen (optional)

Im Space → **Settings** → **Repository secrets** → "New secret":

| Name | Wert |
|------|------|
| `ANTHROPIC_API_KEY` | dein Anthropic-Key (sonst Mock-LLM) |
| `JWT_GEHEIMNIS` | beliebiger langer String |

Nach jedem Secret-Setzen restartet das Space automatisch.

## Fertig

Die URL ist `https://huggingface.co/spaces/DEIN_USERNAME/fishingagend`.
Direkt im Mobil-Browser nutzbar.
