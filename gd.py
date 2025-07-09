import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Data Loading Functions ---
@st.cache_data
def load_data(data):
    """
    Loads a CSV file from the specified path.
    Uses Streamlit's caching to improve performance by loading data only once.
    """
    try:
        df = pd.read_csv(data)
        return df
    except FileNotFoundError:
        st.error(f"Error: Data file not found: '{data}'. Please ensure your CSVs are in the 'data/' directory.")
        return pd.DataFrame() # Return an empty DataFrame on error

# --- Metric Calculation Functions ---
def calculate_data_quality_metrics(df):
    """
    Calculates data quality metrics (Accuracy, Completeness, Consistency).
    These calculations are placeholders and should be customized based on:
    1. The actual structure and content of your 'ESGData.csv'.
    2. The specific definitions of data quality metrics outlined in your
       "Data Governance and Security Dashboard (Business Analyst).pdf" document.
    """
    if df.empty:
        return {
            "Data Accuracy Rate": 0.0,
            "Data Completeness Rate": 0.0,
            "Data Consistency Rate": 0.0
        }

    total_records = len(df)
    if total_records == 0: # Avoid division by zero if DataFrame is empty after filtering
        return {
            "Data Accuracy Rate": 0.0,
            "Data Completeness Rate": 0.0,
            "Data Consistency Rate": 0.0
        }

    # --- Data Accuracy Rate ---
    # Placeholder: Assumes 'Value' column should be non-negative for data to be considered 'accurate'.
    # Replace this with your actual business rules for data accuracy.
    # For example: checking against a lookup table, validating data types, or range checks.
    accurate_records_count = df[df['Value'] >= 0].shape[0] if 'Value' in df.columns else total_records
    data_accuracy_rate = accurate_records_count / total_records

    # --- Data Completeness Rate ---
    # Placeholder: Checks for missing values (NaN) in a set of critical columns.
    # Adjust `critical_columns` list to include all columns that MUST NOT be empty.
    critical_columns = ['Country Code', 'Series Code', 'Time', 'Value']
    # Filter to only include columns that actually exist in the current DataFrame
    existing_critical_columns = [col for col in critical_columns if col in df.columns]

    if existing_critical_columns:
        # Count rows where all specified critical columns have non-null values
        complete_records_count = df.dropna(subset=existing_critical_columns).shape[0]
        data_completeness_rate = complete_records_count / total_records
    else:
        # If no critical columns are found (e.g., due to schema changes), assume 100% completeness
        data_completeness_rate = 1.0

    # --- Data Consistency Rate ---
    # Placeholder: Checks for consistency based on 'Time' being an integer and 'Value' being numeric.
    # Replace with your actual consistency rules. This could involve:
    # - Cross-field validation (e.g., if A then B must be C)
    # - Adherence to specific formats (e.g., date formats, string patterns)
    # - Referential integrity checks against other tables.
    consistent_records_count = total_records # Start by assuming all records are consistent

    if 'Time' in df.columns:
        try:
            # Check if 'Time' can be converted to integer and is indeed an integer
            df['Time_is_int'] = pd.to_numeric(df['Time'], errors='coerce').apply(lambda x: x == int(x) if pd.notna(x) else False)
            consistent_records_count = df[df['Time_is_int']].shape[0]
        except Exception as e:
            st.warning(f"Consistency check for 'Time' column encountered an issue: {e}")

    if 'Value' in df.columns:
        try:
            # Check if 'Value' is numeric. If not, coerce to NaN and drop.
            numeric_values_count = pd.to_numeric(df['Value'], errors='coerce').dropna().shape[0]
            # Take the minimum of existing consistency checks
            consistent_records_count = min(consistent_records_count, numeric_values_count)
        except Exception as e:
            st.warning(f"Consistency check for 'Value' column encountered an issue: {e}")

    data_consistency_rate = consistent_records_count / total_records

    return {
        "Data Accuracy Rate": data_accuracy_rate,
        "Data Completeness Rate": data_completeness_rate,
        "Data Consistency Rate": data_consistency_rate
    }


def calculate_data_access_metrics(df):
    """
    Calculates data access metrics.
    These are simulated placeholder values. In a real-world scenario,
    these metrics would typically be derived from a separate data access log
    that contains fields like 'AccessRequestID', 'RequestStatus', 'RequestDate',
    and 'ApprovalDate' as mentioned in the PDF.
    """
    num_access_requests = 125 # Example: Total number of data access requests
    num_approved_requests = 110 # Example: Number of approved requests
    avg_time_to_approve = 2.8 # Example: Average time in days to approve requests

    return {
        "Number of Data Access Requests": num_access_requests,
        "Number of Approved Requests": num_approved_requests,
        "Average Time to Approve Requests (days)": avg_time_to_approve
    }

def calculate_data_privacy_metrics(df):
    """
    Calculates data privacy compliance metrics.
    This is a placeholder. Real privacy compliance would involve:
    - Auditing data handling processes.
    - Checking for unauthorized PII access/storage.
    - Reviewing data masking/anonymization effectiveness.
    - Assessing adherence to regulations (e.g., GDPR, CCPA).
    """
    # From PDF: SUM(IF [ComplianceStatus] = 'Compliant' THEN 1 ELSE 0 END) / COUNT([ComplianceStatus])
    # Simulating a high compliance rate for demonstration purposes.
    compliance_rate = 0.95

    return {
        "Compliance Rate with Privacy Policies": compliance_rate
    }

def calculate_data_security_metrics(df):
    """
    Calculates data security metrics.
    This is a placeholder. In a production environment, this would integrate with:
    - Security information and event management (SIEM) systems.
    - Intrusion detection/prevention systems (IDS/IPS) logs.
    - Access control logs.
    """
    # From PDF: COUNT(IF [AccessStatus] = 'Unauthorized' THEN 1 ELSE NULL END)
    # Simulating a small, fixed number of unauthorized attempts.
    num_unauthorized_attempts = 7

    return {
        "Number of Unauthorized Access Attempts": num_unauthorized_attempts
    }

def calculate_compliance_metrics(df):
    """
    Calculates general compliance metrics.
    This is a placeholder. General compliance could encompass:
    - Results from internal or external audits (e.g., audit pass rate).
    - Adherence to industry standards or internal policies.
    """
    # From PDF: SUM(IF [AuditStatus] = 'Passed' THEN 1 ELSE 0 END) / COUNT([AuditStatus])
    # Simulating a general compliance rate.
    general_compliance_rate = 0.90

    return {
        "Compliance Rate (General)": general_compliance_rate
    }

# --- Visualization Functions ---
def create_gauge_chart(value, title, max_value=1.0):
    """
    Creates a simple horizontal bar chart that acts as a gauge for a percentage value.
    The bar color changes based on the 'value' to indicate performance (red, orange, green).
    """
    value = max(0, min(value, max_value)) # Ensure value is within bounds [0, max_value]

    # Create a base bar (light gray) representing the full range
    fig = px.bar(
        x=[max_value], y=[0],
        orientation='h',
        range_x=[0, max_value],
        height=120,
        width=300,
        color_discrete_sequence=['lightgray']
    )

    # Determine the color of the value bar based on thresholds
    bar_color = 'red' if value < 0.6 else ('orange' if value < 0.8 else px.colors.sequential.Plotly3[1]) # Green-like color

    # Add the actual value bar on top of the base bar
    fig.add_bar(
        x=[value], y=[0],
        marker_color=bar_color,
        showlegend=False
    )

    # Configure layout for a clean, gauge-like appearance
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", # Transparent plot background
        paper_bgcolor="rgba(0,0,0,0)", # Transparent paper background
        margin=dict(l=0, r=0, t=50, b=0), # Adjust margins
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False), # Hide x-axis elements
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False), # Hide y-axis elements
        title=f"<b>{title}</b>", # Bold title
        title_x=0.5, # Center title horizontally
        title_y=0.9 # Position title near the top
    )

    # Add the percentage text directly on the gauge
    fig.add_annotation(
        x=value, # Position text at the end of the colored bar
        y=0.5, # Vertically centered
        text=f"{value*100:.1f}%", # Format value as percentage with one decimal
        showarrow=False,
        font=dict(size=20, color="black"),
        # Adjust text anchor to prevent overlap with the bar's end
        xanchor="left" if value < max_value * 0.7 else "right",
        xshift=10 if value < max_value * 0.7 else -10 # Shift text slightly
    )

    return fig

def create_bar_chart(df, x_col, y_col, title, color_col=None):
    """
    Creates a bar chart using Plotly Express.
    Includes a message if the DataFrame is empty.
    """
    if df.empty:
        return px.scatter(title=f"<b>{title}</b><br><i>No data available</i>")
    fig = px.bar(df, x=x_col, y=y_col, title=f"<b>{title}</b>", color=color_col)
    fig.update_layout(xaxis_title="", yaxis_title="") # Clean up axis labels
    return fig

def create_line_chart(df, x_col, y_col, title, color_col=None):
    """
    Creates a line chart using Plotly Express.
    Includes a message if the DataFrame is empty.
    """
    if df.empty:
        return px.scatter(title=f"<b>{title}</b><br><i>No data available</i>")
    fig = px.line(df, x=x_col, y=y_col, title=f"<b>{title}</b>", color=color_col)
    fig.update_layout(xaxis_title="", yaxis_title="") # Clean up axis labels
    return fig

# --- Streamlit App Layout ---

# Configure the Streamlit page settings
st.set_page_config(
    page_title="Data Governance Dashboard", # Title that appears in the browser tab
    page_icon="📊", # Icon for the browser tab
    layout="wide", # Use a wide layout for more content space
    initial_sidebar_state="expanded" # Keep the sidebar open by default
)

st.title("📊 Data Governance and Security Dashboard") # Main title of the dashboard

# --- Load Data ---
# Load all necessary CSV files. These paths are relative to where app.py is run.
esg_data = load_data('data/ESGData.csv')
esg_country = load_data('data/ESGCountry.csv')
esg_series = load_data('data/ESGSeries.csv')
# You can uncomment and load other CSV files if your metrics or visualizations require them:
# esg_series_time = load_data('data/ESGSeries-Time.csv')
# esg_footnote = load_data('data/ESGFootNote.csv')
# esg_country_series = load_data('data/ESGCountry-Series.csv')


# Check if core dataframes are loaded successfully before proceeding
if esg_data.empty or esg_country.empty or esg_series.empty:
    st.warning("One or more core data files could not be loaded. Please ensure they are in the 'data/' directory and accessible.")
    st.stop() # Stop the application if essential data is missing

# --- Debugging Output: Display actual columns and head of data ---
st.subheader("Debugging Info (Temporary - will be removed later)")
st.write("Columns in ESG Data:", esg_data.columns.tolist())
st.write("First 5 rows of ESG Data:", esg_data.head())
st.write("Columns in ESG Country:", esg_country.columns.tolist())
st.write("Columns in ESG Series:", esg_series.columns.tolist())
st.subheader("End Debugging Info")

# --- Data Preprocessing (Merging for display names) ---
# Initialize 'Country Name' and 'Indicator Name' columns with placeholders
# This ensures these columns always exist, preventing AttributeError later.
esg_data['Country Name'] = "Unknown Country"
esg_data['Indicator Name'] = "Unknown Indicator"

# Merge Country Names from ESGCountry.csv into ESGData.csv
# This enriches the main data with human-readable country names.
if 'Country Code' in esg_data.columns and 'Country Code' in esg_country.columns:
    esg_data = pd.merge(esg_data, esg_country[['Country Code', 'Table Name']],
                        on='Country Code', how='left', suffixes=('', '_y'))
    # Use the merged 'Table Name' if available, otherwise keep 'Unknown Country'
    esg_data['Country Name'] = esg_data['Table Name'].fillna(esg_data['Country Name'])
    # Drop the temporary merged column
    if 'Table Name' in esg_data.columns:
        esg_data.drop(columns=['Table Name'], inplace=True)
else:
    st.warning("Column 'Country Code' not found in ESGData or ESGCountry for merging. 'Country Name' will be 'Unknown Country'.")


# Merge Indicator Names from ESGSeries.csv into ESGData.csv
# This adds descriptive names for the ESG indicators.
if 'Series Code' in esg_data.columns and 'Series Code' in esg_series.columns:
    esg_data = pd.merge(esg_data, esg_series[['Series Code', 'Indicator Name']],
                        on='Series Code', how='left', suffixes=('', '_y'))
    # Use the merged 'Indicator Name' if available, otherwise keep 'Unknown Indicator'
    esg_data['Indicator Name'] = esg_data['Indicator Name_y'].fillna(esg_data['Indicator Name'])
    # Drop the temporary merged column
    if 'Indicator Name_y' in esg_data.columns:
        esg_data.drop(columns=['Indicator Name_y'], inplace=True)
else:
    st.warning("Column 'Series Code' not found in ESGData or ESGSeries for merging. 'Indicator Name' will be 'Unknown Indicator'.")


# Ensure 'Time' column is numeric and integer for proper filtering and plotting
if 'Time' in esg_data.columns:
    esg_data['Time'] = pd.to_numeric(esg_data['Time'], errors='coerce') # Convert to numeric, errors become NaN
    esg_data.dropna(subset=['Time'], inplace=True) # Remove rows where 'Time' couldn't be converted
    esg_data['Time'] = esg_data['Time'].astype(int) # Convert to integer for cleaner display
else:
    st.warning("No 'Time' column found in ESGData. Year filtering and time-series plots may be limited.")


# --- Sidebar Filters ---
st.sidebar.header("Filter Data")

# Country Filter: Allows users to select a specific country or view all data.
# Ensure 'Country Name' column exists and is not entirely empty before populating selectbox
if 'Country Name' in esg_data.columns and not esg_data['Country Name'].dropna().empty:
    all_countries = ["All"] + sorted(esg_data['Country Name'].dropna().unique().tolist())
else:
    all_countries = ["All"] # Fallback if no country names are available or df is empty
selected_country = st.sidebar.selectbox("Select Country:", all_countries)

# Year Filter: Allows users to select a specific year or view all years.
# Only display if 'Time' column is available in the data.
selected_year = "All" # Default value
if 'Time' in esg_data.columns and not esg_data['Time'].dropna().empty:
    all_years = ["All"] + sorted(esg_data['Time'].dropna().unique().tolist())
    selected_year = st.sidebar.selectbox("Select Year:", all_years)
else:
    st.sidebar.info("Year filter not available as 'Time' column is missing or invalid in the data.")

# Apply filters to create the `filtered_data` DataFrame used for calculations and visualizations
filtered_data = esg_data.copy()
if selected_country != "All":
    filtered_data = filtered_data[filtered_data['Country Name'] == selected_country]
if selected_year != "All":
    filtered_data = filtered_data[filtered_data['Time'] == selected_year]

# --- Dashboard Sections ---

# Section 1: Data Quality Metrics
st.header("Data Quality Metrics")
# Use Streamlit columns to arrange metrics and charts side-by-side
col1, col2, col3 = st.columns(3)
data_quality_metrics = calculate_data_quality_metrics(filtered_data)

with col1:
    st.metric(label="Data Accuracy Rate", value=f"{data_quality_metrics['Data Accuracy Rate']:.2%}")
    st.plotly_chart(create_gauge_chart(data_quality_metrics['Data Accuracy Rate'], "Accuracy Rate"), use_container_width=True)
with col2:
    st.metric(label="Data Completeness Rate", value=f"{data_quality_metrics['Data Completeness Rate']:.2%}")
    st.plotly_chart(create_gauge_chart(data_quality_metrics['Data Completeness Rate'], "Completeness Rate"), use_container_width=True)
with col3:
    st.metric(label="Data Consistency Rate", value=f"{data_quality_metrics['Data Consistency Rate']:.2%}")
    st.plotly_chart(create_gauge_chart(data_quality_metrics['Data Consistency Rate'], "Consistency Rate"), use_container_width=True)

st.markdown("---") # Visual separator

# Section 2: Data Access & Security Metrics
st.header("Data Access & Security")
col4, col5, col6 = st.columns(3)
data_access_metrics = calculate_data_access_metrics(filtered_data) # Uses simulated data
data_security_metrics = calculate_data_security_metrics(filtered_data) # Uses simulated data

with col4:
    st.metric(label="Number of Data Access Requests", value=f"{data_access_metrics['Number of Data Access Requests']:,}")
with col5:
    st.metric(label="Number of Approved Requests", value=f"{data_access_metrics['Number of Approved Requests']:,}")
with col6:
    st.metric(label="Avg. Time to Approve Requests", value=f"{data_access_metrics['Average Time to Approve Requests (days)']:.1f} days")

# Display unauthorized access attempts separately
st.metric(label="Number of Unauthorized Access Attempts", value=f"{data_security_metrics['Number of Unauthorized Access Attempts']:,}")


st.markdown("---") # Visual separator

# Section 3: Data Privacy & General Compliance Metrics
st.header("Data Privacy & Compliance")
col7, col8 = st.columns(2)
data_privacy_metrics = calculate_data_privacy_metrics(filtered_data) # Uses simulated data
compliance_metrics = calculate_compliance_metrics(filtered_data) # Uses simulated data

with col7:
    st.metric(label="Compliance Rate with Privacy Policies", value=f"{data_privacy_metrics['Compliance Rate with Privacy Policies']:.2%}")
    st.plotly_chart(create_gauge_chart(data_privacy_metrics['Compliance Rate with Privacy Policies'], "Privacy Compliance Rate"), use_container_width=True)
with col8:
    st.metric(label="General Compliance Rate", value=f"{compliance_metrics['Compliance Rate (General)']:.2%}")
    st.plotly_chart(create_gauge_chart(compliance_metrics['Compliance Rate (General)'] , "General Compliance Rate"), use_container_width=True)

st.markdown("---") # Visual separator

# Section 4: Data Distribution & Trends
st.header("Data Distribution & Trends")

# Bar chart: Data points by Indicator
if not filtered_data.empty and 'Indicator Name' in filtered_data.columns:
    indicator_counts = filtered_data['Indicator Name'].value_counts().reset_index()
    indicator_counts.columns = ['Indicator Name', 'Count']
    # Slider to allow user to select how many top indicators to display
    n_top_indicators = st.slider("Show Top N Indicators by Data Points:", 5, 20, 10, help="Adjust to see more or fewer top indicators.")
    st.plotly_chart(create_bar_chart(indicator_counts.head(n_top_indicators), 'Indicator Name', 'Count', f"Top {n_top_indicators} Indicators by Data Points"), use_container_width=True)
else:
    st.info("No 'Indicator Name' data or filtered data is empty for distribution analysis.")


# Line chart: Value trends over time for a selected indicator
if 'Time' in filtered_data.columns and 'Value' in filtered_data.columns and 'Indicator Name' in filtered_data.columns:
    st.subheader("Indicator Value Trends Over Time")
    available_indicators = filtered_data['Indicator Name'].dropna().unique().tolist()
    if available_indicators:
        selected_trend_indicator = st.selectbox("Select Indicator for Trend Analysis:", available_indicators)
        # Filter data for the selected indicator and sort by time for correct trend plotting
        trend_data = filtered_data[filtered_data['Indicator Name'] == selected_trend_indicator].sort_values('Time')
        if not trend_data.empty:
            # Aggregate by 'Time' (e.g., average value per year) if multiple entries exist for the same year/indicator
            trend_data_agg = trend_data.groupby('Time')['Value'].mean().reset_index()
            st.plotly_chart(create_line_chart(trend_data_agg, 'Time', 'Value', f"Trend of {selected_trend_indicator}"), use_container_width=True)
        else:
            st.info("No data available for the selected indicator to show trends.")
    else:
        st.info("No indicators available in the filtered data for trend analysis.")
else:
    st.info("Required columns ('Time', 'Value', 'Indicator Name') not found for trend analysis, or filtered data is empty.")


st.markdown("---") # Final visual separatorA
st.caption("Developed as a Data Governance Dashboard using Streamlit. Remember to customize metric calculations for your specific data.")
