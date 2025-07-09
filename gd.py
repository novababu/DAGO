import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page configuration for a wide layout
st.set_page_config(layout="wide")

# Function to load and process data
# Using st.cache_data to cache the data and improve performance
@st.cache_data
def load_data():
    """
    This function loads the ESG data from CSV files, merges them,
    and processes the data into a clean, long format.
    """
    try:
        # Load the datasets from CSV files
        esg_data = pd.read_csv('ESGData.csv')
        esg_country = pd.read_csv('ESGCountry.csv')
        esg_series = pd.read_csv('ESGSeries.csv')

        # Merge the dataframes to combine information
        merged_data = pd.merge(esg_data, esg_series, on='Series Code', how='left')
        merged_data = pd.merge(merged_data, esg_country, on='Country Code', how='left')

        # Remove unnecessary columns that are artifacts of the merge
        if 'Unnamed: 4_x' in merged_data.columns:
            merged_data = merged_data.drop(columns=['Unnamed: 4_x'])
        if 'Unnamed: 4_y' in merged_data.columns:
            merged_data = merged_data.drop(columns=['Unnamed: 4_y'])
        if 'DESCRIPTION' in merged_data.columns:
            merged_data = merged_data.drop(columns=['DESCRIPTION'])


        # 'Melt' the dataframe to convert it from a wide format to a long format.
        # This is a crucial step for making the data plottable and filterable by year.
        id_vars = [col for col in merged_data.columns if 'YR' not in col]
        value_vars = [col for col in merged_data.columns if 'YR' in col]

        melted_data = pd.melt(merged_data, id_vars=id_vars, value_vars=value_vars, var_name='Year', value_name='Value')

        # Clean and convert data types for the 'Year' and 'Value' columns
        melted_data['Year'] = melted_data['Year'].str.extract(r'(\d{4})')
        melted_data['Year'] = pd.to_numeric(melted_data['Year'], errors='coerce')
        melted_data['Value'] = pd.to_numeric(melted_data['Value'], errors='coerce')

        # Drop rows with missing values to ensure data quality
        melted_data.dropna(subset=['Value', 'Year', 'Country Code', 'Series Code', 'Long Name'], inplace=True)
        melted_data['Year'] = melted_data['Year'].astype(int)

        return melted_data

    except FileNotFoundError:
        st.error("One of the required CSV files was not found. Please make sure ESGData.csv, ESGCountry.csv, and ESGSeries.csv are in the same directory as the app.")
        return None

# Load the data using the function defined above
data = load_data()

# Check if the data was loaded successfully before building the UI
if data is not None:
    st.title("Interactive ESG Data Dashboard")

    # --- Sidebar for Filters ---
    st.sidebar.header("Filters")

    # Filter by ESG Topic (e.g., Environment, Social, Governance)
    topics = sorted(data['Topic'].unique())
    selected_topic = st.sidebar.selectbox("Select ESG Topic", topics)

    # Filter by ESG Indicator (dependent on the selected topic)
    series_options = sorted(data[data['Topic'] == selected_topic]['Indicator Name'].unique())
    selected_series = st.sidebar.selectbox("Select ESG Indicator", series_options)

    # Filter by Year
    years = sorted(data['Year'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Select Year", years)

    # Filter the main dataframe based on user selections
    filtered_data = data[
        (data['Topic'] == selected_topic) &
        (data['Indicator Name'] == selected_series) &
        (data['Year'] == selected_year)
    ]

    # Display the detailed description of the selected indicator
    series_description = data[data['Indicator Name'] == selected_series]['Long definition'].iloc[0]
    with st.expander("Indicator Description"):
        st.markdown(series_description)

    # --- Main Dashboard Area ---

    if not filtered_data.empty:
        # Create two columns for the visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"{selected_series} in {selected_year}")
            # Choropleth Map showing global distribution of the selected indicator
            fig_map = px.choropleth(
                filtered_data,
                locations="Country Code",
                color="Value",
                hover_name="Long Name",
                color_continuous_scale=px.colors.sequential.Plasma,
                title="Global Distribution"
            )
            st.plotly_chart(fig_map, use_container_width=True)

        with col2:
            st.subheader(f"Top 20 Countries for {selected_series} in {selected_year}")
            # Bar Chart comparing the top 20 countries for the selected indicator
            bar_data = filtered_data.sort_values('Value', ascending=False).head(20)
            fig_bar = px.bar(
                bar_data,
                x="Long Name",
                y="Value",
                title="Country Comparison",
                labels={'Long Name': 'Country', 'Value': selected_series},
                hover_data=['Value']
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.warning("No data available for the selected filters. Please try different selections.")

else:
    st.info("Data could not be loaded. Please check that the required CSV files are in the correct directory and try again.")
