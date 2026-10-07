# Automation Toolkit

Three small Python command-line tools that automate boring everyday tasks.

| Script | What it does |
|---|---|
| `organizer.py` | Sorts a messy folder (e.g. Downloads) into Images, Documents, Videos, etc. |
| `photo_renamer.py` | Renames photos to `YYYY-MM-DD_001.jpg` using the EXIF date taken |
| `email_scheduler.py` | Sends an automated email (with optional attachment) every day at a set time |

## Setup

```bash
git clone https://github.com/<your-username>/automation-toolkit.git
cd automation-toolkit
pip install -r requirements.txt
```

## Usage

```bash
# 1. File organizer (always preview first!)
python organizer.py ~/Downloads --dry-run
python organizer.py ~/Downloads

# 2. Photo renamer
python photo_renamer.py ~/Pictures/Trip --prefix Goa_ --dry-run
python photo_renamer.py ~/Pictures/Trip --prefix Goa_

# 3. Scheduled email
cp .env.example .env          # then fill in your details
python email_scheduler.py --now                 # send a test email
python email_scheduler.py --time 09:00          # send daily at 9 AM
python email_scheduler.py --time 18:30 --attach report.pdf
```

## Features
- `--dry-run` mode to preview changes safely
- Never overwrites files (name collisions get `_1`, `_2`, ...)
- Safe to re-run (photo renamer is idempotent)
- Credentials kept in `.env`, never committed to Git

## Ideas to extend
- Add a config file for custom categories
- Add an undo log
- Run the organizer on a schedule or when new files appear (`watchdog`)
- Add a Telegram or WhatsApp notification option

## Tech
Python 3, `argparse`, `pathlib`, `shutil`, `smtplib`, `schedule`, `Pillow`
