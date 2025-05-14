import os
import tabula
from PyPDF2 import PdfReader, PdfWriter
from dotenv import load_dotenv
from tabula.errors import CSVParseError


def unlock_pdf(pdf_path, env_var_name):
    """
    Unlocks a password-protected PDF file using the password from the .env file
    and overwrites the unlocked version to the same path.

    Parameters:
        pdf_path (str): The file path of the PDF to unlock.
    """
    # Load the password from the .env file
    load_dotenv()
    password = os.getenv(env_var_name)

    if not password:
        raise ValueError("PDF password not found in the .env file.")

    # Read the PDF file
    reader = PdfReader(pdf_path)

    if reader.is_encrypted:
        try:
            reader.decrypt(password)
        except Exception as e:
            raise ValueError(f"Failed to decrypt PDF: {e}")
    else:
        print("Specified PDF file is already unlocked.")
        return

    # Write the unlocked content back to the same file
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open(pdf_path, "wb") as pdf_file:
        writer.write(pdf_file)

    print(f"Successfully unlocked and saved the PDF at: {pdf_path}")


def extract_tables_from_pdf(pdf_path, coords, coords2, extraction_method):
    """
    Extracts tables from a PDF file within given coordinates using Tabula and saves them as CSV files.

    Parameters:
        pdf_path (str): The file path of the PDF.
        coords (list): Coordinates [top, left, bottom, right] for the table on the first page.
        coords2 (list): Coordinates [top, left, bottom, right] for the table on subsequent pages.
        extraction_method (str): The method for extraction ("lattice" or "stream").

    Returns:
        dict: A dictionary where keys are page numbers and values are DataFrames of extracted tables.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    # Get the total number of pages in the PDF
    pdf_reader = PdfReader(pdf_path)
    total_pages = len(pdf_reader.pages)

    extracted_tables = {}
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.dirname(pdf_path)
    result = []

    # Iterate through each page of the PDF
    for page_number in range(1, total_pages + 1):
        # Use coords for the first page and coords2 for subsequent pages
        current_coords = coords if page_number == 1 else coords2

        try:
            tables = tabula.read_pdf(
                pdf_path,
                area=current_coords,
                pages=page_number,
                multiple_tables=False,
                lattice=(extraction_method == "lattice"),
                stream=(extraction_method == "stream"),
                pandas_options={"header": None}
            )
        except CSVParseError as exc:
            print("Error in processing PDF=%s page_number=%s" % (pdf_path, page_number))

        if tables:
            extracted_tables[page_number] = tables[0]  # Add the first table found

            # Save the table to a CSV file
            sequence = len(extracted_tables)
            output_csv_path = os.path.join(output_dir, f"{base_name}_{sequence}.csv")
            tables[0].to_csv(output_csv_path, index=False)
            result.append(output_csv_path)

    if not extracted_tables:
        print("No tables found within the specified coordinates.")
    else:
        print(f"Extracted tables from {len(extracted_tables)} pages and saved them as CSV files.")

    return result


if __name__ == "__main__":
    unlock_pdf("/Users/lokeshsanapalli/projects/personal_finance/statements/credit_cards/oct_2024/icici_oct_2024.pdf", "ICICI_CREDIT_CARD_PASSWORD")
    extract_tables_from_pdf("/Users/lokeshsanapalli/projects/personal_finance/statements/credit_cards/oct_2024/icici_oct_2024.pdf", [365, 202, 488, 561], "lattice")