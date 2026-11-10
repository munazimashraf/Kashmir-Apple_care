#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

data_dir = Path("data/apple")
total_symlinks = 0
resolved = 0
failed = 0

print("Scanning data/apple for symlinks to convert to real physical files...")
for root, dirs, files in os.walk(data_dir):
    for f in files:
        full_path = Path(root) / f
        if full_path.is_symlink():
            total_symlinks += 1
            try:
                target = full_path.resolve()
                if target.is_file():
                    # Read bytes and overwrite symlink with actual file
                    tmp_path = full_path.with_suffix(full_path.suffix + ".tmp_copy")
                    shutil.copy2(target, tmp_path)
                    full_path.unlink()
                    tmp_path.rename(full_path)
                    resolved += 1
                else:
                    print(f"Broken symlink: {full_path} -> {target}")
                    failed += 1
            except Exception as e:
                print(f"Error resolving {full_path}: {e}")
                failed += 1

print(f"Finished: {resolved}/{total_symlinks} symlinks converted to real physical files. ({failed} failed)")
