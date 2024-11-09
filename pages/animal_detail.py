# this is where the animal details will be displayed
from dotenv import load_dotenv
import streamlit as st
import json
import os

from animal_evolution_agent import AnimalEvolutionAgent
load_dotenv("../.env")
open_api_key = os.getenv("OPEN_API_KEY")

# Prompt for animal name using Streamlit's text input
animal_name = st.text_input("Enter Animal Name:")

# Initialize session state for animal data and previous animal name
if "animal_data" not in st.session_state:
    st.session_state.animal_data = None
if "prev_animal_name" not in st.session_state:
    st.session_state.prev_animal_name = None

# If the animal name is entered and has changed, update the data
if animal_name and animal_name != st.session_state.prev_animal_name:
    agent = AnimalEvolutionAgent(open_api_key)
    animal_data = agent.get_animal_evolution_story(animal_name)
    
    try:
        # Parse and store the new data in session state
        st.session_state.animal_data = json.loads(animal_data[7:-3])
        st.session_state.prev_animal_name = animal_name
    except json.JSONDecodeError as e:
        st.error(animal_data)
        print("Raw API response:", animal_data)
        st.stop()  # Stop further execution if JSON parsing fails

# Check if animal data is available before proceeding
if st.session_state.animal_data:
    # Retrieve data from session state
    data = st.session_state.animal_data
    
    # Display a slider for selecting an evolution stage
    stage = st.select_slider(
        "Select an evolution stage",
        options=list(data.keys()),  
    )
    
    # Retrieve data for the selected stage
    selected_stage_data = data[stage]
    
    # Display selected evolution stage details
    st.write("**Evolution Stage:**", stage)
    st.write("**Description:**", selected_stage_data["description"])
    
    # Display the image if available
    if "imageUrl" in selected_stage_data:
        st.image(
            selected_stage_data["imageUrl"],
            caption=f"{stage} illustration"
        )