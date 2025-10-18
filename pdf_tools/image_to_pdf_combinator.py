import os
from PIL import Image

def run_image_to_pdf_combinator():
    """
    Prompts the user for multiple image files and merges them into a single PDF.
    
    Requires: Pillow (PIL) library
    """
    print("\n--- Image to PDF Combinator Setup ---")
    
    image_paths = []
    
    # Collect image file paths from the user
    while True:
        path = input("Enter path to an image file (e.g., image.jpg or image.png), or type 'DONE' to proceed: ").strip()
        
        if path.upper() == 'DONE':
            break
        
        if os.path.exists(path) and path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp')):
            image_paths.append(path)
            print(f"✅ Added: {os.path.basename(path)}")
        else:
            print(f"❌ Error: File not found or not a supported image format: {path}")

    if not image_paths:
        print("❌ No valid images were provided. Operation cancelled.")
        return

    output_pdf_name = input("Enter the desired name for the output PDF (e.g., images.pdf): ").strip()
    if not output_pdf_name.lower().endswith(".pdf"):
        output_pdf_name += ".pdf"
        
    try:
        # Open the first image
        img_list = [Image.open(path).convert('RGB') for path in image_paths]
        
        # The first image serves as the base
        # All subsequent images are appended to it.
        if len(img_list) == 1:
            img_list[0].save(output_pdf_name, save_all=True)
        else:
            img_list[0].save(
                output_pdf_name,
                save_all=True, 
                append_images=img_list[1:], 
                quality=95
            )
            
        print(f"\n✅ Successfully created {output_pdf_name} from {len(image_paths)} images.")
        
    except FileNotFoundError as e:
        # This catch is mostly for safety, as paths were checked above,
        # but protects against files being moved between checks.
        print(f"❌ File error during processing: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred during image conversion: {e}")