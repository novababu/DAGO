import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration for a wide layout and a custom title
st.set_page_config(layout="wide", page_title="Comprehensive World Bank ESG Data Dashboard")

# Main title and introduction for the dashboard
st.title("Comprehensive World Bank ESG Data Dashboard")
st.markdown("Explore Environmental, Social, and Governance (ESG) indicators with detailed insights across countries and time.")

@st.cache_data
def load_all_data():
    """
    Loads and merges all six ESG datasets.
    This function is cached by Streamlit to improve performance on re-runs.
    """
    try:
        # Load the individual CSV datasets
        df_data = pd.read_csv('ESGData.csv')
        df_country = pd.read_csv('ESGCountry.csv')
        df_series = pd.read_csv('ESGSeries.csv')
        df_series_time = pd.read_csv('ESGSeries-Time.csv')
        df_footnote = pd.read_csv('ESGFootNote.csv')
        df_country_series = pd.read_csv('ESGCountry-Series.csv')

        # --- Data Cleaning and Preprocessing ---

        # 1. Process df_data: Extract Year and rename Value column
        if 'Time Code' in df_data.columns:
            # Ensure 'Time Code' is string type before applying .str accessor
            df_data['Time Code'] = df_data['Time Code'].astype(str)
            # Convert extracted year to float first to handle NaNs, then fill NaNs with 0, then convert to int
            df_data['Year'] = df_data['Time Code'].str.extract(r'YR(\d{4})').astype(float).fillna(0).astype(int)
        else:
            st.warning("Warning: 'Time Code' column not found in ESGData.csv. Some features may be limited.")
            df_data['Year'] = 0 # Default year or handle as appropriate

        df_data = df_data.rename(columns={'Value': 'ESG Value'})

        # 2. Merge df_data with df_country
        df_merged = pd.merge(df_data, df_country[['Country Code', 'Country Name']], on='Country Code', how='left')

        # 3. Merge df_merged with df_series
        df_merged = pd.merge(df_merged, df_series[['Series Code', 'Topic', 'Indicator Name', 'Long definition']], on='Series Code', how='left')

        # 4. Process df_footnote:
        if 'Time Code' in df_footnote.columns:
            # Ensure 'Time Code' is string type before applying .str accessor
            df_footnote['Time Code'] = df_footnote['Time Code'].astype(str)
            # Convert extracted year to float first to handle NaNs, then fill NaNs with 0, then convert to int
            df_footnote['Year'] = df_footnote['Time Code'].str.extract(r'YR(\d{4})').astype(float).fillna(0).astype(int)
        else:
            st.warning("Warning: 'Time Code' column not found in ESGFootNote.csv. Footnotes by year may be limited.")
            df_footnote['Year'] = 0 # Default year or handle as appropriate

        # Drop rows where essential columns have missing values after initial merges
        df_merged.dropna(subset=['Country Name', 'Topic', 'Indicator Name', 'ESG Value', 'Year'], inplace=True)

        return df_merged, df_footnote, df_country, df_series # Return all relevant dataframes

    except FileNotFoundError as e:
        st.error(f"Error loading data: {e}. Please ensure all 6 CSV files are in the same directory as the script.")
        st.stop() # Stop the app if files are missing
    except Exception as e:
        st.error(f"An unexpected error occurred during data loading: {e}. Please check your CSV file formats and column names ('Time Code' in particular).")
        st.stop()

# Load all processed dataframes
df_main, df_footnote, df_country_lookup, df_series_lookup = load_all_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

# 1. ESG Category Filter
# Ensure df_main is not empty before attempting to access its columns
if not df_main.empty and 'Topic' in df_main.columns:
    all_topics = sorted(df_main['Topic'].unique().tolist())
    selected_topic = st.sidebar.selectbox("Select ESG Category", all_topics)
else:
    st.sidebar.error("No ESG data available to filter by category. Please check your data files.")
    st.stop() # Stop if essential data is missing

# Filter the main DataFrame based on the selected ESG category
df_filtered_by_topic = df_main[df_main['Topic'] == selected_topic]

# 2. ESG Indicator Filter (cascades from Category)
if not df_filtered_by_topic.empty:
    filtered_series_df = df_filtered_by_topic.drop_duplicates(subset=['Series Code', 'Indicator Name'])
    series_options = {row['Series Code']: row['Indicator Name'] for index, row in filtered_series_df.iterrows()}
    
    if series_options:
        selected_series_code = st.sidebar.selectbox(
            "Select ESG Indicator", 
            sorted(series_options.keys()),
            format_func=lambda x: series_options[x]
        )
    else:
        st.sidebar.warning("No indicators available for the selected category. Try a different category.")
        selected_series_code = None
else:
    st.sidebar.warning("Please select an ESG Category first to see available indicators.")
    selected_series_code = None

# Filter the DataFrame based on the selected ESG indicator
df_filtered_by_series = pd.DataFrame()
if selected_series_code:
    df_filtered_by_series = df_filtered_by_topic[df_filtered_by_topic['Series Code'] == selected_series_code]

# 3. Year Slider (cascades from Indicator)
selected_year = None
if not df_filtered_by_series.empty:
    all_years = sorted(df_filtered_by_series['Year'].unique().tolist())
    if all_years:
        selected_year = st.sidebar.slider("Select Year", min_value=min(all_years), max_value=max(all_years), value=max(all_years))
    else:
        st.sidebar.warning("No year data available for the selected indicator. Try a different indicator.")
else:
    st.sidebar.warning("Please select an ESG Indicator first to see available years.")

# Filter the DataFrame based on the selected year
df_final = pd.DataFrame()
if selected_year is not None:
    df_final = df_filtered_by_series[df_filtered_by_series['Year'] == selected_year]

# 4. Country Multi-select (cascades from Year)
selected_countries = []
if not df_final.empty:
    all_countries = sorted(df_final['Country Name'].unique().tolist())
    if all_countries:
        default_countries = all_countries[:min(5, len(all_countries))] # Select top 5 or fewer if less than 5
        selected_countries = st.sidebar.multiselect("Select Countries (optional)", all_countries, default=default_countries)
    else:
        st.sidebar.warning("No countries available for the current selections. Try adjusting year or indicator.")
else:
    st.sidebar.warning("Please select a Year to see available countries.")

# Further filter the DataFrame based on selected countries
if selected_countries:
    df_final = df_final[df_final['Country Name'].isin(selected_countries)]

# --- Main Content Area ---

# Check if the final filtered DataFrame is not empty before displaying visualizations
if not df_final.empty:
    # Retrieve the full indicator name and its long definition for display
    current_indicator_name = "N/A"
    indicator_description = "N/A"
    if selected_series_code and not df_series_lookup.empty:
        series_info = df_series_lookup[df_series_lookup['Series Code'] == selected_series_code]
        if not series_info.empty:
            current_indicator_name = series_info['Indicator Name'].iloc[0]
            indicator_description = series_info['Long definition'].iloc[0]
    
    # Display the selected indicator's name and its detailed description
    st.subheader(f"Indicator: {current_indicator_name} (Year: {selected_year})")
    st.markdown(f"**Description:** {indicator_description}")

    # Use columns to arrange the map and bar chart side-by-side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("ESG Value by Country (Map)")
        fig_map = px.choropleth(
            df_final,
            locations="Country Code",
            color="ESG Value",
            hover_name="Country Name",
            color_continuous_scale=px.colors.sequential.Plasma,
            projection="natural earth",
            title=f"{current_indicator_name} by Country in {selected_year}"
        )
        fig_map.update_layout(height=500, margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.subheader("ESG Value Comparison (Bar Chart)")
        df_bar_chart = df_final.sort_values(by="ESG Value", ascending=False)
        fig_bar = px.bar(
            df_bar_chart,
            x="Country Name",
            y="ESG Value",
            title=f"{current_indicator_name} Comparison in {selected_year}",
            labels={"ESG Value": current_indicator_name}
        )
        fig_bar.update_layout(height=500, margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Time Series Trend (New Plot) ---
    st.subheader(f"Time Series Trend for {current_indicator_name}")
    # Filter data for the selected indicator across all available years for the selected countries
    df_time_series = df_filtered_by_series[df_filtered_by_series['Country Name'].isin(selected_countries)]
    
    if not df_time_series.empty:
        fig_line = px.line(
            df_time_series,
            x="Year",
            y="ESG Value",
            color="Country Name",
            title=f"Trend of {current_indicator_name} over Time",
            labels={"ESG Value": current_indicator_name}
        )
        fig_line.update_layout(hovermode="x unified") # Unified hover for easier comparison
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Select countries to view the time series trend.")

    # --- Display Footnotes (if available for selected data) ---
    st.subheader("Relevant Footnotes")
    # Filter footnotes based on selected country, series, and year
    
    # Ensure df_final is not empty before attempting to merge for footnotes
    if not df_final.empty:
        footnote_keys = df_final[['Country Code', 'Series Code', 'Time Code']].drop_duplicates()
        
        # Filter df_footnote for matching entries
        relevant_footnotes = pd.merge(footnote_keys, df_footnote, on=['Country Code', 'Series Code', 'Time Code'], how='inner')

        if not relevant_footnotes.empty:
            # Merge with country and series lookup to display names
            relevant_footnotes = pd.merge(relevant_footnotes, df_country_lookup[['Country Code', 'Country Name']], on='Country Code', how='left')
            relevant_footnotes = pd.merge(relevant_footnotes, df_series_lookup[['Series Code', 'Indicator Name']], on='Series Code', how='left')
            
            st.dataframe(relevant_footnotes[['Country Name', 'Indicator Name', 'Year', 'Footnote']], use_container_width=True)
        else:
            st.info("No specific footnotes found for the current selections.")
    else:
        st.info("No data selected to find relevant footnotes.")

else:
    st.info("Please adjust your filter selections. No data is available for the current combination of ESG Category, Indicator, Year, and Countries.")

st.markdown("---")
st.markdown("Data Source: World Bank ESG Data Draft Dataset")
