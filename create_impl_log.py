#!/usr/bin/env python3
"""
Implementation Log Generator

Generates a timestamped implementation log file in docs/temp/ with base template.

Usage:
    python tools/create_impl_log.py "Brief Title Here"
    python tools/create_impl_log.py "Brief Title Here" "Custom/Path/docs/temp"
"""

import sys
import os
from datetime import datetime
from pathlib import Path


def sanitize_title(title: str) -> str:
    """Convert title to valid filename component."""
    # Replace spaces and special chars with underscores
    sanitized = "".join(c if c.isalnum() else "_" for c in title)
    # Remove consecutive underscores
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    return sanitized.strip("_")


def create_impl_log(title: str, output_dir: str = None) -> str:
    """
    Create an implementation log markdown file.

    Args:
        title: Short descriptive title for this implementation round
        output_dir: Directory to write the file (default: docs/temp)

    Returns:
        Path to the created file
    """
    if not title:
        print("Error: title cannot be empty")
        sys.exit(1)

    # Determine output directory
    if output_dir is None:
        # Find project root and construct docs/temp path
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / "docs" / "temp"
    else:
        output_dir = Path(output_dir)

    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp and filename
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M")
    sanitized_title = sanitize_title(title)
    filename = f"{timestamp}_{sanitized_title}.md"
    filepath = output_dir / filename

    # Create base template
    template = f"""# {title}

**Date:** {now.strftime("%Y-%m-%d")}  
**Time:** {now.strftime("%H:%M")}  
**Scope:** [Describe scope here]  
**Repository:** IMC-Prosperity-4

## Summary

[Describe the changes and their purpose]

## Changes

[List the main changes and improvements]

## Files Changed

- `file1.py`
- `file2.py`

## Validation Performed

- [validation step 1]
- [validation step 2]

## Remaining TODOs

- [any outstanding tasks]

## Notes

[Any additional notes or deferred ideas]
"""

    # Write file
    with open(filepath, "w") as f:
        f.write(template)

    return str(filepath)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/create_impl_log.py 'Brief Title' [output_dir]")
        print("\nExample:")
        print("  python tools/create_impl_log.py 'Add new feature'")
        sys.exit(1)

    title = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        filepath = create_impl_log(title, output_dir)
        print(f"Created: {filepath}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

