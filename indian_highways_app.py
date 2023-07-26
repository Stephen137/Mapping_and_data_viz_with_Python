import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import leafmap.foliumap as leafmap

# Cosmetic config
st.set_page_config(page_title='Dashboard', layout='wide')

st.title('Highway Dashboard')

st.sidebar.title('About')
st.sidebar.info('Explore the Highway Statistics')

# Concatenate file names
data_url = 'https://storage.googleapis.com/spatialthoughts-public-data/python-dataviz/osm/'
gpkg_file = 'karnataka.gpkg'
csv_file = 'highway_lengths_by_district.csv'


@st.cache_data
# custom funciton to load in our spatial data
def read_gdf(url, layer):
    gdf = gpd.read_file(url, layer=layer)
    return gdf

@st.cache_data
# custom function to load road statistics
def read_csv(url):
    df = pd.read_csv(url)
    return df

# Concatenate file names
gpkg_url = data_url + gpkg_file
csv_url = data_url + csv_file


# create districts GeoDataFrame
districts_gdf = read_gdf(gpkg_url, 'karnataka_districts')

# create roads GeoDataFrame
roads_gdf = read_gdf(gpkg_url, 'karnataka_highways')

# create non spatial road stats DataFrame
lengths_df = read_csv(csv_url)

# Add a dropdown for district selection and filter dataset based on user choice
districts = districts_gdf.DISTRICT.values
district = st.sidebar.selectbox('Select a District', districts)

# Give the user option to addd a road overlay
overlay = st.sidebar.checkbox('Overlay roads')

# filter road lengths based on user district choice
district_lengths = lengths_df[lengths_df['DISTRICT'] == district]

# # Visualize the user selection using barchart
fig, ax = plt.subplots(1, 1)
district_lengths.plot(kind='bar', ax=ax, color=['blue', 'red'],
    ylabel='Kilometers', xlabel='Category')
ax.get_xaxis().set_ticklabels([])
stats = st.sidebar.pyplot(fig)

# Create a Folium map
m = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
)

# Add basemap
m.add_basemap('CartoDB.DarkMatter')

# Add districts layer
m.add_gdf(
    gdf=districts_gdf,
    zoom_to_layer=False,
    layer_name='districts',
    info_mode='on_click',
    style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    )

# add roads layer if selected by user
if overlay:
    m.add_gdf(
        gdf=roads_gdf,
        zoom_to_layer=False,
        layer_name='highways',
        info_mode=None,
        style={'color': '#225ea8', 'weight': 1.5},
    )

# filter for user district selection
selected_gdf = districts_gdf[districts_gdf['DISTRICT'] == district]

# add the user selected districts layer
m.add_gdf(
    gdf=selected_gdf,
    layer_name='selected',
    zoom_to_layer=True,
    info_mode=None,
    style={'color': 'yellow', 'fill': None, 'weight': 2}
 )

m_streamlit = m.to_streamlit(600, 600)