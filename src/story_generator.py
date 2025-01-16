# from config import API_KEY
# from openai import OpenAI
# from PIL import Image, ImageDraw, ImageFont
# import requests
# import openai
# import os
# client = OpenAI(api_key=API_KEY)
# from openai import OpenAI
# import time

# #client = OpenAI()
# #from openai import OpenAI

# client = OpenAI(api_key=API_KEY)

# # Set API key

# def generate_story(character_name, theme, style):
#     try:
#         response = client.chat.completions.create(model="gpt-3.5-turbo",  # Use "gpt-4" or "gpt-3.5-turbo"
#         messages=[
#             {"role": "system", "content": "You are a creative story generator."},
#             {
#                 "role": "user",
#                 "content": f"Write a short {style} story  about a child character named {character_name} that teaches a lesson about {theme}. Make sure each paragraph is exactly two consise sentences long. ",
#             },
#         ])
#         story = response.choices[0].message.content.strip()
#         return story
#     except Exception as e:
#         print(f"Error generating story: {e}")
#         return "Oops! Something went wrong while generating your story."

# # def generate_story(character_name, theme, style):
# #     """
# #     Generates a story using GPT based on the character, theme, and style.
# #     """
# #     try:
# #         response = client.chat.completions.create(
# #             model="gpt-3.5-turbo",
# #             messages=[
# #                 {"role": "system", "content": "You are a creative story generator."},
# #                 {
# #                     "role": "user",
# #                     "content": f"Write a short {style} story about a character named {character_name} that teaches a lesson about {theme}. Make each paragraph concise."
# #                 },
# #             ]
# #         )
# #         story = response.choices[0].message.content.strip()
# #         return story
# #     except Exception as e:
# #         print(f"Error generating story: {e}")
# #         return "Oops! Something went wrong while generating your story."





# def generate_image(prompt):
#     """
#     Generates an image based on the provided prompt using OpenAI's image generation API.
#     """
#     try:
#         image_response = client.images.generate(
#             model="dall-e-3",
#             prompt=prompt,
#             n=1,
#             size="1024x1024",
#             quality="hd",
#             style="natural" 
            
#         )
#         image_url = image_response.data[0].url
#         return image_url
#     except Exception as e:
#         print(f"Error generating image: {e}")
#         return None

# def truncate_prompt(prompt, max_length=1000):
#     """
#     Truncates the prompt to ensure it is within the maximum length allowed by the API.
#     """
#     if len(prompt) > max_length:
#         return prompt[:max_length].strip() + "..."
#     return prompt

# def summarize_prompt(prompt, max_length=1000):
#     """
#     Summarizes the prompt using GPT to ensure it fits within the maximum length.
#     """
#     if len(prompt) <= max_length:
#         return prompt  # No need to summarize if it's already short enough

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that summarizes text."},
#                 {"role": "user", "content": f"Summarize this for a children's story illustration: {prompt}"}
#             ],
#             max_tokens=150
#         )
#         summarized = response.choices[0].message.content.strip()
#         return summarized
#     except Exception as e:
#         print(f"Error summarizing prompt: {e}")
#         return truncate_prompt(prompt, max_length)

# def wrap_text(text, font, max_width):
#     """
#     Wraps text into multiple lines to fit within the specified width using font.getbbox.
#     """
#     words = text.split()
#     lines = []
#     current_line = []
#     for word in words:
#         current_line.append(word)
#         # Use font.getbbox to calculate the size of the current line
#         line_width = font.getbbox(' '.join(current_line))[2]  # [2] is the width
#         if line_width > max_width:
#             current_line.pop()  # Remove the last word to fit within max_width
#             lines.append(' '.join(current_line))
#             current_line = [word]  # Start a new line with the current word
#     lines.append(' '.join(current_line))  # Add the last line
#     return '\n'.join(lines)


# def add_text_to_image(image_url, text, output_path, font_path="assets/fonts/CaveatBrush-Regular.ttf", font_size=24):
#     """
#     Adds wrapped text to an image, overlaying it at the bottom of the image.
#     """
#     # import requests
#     # from PIL import Image, ImageDraw, ImageFont
#     # import os

#     # Resolve font path
#     if not os.path.exists(font_path):
#         raise FileNotFoundError(f"Font file not found at {font_path}")

#     # Download the image
#     response = requests.get(image_url, stream=True)
#     image = Image.open(response.raw).convert("RGBA")

#     draw = ImageDraw.Draw(image)
#     try:
#         font = ImageFont.truetype(font_path, font_size)
#     except OSError as e:
#         print(f"Error loading font: {e}. Falling back to default font.")
#         font = ImageFont.load_default()

#     # Wrap text to fit within the image width
#     max_width = image.width - 40  # Leave 20px padding on each side
#     wrapped_text = wrap_text(text, font, max_width)

#     # Calculate text position
#     text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
#     text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
#     x = (image.width - text_width) / 2
#     y = image.height - text_height - 20  # Place text 20px above the bottom edge

#     # Add a semi-transparent background for the text
#     background = Image.new("RGBA", (text_width + 40, text_height + 20), (0, 0, 0, 128))
#     image.paste(background, (int(x) - 20, int(y) - 10), mask=background)

#     # Draw the wrapped text
#     draw.multiline_text((x, y), wrapped_text, font=font, fill="white", align="center")
#     image.save(output_path, "PNG")
#     return output_path




# def generate_visual_prompts(story_parts, character_name, overall_style):
#     """
#     Dynamically generates visual prompts with a consistent theme for the character and evolving story settings.
    
#     Args:
#         story_parts (list): Parts of the story to describe different scenes.
#         character_name (str): The name of the main character.
#         overall_style (str): The desired art style for the illustrations (e.g., "storybook-style").
        
#     Returns:
#         list: A list of prompts for generating visuals dynamically tied to the evolving story.
#     """
#     prompts = []
#     previous_scene_reference = f"A children's illustration in {overall_style}, featuring {character_name}. "
    
#     for idx, part in enumerate(story_parts):
#         if part.strip():
#             if idx == 0:
#                 # First scene: no reference to previous images
#                 prompt = (
#                     f"{previous_scene_reference}This scene shows: {part.strip()}"
#                 )
#             else:
#                 # Subsequent scenes reference the previous scene
#                 prompt = (
#                     f"{previous_scene_reference}Continuing from the previous scene, this part shows: {part.strip()}"
#                 )
        
#         # Update the reference to the latest scene for continuity
#         previous_scene_reference = (
#             f"A children's illustration in {overall_style}, featuring {character_name}. "
#             f"The setting evolves to: {part.strip()}. "
#         )
        
#         prompts.append(prompt)
    
#     return prompts




# def generate_images_for_story_with_text(story, character_name, style):
#     """
#     Generates images with text overlays for each part of the story.
#     """
#     story_parts = story.split("\n")  # Split the story into paragraphs
#     visual_prompts = generate_visual_prompts(story_parts, character_name, style)

#     final_images = []
#     for i, (prompt, part) in enumerate(zip(visual_prompts, story_parts)):
#         print(f"Generating image for prompt {i + 1}: {prompt}")  # Debugging line to print each prompt
#         image_url = generate_image(prompt)
#         if image_url:
#             output_path = os.path.join("generated_images", f"story_page_{i+1}.png")
#             final_image = add_text_to_image(image_url, part, output_path)
#             final_images.append(final_image)
#         time.sleep(3)  # Rate limit handling
#     return final_images



# if __name__ == "__main__":
#     import os

#     # Get user input
#     character_name = input("Enter the character's name: ")
#     theme = input("Enter the theme of the story: ")
#     style = input("Enter the story style (e.g., children, age, funny, serious): ")

#     # Generate the story
#     story = generate_story(character_name, theme, style)
#     print("\nGenerated Story:")
#     print(story)

#     # Create output directory for images
#     output_dir = "generated_images"
#     os.makedirs(output_dir, exist_ok=True)

#     # Generate images with text overlays for each part of the story
#     print("\nGenerating images with text overlays...")
#     final_images = generate_images_for_story_with_text(story, character_name, style)

#     # Print all generated image paths
#     print("\nGenerated Images:")
#     for i, image_path in enumerate(final_images, 1):
#         print(f"Image {i}: {image_path}")

#     print(f"\nAll images have been saved locally in the '{output_dir}' directory!")




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
    key=API_STABLE,  # Use the Stability AI API key from config
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0"  # Choose the engine
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=API_KEY)  # Use the OpenAI API key from config

def generate_story(character_name, theme, style):
    """
    Generates a story using OpenAI GPT.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative story generator."},
                {
                    "role": "user",
                    "content": f"Write a short {style} story about a child character named {character_name} that teaches a lesson about {theme}. Make sure each paragraph is exactly two concise sentences long.",
                },
            ],
        )
        story = response.choices[0].message.content.strip()
        return story
    except Exception as e:
        print(f"Error generating story: {e}")
        return "Oops! Something went wrong while generating your story."

def generate_image(prompt, output_path):
    """
    Generates an image using Stability AI based on the given prompt and saves it.
    """
    try:
        answers = stability_api.generate(
            prompt=prompt,
            seed=12345,  # Optional: for reproducibility
            steps=50,  # Number of diffusion steps
            cfg_scale=8.0,  # Adjust adherence to the prompt
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
                    print(f"Image saved as {output_path}")
                    return output_path
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def add_text_to_image(image_path, text, output_path, font_path="assets/fonts/CaveatBrush-Regular.ttf", font_size=24):
    """
    Adds wrapped text to an image, overlaying it at the bottom of the image.
    """
    try:
        image = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(image)

        # Load the font
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found at {font_path}")
        font = ImageFont.truetype(font_path, font_size)

        # Wrap text to fit within the image width
        max_width = image.width - 40  # Leave 20px padding
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

        # Calculate text position
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        x = (image.width - text_width) / 2
        y = image.height - text_height - 20  # 20px above the bottom

        # Add a semi-transparent background
        background = Image.new("RGBA", (text_width + 40, text_height + 20), (0, 0, 0, 128))
        image.paste(background, (int(x) - 20, int(y) - 10), mask=background)

        # Draw the text
        draw.multiline_text((x, y), wrapped_text, font=font, fill="white", align="center")
        image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Error adding text to image: {e}")
        return None

def generate_visual_prompts(story_parts, character_name, overall_style):
    """
    Dynamically generates unique and concise visual prompts with a consistent theme.
    """
    prompts = []
    previous_scene_reference = f"A children's illustration in {overall_style}, featuring {character_name}."
    
    for idx, part in enumerate(story_parts):
        if part.strip():
            # Ask GPT to extract the main visual elements from the paragraph
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant that generates concise visual descriptions for illustrations."},
                        {"role": "user", "content": f"Generate a visual description for this paragraph: '{part.strip()}'."}
                    ],
                    max_tokens=50
                )
                visual_description = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error generating visual description for paragraph {idx + 1}: {e}")
                visual_description = part.strip()  # Fallback to the full paragraph

            # Construct the final prompt
            if idx == 0:
                prompt = f"{previous_scene_reference} This scene shows: {visual_description}"
            else:
                prompt = f"{previous_scene_reference} Continuing from the previous scene, this part shows: {visual_description}"
            
            prompts.append(prompt)
    
    return prompts



def generate_images_for_story(story, character_name, style):
    """
    Generates images with text overlays for each part of the story using unique prompts.
    """
    story_parts = story.split("\n")  # Split the story into paragraphs
    visual_prompts = generate_visual_prompts(story_parts, character_name, style)

    output_dir = "generated_images"
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
    final_images = []

    seen_prompts = set()  # Keep track of prompts we've processed

    for i, (prompt, part) in enumerate(zip(visual_prompts, story_parts)):
        if prompt in seen_prompts:
            print(f"Skipping duplicate prompt for paragraph {i + 1}.")
            continue
        seen_prompts.add(prompt)  # Mark this prompt as processed

        print(f"Generating image for prompt {i + 1}: {prompt}")
        image_path = os.path.join(output_dir, f"story_page_{i + 1}_raw.png")
        output_path = os.path.join(output_dir, f"story_page_{i + 1}.png")

        # Generate image using Stability AI
        generated_image_path = generate_image(prompt, image_path)
        if generated_image_path:
            # Add text overlay
            final_image_path = add_text_to_image(generated_image_path, part, output_path)
            final_images.append(final_image_path)
        time.sleep(3)  # Avoid hitting rate limits

    return final_images


if __name__ == "__main__":
    # Get user input
    character_name = input("Enter the character's name: ")
    theme = input("Enter the theme of the story: ")
    style = input("Enter the story style (e.g., children, fantasy, serious): ")

    # Generate the story
    story = generate_story(character_name, theme, style)
    print("\nGenerated Story:")
    print(story)

    # Generate images for the story
    print("\nGenerating images with text overlays...")
    images = generate_images_for_story(story, character_name, style)

    # Display all generated image paths
    print("\nGenerated Images:")
    for i, image in enumerate(images, 1):
        print(f"Image {i}: {image}")

    print("\nAll images have been saved locally in the 'generated_images' directory!")
