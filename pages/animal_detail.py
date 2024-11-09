# this is where the animal details will be displayed
import streamlit as st
import json
import replicate

with open('../test_data/giant_panda.json') as json_file: 
    data = json.load(json_file) 
    json_file.close()

# Display a slider for selecting an evolution stage
stage = st.select_slider(
    "Select an evolution stage",
    options=list(data.keys()),  
)

selected_stage_data = data[stage]

output = replicate.run(
      "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
      input={
        "width": 1024,
        "height": 1024,
        "prompt": selected_stage_data["prompt"],
        "refine": "expert_ensemble_refiner",
        "num_outputs": 1,
        "apply_watermark": False,
        "negative_prompt": "low quality, worst quality",
        "num_inference_steps": 25
       }
     )

st.write("**Evolution Stage:**", stage)
st.write("**Description:**", selected_stage_data["description"])
# st.image(
#     "https://s3-us-west-2.amazonaws.com/uw-s3-cdn/wp-content/uploads/sites/6/2017/11/04133712/waterfall.jpg",
#     # selected_stage_data["imageUrl"],
#     width=400, # Manually Adjust the width of the image as per requirement
#     caption=f"{stage} illustration"
# )
st.image(output)