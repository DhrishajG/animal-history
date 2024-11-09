import os
import json
import streamlit as st
from dotenv import load_dotenv
from animal_evolution_agent import AnimalEvolutionAgent
from openai import OpenAI

# Function to generate image for a given stage description
def generate_stage_image(animal_name, stage, description, open_api_key):
    client = OpenAI(api_key=open_api_key)
    prompt = f"An image of {animal_name} at the {stage} evolutionary stage. {description}"
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

# Initialize environment and API key
load_dotenv("../.env")
open_api_key = os.getenv("OPEN_API_KEY")

# Streamlit input for the animal name
animal_name = st.text_input("Enter Animal Name:")

# Initialize session state for data
if "animal_data" not in st.session_state:
    st.session_state.animal_data = None
if "prev_animal_name" not in st.session_state:
    st.session_state.prev_animal_name = None
if "animal_images" not in st.session_state:
    st.session_state.animal_images = {}

# Fetch and cache data only if animal name is entered and changed
if animal_name and animal_name != st.session_state.prev_animal_name:
    agent = AnimalEvolutionAgent(open_api_key)
    animal_data = agent.get_animal_evolution_story(animal_name)
    
    try:
        # Parse animal data and cache it
        st.session_state.animal_data = json.loads(animal_data[7:-3])
        st.session_state.prev_animal_name = animal_name

        # Generate and cache images for each stage
        st.session_state.animal_images = {}
        for stage, details in st.session_state.animal_data.items():
            description = details["description"]
            image_url = generate_stage_image(animal_name, stage, description, open_api_key)
            if image_url:
                st.session_state.animal_images[stage] = image_url

    except json.JSONDecodeError as e:
        st.error("Failed to parse animal data.")
        st.stop()  # Stop further execution if JSON parsing fails

# Check if animal data and images are available before proceeding
if st.session_state.animal_data and st.session_state.animal_images:
    data = st.session_state.animal_data
    images = st.session_state.animal_images

    # Display slider for selecting an evolution stage
    stage = st.select_slider("Select an evolution stage", options=list(data.keys()))
    
    # Retrieve selected stage details and display them
    selected_stage_data = data[stage]
    st.write("**Evolution Stage:**", stage)
    st.write("**Description:**", selected_stage_data["description"])
    
    # Display cached image for selected stage
    if stage in images:
        st.image(images[stage], caption=f"{animal_name} - {stage}")
