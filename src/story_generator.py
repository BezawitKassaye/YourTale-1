from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import io
from PIL import Image, ImageDraw, ImageFont
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_STABLE = os.getenv("API_STABLE")

# Initialize Stability AI client
stability_api = client.StabilityInference(
    key=API_STABLE,
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0"
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=API_KEY)


def generate_story(character_name, theme, style):
    """
    Generates a dynamic story using GPT.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative storyteller."},
                {
                    "role": "user",
                    "content": (
                        f"Write a short {style} story about a child named {character_name} that teaches "
                        f"a lesson about {theme}. Each paragraph should have two sentences."
                    )
                },
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating story: {e}")
        return None


def generate_base_image(character_description, output_path):
    """
    Generates a base portrait of the character for use in Img2Img.
    """
    try:
        answers = stability_api.generate(
            prompt=character_description,
            seed=12345,
            steps=50,
            cfg_scale=8.0,
            width=1024,
            height=1024,
            samples=1
        )
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    print("NSFW content detected. Try a different prompt.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.save(output_path)
                    print(f"Base image saved as {output_path}")
                    return output_path
    except Exception as e:
        print(f"Error generating base image: {e}")
        return None


def generate_scene_image(init_image_path, prompt, output_path, seed, denoising_strength=0.5):
    """
    Generates a scene using Img2Img for continuity with the base image.
    """
    try:
        with Image.open(init_image_path).convert("RGB") as init_image:
            answers = stability_api.generate(
                prompt=prompt,
                init_image=init_image,
                start_schedule=denoising_strength,
                seed=seed,
                steps=50,
                cfg_scale=8.0,
                width=1024,
                height=1024,
                samples=1
            )
            for resp in answers:
                for artifact in resp.artifacts:
                    if artifact.type == generation.ARTIFACT_IMAGE:
                        img = Image.open(io.BytesIO(artifact.binary))
                        img.save(output_path)
                        print(f"Scene image saved as {output_path}")
                        return output_path
    except Exception as e:
        print(f"Error generating scene image: {e}")
        return None


def generate_visual_prompts(story, base_description):
    """
    Combines the base character description with each paragraph's story context
    to generate detailed, scene-specific prompts.
    """
    paragraphs = [p.strip() for p in story.split("\n\n") if p.strip()]
    prompts = []

    for idx, paragraph in enumerate(paragraphs, start=1):
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative assistant that generates scene descriptions for illustrations."},
                    {"role": "user", "content": (
                        f"Base Character Description: {base_description}\n\n"
                        f"Story Paragraph: {paragraph}\n\n"
                        "Generate a vivid visual description for a children's book illustration. "
                        "Include the actions, environment, and objects from the story paragraph, "
                        "while ensuring the character's appearance stays consistent."
                    )}
                ],
                max_tokens=150,
                temperature=0.7
            )
            prompt = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating prompt for paragraph {idx}: {e}")
            prompt = f"{base_description} {paragraph}"  # Fallback

        prompts.append(prompt)

    return prompts


def add_text_to_image(image_path, text, output_path, font_path="assets/fonts/CaveatBrush-Regular.ttf", font_size=24):
    """
    Adds wrapped text to the image and saves it.
    """
    try:
        image = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(image)

        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found at {font_path}")
        font = ImageFont.truetype(font_path, font_size)

        max_width = image.width - 40
        words = text.split()
        lines, current_line = [], []
        for word in words:
            current_line.append(word)
            if font.getbbox(' '.join(current_line))[2] > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        wrapped_text = '\n'.join(lines)

        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (image.width - text_width) / 2
        y = image.height - text_height - 20

        background = Image.new("RGBA", (text_width + 40, text_height + 20), (0, 0, 0, 128))
        image.paste(background, (int(x) - 20, int(y) - 10), mask=background)

        draw.multiline_text((x, y), wrapped_text, font=font, fill="white", align="center")
        image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Error adding text to image: {e}")
        return None


def generate_story_images(story, base_description, base_image_path, output_dir):
    """
    Generates images for each paragraph of the story using Img2Img and overlays text.
    """
    prompts = generate_visual_prompts(story, base_description)
    os.makedirs(output_dir, exist_ok=True)

    images = []
    for idx, (prompt, paragraph) in enumerate(zip(prompts, story.split("\n\n")), start=1):
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        print(f"\nProcessing scene {idx} with prompt:\n{prompt}\n")

        temp_output_path = os.path.join(output_dir, f"temp_story_page_{idx}.png")
        final_output_path = os.path.join(output_dir, f"story_page_{idx}.png")

        scene_image = generate_scene_image(base_image_path, prompt, temp_output_path,seed=12345 + idx, denoising_strength=1.5)
        if scene_image:
            final_image = add_text_to_image(scene_image, paragraph, final_output_path)
            if final_image:
                images.append(final_image)
            else:
                print(f"Failed to add text overlay for scene {idx}.")
        else:
            print(f"Failed to generate image for scene {idx}.")

    return images


if __name__ == "__main__":
    character_name = input("Enter the character's name: ")
    theme = input("Enter the theme/lesson of the story: ")
    style = input("Enter the story style (e.g., children, fantasy, serious): ")
    hair = input("Enter the hair description (e.g., 'short curly brown'): ")
    eyes = input("Enter the eye color (e.g., 'blue', 'green', etc.'): ")
    clothes = input("Enter the clothing (e.g., 'red hat and a yellow jacket'): ")
    age = input("Enter the character's age (e.g., 7, 8, 11, etc.): ")

    character_description = (
        f"A children's book illustration of {character_name}, a {age}-year-old child with {hair}, {eyes} eyes, "
        f"wearing {clothes}. The art style is vivid natural children illustration, bright, and colorful."
    )

    story = generate_story(character_name, theme, style)
    print("\nGenerated Story:\n", story)

    base_image_path = "base_image.png"
    generate_base_image(character_description, base_image_path)

    output_dir = "generated_images"
    print("\nGenerating images for the story...")
    images = generate_story_images(story, character_description, base_image_path, output_dir)

    print("\nGenerated Images:")
    for img in images:
        print(img)
