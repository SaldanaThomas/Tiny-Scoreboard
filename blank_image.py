from PIL import Image

# Overwrites a PNG image with a blank, transparent version of the same size
def make_image_blank(image_path):
    try:
        # Open the original image to get its dimensions
        with Image.open(image_path) as original_img:
            width, height = original_img.size

        blank_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        blank_img.save(image_path)
        print(f"Successfully updated '{image_path}' to be a blank PNG.")

    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")