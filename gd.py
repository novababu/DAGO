import streamlit as st
import pandas as pd
import os # Import the os module for path manipulation

# --- Configuration for File Paths ---
# Get the directory of the current script.
# This ensures that the app can find the data files regardless of where you run it from.
SCRIPT_DIR = os.path.dirname(__file__)

# Define paths to your data files.
# ADJUST THESE PATHS BASED ON WHERE YOUR CSV FILES ARE LOCATED:
# Option 1: Data files are in a 'data' subfolder within the app's directory (RECOMMENDED)
DATA_FOLDER = os.path.join(SCRIPT_DIR, 'data')
ESG_DATA_PATH = os.path.join(DATA_FOLDER, 'esg_data.csv')
ESG_SERIES_PATH = os.path.join(DATA_FOLDER, 'esg_series.csv')

# Option 2: Data files are in the SAME directory as the app script
# ESG_DATA_PATH = os.path.join(SCRIPT_DIR, 'esg_data.csv')
# ESG_SERIES_PATH = os.path.join(SCRIPT_DIR, 'esg_series.csv')

# Option 3: Data files are in an ABSOLUTE PATH (e.g., C:/data/esg_data.csv on Windows)
# Only use this if you are absolutely sure of the exact path and it's not changing.
# ESG_DATA_PATH = '/path/to/your/esg_data.csv'
# ESG_SERIES_PATH = '/path/to/your/esg_series.csv'


@st.cache_data
def load_data():
    """
    Loads ESG data and series data, and merges them.
    Includes robust error handling for common merging issues.
    """
    st.subheader("Data Loading Process:")

    # 1. Check if the data folder exists (if applicable)
    if 'data' in DATA_FOLDER and not os.path.exists(DATA_FOLDER):
        st.error(f"Error: The data folder '{DATA_FOLDER}' does not exist.")
        st.info("Please create a 'data' folder in the same directory as this script and place your CSV files inside.")
        st.stop()

    # 2. Load the dataframes
    esg_data = pd.DataFrame() # Initialize as empty to prevent NameError if load fails
    esg_series = pd.DataFrame()

    try:
        if not os.path.exists(ESG_DATA_PATH):
            st.error(f"Error: `esg_data.csv` not found at '{ESG_DATA_PATH}'.")
            st.info("Please ensure the file exists and the `ESG_DATA_PATH` in the code is correct.")
            st.stop()
        esg_data = pd.read_csv(ESG_DATA_PATH)
        st.success(f"Successfully loaded `esg_data.csv` from '{ESG_DATA_PATH}'.")

        if not os.path.exists(ESG_SERIES_PATH):
            st.error(f"Error: `esg_series.csv` not found at '{ESG_SERIES_PATH}'.")
            st.info("Please ensure the file exists and the `ESG_SERIES_PATH` in the code is correct.")
            st.stop()
        esg_series = pd.read_csv(ESG_SERIES_PATH)
        st.success(f"Successfully loaded `esg_series.csv` from '{ESG_SERIES_PATH}'.")

    except pd.errors.EmptyDataError:
        st.error("Error: One of your CSV files is empty. Please check the content.")
        st.stop()
    except pd.errors.ParserError as e:
        st.error(f"Error parsing CSV file: {e}. Check if your CSV is well-formed.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data: {e}")
        st.stop()

    # --- Debugging and Column Name Handling for Merge ---
    st.subheader("Column Information Before Merge:")
    st.write("Columns in `esg_data`:", esg_data.columns.tolist())
    st.write("Columns in `esg_series`:", esg_series.columns.tolist())

    # Define the expected merge key
    merge_key = 'Series Code'
    st.info(f"Attempting to merge on column: '{merge_key}'")

    # Function to check and potentially rename a column
    def ensure_merge_key(df, df_name):
        cols = df.columns.tolist()
        if merge_key not in cols:
            st.warning(f"Warning: '{merge_key}' not found in `{df_name}`.")
            st.info(f"Attempting to find similar column names in `{df_name}` for a potential rename.")
            found = False
            for col in cols:
                # Case-insensitive and space/underscore insensitive comparison
                if col.lower().replace('_', ' ').strip() == merge_key.lower().replace('_', ' ').strip():
                    st.info(f"Renaming '{col}' in `{df_name}` to '{merge_key}'.")
                    df = df.rename(columns={col: merge_key})
                    found = True
                    break
            if not found:
                st.error(f"Could not find a suitable column to rename in `{df_name}` to '{merge_key}'. Merge will likely fail.")
                return None, False # Indicate failure
        return df, True # Indicate success

    esg_data, data_key_ok = ensure_merge_key(esg_data, 'esg_data')
    esg_series, series_key_ok = ensure_merge_key(esg_series, 'esg_series')

    if not data_key_ok or not series_key_ok:
        st.error("Merge cannot proceed because the required merge key is missing or could not be corrected in one or both dataframes.")
        st.stop()

    # Ensure the merge key column is of the same type (e.g., string)
    try:
        esg_data[merge_key] = esg_data[merge_key].astype(str)
        esg_series[merge_key] = esg_series[merge_key].astype(str)
        st.info(f"Successfully converted '{merge_key}' column to string type in both dataframes.")
    except Exception as e:
        st.warning(f"Could not convert '{merge_key}' column to string type: {e}. Proceeding with merge, but type mismatch could be an issue.")


    st.success(f"Both dataframes are ready for merge with a '{merge_key}' column.")

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
st.set_page_config(layout="wide", page_title="ESG Data Explorer")
st.title("🌎 Global ESG Data Explorer")

# Load data
data = load_data()

# Only proceed with UI if data loaded successfully
if data is not None and not data.empty:
    st.header("🔍 Explore Your Data")
    st.write("Use the sidebar filters to narrow down the dataset and visualize insights.")

    # Sidebar Filters
    st.sidebar.header("⚙️ Filters")

    # Example: Simple filtering (customize as needed)
    # Ensure columns exist before attempting to filter
    if 'Country Name' in data.columns:
        countries = data['Country Name'].dropna().unique().tolist()
        selected_country = st.sidebar.selectbox("Select Country", ['All'] + sorted(countries))
        if selected_country != 'All':
            data = data[data['Country Name'] == selected_country]
    else:
        st.sidebar.info(" 'Country Name' column not found for filtering.")

    if 'Year' in data.columns:
        # Convert 'Year' to integer and drop NaNs for correct sorting and filtering
        data['Year'] = pd.to_numeric(data['Year'], errors='coerce').dropna().astype(int)
        years = data['Year'].unique().tolist()
        selected_year = st.sidebar.selectbox("Select Year", ['All'] + sorted(years, reverse=True))
        if selected_year != 'All':
            data = data[data['Year'] == selected_year]
    else:
        st.sidebar.info(" 'Year' column not found for filtering.")

    if 'Series Name' in data.columns:
        series_names = data['Series Name'].dropna().unique().tolist()
        selected_series = st.sidebar.multiselect("Select Series Name(s)", sorted(series_names))
        if selected_series:
            data = data[data['Series Name'].isin(selected_series)]
    else:
        st.sidebar.info(" 'Series Name' column not found for filtering.")


    st.subheader("Filtered Data Preview")
    if not data.empty:
        st.dataframe(data.head(10)) # Show top 10 rows of filtered data
        st.info(f"Displaying {len(data)} rows.")
    else:
        st.warning("No data available after applying filters. Adjust your selections.")


    # Add more visualizations or analysis here using the 'data' dataframe
    st.header("📊 Data Visualizations")

    # Example: Display a simple metric
    st.subheader("Key Statistics (Filtered Data)")
    if 'Value' in data.columns:
        # Ensure 'Value' is numeric for calculations
        data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
        # Drop NaNs for sum calculation
        valid_values = data['Value'].dropna()
        if not valid_values.empty:
            st.metric("Total Value (Filtered)", f"{valid_values.sum():,.2f}")
            st.metric("Average Value (Filtered)", f"{valid_values.mean():,.2f}")
        else:
            st.info("No valid 'Value' data to calculate statistics with current filters.")
    else:
        st.info("The 'Value' column is not available for calculating statistics.")


    # Example Plotly Plot
    if 'Year' in data.columns and 'Value' in data.columns and 'Series Name' in data.columns:
        st.subheader("Value Over Time by Series")
        # Ensure 'Value' is numeric and 'Year' is suitable for plotting
        plot_data = data.dropna(subset=['Year', 'Value', 'Series Name']).copy() # Use .copy() to avoid SettingWithCopyWarning
        plot_data['Value'] = pd.to_numeric(plot_data['Value'], errors='coerce')
        plot_data['Year'] = pd.to_numeric(plot_data['Year'], errors='coerce').astype(int) # Ensure Year is int for plotting

        if not plot_data.empty:
            import plotly.express as px
            # Aggregate data for cleaner line plots if many series or data points
            plot_data_agg = plot_data.groupby(['Year', 'Series Name'])['Value'].mean().reset_index()

            fig = px.line(plot_data_agg, x='Year', y='Value', color='Series Name',
                          title='Average ESG Value Trends by Series',
                          labels={'Value': 'Average ESG Value', 'Year': 'Year'},
                          hover_name='Series Name',
                          markers=True) # Add markers for clarity
            fig.update_layout(hovermode="x unified") # Improves hover experience
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough valid 'Year', 'Value', and 'Series Name' data to generate the line plot with current filters.")
    else:
        st.info("Missing 'Year', 'Value', or 'Series Name' columns for plotting. Check your data.")

    # Add more complex plots or analysis here
    st.header("📚 Data Dictionary")
    st.write("This section could provide details about the columns in your merged dataset.")
    if 'Series Name' in data.columns and 'Definition' in data.columns:
        st.dataframe(data[['Series Code', 'Series Name', 'Definition']].drop_duplicates().set_index('Series Code'))
    else:
        st.info("Columns 'Series Name' or 'Definition' not available for data dictionary.")

else:
    st.warning("Data could not be loaded or is empty. Please check the error messages above.")
