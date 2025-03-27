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

pd.set_option('display.max_columns', None)

start_date = int(pd.to_datetime('2025-03-25').timestamp())
end_date = int(pd.to_datetime('2025-03-30').timestamp())

response = requests.get(f'https://sensornet.nl/dataserver3/event/collection/nina_events/stream?conditions%5B0%5D%5B%5D=time&conditions%5B0%5D%5B%5D=%3E%3D&conditions%5B0%5D%5B%5D={start_date}&conditions%5B1%5D%5B%5D=time&conditions%5B1%5D%5B%5D=%3C&conditions%5B1%5D%5B%5D={end_date}&conditions%5B2%5D%5B%5D=label&conditions%5B2%5D%5B%5D=in&conditions%5B2%5D%5B2%5D%5B%5D=21&conditions%5B2%5D%5B2%5D%5B%5D=32&conditions%5B2%5D%5B2%5D%5B%5D=33&conditions%5B2%5D%5B2%5D%5B%5D=34&args%5B%5D=aalsmeer&args%5B%5D=schiphol&fields%5B%5D=time&fields%5B%5D=location_short&fields%5B%5D=location_long&fields%5B%5D=duration&fields%5B%5D=SEL&fields%5B%5D=SELd&fields%5B%5D=SELe&fields%5B%5D=SELn&fields%5B%5D=SELden&fields%5B%5D=SEL_dB&fields%5B%5D=lasmax_dB&fields%5B%5D=callsign&fields%5B%5D=type&fields%5B%5D=altitude&fields%5B%5D=distance&fields%5B%5D=winddirection&fields%5B%5D=windspeed&fields%5B%5D=label&fields%5B%5D=hex_s&fields%5B%5D=registration&fields%5B%5D=icao_type&fields%5B%5D=serial&fields%5B%5D=operator&fields%5B%5D=tags')

colnames = pd.DataFrame(response.json()['metadata'])
data = pd.DataFrame(response.json()['rows'])
data.columns = colnames.headers

data['time'] = pd.to_datetime(data['time'], unit = 's')

print(data['time'].min(),data['time'].max())

@st.cache_data
def load_data_api():
    return pd.read_csv("27-03-2025.csv")
df = load_data_api()

@st.cache_data
def load_data_loc():
    return pd.read_csv("flight.csv")
livevlucht = load_data_loc()

@st.cache_data
def load_data2():
    return pd.read_csv("Hackaton2.csv")
df2 = load_data2()


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

#-------------------------------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------------------------------------

pagina = st.sidebar.radio("Selecteer een pagina", ['Inleiding', 'Onderbouwing', 'Vluchten', 'Geluid'])
if pagina == 'Inleiding':
    st.title('Draagt het schrappen van overbodige Europese vluchten bij aan het verminderen van geluidsoverlast rondom Schiphol?')
    st.write('1. Welke Europese vluchten vanaf Schiphol kunnen als overbodig of vervangbaar worden beschouwd?')
    st.write('2. Welke gebieden ervaren de meeste geluidsoverlast van overbodige Europese vluchten?')
    st.write('3. Hoeveel geluidsoverlast wordt veroorzaakt zonder overbodige Europese vluchten?')

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

    st.title('Bronnen')
    st.write('- Schiphol API')
    st.write('- Wikipedia IATA-codes')
    st.write('- ')
    st.write('- ')

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

if pagina == 'Onderbouwing':
    st.title("Interactieve Kaart met Steden en Spoorlijnen")

# Coördinaten Schiphol
    latitude = 52.3676
    longitude = 4.9041

    # Straal van de cirkel in m
    radius = 1000000

    # Kaart aanmaken
    m = folium.Map(location=[latitude, longitude], zoom_start=4)

    # Cirkel toevoegen aan een FeatureGroup, zodat deze later in/uitgeschakeld kan worden
    circle_group = folium.FeatureGroup(name="Cirkel", show=False)

    # Cirkel toevoegen aan de groep
    folium.Circle(
        location=[latitude, longitude],
        radius=radius,  
        color='blue', 
        fill=True,
        fill_color='blue',
        fill_opacity=0.3
    ).add_to(circle_group)



    # OpenRailWay toevoegen
    folium.TileLayer(
        tiles='https://tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png',
        attr='&copy; OpenRailwayMap contributors',
        name='Railways',
        overlay=True 
    ).add_to(m)

    railway_group = folium.FeatureGroup(name="Railways", show=False)

    # Kleuren voor de steden
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
    'Venetië': 'lightcoral',
    'Milaan': 'darkblue',
    'Geneve': 'lightgreen',
    'Zürich': 'darkviolet',
    'Wenen': 'beige',
    'Praag': 'lightgray',
    'Kopenhagen': 'gold'
}

# Markers toevoegen aan een FeatureGroup
    marker_group = folium.FeatureGroup(name="Steden", show=False)

    # Markers toevoegen aan de groep
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

# Voeg markers toe aan de marker groep
    for stad, coords in steden.items():
        folium.Marker(
            location=coords,
            popup=stad,
            tooltip=stad,
            icon=folium.Icon(color=stad_kleuren.get(stad, 'gray'))
        ).add_to(marker_group)

    # Voeg de marker groep en cirkel groep toe aan de kaart
    marker_group.add_to(m)
    circle_group.add_to(m)

    # Layer control toevoegen
    folium.LayerControl().add_to(m)

    # Streamlit-kaart weergeven
    folium_static(m)



    # ---------------------------------------------------------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------------------------------------------------------



    st.title("Visualisatie van de Steden Verdeler")

    stedenlijst= ['Parijs', 'Brussel', 'Praag', 'Londen', 'Hamburg', 'Frankfurt', 'Wenen', 'Luxemburg', 'Milaan', 'Venetië', 'Berlijn', 'München', 'Zurich', 'Marseille', 'Nice', 'Kopenhagen']
    aantal_vluchten = [28, 25, 13, 39, 15, 18, 11, 6, 10, 8, 17, 24, 22, 4, 8, 21, ]


# Zorg ervoor dat elke stad een kleur krijgt uit de dict (standaard blauw als niet gedefinieerd)
    kleuren = [stad_kleuren.get(stad, 'royalblue') for stad in stedenlijst]

# Maak een staafdiagram met Plotly
    fig8 = go.Figure()

    fig8.add_trace(go.Bar(
    x=stedenlijst,
    y=aantal_vluchten,
    marker=dict(color=kleuren),
    name="Aantal vluchten"
))

# Layout instellingen
    fig8.update_layout(
    title="Verdeling van Aantal Vluchten per Stad",
    xaxis_title="Steden",
    yaxis_title="Aantal Vluchten",
    xaxis=dict(tickangle=45),
    bargap=0.2
)

# Toon de grafiek in Streamlit
    st.plotly_chart(fig8)




    df4= pd.read_csv("ReisTijd.csv", sep=",")

# Maak de barplot
    fig = px.bar(
    df4, 
    x="Bestemming", 
    y="TijdVerschil_min", 
    title="Tijdverschil per Bestemming",
    labels={"Bestemming": "Bestemming", "TijdVerschil_min": "Tijdverschil in Minuten"},
    color="TijdVerschil_min",  # Kleuren bepalen op basis van TijdVerschil_min
    color_continuous_scale='RdYlGn'  # Kies een kleurenpalet, bijv. 'Viridis'
)

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
            'HOP1740', 'KLM1758', 'KLM1784', 'NJE622F', 'KLM1782', 'EZY5285',
            'KLM1854',  'DLH992', 'KLM1706', 'GER1714', 'KLM1476',
            'TRA5588', 'KLM1478', 'KLM1470', 'KLM1466', 'EZY7816', 'KLM1628', 'KLM1634',
            'ITY112', 'KLM1938',  'EZY1517', 'KLM1936', 'SWR728',
             'OAW734', 'KLM1926', 'AUA377', 'AUA375', 'KLM1354', 'EZY7928',
            'KLM1360', 'KLM1358', 'SAS549', 'EZY7938']
    alle = noord + oost + zuid

    # Maak een DataFrame voor een overzicht (optioneel)
    aantal = {
        'Regio': ['Noord', 'Oost', 'Zuid'],
        'Aantal Vluchten': [18, 2, 47]
    }
    aankomst = pd.DataFrame(aantal)
    st.dataframe(aankomst)

    # Streamlit dropdown voor regio-keuze
    gewenste_vluchtcodes = alle

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

        kleur = stad_kleuren.get(stad, None)

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
                        {beigestreep} Wenen | {lightgraystreep} Praag | {goldstreep} Kopenhagen<br>\
                        <br>\
                            <br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------


    @st.cache_data
    def load_data_fil():
        return pd.read_csv("filtered_flight1.csv")
    filtered_livevlucht = load_data_fil()


    # Definieer een kleurenschaal: rood (laag) → geel → blauw (hoog)
    colormap = linear.RdYlBu_11.scale(0, 0.7)

    # Maak de kaart
    map_obj = folium.Map(location=[52.3053, 4.7458], zoom_start=10)

    # Voeg cirkels toe op basis van de cumulatieve som van ClimbRate per vluchtcode
    for _, row in filtered_livevlucht.iterrows():
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

elif pagina == 'Geluid':
    st.title("MOET NOG TEKST")

    A220= pd.read_csv("220.csv")
    E90= pd.read_csv("E90.csv")
    E175= pd.read_csv("E175.csv")
    A321= pd.read_csv("321.csv")
    B7378= pd.read_csv("7378.csv")
    A320= pd.read_csv("320.csv")

    df2= pd.read_csv("Hackaton2.csv")
    Type_vliegtuig= {'EMJ-E90': 'Embraer-E90', '220-223': 'Airbus A220-300', '32S-32Q': 'Airbus A-321neo', 'EMJ-E7W':'Embraer-175', '73F-73K': 'Boeing 737-800', '737-73W': 'Boeing 737-700', '32S-320': 'Airbus A320-200' }
    df['TypeVliegtuig']= df['aircraftType.iataMain']+ '-' + df['aircraftType.iataSub']
    df['ModelVliegtuig']= df['TypeVliegtuig'].map(Type_vliegtuig)
    stedenlijst2= ['Antwerpen', 'Brussel', 'Frankfort', 'Parijs']
    SubStedenHackaton = df['Stad'].isin(stedenlijst2)
    Subvliegtuigtypen= df.loc[SubStedenHackaton, ['ModelVliegtuig']].value_counts()
    fig10= px.pie(df2, names='ModelVliegtuig', title="Soorten Vliegtuig")
    st.plotly_chart(fig10)

    Air220= data['type'].isin(A220)
    dbA320=data.loc[Air220, ['SEL_dB']].agg(['mean', 'min', 'max', 'std', 'median'])

    E90= data['type'].isin(E90)
    dbA320=data.loc[E90, ['SEL_dB']].agg(['mean', 'min', 'max', 'std', 'median'])

    E175= data['type'].isin(E175)
    dbA320=data.loc[E175, ['SEL_dB']].agg(['mean', 'min', 'max', 'std', 'median'])

    A321= data['type'].isin(A321)
    dbA320=data.loc[A321, ['SEL_dB']].agg(['mean', 'min', 'max', 'std', 'median'])

    B7378= data['type'].isin(B7378)
    dbA320=data.loc[B7378, ['SEL_dB']].agg(['mean', 'min', 'max', 'std', 'median'])

    Air320= data['type'].isin(A320)
    dbA320=data.loc[Air320, ['SEL_dB']].agg(['mean', 'min', 'max', 'std', 'median'])

    from PIL import Image

# Title of the Streamlit app
    st.title('MOET NOG TEKST')

# Create 2 columns
    col1, col2 = st.columns(2)

    # In the first column (col1) place the first 3 images
    with col1:

        image1 = Image.open("boeing 737-800.jpg")  # Replace with your actual image path
        st.image(image1, caption="boeing 737-800", use_container_width=True)

        # Image 2
        image2 = Image.open("A321.jpg")
        st.image(image2, caption="A321", use_container_width=True)

        # Image 3
        image3 = Image.open("A320.jpg")
        st.image(image3, caption="A320",  use_container_width=True)

    # In the second column (col2) place the other 3 images
    with col2:
        # Image 4
        image4 = Image.open("A220.jpg")
        st.image(image4, caption="A220", use_container_width=True)

        # Image 5
        image5 = Image.open("E90.jpg")
        st.image(image5, caption="E90", use_container_width=True)

        # Image 6
        image6 = Image.open("E175.jpg")
        st.image(image6, caption="E175", use_container_width=True)


    image7 = Image.open("formule.jpg")
    st.image(image7)
    st.write('')
    st.write('')
    st.write('')
# Gegeven data
    totale_sel_voor = 117.19710174279471
    totale_sel_na = 117.1652868299973
    sel_nutteloze_vluchten = 95.82966825644425
    vermindering_sel = 0.03181491279741522

    # Gegeven waarden voor de grafiek
    voor = 117.19710174279471
    na = 117.1652868299973

    # Maak de indeling met 2 kolommen
    col1, col2 = st.columns([1, 2])  # Kolom 1 is kleiner, kolom 2 is groter

    # Toon de metrics in de eerste kolom (links)
    with col1:
        st.metric("Totale SEL Voor", f"{totale_sel_voor:.4f} dB")
        st.metric("Totale SEL Na", f"{totale_sel_na:.4f} dB")
        st.metric("SEL 'Nutteloze' Vluchten", f"{sel_nutteloze_vluchten:.4f} dB")
        st.metric("Vermindering in SEL", f"{vermindering_sel:.4f} dB")

    # Maak een figuur voor de grafiek
    fig, ax = plt.subplots()

    # Teken de horizontale lijnen
    ax.axhline(y=voor, color='blue', linestyle='--', label='Voor')
    ax.axhline(y=na, color='red', linestyle='--', label='Na')

    # Voeg labels en titel toe
    ax.set_xlabel('X-as')
    ax.set_ylabel('Y-as')
    ax.set_title('Horizontale lijnen')

    # Stel het zoomniveau in
    ax.set_ylim(117.140, 117.230)

    ax.annotate('', xy=(0.5, na), xytext=(0.5, voor),
            arrowprops=dict(facecolor='black', edgecolor='black', arrowstyle='<->', lw=1.5))
    
    ax.text(0.55, (voor + na) / 2, '0.03', ha='center', va='center', fontsize=12, color='black')

    ax.get_xaxis().set_visible(False)

    # Toon de legenda
    ax.legend()

    # Toon de grafiek in de tweede kolom (rechts)
    with col2:
        st.pyplot(fig)

