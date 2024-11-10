import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from animal_evolution_agent import AnimalEvolutionAgent

from chatbot import AnimalChatbotAgent
import pydeck as pdk
import plotly.express as px


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
    params = {"q": search_term, "count":1}  # Adjust count as needed
    
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

st.set_page_config(layout="wide")


# Streamlit UI Setup
st.header('Tails of Time')

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
        st.session_state.show_chat = False
        st.session_state.chat_history = [{"role": "assistant", "content": ""}]
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
        if type(animal_data) is str:
            st.error(animal_data)
        else:
            st.error("Sorry something went wrong! Try again")
        print("Raw API response:", animal_data)
        st.stop()  # Stop further execution if JSON parsing fails    

# Check if animal data is available before proceeding
if st.session_state.animal_data:
    # Retrieve data from session state
    data = st.session_state.animal_data
    
    # Display a slider for selecting an evolution stage
    options = list(reversed(list(data.keys())))
    stage = st.select_slider(
        "Select an Evolution Stage",
        options=options, 
        value=options[-1], 
    )
    
    # Retrieve data for the selected stage
    selected_stage_data = data[stage]


    col1, col2 = st.columns(2)

    with col1:
# =============================
        # Display selected evolution stage details
        st.write("**Evolution Stage:**", stage)
        st.write("**Description:**", selected_stage_data["description"])
        st.write("**Time Period:**", selected_stage_data["time_period"])
        st.write("**Emotional State:**", selected_stage_data["emotional_state"])
        st.write("**Extinction Story:**", selected_stage_data["extinction_story"])
        st.write("**Year of Extinction:**", selected_stage_data["year_of_extinction"])
        st.write("**Population:**", selected_stage_data["population"])

        mood_level = int(selected_stage_data["number_mood"])
        # Visualizing mood with a color scale and a gauge
        # Create a bar of 10 rectangles to represent mood
        mood_color = "red" if mood_level > 70 else "green" if mood_level < 40 else "yellow"
        
        st.write(f"**Mood Level Visualization:**")

        # Create 10 rectangles to represent mood level (out of 100)
        for i in range(10):
            mood_rect_color = "green" if i * 10 < mood_level else "gray"  # Colors depending on mood level
            st.markdown(f'<div style="width: 80px; height: 20px; background-color: {mood_rect_color}; display: inline-block; margin-right: 5px;"></div>', unsafe_allow_html=True)
    
    with col2: 
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
            auto_highlight=False
        )

        view_state = pdk.ViewState(
            latitude=27.0, longitude=85.0, zoom=0.1, min_zoom=1, max_zoom=1, pitch=0, bearing=0
        )

        if len(filtered_features) == 0:
            st.error(selected_stage_data['country'][0])

        # Render map with Streamlit
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}"}))
    
    # =============================
    '''EXPERIMENTAL CHATBOT AREA'''

    # Initialize chatbot agent with OpenAI API key
    chatbot_agent = AnimalChatbotAgent(open_api_key)

    # Chat button to open chat interface
    if st.button(f"Chat with {stage} now"):
        st.session_state.show_chat = True  # Toggle chat interface visibility
        # Get initial story and set up chat history
        animal_story = chatbot_agent.get_animal_contextual_story(stage, selected_stage_data["time_period"])
        st.session_state.chat_history = [{"role": "assistant", "content": animal_story}]

    # Check if the chat interface should be displayed
    if st.session_state.get("show_chat", False):
        # Use an expander to create a minimizable chat window
        with st.expander(f"Chat with {animal_name} ({stage} stage)", expanded=True):
        
            # if 'something' not in st.session_state:
            #     st.session_state.something = ''

            # def submit():
            #     st.session_state.something = st.session_state.chat_input
            #     st.session_state.chat_input = ''

            # Display chat history
            for msg in st.session_state.chat_history:
                role = "User" if msg["role"] == "user" else f"{animal_name} (Chatbot)"
                st.write(f"**{role}:** {msg['content']}")

            # Input box for user to enter a message
            # user_message = st.text_input("Type your message:", key="chat_input", on_change=submit)
            user_message = st.text_input("Type your message:", key="chat_input")


            # Handle the 'Send' button and add logic to manage message input and response
            if st.button("Send"):
                # Add user message to chat history
                print(f"User Message: {user_message}")
                st.session_state.chat_history.append({"role": "user", "content": user_message})

                # Get the chatbot's response based on the current conversation
                agent_response = chatbot_agent.continue_conversation(stage, selected_stage_data["time_period"], user_message)
                st.session_state.chat_history.append({"role": "assistant", "content": agent_response})