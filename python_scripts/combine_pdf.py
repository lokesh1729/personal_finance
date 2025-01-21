#!/usr/bin/env python3
import argparse
import os
from PyPDF2 import PdfMerger


def combine_pdfs(pdf_files):
    """
    Combines multiple PDF files into a single PDF.

    Args:
        pdf_files (list): List of PDF file paths

    Returns:
        str: Path to the output combined PDF file
    """
    # Create a PDF merger object
    merger = PdfMerger()

    # Get the base directory from the first PDF file
    base_dir = os.path.dirname(os.path.abspath(pdf_files[0]))

    try:
        # Add each PDF to the merger
        for pdf in pdf_files:
            merger.append(pdf)

        # Create output filename
        output_path = os.path.join(base_dir, 'combined_output.pdf')

        # Write the combined PDF to file
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)

        return output_path

    finally:
        # Always close the merger
        merger.close()


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Combine multiple PDF files into a single PDF'
    )
    parser.add_argument(
        'pdf_files',
        nargs='+',
        help='PDF files to combine (in order)'
    )

    # Parse arguments
    args = parser.parse_args()

    try:
        # Verify all files exist and are PDFs
        for pdf_file in args.pdf_files:
            if not os.path.exists(pdf_file):
                raise FileNotFoundError(f"File not found: {pdf_file}")
            if not pdf_file.lower().endswith('.pdf'):
                raise ValueError(f"File is not a PDF: {pdf_file}")

        # Combine PDFs
        output_path = combine_pdfs(args.pdf_files)
        print(f"Successfully combined PDFs into: {output_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()