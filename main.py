import pdf_tools
# Change the import below:
# from image_to_pdf_combinator import run_image_to_pdf_combinator 
from pdf_tools.image_to_pdf_combinator import run_image_to_pdf_combinator 
import os
# ... rest of main.py

def main():
    while True:
        print("\nChoose a program to run:")
        print("1. PDF-PDF Combinator (Merge Two PDFs)")
        print("2. PDF Extractor (Extract Pages from One PDF)")
        print("3. Image-to-PDF Combinator (Merge Multiple Images)") # New Option
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            # --- Dynamic Input for PDF Combinator ---
            print("\n--- PDF Combinator Setup ---")
            pdf1 = input("Enter the path for the FIRST PDF to merge: ")
            pdf2 = input("Enter the path for the SECOND PDF to merge: ")
            output = input("Enter the desired name for the MERGED output file (e.g., final.pdf): ")
            
            if not output.lower().endswith(".pdf"):
                output += ".pdf"
            
            pdf_tools.merge_pdfs(pdf1, pdf2, output)
            
        elif choice == "2":
            # --- Dynamic Input for Extractor ---
            print("\n--- PDF Extractor Setup ---")
            input_file = input("Enter the path for the PDF to extract pages from: ")
            pdf_tools.extract_pdf_pages(input_file)
            
        elif choice == "3":
            # --- New: Image-to-PDF Combinator ---
            run_image_to_pdf_combinator()
            
        elif choice == "4":
            print("Exiting program. Goodbye! 👋")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()