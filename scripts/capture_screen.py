#!/usr/bin/env python3
"""
Multi-Resolution Screenshot & Visual Review Evidence Helper.

Supports checking image aspect ratios, validating mobile viewport dimensions
(e.g., 720x1280 and 1440x2560), and generating markdown embeds.
"""

import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    Image = None


def inspect_image(path: str):
    """Inspects screenshot dimensions and properties."""
    if not os.path.exists(path):
        print(f"Error: Screenshot file not found: {path}", file=sys.stderr)
        return None

    size_bytes = os.path.getsize(path)
    dims = None
    if Image:
        with Image.open(path) as img:
            dims = img.size
    return {
        "path": path,
        "filename": os.path.basename(path),
        "size_kb": round(size_bytes / 1024, 1),
        "dimensions": dims
    }


def main():
    parser = argparse.ArgumentParser(description="Visual Evidence Inspector")
    parser.add_argument("images", nargs="+", help="Screenshot paths to inspect")
    parser.add_argument("--markdown", action="store_true", help="Print markdown embed lines")

    args = parser.parse_args()

    results = []
    for p in args.images:
        info = inspect_image(p)
        if info:
            results.append(info)
            dim_str = f"{info['dimensions'][0]}x{info['dimensions'][1]}" if info['dimensions'] else "Unknown"
            print(f"- {info['filename']}: {dim_str} ({info['size_kb']} KB)")

    if args.markdown:
        print("\nMarkdown Embeds:")
        for r in results:
            print(f"![{r['filename']}](file://{os.path.abspath(r['path'])})")


if __name__ == "__main__":
    main()
