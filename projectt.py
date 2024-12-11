"""
Name : Alejandro Acebal
Date : 12/11/2024
Data: Fast Food USA
Description: This program aims to provide people a tool to find fast food locations near them. To look at data
and compare fast food in states and the amount of fast food chains in the country.
"""



import pandas as pd
import pydeck as pdk
import os
import streamlit as st
import matplotlib.pyplot as plt
import toml
import re

# Read the CSV file and create a DataFrame
data_path = "/Users/aleak/Library/CloudStorage/GoogleDrive-acekur04@gmail.com/My Drive/University/Bentley Fall Semester 2024/Python/Final Project/archive/data/fast_food_usa(in).csv"
merged_df = pd.read_csv(data_path)

# Validate geolocation data (latitude and longitude)
merged_df.dropna(subset=['latitude', 'longitude'], inplace=True)

#Cleaning Repeated Fast Food Chains and Standardizing Websites

#McDonald's
# Define a function to standardize the name "McDonald's"
def standardize_mcdonalds(name):
    # Use regular expression to find pattern matches
    if re.search(r"mc\s*donald['’´`]?\w*", name.lower().replace(" ", "")):
        return "McDonald's"
    return name

# Apply the function to the 'name' column
merged_df['name'] = merged_df['name'].apply(standardize_mcdonalds)

# Define the correct McDonald's website based on a known good entry
mc_website = merged_df.loc[38, 'websites']  # Assuming this is a valid entry
merged_df.loc[merged_df['name'] == "McDonald's", 'websites'] = mc_website


#Wendys
# Define a function to standardize the name "Wendy's"
def standardize_wendys(name):
    # Use regular expression to find pattern matches
    if re.search(r"wendy['’`]?\w*", name.lower().replace(" ", "")):
        return "Wendy's"
    return name

# Apply the function to the 'name' column
merged_df['name'] = merged_df['name'].apply(standardize_wendys)

# Define the correct Wendy's website based on a known good entry
wendys_website = merged_df.loc[58, 'websites']  # Assuming this is a valid entry
merged_df.loc[merged_df['name'] == "Wendy's", 'websites'] = wendys_website

#Dunkin Donuts
# Define a function to standardize the name "Dunkin Donuts"
def standardize_dunkin_donuts(name):
    # Use regular expression to find pattern matches
    if re.search(r"dunkin\w*", name.lower().replace(" ", "")):
        return "Dunkin' Donuts"
    return name

# Apply the function to the 'name' column
merged_df['name'] = merged_df['name'].apply(standardize_dunkin_donuts)

# Define the correct Dunkin' Donuts website based on a known good entry
dunkin_donuts_website = merged_df.loc[560, 'websites']  # Assuming this is a valid entry
merged_df.loc[merged_df['name'] == "Dunkin' Donuts", 'websites'] = dunkin_donuts_website

# Style the title and text using HTML
st.markdown("<h1 style='text-align: center;'>Fast Food World</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Find everything you need from fast food!</p>", unsafe_allow_html=True)


# Style the sub-title and text using HTML
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>Fast Food Locator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Find fast food options near you!</p>", unsafe_allow_html=True)

# Dropdown to select province
province_options = sorted(merged_df['province'].unique())
selected_province = st.selectbox("Select a province:", options=province_options)

# Filter cities based on the selected province
if selected_province:
    city_options = sorted(merged_df[merged_df['province'] == selected_province]['city'].unique())
    selected_city = st.selectbox("Select a city:", options=city_options)
else:
    selected_city = None

# Dropdown to select fast food chain
chain_options = sorted(merged_df['name'].unique())
selected_chain = st.selectbox("Select a fast food chain:", options=["All"] + chain_options)

# Filter data based on province, city, and chain
def filter_data(province, city, chain):
    if chain == "All":
        return merged_df[
            (merged_df['province'] == province) & 
            (merged_df['city'].str.lower() == city.lower())
        ]
    else:
        return merged_df[
            (merged_df['province'] == province) & 
            (merged_df['city'].str.lower() == city.lower()) & 
            (merged_df['name'].str.lower() == chain.lower())
        ]


# Filter the data
if selected_province and selected_city:
    filtered_data = filter_data(selected_province, selected_city, selected_chain).copy()

    if not filtered_data.empty:
        st.write(f"Locations for {selected_chain} in {selected_city}, {selected_province}:")

        # Handle websites column
        if 'websites' in merged_df.columns:
            filtered_data.loc[:, 'websites'] = filtered_data['websites'].fillna("No Website")
            filtered_data['Website Link'] = filtered_data['websites'].apply(
                lambda url: f"<a href='{url}'>Visit Website</a>" if url != "No Website" else "No Website"
            )
            st.markdown(
                filtered_data[['name', 'address', 'city', 'Website Link']].to_html(index=False, escape=False),
                unsafe_allow_html=True
            )
        else:
            st.dataframe(filtered_data[['name', 'address', 'city', 'province']])

        # Generate map with text labels
        def create_map(data):
            latitude = data['latitude'].mean() if len(data) > 1 else data['latitude'].iloc[0]
            longitude = data['longitude'].mean() if len(data) > 1 else data['longitude'].iloc[0]
            return pdk.Deck(
                initial_view_state=pdk.ViewState(
                    latitude=latitude,
                    longitude=longitude,
                    zoom=11
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=data,
                        get_position='[longitude, latitude]',
                        get_color='[200, 30, 0, 160]',
                        get_radius=200,
                    ),
                    pdk.Layer(
                        'TextLayer',
                        data=data,
                        get_position='[longitude, latitude]',
                        get_text='name',
                        get_size=7,
                        get_color=[0, 0, 0, 200],
                        get_alignment_baseline="'bottom'"
                    )
                ]
            )

        st.pydeck_chart(create_map(filtered_data))
    else:
        st.write(f"No fast food locations found in {selected_city}, {selected_province}.")


# Create a separator line
st.markdown("---")

# Style the title and text using HTML
st.markdown("<h2 style='text-align: center;'>Fast Food State Comparison</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Compare the number of restaurants in different states!</p>", unsafe_allow_html=True)

# Chart to compare the number of restaurants in two states
state_options = sorted(merged_df['province'].unique())
selected_state1 = st.selectbox("Select the first state:", options=state_options)
selected_state2 = st.selectbox("Select the second state:", options=state_options)

if selected_state1 and selected_state2:
    state1_restaurants = merged_df[merged_df['province'] == selected_state1]['name'].nunique()
    state2_restaurants = merged_df[merged_df['province'] == selected_state2]['name'].nunique()

    chart_data = pd.DataFrame({
        'State': [selected_state1, selected_state2],
        'Number of Restaurants': [state1_restaurants, state2_restaurants]
    })

    st.bar_chart(chart_data, x='State', y='Number of Restaurants')



    # Create a separator line
st.markdown("---")

# Style the title and text using HTML
st.markdown("<h2 style='text-align: center;'>Fast Food Mode</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>What are the most repeated fast food chains in the nation?</p>", unsafe_allow_html=True)

# Create a bar chart of the most repeated restaurants
top_restaurants = merged_df['name'].value_counts().head(10)
st.bar_chart(top_restaurants)
