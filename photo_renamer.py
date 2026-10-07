"""Bulk Photo Renamer: renames photos to YYYY-MM-DD_001.jpg using the date taken.

Uses EXIF data if Pillow is installed, otherwise falls back to the file's
modified time.

Usage:
    python photo_renamer.py ~/Pictures/Trip --dry-run
    python photo_renamer.py ~/Pictures/Trip --prefix Goa_
"""
import argparse
from datetime import datetime
from pathlib import Path

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".webp"}


def get_date_taken(path: Path) -> datetime:
    """Read the EXIF 'date taken'; fall back to the file's modified time."""
    try:
        from PIL import Image

        with Image.open(path) as img:
            exif = img.getexif()
            value = exif.get_ifd(0x8769).get(36867) or exif.get(306)
            if value:
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass  # no Pillow, no EXIF, or unreadable file
    return datetime.fromtimestamp(path.stat().st_mtime)


def plan_renames(folder: Path, prefix: str = "") -> list:
    """Build a list of (old_path, new_path) pairs without touching any file."""
    photos = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in PHOTO_EXTENSIONS]
    photos.sort(key=lambda p: (get_date_taken(p), p.name))  # name = stable tie-breaker

    per_day = {}
    used = set()
    plan = []
    for photo in photos:
        day = get_date_taken(photo).strftime("%Y-%m-%d")
        while True:
            per_day[day] = per_day.get(day, 0) + 1
            new_name = f"{prefix}{day}_{per_day[day]:03d}{photo.suffix.lower()}"
            new_path = folder / new_name
            # Accept the name if it's the file itself, or nothing else uses it
            if new_path == photo or (new_name not in used and not new_path.exists()):
                break
        used.add(new_name)
        plan.append((photo, new_path))
    return plan


def main():
    parser = argparse.ArgumentParser(description="Rename photos by date taken.")
    parser.add_argument("folder", type=Path, help="Folder containing photos")
    parser.add_argument("--prefix", default="", help="Text to put before each name")
    parser.add_argument("--dry-run", action="store_true", help="Preview without renaming")
    args = parser.parse_args()

    if not args.folder.is_dir():
        parser.error(f"'{args.folder}' is not a valid folder")

    plan = plan_renames(args.folder, args.prefix)
    renamed = 0
    for old, new in plan:
        if old == new:
            continue
        print(f"{old.name}  ->  {new.name}")
        if not args.dry_run:
            old.rename(new)
        renamed += 1

    action = "would be renamed" if args.dry_run else "renamed"
    print(f"\n{renamed} photo(s) {action}.")


if __name__ == "__main__":
    main()
