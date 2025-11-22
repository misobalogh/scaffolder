import re
import argparse
from pathlib import Path
from dataclasses import dataclass

@dataclass
class FileSystemItem:
    name: str
    indent: int
    is_dir: bool


@dataclass
class PathStackItem:
    path: str
    indent: int


def parse_structure(file_path, output_dir="."):
    output_base = Path(output_dir)
    output_base.mkdir(parents=True, exist_ok=True)

    # List of binary file extensions to ignore
    IGNORED_EXTENSIONS = {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".pdf", ".exe", ".zip", ".tar", ".gz",
        ".rar", ".7z", ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".flac", ".ogg", ".webp",
        ".ico", ".svg", ".bin", ".dll"
    }

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    parsed_lines = []
    for line in lines:
        # Remove comments
        line = line.split("#", 1)[0].rstrip()
        if not line:
            continue

        # Calculate indent based on tree characters or whitespace
        match = re.match(r"^[\s│├└─]*", line)
        prefix = match.group(0)
        indent = len(prefix)
        name = line[len(prefix) :].strip()

        if not name:
            continue

        # Handle *.ext syntax for multiple files
        if name.startswith("*.") and " " in name:
            parts = name.split()
            ext = parts[0][1:]  # e.g. .py
            filenames = parts[1:]
            for fname in filenames:
                parsed_lines.append(FileSystemItem(f"{fname}{ext}", indent, False))
        # Handle multiple files on one line (e.g. main.py utils.py)
        elif " " in name:
            for fname in name.split():

                is_explicit_dir = fname.endswith("/")
                clean_name = fname.rstrip("/")
                parsed_lines.append(FileSystemItem(clean_name, indent, is_explicit_dir))
        else:
            is_explicit_dir = name.endswith("/")
            clean_name = name.rstrip("/")
            parsed_lines.append(FileSystemItem(clean_name, indent, is_explicit_dir))

    for i, item in enumerate(parsed_lines):
        if i < len(parsed_lines) - 1:
            next_indent = parsed_lines[i + 1].indent
            if next_indent > item.indent:
                item.is_dir = True

    path_stack = []

    for item in parsed_lines:
        indent = item.indent
        name = item.name

        while path_stack and path_stack[-1].indent >= indent:
            path_stack.pop()

        if path_stack:
            full_path = output_base / path_stack[-1].path / name
        else:
            full_path = output_base / name

        # Check for ignored binary file extensions
        if not item.is_dir:
            ext = Path(name).suffix.lower()
            if ext in IGNORED_EXTENSIONS:
                continue

        if item.is_dir:
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()

        if item.is_dir:
            path_stack.append(
                PathStackItem(
                    name if not path_stack else f"{path_stack[-1].path}/{name}", indent
                )
            )


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold directory structure from text file."
    )
    parser.add_argument("file", help="Path to the structure file")
    parser.add_argument(
        "--output", "-o", default=".", help="Output directory"
    )

    args = parser.parse_args()
    parse_structure(args.file, args.output)


if __name__ == "__main__":
    main()
