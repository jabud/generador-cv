#!/usr/bin/env python3
"""
Generate a PDF CV from data/cv_data.yaml.

Usage:
    python generate_cv.py [--data path/to/cv_data.yaml] [--output path/to/output.pdf]
"""
import argparse
from pathlib import Path

from cv_renderer import BASE_DIR, DEFAULT_DATA, load_yaml_file, render_pdf_file


def main():
    parser = argparse.ArgumentParser(description="Generate a PDF CV from YAML data.")
    parser.add_argument(
        "--data",
        default=str(DEFAULT_DATA),
        help="Path to the YAML data file (default: data/cv_data.yaml)",
    )
    parser.add_argument(
        "--output",
        default=str(BASE_DIR / "output" / "cv.pdf"),
        help="Path for the generated PDF (default: output/cv.pdf)",
    )
    args = parser.parse_args()

    cv_data = load_yaml_file(Path(args.data))
    output_path = render_pdf_file(cv_data, Path(args.output))

    print(f"CV generated: {output_path}")


if __name__ == "__main__":
    main()
