import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter 

def merge_pdfs(pdf1: str, pdf2: str, output: str):
    """Merges two specified PDF files into a single output file."""
    print(f"\n--- Running PDF Combinator: Merging {pdf1} and {pdf2} ---")

    try:
        if not os.path.exists(pdf1):
            raise FileNotFoundError(f"Input file not found: {pdf1}")
        if not os.path.exists(pdf2):
            raise FileNotFoundError(f"Input file not found: {pdf2}")

        merger = PdfMerger()
        
        print(f"Adding to merge: {pdf1}")
        merger.append(pdf1)
        
        print(f"Adding to merge: {pdf2}")
        merger.append(pdf2)
        
        merger.write(output)
        merger.close()
        print(f"✅ Successfully created {output}")

    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
    except Exception as e:
        print(f"❌ Error merging PDFs: {e}")


def extract_pdf_pages(input_file: str):
    """Extracts all pages from an input PDF into separate single-page PDFs."""
    print(f"\n--- Running PDF Extractor on {input_file} ---")
    
    try:
        # Check if the file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File '{input_file}' not found.")

        # Load the PDF
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)

        # Extract and save each page
        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            output_filename = f"page_{i + 1}_from_{os.path.basename(input_file)}"
            with open(output_filename, "wb") as f:
                writer.write(f)
            print(f"✅ Saved: {output_filename}")

    except FileNotFoundError as fnf_error:
        print(f"❌ File error: {fnf_error}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")