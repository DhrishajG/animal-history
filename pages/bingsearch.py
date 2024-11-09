import requests

# Set up your API key and endpoint
api_key = "2df1772f2bde44648cf075c84cb2d80e"
search_term = "ducati"

# Base URL for Bing Web Search
web_search_url = "https://api.bing.microsoft.com/v7.0/search"
image_search_url = "https://api.bing.microsoft.com/v7.0/images/search"

# Headers with the API key
headers = {"Ocp-Apim-Subscription-Key": api_key}

# Parameters for the search
params = {"q": search_term, "count": 5}  # Adjust count as needed

# Perform a web search to get URLs
web_response = requests.get(web_search_url, headers=headers, params=params)
web_results = web_response.json()

# Extract URLs from the web search results
web_urls = [result['url'] for result in web_results.get("webPages", {}).get("value", [])]

# Perform an image search to get image URLs
image_response = requests.get(image_search_url, headers=headers, params=params)
image_results = image_response.json()

# Extract image URLs from the image search results
image_urls = [img['contentUrl'] for img in image_results.get("value", [])]

# Print results
print("Web URLs:", web_urls)
print("Image URLs:", image_urls)
