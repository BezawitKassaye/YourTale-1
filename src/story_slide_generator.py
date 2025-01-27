import os
import requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Initialize OpenAI client
openai_client = OpenAI(api_key=API_KEY)


def generate_story(character_name, theme, style):
    """
    Generate a story using GPT.
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
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating story: {e}")
        return None


def generate_collage_prompt(character_name, theme, style, hair, eyes, clothes, age, skin_color, story):
    """
    Generate a cohesive prompt for a story collage using GPT-4.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that generates visual prompts for collages."},
                {
                    "role": "user",
                    "content": (
                        f"The main character of the story is {character_name}, a {age}-year-old child with {hair}, {eyes} eyes, "
                        f"{skin_color} skin, wearing {clothes}. The story teaches a lesson about {theme} and is written in a "
                        f"{style} style. Based on the following story, generate a detailed visual prompt for a single image collage "
                        f"that illustrates key scenes and elements from the story:\n\n{story}\n\n"
                        "The collage should include the character in various actions, settings from the story, and other relevant elements. "
                        "The style should be colorful, vibrant, and consistent with a children's storybook."
                    )
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating collage prompt: {e}")
        return None


def condense_collage_prompt_with_gpt(base_prompt):
    """
    Use GPT-4 to condense a detailed collage prompt while retaining critical details.
    """
    if not base_prompt:
        print("You didn't provide a specific prompt to condense.")
        return None

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that condenses detailed prompts for DALL-E."},
                {
                    "role": "user",
                    "content": (
                        f"The following prompt is too long for DALL-E to process (over 1000 characters). "
                        "Condense it to include only the critical details about the character, their actions, "
                        "and the environment, ensuring it remains coherent and descriptive:\n\n{base_prompt}"
                    )
                }
            ],
            max_tokens=200,
            temperature=0.5
        )
        condensed_prompt = response.choices[0].message.content.strip()
        print("\nCondensed Prompt:\n", condensed_prompt)
        return condensed_prompt
    except Exception as e:
        print(f"Error condensing prompt with GPT-4: {e}")
        return base_prompt  # Fallback to the original prompt if condensing fails


def generate_dalle_image_with_condensed_prompt(prompt, output_path):
    """
    Generate a collage image using DALL-E with a condensed prompt.
    """
    condensed_prompt = condense_collage_prompt_with_gpt(prompt)  # Condense the prompt first
    if not condensed_prompt:
        print("Failed to generate a condensed prompt.")
        return None

    try:
        # Generate image with the condensed prompt
        response = openai_client.images.generate(
            prompt=condensed_prompt,
            n=1,
            size="1024x1024"
        )

        # Access the image URL from the response
        image_url = response.data[0].url  # Correctly parse the first image URL
        print(f"Image URL: {image_url}")

        # Download and save the image locally
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                for chunk in response:
                    file.write(chunk)
            print(f"Collage image saved as {output_path}")
            return output_path
        else:
            print(f"Failed to download image. HTTP Status: {response.status_code}")
        return None
    except Exception as e:
        print(f"Error generating image with DALL-E: {e}")
        return None


def add_paragraph_overlays(collage_path, story, output_path, font_path="assets/fonts/CaveatBrush-Regular.ttf", font_size=24):
    """
    Add story paragraphs as text overlays to the collage.
    """
    try:
        image = Image.open(collage_path).convert("RGBA")
        draw = ImageDraw.Draw(image)

        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found at {font_path}")
        font = ImageFont.truetype(font_path, font_size)

        paragraphs = [p.strip() for p in story.split("\n\n") if p.strip()]
        num_paragraphs = len(paragraphs)

        # Divide the image into sections for each paragraph
        section_height = image.height // num_paragraphs
        for idx, paragraph in enumerate(paragraphs):
            y_start = idx * section_height
            x_margin = 20
            text_x = x_margin
            text_y = y_start + (section_height // 2) - (font_size * len(paragraph.splitlines()) // 2)

            draw.multiline_text((text_x, text_y), paragraph, font=font, fill="white")

        image.save(output_path)
        print(f"Final collage with overlays saved as {output_path}")
        return output_path
    except Exception as e:
        print(f"Error adding paragraph overlays: {e}")
        return None


if __name__ == "__main__":
    # Gather user input
    character_name = input("Enter the character's name: ")
    theme = input("Enter the theme/lesson of the story: ")
    style = input("Enter the story style (e.g., children, fantasy, serious): ")
    hair = input("Enter the hair description (e.g., 'short curly brown'): ")
    eyes = input("Enter the eye color (e.g., 'blue', 'green', etc.'): ")
    clothes = input("Enter the clothing (e.g., 'red hat and a yellow jacket'): ")
    age = input("Enter the character's age (e.g., 7, 8, 11, etc.): ")
    skin_color = input("Enter the skin color (e.g., 'light brown', 'dark', etc.'): ")

    # Generate a short story
    story = generate_story(character_name, theme, style)
    print("\nGenerated Story:\n", story)

    # Generate a detailed collage prompt
    detailed_collage_prompt = generate_collage_prompt(character_name, theme, style, hair, eyes, clothes, age, skin_color, story)

    # Generate the collage image using the condensed prompt
    collage_image_path = "condensed_collage_image.png"
    collage_image = generate_dalle_image_with_condensed_prompt(detailed_collage_prompt, collage_image_path)

    # Add paragraph overlays
    if collage_image:
        final_image_path = "final_collage_with_paragraphs.png"
        add_paragraph_overlays(collage_image, story, final_image_path)
