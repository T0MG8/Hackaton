import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import pandas as pd
import plotly.express as px
from io import StringIO
import plotly.graph_objects as go

# De base URL en headers
url = "https://api.schiphol.nl/public-flights/flights?includedelays=false&page={}&sort=%2BscheduleTime"
headers = {
    "app_id": "c93492b2",
    "app_key": "16a5764ed747d28fc0c58196e7322a04",
    'ResourceVersion': 'v4'
}

# Een lege lijst om alle vluchtdata op te slaan
all_flights_data = []

# Loop over de pagina's (0 tot 29, dus 30 pagina's)
for page in range(50):
    # Stel de volledige URL samen met de pagina
    page_url = url.format(page)
    
    # Haal de gegevens op van de API
    response = requests.get(page_url, headers=headers)
    data = response.json()  # Verkrijg de JSON reactie
    
    # Haal de 'flights' lijst op uit de response
    flights_data = data.get('flights', [])
    
    # Voeg de gegevens toe aan de lijst
    all_flights_data.extend(flights_data)

# Normaliseer de vluchtgegevens naar een DataFrame
df = pd.json_normalize(all_flights_data)

url = "https://nl.wikipedia.org/wiki/Vliegvelden_gesorteerd_naar_IATA-code"

# Set the headers with a User-Agent
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

# Fetch the HTML content with requests
response = requests.get(url, headers=headers)

# Use StringIO to convert the HTML content to a file-like object
html_content = StringIO(response.text)

# Use pandas to read the table from the HTML content
tables = pd.read_html(html_content)

# Select the table you want (in your case, the correct one based on the structure of the page)
vliegvelden = tables[1]  # Adjust the index based on the correct table

# Zet de lijstkolom om naar een stringkolom door het eerste element te selecteren:
df['route.destinations'] = df['route.destinations'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)

# Verwijder dubbele IATA-codes en behoud alleen de laatste instantie
vliegvelden_clean = vliegvelden.drop_duplicates(subset='IATA', keep='last')

# Maak een mapping van IATA-code naar de bijbehorende luchthavennaam
mapping = vliegvelden_clean.set_index('IATA')['Luchthaven']
mapping2 = vliegvelden_clean.set_index('IATA')['Stad']
mapping3 = vliegvelden_clean.set_index('IATA')['Land']

# Voeg een nieuwe kolom toe aan df door de afkorting te mappen op de juiste luchthavennaam
df['Luchthaven'] = df['route.destinations'].map(mapping)
df['Stad'] = df['route.destinations'].map(mapping2)
df['Land'] = df['route.destinations'].map(mapping3)

df = df[['aircraftRegistration', 'Luchthaven', 'Stad', 'Land', 'flightName']]
stedenlijst= ['Parijs', 'Brussel', 'Antwerpen', 'Praag', 'Londen', 'Hamburg', 'Frankfurt', 'Wenen', 'Luxemburg', 'Milaan', 'Venetië', 'Berlijn', 'München', 'Luxemburg-stad', 'Zurich', 'Marseille', 'Nice', 'Kopenhagen', 'Geneve', 'Luxemburg-Stad']
StedenHackaton= df['Stad'].isin(stedenlijst)
filtered_df = df.loc[StedenHackaton,'Stad']

#-------------------------------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Titel van de app
st.title("Interactieve Kaart met Steden en Spoorlijnen")

# Coördinaten Schiphol
latitude = 52.3676
longitude = 4.9041

# Straal van de cirkel in m
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


# ---------------------------------------------------------------------------------------------------------------------------------------------

st.title("Visualisatie van de Steden Verdeler")

stedenlijst= ['Parijs', 'Brussel', 'Antwerpen', 'Praag', 'Londen', 'Hamburg', 'Frankfurt', 'Wenen', 'Luxemburg', 'Milaan', 'Venetië', 'Berlijn', 'München', 'Luxemburg-stad', 'Zurich', 'Marseille', 'Nice', 'Kopenhagen', 'Geneve', 'Luxemburg-Stad']
StedenHackaton= df['Stad'].isin(stedenlijst)
filtered_df = df.loc[StedenHackaton,'Stad']

# Maak histogram met Plotly
fig8 = go.Figure()

# Voeg histogram-trace toe
fig8.add_trace(go.Histogram(x=filtered_df, marker=dict(color='royalblue')))

# Layout instellingen
fig8.update_layout(
    title="Verdeling van Steden in de Dataset",
    xaxis_title="Steden",
    yaxis_title="Aantal",
    xaxis=dict(tickangle=45),
    bargap=0.1
)

# Toon grafiek in Streamlit
st.plotly_chart(fig8)