# -*- coding: utf-8 -*-
"""ucla type.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1VCg3UO4_ehRHYXDEGSMJKLT8IvpPpn6p
"""

# Module installations (if running in a Jupyter Notebook)
!pip install geopy
!pip install geopandas mapclassify contextily
!sudo apt install -y libspatialindex-dev
!pip install geopandas contextily rtree geoplot
!pip install scikit-learn
!pip install mapclassify

# Module imports
import pandas as pd
import geopandas as gpd
import contextily as cx
import geoplot as gplt
import shapely as sh
from sklearn.preprocessing import LabelEncoder
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import numpy as np
import requests
from geopy.geocoders import Nominatim
import folium

# Data read and CRS update
los_angeles_listings = pd.read_csv('http://data.insideairbnb.com/united-states/ca/los-angeles/2023-12-03/visualisations/listings.csv')
area = gpd.read_file('http://data.insideairbnb.com/united-states/ca/los-angeles/2023-12-03/visualisations/neighbourhoods.geojson')
area = area.to_crs(3310)
los_angeles_listings_df = gpd.GeoDataFrame(los_angeles_listings, geometry=gpd.points_from_xy(los_angeles_listings.longitude, los_angeles_listings.latitude), crs=4326)
los_angeles_listings_df = los_angeles_listings_df.to_crs(3310)

# Widgets Entry
start = widgets.Button(
    description='Begin!: ',
    disabled=False,
    button_style='success',
    tooltip='Click to search')

address = widgets.Text(
    value='',
    description='Address',
    disabled=False)

radius = widgets.FloatText(
    value=0,
    description='Radius',
    disabled=False,
    layout={'width': 'max-content'},
    style={'description_width': 'initial'})

grid = widgets.GridspecLayout(1, 3, height='60px')
grid[0, 0] = start
grid[0, 1] = address
grid[0, 2] = radius

def airbnb_location_finder(event=None):
    clear_output(wait=True)
    display(grid)

    geocoder = Nominatim(user_agent='Ohtani is a Dodger')
    location = geocoder.geocode(address.value)
    if location:
        latitude, longitude = location.latitude, location.longitude
        geocoded = gpd.GeoDataFrame({'latitude': [latitude], 'longitude': [longitude]}, geometry=gpd.points_from_xy([longitude], [latitude]), crs=4326)
        geocoded = geocoded.to_crs(3310)
        geocoded_buffer = geocoded.buffer(float(radius.value))

        geocoded_buffer_df = gpd.GeoDataFrame(geometry=geocoded_buffer)

        geocoded_join = geocoded_buffer_df.sjoin(los_angeles_listings_df, how='inner')

        num_locations_within_buffer = len(geocoded_join)
        print("The number of airbnbs within the given radius is:", num_locations_within_buffer)

        mean_airbnb_cost_within_set_radius_buffer = geocoded_join['price'].mean()
        print("The mean AirBNB cost within the given radius is:", mean_airbnb_cost_within_set_radius_buffer)

        if num_locations_within_buffer == 0:
          print('Please try again!')
        else:
          region_average_price = los_angeles_listings_df['price'].mean()
          if mean_airbnb_cost_within_set_radius_buffer > region_average_price:
              result = 'Higher than radius, not great!'
          elif mean_airbnb_cost_within_set_radius_buffer < region_average_price:
              result = 'Lower than radius, sweet!'
          else:
              result = 'Same as radius, amazing!'
          answer_here = result
          print(answer_here)

        # Create a map centered on the user's entered location
        m = folium.Map(location=[latitude, longitude], zoom_start=12)
        # Add a marker for the user's entered location
        folium.Marker(location=[latitude, longitude], popup='User Location').add_to(m)
        # Add markers for Airbnb listings within the specified radius
        for _, listing in geocoded_join.iterrows():
            folium.Marker(location=[listing['latitude'], listing['longitude']], popup=f'Price: ${listing["price"]}').add_to(m)

        display(m)

start.on_click(airbnb_location_finder)
display(grid)