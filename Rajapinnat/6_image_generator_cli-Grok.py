import argparse
import os
import requests
import json

# Assuming you have the OpenAI API key set as an environment variable
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    print("Please set the OPENAI_API_KEY environment variable.")
    exit(1)

BASE_URL = "https://api.openai.com/v1/images/generations"

def generate_images(prompt, aspect_ratio, num_images):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # Map aspect ratios to OpenAI DALL-E-3 sizes
    aspect_map = {
        "1:1": "1024x1024",
        "16:9": "1792x1024",
        "4:3": "1024x1024",  # Closest approximation
        "3:4": "1024x1792",
    }
    size = aspect_map.get(aspect_ratio, "1024x1024")

    body = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,  # DALL-E-3 only supports n=1 per request
        "size": size,
        "quality": "standard",  # Can add as parameter if desired
        "style": "vivid",  # Can add as parameter if desired
    }

    for i in range(num_images):
        response = requests.post(BASE_URL, headers=headers, json=body)

        if response.status_code != 200:
            raise Exception(f"Non-200 response: {response.text}")

        data = response.json()
        images = data["data"]

        for image in images:  # Should be only one
            image_url = image["url"]
            print(f"Image URL: {image_url}")
            # Download the image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                filename = f"generated_image_{i+1}.png"
                with open(filename, "wb") as f:
                    f.write(img_response.content)
                print(f"Downloaded: {filename}")
            else:
                print(f"Failed to download image {i+1}")

def interactive_mode():
    prompt = input("Enter the prompt: ")
    aspect_ratio = input("Enter aspect ratio (1:1, 16:9, 4:3, 3:4): ")
    num_images = int(input("Enter number of images (1-10): "))
    generate_images(prompt, aspect_ratio, num_images)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images using OpenAI DALL-E-3.")
    parser.add_argument("--prompt", help="Image prompt")
    parser.add_argument("--aspect_ratio", help="Aspect ratio (1:1, 16:9, 4:3, 3:4)")
    parser.add_argument("--num_images", type=int, help="Number of images (1-10)")

    args = parser.parse_args()

    if not any([args.prompt, args.aspect_ratio, args.num_images]):
        interactive_mode()
    else:
        # Use provided args, with defaults if missing
        prompt = args.prompt or input("Enter the prompt: ")
        aspect_ratio = args.aspect_ratio or input("Enter aspect ratio: ")
        num_images = args.num_images or int(input("Enter number of images: "))
        generate_images(prompt, aspect_ratio, num_images)