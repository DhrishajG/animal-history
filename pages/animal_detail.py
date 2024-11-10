# this is where the animal details will be displayed
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from animal_evolution_agent import AnimalEvolutionAgent
import pydeck as pdk
import geopandas as gpd

import math

load_dotenv("../.env")
open_api_key = os.getenv("OPEN_API_KEY")

st.header('brat')

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
        if len(st.session_state.animal_data) != 5:
            st.session_state.animal_data = None
            st.error("Something went wrong! Please try again")
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
    st.write("**Time Period:**", selected_stage_data["time_period"])
    st.write("**Emotional State:**", selected_stage_data["emotional_state"])
    st.write("**Extinction Story:**", selected_stage_data["extinction_story"])
    st.write("**Year of Extinction:**", selected_stage_data["year_of_extinction"])
    st.write("**Population:**", selected_stage_data["population"])
    
    # Display the image if available
    imgUrl = "https://i.pinimg.com/564x/3a/1d/a3/3a1da35d96a40c0c87564acb18508989.jpg" # placeholder

    if imgUrl:
        st.image(
            imgUrl,
            caption=f"{stage} illustration"
        )

    
    st.write("**Native To:**")

    # URL for world countries GeoJSON data
    geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"

    # List of countries to highlight
    highlighted_countries = selected_stage_data["country"]

    # Load the GeoJSON data
    geojson_data = requests.get(geojson_url).json()

    # Filter GeoJSON features to include only the highlighted countries
    filtered_features = [
        feature for feature in geojson_data["features"]
        if feature["properties"]["name"] in highlighted_countries
    ]

    # Create a new GeoJSON dictionary with only the filtered features
    filtered_geojson = {
        "type": "FeatureCollection",
        "features": filtered_features
    }

    # Define a Pydeck Layer for the filtered GeoJSON data
    layer = pdk.Layer(
        "GeoJsonLayer",
        data=filtered_geojson,
        get_fill_color="[200, 30, 30, 140]",  # Red color with some transparency
        get_line_color=[255, 255, 255],       # White border for highlighted countries
        pickable=True,
        auto_highlight=True
    )

    # Set the map view to focus on Asia
    view_state = pdk.ViewState(
        latitude=27.0,  # Center the map around the region
        longitude=85.0,
        zoom=3,
        min_zoom=2,
        max_zoom=5,
        pitch=0,
        bearing=0
    )

    if len(filtered_features) == 0:
        st.error(selected_stage_data["country"][0])

    # Render the map in Streamlit
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}"}))