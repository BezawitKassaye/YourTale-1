from openai import OpenAI
import openai
client = OpenAI(api_key=API_KEY)
import requests
from flask import Flask, request, jsonify
import os

# Import your API key securely
from config import API_KEY  # Ensure you have your OpenAI API key in a config file

# Initialize OpenAI API client

# Initialize Flask app
app = Flask(__name__)

# @app.route('/')
# def home():
#     return 'Welcome to the Story Generator!'
# API endpoint to generate story and image
# @app.route('/generate_story')#, methods = ['POST']) #generate_story', methods=['POST'])
@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.get_json()

    # Get parameters from the request
    character_name = data.get('character_name')
    theme = data.get('theme')
    style = data.get('style')

    # Generate the story text using GPT-3.5 (or GPT-4)
    story_text = generate_story_text(character_name, theme, style)

    # Generate an image based on the story text using OpenAI DALL-E or another image API
    image_url = generate_image(story_text)

    # Return the story text and image URL in the response
    return jsonify({
        'story_text': story_text,
        'image_url': image_url
    })


# Function to generate story text using GPT-3.5
def generate_story_text(character_name, theme, style):
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",  # You can also try "gpt-4"
        messages=[
            {"role": "system", "content": "You are a creative story generator."},
            {
                "role": "user",
                "content": f"Write a short {style} story about a character named {character_name} that teaches a lesson about {theme}.",
            },
        ])
        # Access the story text from the response
        story = response.choices[0].message.content.strip()
        return story
    except Exception as e:
        print(f"Error generating story: {e}")
        return "Oops! Something went wrong while generating your story."

# Function to generate an image using OpenAI DALL-E or similar API
def generate_image(story_text):
    try:
        # Generate an image based on the story text using DALL-E or another image API
        image_response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers={'Authorization': f'Bearer {openai.api_key}'},
            json={
                'prompt': story_text,
                'n': 1,
                'size': '512x512'
            }
        )

        # Extract the image URL from the response
        image_data = image_response.json()
        image_url = image_data['data'][0]['url']
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return "Oops! Something went wrong while generating the image."


@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.get_json()
    character_name = data.get('character_name')
    theme = data.get('theme')
    style = data.get('style')

    # Generate the story
    story_text = generate_story_text(character_name, theme, style)

    # Generate images with overlaid text
    final_images = generate_images_for_story_with_text(story_text)

    # Return story and final images
    return jsonify({
        'story_text': story_text,
        'images': final_images
    })

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
