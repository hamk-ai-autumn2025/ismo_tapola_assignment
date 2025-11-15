import argparse
import base64
import os
from openai import OpenAI
import requests

def find_new_file_name(base_name):
    """Finds a new file name to avoid overwriting existing files."""
    name, ext = os.path.splitext(base_name)
    i = 0
    while os.path.exists(base_name):
        i += 1
        base_name = f"{name}_{i}{ext}"
    return base_name

def save_binary_file(data, filename):
    """Saves binary data to a file."""
    try:
        with open(filename, "wb") as f:
            f.write(data)
        return True
    except IOError as e:
        print(f"Error saving file {filename}: {e}")
        return False

def fetch_url(url):
    """Fetches content from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate an image from a description of an input image.")
    parser.add_argument("image_path", nargs='?', default=None, help="Path to the input image file.")
    args = parser.parse_args()

    image_path = args.image_path
    if image_path is None:
        while True:
            image_path = input("Please enter the path to the image file: ")
            if os.path.exists(image_path):
                break
            else:
                print(f"Error: Image file not found at {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    # Initialize OpenAI client
    try:
        client = OpenAI()
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("Please make sure your OPENAI_API_KEY environment variable is set correctly.")
        return

    # Encode the image
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    except IOError as e:
        print(f"Error reading image file: {e}")
        return

    # Generate a description of the image
    print("Generating description for the image...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in a detailed and creative way, suitable as a prompt for an image generation model."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        description = response.choices[0].message.content
        print("Generated Description:")
        print(description)
    except Exception as e:
        print(f"Error generating description: {e}")
        return

    # Generate an image from the description
    print("\nGenerating new image from the description...")
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=description,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
    except Exception as e:
        print(f"Error generating image: {e}")
        return

    # Download and save the new image
    print("Downloading and saving the new image...")
    image_data = fetch_url(image_url)
    if image_data:
        input_filename = os.path.basename(image_path)
        name, ext = os.path.splitext(input_filename)
        output_filename = find_new_file_name(f"{name}_generated.png")
        if save_binary_file(image_data, output_filename):
            print(f"New image saved as {output_filename}")

if __name__ == "__main__":
    main()
