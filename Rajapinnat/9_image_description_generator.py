from google import genai
from google.genai import types
import argparse
import os
import mimetypes

def main():
    parser = argparse.ArgumentParser(description="Generate product descriptions and marketing slogans from images using Gemini AI.")
    parser.add_argument('--images', nargs='+', help='Paths to image files (space-separated)')
    parser.add_argument('--user_text', help='User input text for better accuracy')
    parser.add_argument('--api_key', help='Google API key (or set GEMINI_API_KEY env var)')

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = input("Enter your Google API key: ").strip()
    os.environ["GEMINI_API_KEY"] = api_key
    client = genai.Client()

    # Get images
    images = args.images
    if not images:
        images_input = input("Enter paths to image files, separated by commas: ")
        images = [img.strip() for img in images_input.split(',') if img.strip()]

    if not images:
        print("No images provided. Exiting.")
        return

    # Load images
    image_parts = []
    for img_path in images:
        if not os.path.exists(img_path):
            print(f"Image file not found: {img_path}")
            continue
        try:
            mime_type, _ = mimetypes.guess_type(img_path)
            if not mime_type:
                mime_type = "image/jpeg"  # default
            with open(img_path, "rb") as f:
                image_data = f.read()
            image_part = types.Part(
                inline_data=types.Blob(
                    mime_type=mime_type,
                    data=image_data
                )
            )
            image_parts.append(image_part)
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")

    if not image_parts:
        print("No valid images loaded. Exiting.")
        return

    # Get user text
    user_text = args.user_text
    if not user_text:
        user_text = input("Enter any additional description or context (optional): ").strip()

    # Create prompt
    prompt = "Analyze these product images."
    if user_text:
        prompt += f" Additional context: {user_text}"
    prompt += " Generate detailed product descriptions and creative marketing slogans for each product visible in the images. Structure the output with clear headings for each product."

    # Prepare contents
    contents = [types.Part(text=prompt)] + image_parts

    # Generate content
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
        print("\nGenerated Content:\n")
        print(response.text)
    except Exception as e:
        print(f"Error generating content: {e}")

if __name__ == "__main__":
    main()