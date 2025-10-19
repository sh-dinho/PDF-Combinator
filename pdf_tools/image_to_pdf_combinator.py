import os
import re
import io
from PIL import Image, ImageDraw, ImageFont

# Define the target size in bytes (2.0 MB)
TARGET_MAX_SIZE = 2.0 * 1024 * 1024

def natural_sort_key(s):
    """Sort key for natural alphanumeric sorting (e.g., img1, img2, img10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def resize_image(img, min_dim=1200, max_dim=1600):
    """
    Resize every photo so its longest side is between min_dim and max_dim.
    Upscales if smaller than min_dim, downscales if larger than max_dim.
    Keeps aspect ratio intact.
    """
    width, height = img.size
    longest_side = max(width, height)

    # Decide target dimension
    if longest_side < min_dim:
        target = min_dim
    elif longest_side > max_dim:
        target = max_dim
    else:
        target = longest_side  # already within range

    if width >= height:
        new_width = target
        new_height = int(target * (height / width))
    else:
        new_height = target
        new_width = int(target * (width / height))

    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

def add_page_number(img, page_num):
    """Draw page number on bottom-right corner."""
    draw = ImageDraw.Draw(img)

    # Try to load a truetype font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

    text = str(page_num)
    try:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except Exception:
        text_width, text_height = draw.textlength(text, font=font), font.getmetrics()[0]

    x = img.width - text_width - 20
    y = img.height - text_height - 20

    draw.rectangle((x - 5, y - 5, x + text_width + 5, y + text_height + 5), fill="white")
    draw.text((x, y), text, fill="black", font=font)

    return img

def get_pdf_size(images, quality):
    """Return size in bytes of a PDF built from images (in memory)."""
    buf = io.BytesIO()
    if len(images) == 1:
        images[0].save(buf, save_all=True, quality=quality, format="PDF")
    else:
        images[0].save(buf, save_all=True, append_images=images[1:], quality=quality, format="PDF")
    return buf.tell()

def save_pdf_batch(images, output_name, quality):
    """Save images as a PDF file."""
    if not images:
        return
    if len(images) == 1:
        images[0].save(output_name, save_all=True, quality=quality, format="PDF")
    else:
        images[0].save(output_name, save_all=True, append_images=images[1:], quality=quality, format="PDF")

def run_image_to_pdf_combinator():
    """Main function: combine images into PDFs under 2MB each."""
    print("\n--- Image to PDF Combinator (Folder Mode) ---")

    folder_path = input("Enter the path to the folder containing images: ").strip()
    if not os.path.isdir(folder_path):
        print(f"❌ Error: Folder not found: {folder_path}")
        return

    supported_formats = ('.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp')
    file_list = sorted(os.listdir(folder_path), key=natural_sort_key)
    image_paths = [os.path.join(folder_path, f) for f in file_list if f.lower().endswith(supported_formats)]

    if not image_paths:
        print("❌ No valid images were found in that folder. Operation cancelled.")
        return

    print(f"✅ Found {len(image_paths)} images. Proceeding to PDF creation...")

    output_pdf_name = input("Enter the base name for the output PDF (e.g., images.pdf): ").strip()
    base_name = output_pdf_name[:-4] if output_pdf_name.lower().endswith(".pdf") else output_pdf_name

    compression_attempts = [
        (95),  # start high quality
        (90),
        (85),
        (80),
        (75)   # lowest quality fallback
    ]

    success = False

    try:
        for quality in compression_attempts:
            print(f"\nAttempting batching: Quality={quality}%")

            pdf_counter = 1
            current_batch_images = []
            single_image_too_large = False

            for i, path in enumerate(image_paths):
                page_counter = i + 1
                with Image.open(path) as original_img:
                    resized_img = resize_image(original_img, 1200, 1600)
                    rgb_img = resized_img.convert('RGB')
                    numbered_img = add_page_number(rgb_img, page_counter)
                    current_batch_images.append(numbered_img)

                # Check size in memory
                size_bytes = get_pdf_size(current_batch_images, quality)
                if size_bytes >= TARGET_MAX_SIZE:
                    # Try compress-to-fit for this batch
                    temp_quality = quality
                    while temp_quality > 40:  # don’t go below 40% quality
                        size_bytes = get_pdf_size(current_batch_images, temp_quality)
                        if size_bytes < TARGET_MAX_SIZE:
                            output_name = f"{base_name}.pdf" if pdf_counter == 1 else f"{base_name}-{pdf_counter}.pdf"
                            save_pdf_batch(current_batch_images, output_name, temp_quality)
                            file_size_mb = os.path.getsize(output_name) / (1024 * 1024)
                            print(f"   ✅ Created {output_name} ({file_size_mb:.2f} MB) at quality {temp_quality}%")
                            break
                        temp_quality -= 5
                    else:
                        # If still too big, back off last image
                        safe_batch = current_batch_images[:-1]
                        if not safe_batch:
                            print(f"   ⚠️ Single image ({os.path.basename(path)}) is too large at this setting.")
                            single_image_too_large = True
                            break
                        output_name = f"{base_name}.pdf" if pdf_counter == 1 else f"{base_name}-{pdf_counter}.pdf"
                        save_pdf_batch(safe_batch, output_name, quality)
                        file_size_mb = os.path.getsize(output_name) / (1024 * 1024)
                        print(f"   ✅ Created {output_name} ({file_size_mb:.2f} MB)")
                        current_batch_images = [numbered_img]
                        pdf_counter += 1
                        continue

                    # Start new batch after saving
                    pdf_counter += 1
                    current_batch_images = []

            if single_image_too_large:
                print("   Retrying with lower quality settings...")
                continue

            if current_batch_images:
                # Final batch compress-to-fit
                temp_quality = quality
                while temp_quality > 40:
                    size_bytes = get_pdf_size(current_batch_images, temp_quality)
                    if size_bytes < TARGET_MAX_SIZE:
                        output_name = f"{base_name}.pdf" if pdf_counter == 1 else f"{base_name}-{pdf_counter}.pdf"
                        save_pdf_batch(current_batch_images, output_name, temp_quality)
                        file_size_mb = os.path.getsize(output_name) / (1024 * 1024)
                        print(f"   ✅ Created {output_name} ({file_size_mb:.2f} MB) at quality {temp_quality}%")
                        break
                    temp_quality -= 5
                else:
                    output_name = f"{base_name}.pdf" if pdf_counter == 1 else f"{base_name}-{pdf_counter}.pdf"
                    save_pdf_batch(current_batch_images, output_name, quality)
                    file_size_mb = os.path.getsize(output_name) / (1024 * 1024)
                    print(f"   ✅ Created {output_name} ({file_size_mb:.2f} MB)")

            print(f"\n✅ Successfully created {pdf_counter} PDF(s).")
            print(f"   Used settings: Quality={quality}%")
            success = True
            break

        if not success:
            print("\n❌ Warning: Could not create PDFs.")
            print("   Even at the lowest quality, a single image was too large to fit in a 2MB file.")

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

# Example run
# if __name__ == "__main__":
#     run_image_to_pdf_combinator()