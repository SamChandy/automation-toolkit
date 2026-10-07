"""File Organizer: sorts files in a folder into subfolders by file type.

Usage:
    python organizer.py ~/Downloads --dry-run   # preview only
    python organizer.py ~/Downloads             # actually move files
"""
import argparse
import logging
import shutil
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".java", ".cpp", ".json"},
    "Installers": {".exe", ".msi", ".dmg", ".apk"},
}


def get_category(path: Path) -> str:
    """Return the category folder name for a file based on its extension."""
    ext = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"


def unique_destination(dest: Path) -> Path:
    """If dest already exists, return dest with _1, _2, ... added to the name."""
    if not dest.exists():
        return dest
    counter = 1
    while True:
        candidate = dest.with_name(f"{dest.stem}_{counter}{dest.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize(folder: Path, dry_run: bool = False) -> dict:
    """Move every file in `folder` into a category subfolder. Returns counts."""
    counts = {}
    for item in sorted(folder.iterdir()):
        if not item.is_file() or item.name.startswith("."):
            continue  # skip subfolders and hidden files

        category = get_category(item)
        target_dir = folder / category
        destination = unique_destination(target_dir / item.name)

        logging.info("%s -> %s/%s", item.name, category, destination.name)
        if not dry_run:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(item), str(destination))
        counts[category] = counts.get(category, 0) + 1
    return counts


def main():
    parser = argparse.ArgumentParser(description="Organize files into folders by type.")
    parser.add_argument("folder", type=Path, help="Folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview without moving files")
    args = parser.parse_args()

    if not args.folder.is_dir():
        parser.error(f"'{args.folder}' is not a valid folder")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    mode = "DRY RUN" if args.dry_run else "MOVING"
    logging.info("[%s] Organizing %s\n", mode, args.folder.resolve())

    counts = organize(args.folder, args.dry_run)

    print("\nSummary:")
    if not counts:
        print("  Nothing to organize.")
    for category, n in sorted(counts.items()):
        print(f"  {category}: {n} file(s)")


if __name__ == "__main__":
    main()
