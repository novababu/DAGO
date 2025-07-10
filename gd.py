import streamlit as st
import pandas as pd

# Define paths to your data files (adjust these as necessary)
ESG_DATA_PATH = 'esg_data.csv'
ESG_SERIES_PATH = 'esg_series.csv'

@st.cache_data
def load_data():
    """
    Loads ESG data and series data, and merges them.
    Includes robust error handling for common merging issues.
    """
    try:
        esg_data = pd.read_csv(ESG_DATA_PATH)
        esg_series = pd.read_csv(ESG_SERIES_PATH)

    except FileNotFoundError as e:
        st.error(f"Error: Data file not found. Please ensure '{e.filename}' exists.")
        st.stop() # Stop the app execution if files are missing
    except pd.errors.EmptyDataError:
        st.error("Error: One of your CSV files is empty.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data: {e}")
        st.stop()


    # --- Debugging and Column Name Handling ---
    st.subheader("Data Loading Debug Information:")
    st.write("Columns in `esg_data`:", esg_data.columns.tolist())
    st.write("Columns in `esg_series`:", esg_series.columns.tolist())

    # Define the expected merge key
    merge_key = 'Series Code'

    # Check if 'Series Code' exists in both dataframes
    esg_data_cols = esg_data.columns.tolist()
    esg_series_cols = esg_series.columns.tolist()

    data_key_exists = merge_key in esg_data_cols
    series_key_exists = merge_key in esg_series_cols

    if not data_key_exists and not series_key_exists:
        st.error(f"Error: Neither '{merge_key}' found in `esg_data` nor `esg_series`.")
        st.info("Please check your CSV files or data loading logic for correct column names.")
        st.stop()
    elif not data_key_exists:
        st.warning(f"Warning: '{merge_key}' not found in `esg_data`.")
        st.info("Attempting to find similar column names in `esg_data` for a potential rename.")
        # Attempt to find similar columns and rename
        found = False
        for col in esg_data_cols:
            if col.lower().replace('_', ' ') == merge_key.lower().replace('_', ' '):
                st.info(f"Renaming '{col}' in `esg_data` to '{merge_key}'.")
                esg_data = esg_data.rename(columns={col: merge_key})
                found = True
                break
        if not found:
            st.error(f"Could not find a suitable column to rename in `esg_data` to '{merge_key}'. Merge will likely fail.")
            st.stop() # Stop if we can't fix it

    elif not series_key_exists:
        st.warning(f"Warning: '{merge_key}' not found in `esg_series`.")
        st.info("Attempting to find similar column names in `esg_series` for a potential rename.")
        # Attempt to find similar columns and rename
        found = False
        for col in esg_series_cols:
            if col.lower().replace('_', ' ') == merge_key.lower().replace('_', ' '):
                st.info(f"Renaming '{col}' in `esg_series` to '{merge_key}'.")
                esg_series = esg_series.rename(columns={col: merge_key})
                found = True
                break
        if not found:
            st.error(f"Could not find a suitable column to rename in `esg_series` to '{merge_key}'. Merge will likely fail.")
            st.stop() # Stop if we can't fix it


    # Ensure the merge key column is of the same type if possible (e.g., string)
    try:
        esg_data[merge_key] = esg_data[merge_key].astype(str)
        esg_series[merge_key] = esg_series[merge_key].astype(str)
        st.info(f"Successfully converted '{merge_key}' column to string type in both dataframes.")
    except KeyError:
        # This case should ideally be caught by the above checks, but good for robustness
        st.error(f"Critical Error: '{merge_key}' column not found after renaming attempts. Cannot proceed with type conversion.")
        st.stop()
    except Exception as e:
        st.warning(f"Could not convert '{merge_key}' column to string type: {e}. Proceeding with merge, but type mismatch could be an issue.")


    st.success(f"Both dataframes now have a '{merge_key}' column. Proceeding with merge.")

    # Perform the merge
    try:
        merged_data = pd.merge(esg_data, esg_series, on=merge_key, how='left')
        st.success("Data merged successfully!")
        st.write("Shape of merged data:", merged_data.shape)
        st.dataframe(merged_data.head()) # Show a preview of the merged data
        return merged_data
    except KeyError as e:
        st.error(f"Merge failed due to a KeyError: {e}. This indicates a problem with the merge key even after checks.")
        st.error("Double-check column names and data types, and ensure there's truly a common key.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during the merge operation: {e}")
        st.stop()


# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("ESG Data Explorer")

# Load data
data = load_data()

if data is not None:
    st.header("Exploratory Data Analysis")
    st.write("Use the sidebar filters to explore the data.")

    # Example: Simple filtering (customize as needed)
    st.sidebar.header("Filters")
    if 'Country Name' in data.columns:
        countries = data['Country Name'].unique().tolist()
        selected_country = st.sidebar.selectbox("Select Country", ['All'] + countries)
        if selected_country != 'All':
            data = data[data['Country Name'] == selected_country]

    if 'Year' in data.columns:
        years = data['Year'].unique().tolist()
        selected_year = st.sidebar.selectbox("Select Year", ['All'] + sorted(years, reverse=True))
        if selected_year != 'All':
            data = data[data['Year'] == selected_year]

    st.subheader("Filtered Data Preview")
    st.dataframe(data.head())

    # Add more visualizations or analysis here using the 'data' dataframe
    # Example: Display a simple metric
    st.subheader("Key Statistics")
    if 'Value' in data.columns:
        st.metric("Total Value (Filtered)", f"{data['Value'].sum():,.2f}")
    else:
        st.info("The 'Value' column is not available for calculating total.")


    # Example Plot (requires altair or plotly)
    if 'Year' in data.columns and 'Value' in data.columns and 'Series Name' in data.columns:
        st.subheader("Value Over Time by Series")
        # Ensure 'Value' is numeric
        data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
        plot_data = data.dropna(subset=['Year', 'Value', 'Series Name'])
        if not plot_data.empty:
            import plotly.express as px
            fig = px.line(plot_data, x='Year', y='Value', color='Series Name',
                          title='Value Trends by Series',
                          labels={'Value': 'ESG Value', 'Year': 'Year'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to generate the 'Value Over Time' plot with current filters.")
    else:
        st.info("Missing 'Year', 'Value', or 'Series Name' columns for plotting.")
