import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import pandas as pd
import plotly.express as px
from io import StringIO
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from branca.colormap import linear
from streamlit_folium import st_folium

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Inladen bestanden en HTML
# ------------------------------------------------------------------------------------------------------------------------------------------------------------

@st.cache_data
def load_data_api():
    return pd.read_csv("26-03-2025.csv")
df = load_data_api()

@st.cache_data
def load_data_loc():
    return pd.read_csv("flights_today_master.csv")
livevlucht = load_data_loc()

@st.cache_data
def load_airport_data():
    url = "https://nl.wikipedia.org/wiki/Vliegvelden_gesorteerd_naar_IATA-code"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    html_content = StringIO(response.text)
    
    tables = pd.read_html(html_content)
    return tables[1]  # Pas de index aan als nodig

# Roep de functie aan en cache het resultaat
vliegvelden = load_airport_data()

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

df = df[['aircraftRegistration', 'route.destinations', 'Luchthaven', 'Stad', 'Land', 'flightName']]
stedenlijst= ['Parijs', 'Brussel', 'Antwerpen', 'Praag', 'Londen', 'Hamburg', 'Frankfurt', 'Wenen', 'Luxemburg', 'Milaan', 'Venetië', 'Berlijn', 'München', 'Luxemburg-stad', 'Zurich', 'Marseille', 'Nice', 'Kopenhagen', 'Geneve', 'Luxemburg-Stad']
StedenHackaton= df['Stad'].isin(stedenlijst)
filtered_df = df.loc[StedenHackaton,'Stad']

#-------------------------------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------------------------------------

pagina = st.sidebar.radio("Selecteer een pagina", ['Inleiding', 'Vluchten'])
if pagina == 'Inleiding':
    st.title('Welke '"nutteloze"' vluchten kan Schiphol schrappen in Europa om het geluidsoverlast te verminderen rondom Schiphol.')

# Gegevens
    labels = ['Europa', 'Internationaal']
    sizes = [47.6, 19.2]
    colors = ['blue', 'orange']

    # Maak een Plotly Piechart
    fig = px.pie(
        names=labels,
        values=sizes,
        color=labels,
        color_discrete_map={'Europa': 'blue', 'Internationaal': 'orange'},
        title='Verdeling Europa vs Internationaal'
    )

    # Toon zowel de naam, waarde als percentage
    fig.update_traces(pull=[0.1, 0])  

    # Weergeven in Streamlit
    st.plotly_chart(fig)

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------


    # Titel van de app
    st.title("Interactieve Kaart met Steden en Spoorlijnen")

    # Coördinaten Schiphol
    latitude = 52.3676
    longitude = 4.9041

    # Straal van de cirkel in m
    radius = 1000000

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

    stad_kleuren = {
        'Londen': 'blue',
        'Parijs': 'red',
        'Hamburg': 'green',
        'Berlijn': 'purple',
        'München': 'orange',
        'Frankfurt': 'pink',
        'Brussel': 'yellow',
        'Luxemburg': 'brown',
        'Nice': 'lightblue',
        'Marseille': 'darkgreen',
        'Venetië': 'lightred',
        'Milaan': 'darkblue',
        'Geneve': 'lightgreen',
        'Zürich': 'darkviolet',
        'Wenen': 'beige',
        'Praag': 'lightgray',
        'Kopenhagen': 'gold'
    }

    df4= pd.read_csv("ReisTijd.csv", sep=",")

    fig = px.bar(
    df4, 
    x="Bestemming", 
    y="TijdVerschil_min", 
    title="Tijdverschil per Bestemming",
    labels={"Bestemming": "Bestemming", "TijdVerschil_min": "Tijdverschil in Minuten"})

# Draai de x-as labels 90 graden
    fig.update_layout(
        xaxis_tickangle=-90
)

# Streamlit weergeven
    st.title('Barplot van Tijdverschil per Bestemming') 
    st.plotly_chart(fig)


# ---------------------------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------------------------------

elif pagina == 'Vluchten':
    @st.cache_data
    def load_flight_data():
        return {
        "londen": ['BAW441', 'KLM1016', 'KLM1016', 'BAW444', 'BAW438', 'BAW428'],
        "parijs": ['TAY9MS', 'AFR1240', 'HOP1740A', 'FR1140A', 'FR1640', 'HOP1740'],
        "hamburg": ['KLM1758', 'KLM1754', 'KLM1750', 'KLM1752'],
        "berlijn": ['KLM1784', 'NJE622F', 'KLM1782', 'KLM1770', 'EZY5281', 'EZY5285'],
        "munchen": ['DLH2304', 'KLM1854'],
        "frankfurt": ['KLM1818', 'DLH992'],
        "brussel": ['KLM1706', 'KLM1700', 'KLM1702'],
        "luxemburg": ['GER1714', 'KLM1708'],
        "nice": ['KLM1476', 'KLM1472', 'TRA5588', 'KLM1478'],
        "marseille": ['KLM1470', 'KLM1464', 'KLM1466'],
        "venetie": ['EZY7816', 'KLM1628', 'KLM1634'],
        "milaan": ['KLM1614', 'EZY7830', 'ITY112', 'KLM1612', 'EZY7830'],
        "geneve": ['KLM1938', 'KLM1928', 'KLM1932', 'EZY1517', 'KLM1936'],
        "zurich": ['SWR728', 'KLM1920', 'OAW734', 'KLM1926'],
        "wenen": ['AUA371', 'KLM1900', 'AUA377', 'AUA375', 'AUA371'],
        "praag": ['KLM1354', 'EZY7928', 'KLM1360', 'KLM1358', 'EZY7928'],
        "kopenhagen": ['SAS2551', 'SAS549', 'EZY7938', 'KLM1266', 'KLM1270'],
    }

# Roep de vluchtcode-data op en koppel per stad een variabele
    vluchten = load_flight_data()
    londen     = vluchten["londen"]
    parijs     = vluchten["parijs"]
    hamburg    = vluchten["hamburg"]
    berlijn    = vluchten["berlijn"]
    munchen    = vluchten["munchen"]
    frankfurt  = vluchten["frankfurt"]
    brussel    = vluchten["brussel"]
    luxemburg  = vluchten["luxemburg"]
    nice       = vluchten["nice"]
    marseille  = vluchten["marseille"]
    venetie    = vluchten["venetie"]
    milaan     = vluchten["milaan"]
    geneve     = vluchten["geneve"]
    zurich     = vluchten["zurich"]
    wenen     = vluchten["wenen"]
    praag      = vluchten["praag"]
    kopenhagen = vluchten["kopenhagen"]

    # --- Definities voor regio's ---
    noord = ['BAW441', 'BAW428', 'TAY9MS', 'AFR1240', 'KLM1750', 'EZY5281', 'KLM1770',
             'KLM1708', 'KLM1472', 'KLM1464', 'EZY7830', 'KLM1612', 'KLM1928', 'KLM1900',
             'KLM1266', 'KLM1702', 'KLM1700', 'AUA371']
    oost = ['SAS2551', 'KLM1752']
    zuid = ['KLM1016', 'KLM1016', 'BAW444', 'BAW438', 'HOP1740A', 'FR1140A', 'FR1640',
            'HOP1740', 'KLM1758', 'KLM1754', 'KLM1784', 'NJE622F', 'KLM1782', 'EZY5285',
            'DLH2304', 'KLM1854', 'KLM1818', 'DLH992', 'KLM1706', 'GER1714', 'KLM1476',
            'TRA5588', 'KLM1478', 'KLM1470', 'KLM1466', 'EZY7816', 'KLM1628', 'KLM1634',
            'KLM1614', 'ITY112', 'KLM1938', 'KLM1932', 'EZY1517', 'KLM1936', 'SWR728',
            'KLM1920', 'OAW734', 'KLM1926', 'AUA377', 'AUA375', 'KLM1354', 'EZY7928',
            'KLM1360', 'KLM1358', 'SAS549', 'EZY7938', 'KLM1270']
    alle = noord + oost + zuid

    # Streamlit dropdown voor regio-keuze
    keuze = st.selectbox("Kies een regio", ["Alle vluchten", "Noord", "Oost", "Zuid"])
    if keuze == "Alle vluchten":
        gewenste_vluchtcodes = alle
    elif keuze == "Noord":
        gewenste_vluchtcodes = noord
    elif keuze == "Oost":
        gewenste_vluchtcodes = oost
    else:
        gewenste_vluchtcodes = zuid

    # Maak een DataFrame voor een overzicht (optioneel)
    data = {
        'Regio': ['Noord', 'Oost', 'Zuid', 'Totaal'],
        'Aantal Vluchten': [len(noord), len(oost), len(zuid), len(alle)]
    }
    aankomst = pd.DataFrame(data)

    # Definieer kleuren per stad
    stad_kleuren = {
        'Londen': 'blue',
        'Parijs': 'red',
        'Hamburg': 'green',
        'Berlijn': 'purple',
            'München': 'orange',
        'Frankfurt': 'pink',
        'Brussel': 'yellow',
        'Luxemburg': 'brown',
        'Nice': 'lightblue',
        'Marseille': 'darkgreen',
        'Venetië': 'lightred',
        'Milaan': 'darkblue',
        'Geneve': 'lightgreen',
        'Zürich': 'darkviolet',
        'Wenen': 'beige',
        'Praag': 'lightgray',
        'Kopenhagen': 'gold'
    }

# Filter de unieke vluchtcodes uit de live data op basis van de gekozen codes
    unieke_vluchtcodes = livevlucht[livevlucht['FlightNumber'].isin(gewenste_vluchtcodes)]['FlightNumber'].unique()

# Maak de folium-kaart
    m = folium.Map(location=[52.308916, 4.769637], zoom_start=9)

# Voor elke vluchtcode: bepaal de stad en voeg de lijn toe aan de kaart
    for vluchtcode in unieke_vluchtcodes:
        vlucht_data = livevlucht[livevlucht['FlightNumber'] == vluchtcode]
        coordinates = vlucht_data[['Latitude', 'Longitude']].values.tolist()

        # Bepaal de stad op basis van in welke lijst de vluchtcode voorkomt
        if vluchtcode in londen:
            stad = 'Londen'
        elif vluchtcode in parijs:
            stad = 'Parijs'
        elif vluchtcode in hamburg:
            stad = 'Hamburg'
        elif vluchtcode in berlijn:
            stad = 'Berlijn'
        elif vluchtcode in munchen:
            stad = 'München'
        elif vluchtcode in frankfurt:
            stad = 'Frankfurt'
        elif vluchtcode in brussel:
            stad = 'Brussel'
        elif vluchtcode in luxemburg:
            stad = 'Luxemburg'
        elif vluchtcode in nice:
            stad = 'Nice'
        elif vluchtcode in marseille:
            stad = 'Marseille'
        elif vluchtcode in venetie:
            stad = 'Venetië'
        elif vluchtcode in milaan:
            stad = 'Milaan'
        elif vluchtcode in geneve:
            stad = 'Geneve'
        elif vluchtcode in zurich:
            stad = 'Zürich'
        elif vluchtcode in wenen:
            stad = 'Wenen'
        elif vluchtcode in praag:  # Hier is de variabele 'praag' beschikbaar als praal
            stad = 'Praag'
        elif vluchtcode in kopenhagen:
            stad = 'Kopenhagen'
        else:
            stad = 'Onbekend'

        kleur = stad_kleuren.get(stad, 'gray')

        folium.PolyLine(
            coordinates,
            weight=3,
            opacity=1,
            color=kleur,
            popup=f"City: {stad.capitalize()}"
        ).add_to(m)

    # Toon de kaart in Streamlit
    st_folium(m, width=700, height=500)


    blauwstreep = '<div style="width: 20px; height: 3px; background-color: blue; display: inline-block;"></div>'
    redstreep = '<div style="width: 20px; height: 3px; background-color: red; display: inline-block;"></div>'
    greenstreep = '<div style="width: 20px; height: 3px; background-color: green; display: inline-block;"></div>'
    purplestreep = '<div style="width: 20px; height: 3px; background-color: purple; display: inline-block;"></div>'
    orangestreep = '<div style="width: 20px; height: 3px; background-color: orange; display: inline-block;"></div>'
    pinkstreep = '<div style="width: 20px; height: 3px; background-color: pink; display: inline-block;"></div>'
    yellowstreep = '<div style="width: 20px; height: 3px; background-color: yellow; display: inline-block;"></div>'
    brownstreep = '<div style="width: 20px; height: 3px; background-color: brown; display: inline-block;"></div>'
    lightbluestreep = '<div style="width: 20px; height: 3px; background-color: lightblue; display: inline-block;"></div>'
    darkgreenstreep = '<div style="width: 20px; height: 3px; background-color: darkgreen; display: inline-block;"></div>'
    lightredstreep = '<div style="width: 20px; height: 3px; background-color: lightred; display: inline-block;"></div>'
    darkbluestreep = '<div style="width: 20px; height: 3px; background-color: darkblue; display: inline-block;"></div>'
    lightgreenstreep = '<div style="width: 20px; height: 3px; background-color: lightgreen; display: inline-block;"></div>'
    darkvioletstreep = '<div style="width: 20px; height: 3px; background-color: darkviolet; display: inline-block;"></div>'
    beigestreep = '<div style="width: 20px; height: 3px; background-color: beige; display: inline-block;"></div>'
    lightgraystreep = '<div style="width: 20px; height: 3px; background-color: lightgray; display: inline-block;"></div>'
    goldstreep = '<div style="width: 20px; height: 3px; background-color: gold; display: inline-block;"></div>'


    st.markdown(f"{blauwstreep} London | {redstreep} Parijs | {greenstreep} Hamburg | {purplestreep} Berlijn | {orangestreep} München |\
                {pinkstreep} Frankfurt | {yellowstreep} Brussel <br>| {brownstreep} Luxemburg | {lightbluestreep} Nice | {darkgreenstreep} Marseille |\
                     {lightredstreep} Venetië | {darkbluestreep} Milaan | {lightgreenstreep} Geneve | {darkvioletstreep} Zürich |<br>\
                        {beigestreep} Wenen | {lightgraystreep} Praag | {goldstreep} Kopenhagen", unsafe_allow_html=True)

    st.dataframe(aankomst)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Definieer een kleurenschaal: rood (laag) → geel → blauw (hoog)
    colormap = linear.RdYlBu_11.scale(0, 0.7)

    # Maak de kaart
    map_obj = folium.Map(location=[52.3053, 4.7458], zoom_start=10)

    # Voeg cirkels toe op basis van de cumulatieve som van ClimbRate per vluchtcode
    for _, row in livevlucht.iterrows():
        folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
            radius=5,  # Pas dit aan voor grotere/kleinere cirkels
            color=colormap(row['alt_norm']),
            fill=True,
    fill_color=colormap(row['alt_norm']),
            fill_opacity=0.7,
            popup=f"Vlucht: {row['FlightNumber']}<br>Cumulatieve Klimsnelheid: {row['cumsum_ClimbRate']} ft/min"
        ).add_to(map_obj)

    # Voeg de colormap-legend toe
    colormap.caption = "Cumulatieve Klimsnelheid (ClimbRate)"
    map_obj.add_child(colormap)

    # Toon de kaart
    st_folium(map_obj, width=700, height=500)