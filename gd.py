import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="ESG Data Governance Dashboard")

# --- Load Data ---
# It's assumed these CSVs are in the same directory as the Streamlit app.
# For this example, we'll load them directly. In a real scenario, you might use st.cache_data.
try:
    df_data = pd.read_csv("ESGData.csv")
    df_country = pd.read_csv("ESGCountry.csv")
    df_series = pd.read_csv("ESGSeries.csv")
    df_country_series = pd.read_csv("ESGCountry-Series.csv")
    df_series_time = pd.read_csv("ESGSeries-Time.csv")
    df_footnote = pd.read_csv("ESGFootNote.csv")
except FileNotFoundError:
    st.error("One or more CSV files not found. Please ensure all ESG CSV files are in the same directory.")
    st.stop()

# --- Data Preprocessing ---
# Merge datasets to create a comprehensive view
# Merge df_data with df_country to get Country Names
df_merged = pd.merge(df_data, df_country, on='Country Code', how='left')

# Merge with df_series to get Series Name and Description
df_merged = pd.merge(df_merged, df_series, on='Series Code', how='left')

# Clean column names (remove extra spaces/newlines from PDF instructions)
df_merged.columns = df_merged.columns.str.strip()

# Rename '2023' column to 'Value' for easier plotting (assuming 2023 is the relevant year for values)
# The PDF implies "ESG value" without specifying a year. Let's use the latest year available.
# We need to find the year columns dynamically.
year_columns = [col for col in df_merged.columns if col.isdigit() and len(col) == 4]
if year_columns:
    latest_year = max(year_columns)
    df_merged['Value'] = pd.to_numeric(df_merged[latest_year], errors='coerce')
    st.sidebar.info(f"Displaying data for the latest available year: **{latest_year}**")
else:
    st.error("No year columns found in ESGData.csv for values. Please check the data format.")
    st.stop()

# Drop rows where 'Value' is NaN (missing ESG data for the selected year)
df_merged.dropna(subset=['Value'], inplace=True)

# Define ESG Categories based on Series Name keywords (as categories are not explicitly in CSVs)
# This is an interpretation based on common ESG definitions and the PDF's mention of categories.
def assign_category(series_name):
    series_name_lower = series_name.lower()
    if any(keyword in series_name_lower for keyword in ['co2', 'energy', 'emission', 'renewable', 'climate', 'environmental', 'pollution', 'water', 'land', 'waste']):
        return 'Environment'
    elif any(keyword in series_name_lower for keyword in ['social', 'health', 'education', 'poverty', 'gender', 'labor', 'welfare', 'community', 'human rights']):
        return 'Social'
    elif any(keyword in series_name_lower for keyword in ['governance', 'corruption', 'board', 'management', 'ethics', 'transparency', 'accountability']):
        return 'Governance'
    return 'Other'

df_merged['Category'] = df_merged['Series Name'].apply(assign_category)

# --- Dashboard Title and Introduction ---
st.title("🌍 Data Governance & ESG Dashboard")
st.markdown(
    """
    This interactive dashboard visualizes Environmental, Social, and Governance (ESG) data across different countries.
    Use the filters on the sidebar to explore various ESG indicators and compare country performance.
    """
)

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters")

# Filter by Category
all_categories = ['All'] + sorted(df_merged['Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Select ESG Category", all_categories)

filtered_by_category_df = df_merged.copy()
if selected_category != 'All':
    filtered_by_category_df = df_merged[df_merged['Category'] == selected_category]

# Filter by Series Code/Name
all_series = ['All'] + sorted(filtered_by_category_df['Series Name'].unique().tolist())
selected_series_name = st.sidebar.selectbox("Select ESG Indicator (Series)", all_series)

# Get the Series Description for the selected series
series_description = ""
if selected_series_name != 'All':
    series_desc_df = df_series[df_series['Series Name'] == selected_series_name]['Description'].iloc[0]
    series_description = f"**Description:** {series_desc_df}"
    df_filtered = filtered_by_category_df[filtered_by_category_df['Series Name'] == selected_series_name]
else:
    df_filtered = filtered_by_category_df.copy()

# Filter by Country Code
all_countries = ['All'] + sorted(df_filtered['Country Name'].unique().tolist())
selected_country_name = st.sidebar.selectbox("Select Country", all_countries)

if selected_country_name != 'All':
    df_filtered = df_filtered[df_filtered['Country Name'] == selected_country_name]

# Display Series Description Panel
if selected_series_name != 'All':
    st.sidebar.markdown(f"---")
    st.sidebar.markdown(f"**Selected Indicator Details:**")
    st.sidebar.markdown(f"**Series Name:** {selected_series_name}")
    st.sidebar.markdown(series_description)
    st.sidebar.markdown(f"---")

# Check if filtered data is empty
if df_filtered.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
else:
    # --- Main Dashboard Components ---

    # 1. Map Visualization
    st.header("🌎 ESG Indicator Map by Country")
    st.markdown("Color-coded map showing the selected ESG indicator value for each country.")

    if selected_series_name == 'All':
        st.info("Please select a specific ESG Indicator from the sidebar to view the map visualization.")
    else:
        # For map, we need one value per country for the selected series
        df_map_data = df_filtered.groupby(['Country Code', 'Country Name', 'Series Name'])['Value'].mean().reset_index()

        fig_map = px.choropleth(
            df_map_data,
            locations="Country Code",
            color="Value",
            hover_name="Country Name",
            color_continuous_scale=px.colors.sequential.Plasma,
            title=f"'{selected_series_name}' Value Across Countries",
            height=600
        )
        fig_map.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            ),
            margin={"r":0,"t":50,"l":0,"b":0}
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # 2. Bar Chart
    st.header("📊 ESG Indicator Comparison Bar Chart")
    st.markdown("Compare the selected ESG indicator across different countries.")

    if selected_series_name == 'All':
        st.info("Please select a specific ESG Indicator from the sidebar to view the bar chart comparison.")
    else:
        # Group by country and get the mean value for the selected series
        df_bar_data = df_filtered.groupby(['Country Name'])['Value'].mean().reset_index()
        df_bar_data = df_bar_data.sort_values(by='Value', ascending=False) # Default sort

        # Allow sorting
        sort_order = st.radio("Sort by:", ('Descending Value', 'Ascending Value'), horizontal=True)
        if sort_order == 'Ascending Value':
            df_bar_data = df_bar_data.sort_values(by='Value', ascending=True)

        fig_bar = px.bar(
            df_bar_data,
            x="Country Name",
            y="Value",
            title=f"'{selected_series_name}' Value by Country",
            labels={"Country Name": "Country", "Value": f"{selected_series_name} Value"},
            height=500
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Optional: Display raw data (for debugging/exploration)
    with st.expander("View Raw Filtered Data"):
        st.dataframe(df_filtered)

st.markdown("---")
st.markdown("Dashboard created using Streamlit and Plotly.")
