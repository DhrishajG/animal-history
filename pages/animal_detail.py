import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from animal_evolution_agent import AnimalEvolutionAgent
import pydeck as pdk

# Function to get animal image from Bing search based on evolutionary stage (now cached)
@st.cache_data
def get_evolution_stage_image_bing_search(animal_name, stage_name, description):
    # Load environment variables from the .env file
    load_dotenv("../.env")
    api_key = os.getenv("BING_SEARCH_API_KEY")
    
    # Construct search query based on animal name and evolutionary stage
    search_term = f"{animal_name} at the {stage_name} evolutionary stage. {description}"
    
    # Set up your API key and endpoint
    image_search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": search_term, "count": 5}  # Adjust count as needed
    
    try:
        # Perform an image search to get image URLs
        image_response = requests.get(image_search_url, headers=headers, params=params)
        print("bing api called")
        image_results = image_response.json()
    
        # Extract image URLs
        image_urls = [img['contentUrl'] for img in image_results.get("value", [])]

        # Return image URLs or an empty list if no images found
        return image_urls if image_urls else None
    except Exception as e:
        st.error(f"Error fetching images: {e}")
        return None

# Load the environment variables and OpenAI key
load_dotenv("../.env")
open_api_key = os.getenv("OPEN_API_KEY")

# Streamlit UI Setup
st.header('Animal Evolution Stages')

# Prompt for animal name
animal_name = st.text_input("Enter Animal Name:")

# Initialize session state for animal data and previous animal name
if "animal_data" not in st.session_state:
    st.session_state.animal_data = None
if "prev_animal_name" not in st.session_state:
    st.session_state.prev_animal_name = None
if "animal_images" not in st.session_state:
    st.session_state.animal_images = {}

# If animal name is entered and has changed, fetch new data
if animal_name and animal_name != st.session_state.prev_animal_name:
    agent = AnimalEvolutionAgent(open_api_key)
    animal_data = agent.get_animal_evolution_story(animal_name)
    
    try:
        # Parse and store the new data
        st.session_state.animal_data = json.loads(animal_data[7:-3])
        if len(st.session_state.animal_data) != 5:
            st.session_state.animal_data = None
            st.error("Something went wrong! Please try again.")
        st.session_state.prev_animal_name = animal_name

        # Preload all images for the animal and store in session state
        if animal_name not in st.session_state.animal_images:
            # Preload images for each evolutionary stage
            images = {}
            for stage, stage_data in st.session_state.animal_data.items():
                img_urls = get_evolution_stage_image_bing_search(
                    animal_name, stage, stage_data["description"]
                )
                if img_urls:
                    images[stage] = img_urls[0]  # Save the first image for each stage
            st.session_state.animal_images[animal_name] = images

    except json.JSONDecodeError as e:
        st.error(f"Error parsing data: {e}")
        st.stop()  # Stop further execution if JSON parsing fails

# Check if animal data is available before proceeding
if st.session_state.animal_data:
    # Retrieve data from session state
    data = st.session_state.animal_data
    
    # Display a slider for selecting an evolution stage
    stage = st.select_slider(
        "Select an Evolution Stage",
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
    
    # Retrieve preloaded image URLs from session state for the selected stage
    img_urls = st.session_state.animal_images.get(animal_name, {}).get(stage)

    if img_urls:
        # Display the preloaded image
        st.image(img_urls, caption=f"{stage} Illustration")
    else:
        # Fallback: display a placeholder image if no image is found
        st.image("https://via.placeholder.com/1024x512?text=No+Image+Available", caption="No image available")

    # Display map with countries native to the animal
    st.write("**Native To:**")
    
    geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    highlighted_countries = selected_stage_data["country"]

    # Load and filter GeoJSON data for the selected countries
    geojson_data = requests.get(geojson_url).json()
    filtered_features = [
        feature for feature in geojson_data["features"]
        if feature["properties"]["name"] in highlighted_countries
    ]
    
    filtered_geojson = {"type": "FeatureCollection", "features": filtered_features}

    # Pydeck layer for filtered countries
    layer = pdk.Layer(
        "GeoJsonLayer",
        data=filtered_geojson,
        get_fill_color="[200, 30, 30, 140]",  # Red color with transparency
        get_line_color=[255, 255, 255],       # White border for countries
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        latitude=27.0, longitude=85.0, zoom=3, min_zoom=2, max_zoom=5, pitch=0, bearing=0
    )

    if len(filtered_features) == 0:
        st.error(f"No countries found for {selected_stage_data['country'][0]}")

    # Render map with Streamlit
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}"}))
