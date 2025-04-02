import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from geopy.distance import geodesic
from datetime import datetime
import json

# Default coordinates (NIT Calicut)
DEFAULT_LATITUDE = 10.906252
DEFAULT_LONGITUDE = 76.898003

# Default parking locations (latitude, longitude, name)
PARKING_SPOTS = [
    {"name": "AB1 PARKING LOT", "coordinates": [10.901179, 76.902300]},
    {"name": "AB2 PARKING LOT", "coordinates": [10.904198, 76.898769]},
    {"name": "AB3 PARKING LOT", "coordinates": [10.906691, 76.897503]},
    {"name": "AB3 PARKING LOT2", "coordinates": [10.908491, 76.897149]},
    {"name": "MAIN GROUND PARKING", "coordinates": [10.903033, 76.904000]},
    {"name": "Swimming Pool PARKING", "coordinates": [10.905685, 76.899035]},
    {"name": "ASB PARKING", "coordinates": [10.904242, 76.901741]}
]

# Streamlit UI Setup
st.set_page_config(layout="wide", page_title="Parking Navigation", page_icon="🚗")
st.title("🚗 Parking Navigation System")
st.write("Find the nearest parking spot based on your current location.")
st.divider()

# JavaScript to get browser location
get_location_js = """
<script>
function updateLocation(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    window.parent.postMessage({
        "type": "locationUpdate",
        "latitude": latitude,
        "longitude": longitude
    }, "*");
}

function handleError(error) {
    let errorMessage = "Error getting location: ";
    switch(error.code) {
        case error.PERMISSION_DENIED:
            errorMessage += "User denied the request for Geolocation.";
            break;
        case error.POSITION_UNAVAILABLE:
            errorMessage += "Location information is unavailable.";
            break;
        case error.TIMEOUT:
            errorMessage += "The request to get user location timed out.";
            break;
        case error.UNKNOWN_ERROR:
            errorMessage += "An unknown error occurred.";
            break;
    }
    window.parent.postMessage({
        "type": "locationError",
        "message": errorMessage
    }, "*");
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(updateLocation, handleError);
} else {
    window.parent.postMessage({
        "type": "locationError",
        "message": "Geolocation is not supported by this browser."
    }, "*");
}
</script>
"""

# Display the JavaScript component
st.components.v1.html(get_location_js, height=0)

# Initialize session state for location
if 'user_location' not in st.session_state:
    st.session_state.user_location = {
        "latitude": DEFAULT_LATITUDE,
        "longitude": DEFAULT_LONGITUDE
    }

# Handle messages from JavaScript
try:
    # In a real Streamlit app, you would use st.experimental_get_query_params()
    # For this example, we'll simulate the message handling
    received_data = {"type": "locationUpdate", "latitude": DEFAULT_LATITUDE, "longitude": DEFAULT_LONGITUDE}
    
    if received_data.get("type") == "locationUpdate":
        st.session_state.user_location = {
            "latitude": received_data["latitude"],
            "longitude": received_data["longitude"]
        }
    elif received_data.get("type") == "locationError":
        st.warning(received_data["message"])
except:
    pass

# Use the location from session state
user_coords = (st.session_state.user_location["latitude"], st.session_state.user_location["longitude"])

# Function to find the nearest parking spot
def find_nearest_parking(user_coords):
    min_distance = float("inf")
    nearest_spot = None
    
    for spot in PARKING_SPOTS:
        distance = geodesic(user_coords, tuple(spot["coordinates"])).km
        if distance < min_distance:
            min_distance = distance
            nearest_spot = spot
    
    return nearest_spot, min_distance

# Get nearest parking location
nearest_spot, nearest_distance = find_nearest_parking(user_coords)

# Create map centered at user's location
m = folium.Map(location=user_coords, zoom_start=16, tiles="CartoDB positron")
folium.Marker(
    user_coords,
    popup="Your Location",
    icon=folium.Icon(color="blue", icon="user")
).add_to(m)

# Add parking spots to the map
for spot in PARKING_SPOTS:
    folium.Marker(
        spot["coordinates"], 
        popup=f"{spot['name']}",
        icon=folium.Icon(color="green" if spot == nearest_spot else "gray")
    ).add_to(m)

# Show nearest parking info
if nearest_spot:
    st.success(f"🚗 Nearest Parking: {nearest_spot['name']} ({nearest_distance:.2f} km away)")

Fullscreen().add_to(m)

# Display the map with wider width
st_folium(m, width=1300, height=600)

st.markdown("---")

if st.button("Reserve You're Parking Space"):
    st.markdown('<meta http-equiv="refresh" content="0; url=https://first-chat-app-bbc0f.web.app/home/parkings/find" />', unsafe_allow_html=True)