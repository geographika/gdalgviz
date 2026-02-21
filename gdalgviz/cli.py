import argparse
import re
import sys
import json
from pathlib import Path
from typing import Optional

from gdalgviz import __version__
from gdalgviz.main import generate_diagram, DOCS_ROOT


def validate_color(color: str) -> str:
    if not re.match(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$", color):
        raise argparse.ArgumentTypeError(
            f"Invalid hex color '{color}'. Expected format: #rgb or #rrggbb"
        )
    return color


def parse_file(fn: str) -> str:
    """
    Open a file and return its pipeline command.
    If the file is JSON (.json or .JSON), then the JSON is parsed data['command_line'] is returned.
    Otherwise, the raw text content is returned.
    """
    file_path = Path(fn)

    if file_path.suffix.lower() == ".json":
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("command_line")
    else:
        with file_path.open("r", encoding="utf-8") as f:
            return f.read()


def main(argv: Optional[list[str]] = None) -> int:
    """
    CLI entry point for gdalgviz.
    Returns an exit code: 0 = success, non-zero = error.
    """
    parser = argparse.ArgumentParser(
        prog="gdalgviz",
        description="Visualize GDAL datasets from the command line",
    )

    parser.add_argument(
        "input_path",
        nargs="?",
        help="Path to a GDALG pipeline in JSON or text format",
    )

    parser.add_argument(
        "output_path",
        help="Path to save the generated diagram (e.g., output.svg)",
    )

    parser.add_argument(
        "--pipeline",
        help="Provide a raw GDALG pipeline string instead of a file",
    )

    parser.add_argument(
        "--vertical",
        action="store_true",
        default=False,
        help="Render the diagram top-to-bottom instead of left-to-right",
    )

    parser.add_argument(
        "--font",
        default="Helvetica",
        help="Font name for diagram nodes (default: Helvetica)",
    )

    parser.add_argument(
        "--header-color",
        default="#cfe2ff",
        type=validate_color,
        help="Background color for node headers as a hex color code (default: #cfe2ff)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"gdalgviz {__version__}",
    )

    parser.add_argument(
        "--docs-root",
        default=None,
        help=("Root URL for GDAL documentation links" f"(default: {DOCS_ROOT})"),
    )

    args = parser.parse_args(argv)

    # validate that input_path exists if not using --pipeline
    if not args.pipeline and not Path(args.input_path).exists():
        print(f"Error: File '{args.input_path}' does not exist.", file=sys.stderr)
        return 1

    # get the pipeline text
    if args.pipeline:
        pipeline = args.pipeline
    elif args.input_path:
        input_fn = args.input_path
        pipeline = parse_file(input_fn)
    else:
        parser.print_help()
        return 1

    exit_code = generate_diagram(
        pipeline=pipeline,
        output_fn=args.output_path,
        vertical=args.vertical,
        fontname=args.font,
        header_color=args.header_color,
        docs_root=args.docs_root or DOCS_ROOT,
    )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
