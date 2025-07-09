import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(layout="wide", page_title="ESG Data Governance Dashboard")

# Load datasets
esg_data = pd.read_csv("ESGData.csv")
series_info = pd.read_csv("ESGSeries.csv")
series_notes = pd.read_csv("ESGFootNote.csv")
country_info = pd.read_csv("ESGCountry.csv")
country_series = pd.read_csv("ESGCountry-Series.csv")
time_info = pd.read_csv("ESGSeries-Time.csv")

# Merge description into data
esg_data = esg_data.merge(series_info, on="SeriesCode", how="left")
esg_data = esg_data.merge(country_info, on="CountryCode", how="left")

# Sidebar filters
st.sidebar.title("🔎 Filter ESG Indicators")

esg_categories = ['Environmental', 'Social', 'Governance']
selected_category = st.sidebar.selectbox("Select ESG Category", esg_categories)

# Filter SeriesCode based on category
filtered_series = series_info[series_info["Category"] == selected_category]
series_options = filtered_series["SeriesDescription"].tolist()
selected_series_desc = st.sidebar.selectbox("Select Indicator", series_options)

# Get the SeriesCode from description
selected_series_code = filtered_series[filtered_series["SeriesDescription"] == selected_series_desc]["SeriesCode"].values[0]

# Filter data for selected series
filtered_data = esg_data[esg_data["SeriesCode"] == selected_series_code]

# Most recent year available
filtered_data = filtered_data.sort_values(by="Year", ascending=False).dropna(subset=["Value"])
latest_year = filtered_data["Year"].max()
filtered_data = filtered_data[filtered_data["Year"] == latest_year]

# Title
st.title("🌍 ESG Dashboard - Data Governance & Security")
st.markdown(f"### Showing data for: **{selected_series_desc}** ({latest_year})")

# Map
fig_map = px.choropleth(
    filtered_data,
    locations="CountryCode",
    color="Value",
    hover_name="CountryName",
    color_continuous_scale="Viridis",
    title="ESG Indicator by Country"
)
st.plotly_chart(fig_map, use_container_width=True)

# Bar Chart
sorted_bar = filtered_data.sort_values(by="Value", ascending=False)
fig_bar = px.bar(
    sorted_bar,
    x="CountryName",
    y="Value",
    text="Value",
    title="Comparison of Selected ESG Indicator"
)
fig_bar.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# Show description
st.subheader("ℹ️ Indicator Description")
description_text = filtered_series[filtered_series["SeriesDescription"] == selected_series_desc]["LongDefinition"].values[0]
st.info(description_text)

# Data Table
with st.expander("📊 View Raw Data"):
    st.dataframe(filtered_data[["CountryName", "Value", "Year"]].sort_values(by="Value", ascending=False))

