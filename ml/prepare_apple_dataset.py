"""Prepare the six-class AppleCare dataset from the supplied image archives."""
from __future__ import annotations

import argparse
import hashlib
import shutil
import zipfile
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_SOURCES = {
    "apple_scab": ("Apple___Apple_scab", "Apple Apple scab"),
    "alternaria_leaf_blotch": ("Alternaria apple",),
    "powdery_mildew": ("Apple Powdery Mildew",),
    "black_rot": ("Apple___Black_rot",),
    "cedar_apple_rust": ("Apple___Cedar_apple_rust",),
    "healthy": ("Apple___healthy",),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-zip", type=Path, required=True)
    parser.add_argument("--icar-zip", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def split_name(index: int, total: int) -> str:
    train_end = round(total * 0.8)
    val_end = train_end + round(total * 0.1)
    return "train" if index < train_end else "val" if index < val_end else "test"


def main() -> None:
    args = parse_args()
    if args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True)

    sources = {
        "primary": zipfile.ZipFile(args.primary_zip),
        "icar": zipfile.ZipFile(args.icar_zip),
    }
    try:
        counts: dict[str, int] = {}
        for class_name, prefixes in CLASS_SOURCES.items():
            archive_names = ("primary",) if class_name in {
                "apple_scab", "black_rot", "cedar_apple_rust", "healthy"
            } else ("icar",)
            members: list[tuple[str, str]] = []
            for archive_name in archive_names:
                archive = sources[archive_name]
                for info in archive.infolist():
                    path = Path(info.filename)
                    if info.is_dir() or path.suffix.lower() not in IMAGE_SUFFIXES:
                        continue
                    if archive_name == "primary" and len(path.parts) != 2:
                        continue
                    if path.parts[-2] in prefixes:
                        members.append((archive_name, info.filename))
            members.sort(key=lambda item: hashlib.sha256(
                f"{item[0]}:{item[1]}:{args.seed}".encode()
            ).hexdigest())
            counts[class_name] = len(members)
            for index, (archive_name, member) in enumerate(members):
                split = split_name(index, len(members))
                digest = hashlib.sha256(f"{archive_name}:{member}".encode()).hexdigest()[:12]
                destination = args.output_dir / split / class_name / f"{digest}{Path(member).suffix.lower()}"
                destination.parent.mkdir(parents=True, exist_ok=True)
                with sources[archive_name].open(member) as source, destination.open("wb") as target:
                    shutil.copyfileobj(source, target)
        print("Prepared image counts:")
        for class_name, count in counts.items():
            print(f"  {class_name}: {count}")
    finally:
        for archive in sources.values():
            archive.close()


if __name__ == "__main__":
    main()
