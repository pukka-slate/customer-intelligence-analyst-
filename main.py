#!/usr/bin/env python3
"""
Slate & Sachi — Customer Intelligence Agent v2.0
CLI entry point.

Usage:
    # Analyze text passed directly
    python main.py "LinkedIn profile text or any other input..."

    # Analyze from a file
    python main.py --file profile.txt

    # Interactive mode (type/paste input, then Ctrl+D to submit)
    python main.py
"""

import argparse
import sys

from agent import analyze


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Slate & Sachi Customer Intelligence Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input text to analyze (LinkedIn profile, post, transcript, etc.)",
    )
    parser.add_argument(
        "--file",
        "-f",
        metavar="PATH",
        help="Path to a file containing the input to analyze",
    )

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                input_data = f.read().strip()
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.input:
        input_data = args.input.strip()
    elif not sys.stdin.isatty():
        input_data = sys.stdin.read().strip()
    else:
        print("Slate & Sachi — Customer Intelligence Agent v2.0")
        print("=" * 50)
        print("Paste your input below (LinkedIn profile, post, transcript, etc.)")
        print("Press Ctrl+D (Unix) or Ctrl+Z then Enter (Windows) when done.\n")
        try:
            input_data = sys.stdin.read().strip()
        except KeyboardInterrupt:
            print("\nAborted.", file=sys.stderr)
            sys.exit(0)

    if not input_data:
        print("Error: no input provided.", file=sys.stderr)
        sys.exit(1)

    print("\nGenerating ICP Intelligence Report...\n")
    print("=" * 60)
    print()

    analyze(input_data)


if __name__ == "__main__":
    main()
