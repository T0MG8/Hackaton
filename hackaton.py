import streamlit as st
import folium
from streamlit_folium import folium_static

# Titel van de app
st.title("Interactieve Kaart met Steden en Spoorlijnen")

# Coördinaten Schiphol
latitude = 52.3676
longitude = 4.9041

# Straal van de cirkel
radius = 1050000

# Kaart aanmaken
m = folium.Map(location=[latitude, longitude], zoom_start=4)

# Cirkel toevoegen
folium.Circle(
    location=[latitude, longitude],
    radius=radius,  
    color='blue', 
    fill=True,
    fill_color='blue',
    fill_opacity=0.3
).add_to(m)

# OpenRailWay toevoegen
folium.TileLayer(
    tiles='https://tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png',
    attr='&copy; OpenRailwayMap contributors',
    name='Railways',
    overlay=True 
).add_to(m)

# Markers toevoegen
steden = {
    "Amsterdam": (52.3676, 4.9041),
    "Antwerpen": (51.2194475, 4.4024643),
    "Brussel": (50.8465573, 4.351697),
    "Hamburg": (53.5510846, 9.9936819),
    "Berlijn": (52.5170365, 13.3888599),
    "München": (48.1351253, 11.5819805),
    "Luxemburg-stad": (49.6294233, 6.0211741),
    "Nice": (43.7009385, 7.2683912),
    "Marseille": (43.296482, 5.36978),
    "Venetië": (45.4408474, 12.3155151),
    "Milaan": (45.4668, 9.1905),
    "Geneve": (46.2043907, 6.1431577),
    "Zurich": (47.3744489, 8.5410422),
    "Wenen": (48.2081743, 16.3738189),
    "Praag": (50.0755381, 14.4378005),
    "Londen": (51.507351, -0.12766),
    "Kopenhagen": (55.6760968, 12.5683371),
    "Parijs": (48.856663, 2.351556),
    "Frankfurt": (50.1109221, 8.6821267)
}

for stad, coords in steden.items():
    folium.Marker(
        location=coords,
        popup=stad,
        tooltip=stad
    ).add_to(m)

# Layer control toevoegen
folium.LayerControl().add_to(m)

# Streamlit-kaart weergeven
folium_static(m)