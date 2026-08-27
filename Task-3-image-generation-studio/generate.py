import time

import argparse
import requests
from PIL import Image, UnidentifiedImageError

ASPECT_RATIO_MAP = {
    "square": "1024x1024",
    "landscape": "1536x1024",
    "portrait": "1024x1536",
}

def resolve_size(aspect_ratio):
    key = aspect_ratio.strip().lower()
    if key not in ASPECT_RATIO_MAP:
        valid = ", ".join(ASPECT_RATIO_MAP.keys())
        raise ValueError(f"Unsupported aspect ratio '{aspect_ratio}'. Choose from: {valid}")
    return ASPECT_RATIO_MAP[key]

def build_url(prompt, size):
    width, height = size.split("x")
    encoded_prompt = requests.utils.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

def main():
    parser = argparse.ArgumentParser(description="Generate an image from a text prompt")
    parser.add_argument("prompt", help="Text description of the image to generate")
    parser.add_argument("--aspect", default="square", help="Aspect ratio: square, landscape, portrait")
    args = parser.parse_args()

    print(f"Prompt received: {args.prompt}")

    try:
        size = resolve_size(args.aspect)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(f"Resolved size: {size}")
    url = build_url(args.prompt, size)
    print("Requesting image...")

    for attempt in range(1, 4):
        try:
            response = requests.get(url, timeout=(5, 90))
            break
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < 3:
                wait = 2 ** attempt
                print(f"Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print("Giving up after 3 attempts.")
                return

    with open("output.png", "wb") as f:
        f.write(response.content)

    print("Saved to output.png")

    try:
        with Image.open("output.png") as img:
            img.load()
        print("Image verified OK")
    except (UnidentifiedImageError, OSError) as e:
        print(f"Image is corrupted: {e}")

if __name__ == "__main__":
    main()