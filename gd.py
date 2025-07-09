import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Data Loading Functions ---
@st.cache_data
def load_data(file_path):
    """Loads a CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Error: {file_path} not found. Please ensure the data files are in the 'data/' directory.")
        return pd.DataFrame()

# --- Metric Calculation Functions ---
def calculate_data_quality_metrics(df):
    """
    Calculates data quality metrics (Accuracy, Completeness, Consistency).
    Assumes `df` is your processed ESG data.
    YOU WILL NEED TO ADAPT THESE CALCULATIONS BASED ON YOUR ACTUAL DATA COLUMNS
    AND THE DEFINITIONS IN THE PDF.
    """
    if df.empty:
        return {
            "Data Accuracy Rate": 0.0,
            "Data Completeness Rate": 0.0,
            "Data Consistency Rate": 0.0
        }

    total_records = len(df)
    if total_records == 0:
        return {
            "Data Accuracy Rate": 0.0,
            "Data Completeness Rate": 0.0,
            "Data Consistency Rate": 0.0
        }

    # --- Data Accuracy Rate ---
    # From PDF: SUM([AccurateRecords]) / SUM([TotalRecords])
    # Placeholder: Assuming you have a way to determine 'accurate' records.
    # For ESG data, accuracy might mean:
    # 1. Values are within expected ranges.
    # 2. Values match external benchmarks (if available).
    # 3. No obvious data entry errors (e.g., negative population counts).
    # Example: Let's assume 'Value' column should always be non-negative.
    accurate_records_count = df[df['Value'] >= 0].shape[0] if 'Value' in df.columns else total_records
    data_accuracy_rate = accurate_records_count / total_records

    # --- Data Completeness Rate ---
    # From PDF: SUM([CompleteRecords]) / SUM([TotalRecords])
    # Placeholder: Check for missing values in critical columns.
    # Identify key columns that MUST NOT be null.
    critical_columns = ['Country Code', 'Series Code', 'Time', 'Value']
    # Filter to only include columns that actually exist in the dataframe
    existing_critical_columns = [col for col in critical_columns if col in df.columns]

    if existing_critical_columns:
        complete_records_count = df.dropna(subset=existing_critical_columns).shape[0]
        data_completeness_rate = complete_records_count / total_records
    else:
        # If no critical columns are found, consider all records 'complete' for placeholder
        data_completeness_rate = 1.0


    # --- Data Consistency Rate ---
    # From PDF: SUM([ConsistentRecords]) / SUM([TotalRecords])
    # Placeholder: This is highly domain-specific.
    # Example: If a 'Year' column should only contain integer values, or 'Value'
    # should be consistent with other related series data.
    # Let's check if 'Time' (year) is an integer and 'Value' is numeric.
    consistent_records_count = total_records # Start assuming all are consistent
    if 'Time' in df.columns:
        # Check if 'Time' can be converted to integer without error for most values
        try:
            df['Time_int_check'] = pd.to_numeric(df['Time'], errors='coerce').apply(lambda x: x == int(x) if pd.notna(x) else False)
            consistent_records_count = df[df['Time_int_check']].shape[0]
        except:
            pass # Fallback if column is not suitable

    if 'Value' in df.columns:
        try:
            # Check if 'Value' is numeric for consistency
            numeric_values = pd.to_numeric(df['Value'], errors='coerce').dropna()
            # If there are specific rules, apply them here (e.g., Value > 0 for certain series)
            # For simplicity, if it's numeric, consider it consistent in this placeholder.
            consistent_records_count = min(consistent_records_count, numeric_values.shape[0])
        except:
            pass

    data_consistency_rate = consistent_records_count / total_records

    return {
        "Data Accuracy Rate": data_accuracy_rate,
        "Data Completeness Rate": data_completeness_rate,
        "Data Consistency Rate": data_consistency_rate
    }


def calculate_data_access_metrics(df):
    """
    Calculates data access metrics.
    YOU WILL LIKELY NEED A SEPARATE DATASET FOR ACCESS REQUESTS AS PER THE PDF'S MENTION
    OF [AccessRequestID], [RequestStatus], [RequestDate], [ApprovalDate].
    These are placeholder values as ESGData.csv doesn't contain this info.
    """
    # From PDF:
    # Number of Data Access Requests: COUNT([AccessRequestID])
    # Number of Approved Requests: COUNT(IF [RequestStatus] = 'Approved' THEN 1 ELSE NULL END)
    # Average Time to Approve Requests: AVG(DATEDIFF('day', [RequestDate], [ApprovalDate]))

    # Placeholder: Simulating values for demonstration
    num_access_requests = 125
    num_approved_requests = 110
    avg_time_to_approve = 2.8 # days

    return {
        "Number of Data Access Requests": num_access_requests,
        "Number of Approved Requests": num_approved_requests,
        "Average Time to Approve Requests (days)": avg_time_to_approve
    }

def calculate_data_privacy_metrics(df):
    """
    Calculates data privacy metrics.
    YOU WILL NEED TO ADAPT THESE CALCULATIONS BASED ON YOUR ACTUAL DATA COLUMNS
    AND HOW YOU DEFINE PRIVACY COMPLIANCE (e.g., based on [ComplianceStatus] column).
    """
    if df.empty:
        return {
            "Compliance Rate with Privacy Policies": 0.0
        }

    # From PDF: Compliance Rate with Privacy Policies: SUM(IF [ComplianceStatus] = 'Compliant' THEN 1 ELSE 0 END) / COUNT([ComplianceStatus])

    # Placeholder: Assume 95% compliance for demonstration
    compliance_rate = 0.95

    return {
        "Compliance Rate with Privacy Policies": compliance_rate
    }

def calculate_data_security_metrics(df):
    """
    Calculates data security metrics.
    YOU WILL LIKELY NEED A SEPARATE SECURITY LOG DATASET.
    These are placeholder values.
    """
    if df.empty:
        return {
            "Number of Unauthorized Access Attempts": 0
        }

    # From PDF: Number of Unauthorized Access Attempts: COUNT(IF [AccessStatus] = 'Unauthorized' THEN 1 ELSE NULL END)

    # Placeholder: Simulating a number of unauthorized attempts
    num_unauthorized_attempts = 7

    return {
        "Number of Unauthorized Access Attempts": num_unauthorized_attempts
    }

def calculate_compliance_metrics(df):
    """
    Calculates general compliance metrics.
    YOU WILL NEED TO ADAPT THESE CALCULATIONS BASED ON YOUR ACTUAL DATA COLUMNS
    AND HOW YOU DEFINE GENERAL COMPLIANCE (e.g., based on [AuditStatus] column).
    """
    if df.empty:
        return {
            "Compliance Rate (General)": 0.0
        }

    # From PDF: Compliance Rate: SUM(IF [AuditStatus] = 'Passed' THEN 1 ELSE 0 END) / COUNT([AuditStatus])

    # Placeholder: Assume 90% general compliance for demonstration
    general_compliance_rate = 0.90

    return {
        "Compliance Rate (General)": general_compliance_rate
    }

# --- Visualization Functions ---
def create_gauge_chart(value, title, max_value=1.0):
    """
    Creates a simple gauge chart for a percentage value using Plotly Express.
    """
    value = max(0, min(value, max_value)) # Ensure value is within bounds

    fig = px.bar(
        x=[value], y=[0],
        orientation='h',
        range_x=[0, max_value],
        height=120,
        width=300,
        color_discrete_sequence=['lightgray'] # Background bar
    )

    # Add a colored bar for the actual value
    fig.add_bar(
        x=[value], y=[0],
        marker_color=px.colors.sequential.Plotly3[1] if value >= 0.8 else ('red' if value < 0.6 else 'orange'),
        showlegend=False
    )

    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        title=f"<b>{title}</b>",
        title_x=0.5, # Center title
        title_y=0.9
    )

    # Add text for the value
    fig.add_annotation(
        x=value, # Position at the end of the colored bar
        y=0.5, # Mid-height
        text=f"{value*100:.1f}%",
        showarrow=False,
        font=dict(size=20, color="black"),
        xanchor="left" if value < max_value * 0.7 else "right", # Adjust text anchor
        xshift=10 if value < max_value * 0.7 else -10
    )

    return fig

def create_bar_chart(df, x_col, y_col, title, color_col=None):
    """
    Creates a bar chart.
    """
    if df.empty:
        return px.scatter(title=f"<b>{title}</b><br><i>No data available</i>")
    fig = px.bar(df, x=x_col, y=y_col, title=f"<b>{title}</b>", color=color_col)
    fig.update_layout(xaxis_title="", yaxis_title="") # Clean up labels
    return fig

def create_line_chart(df, x_col, y_col, title, color_col=None):
    """
    Creates a line chart.
    """
    if df.empty:
        return px.scatter(title=f"<b>{title}</b><br><i>No data available</i>")
    fig = px.line(df, x=x_col, y=y_col, title=f"<b>{title}</b>", color=color_col)
    fig.update_layout(xaxis_title="", yaxis_title="")
    return fig

# --- Streamlit App Layout ---

# Set Streamlit page configuration
st.set_page_config(
    page_title="Data Governance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Data Governance and Security Dashboard")

# --- Load Data ---
# All data loading moved here for consolidation
esg_data = load_data('data/ESGData.csv')
esg_country = load_data('data/ESGCountry.csv')
esg_series = load_data('data/ESGSeries.csv')
# You can load other files if needed, e.g.,
# esg_series_time = load_data('data/ESGSeries-Time.csv')
# esg_footnote = load_data('data/ESGFootNote.csv')
# esg_country_series = load_data('data/ESGCountry-Series.csv')


if esg_data.empty or esg_country.empty or esg_series.empty:
    st.warning("One or more core data files could not be loaded. Please ensure they are in the 'data/' directory.")
    st.stop() # Stop the app if core data isn't loaded

# --- Data Preprocessing (Example: Merge for Country and Indicator Names) ---
# Merge Country Names
if 'Country Code' in esg_data.columns and 'Country Code' in esg_country.columns:
    esg_data = pd.merge(esg_data, esg_country[['Country Code', 'Table Name']],
                        on='Country Code', how='left')
    esg_data.rename(columns={'Table Name': 'Country Name'}, inplace=True)
else:
    st.warning("Country Code column not found in ESGData or ESGCountry for merging. Using Country Code as Country Name.")
    esg_data['Country Name'] = esg_data['Country Code'] # Fallback

# Merge Indicator Names
if 'Series Code' in esg_data.columns and 'Series Code' in esg_series.columns:
    esg_data = pd.merge(esg_data, esg_series[['Series Code', 'Indicator Name']],
                        on='Series Code', how='left')
else:
    st.warning("Series Code column not found in ESGData or ESGSeries for merging. Using Series Code as Indicator Name.")
    esg_data['Indicator Name'] = esg_data['Series Code'] # Fallback

# Ensure 'Time' column is numeric for filtering
if 'Time' in esg_data.columns:
    esg_data['Time'] = pd.to_numeric(esg_data['Time'], errors='coerce')
    esg_data.dropna(subset=['Time'], inplace=True)
    esg_data['Time'] = esg_data['Time'].astype(int)


# --- Sidebar Filters ---
st.sidebar.header("Filter Data")

# Country Filter
all_countries = ["All"] + sorted(esg_data['Country Name'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country:", all_countries)

# Year Filter (assuming 'Time' column in ESGData represents year)
if 'Time' in esg_data.columns:
    all_years = ["All"] + sorted(esg_data['Time'].dropna().unique().tolist())
    selected_year = st.sidebar.selectbox("Select Year:", all_years)
else:
    selected_year = "All"
    st.sidebar.warning("No 'Time' column found in ESGData for year filtering.")

# Apply filters
filtered_data = esg_data.copy()
if selected_country != "All":
    filtered_data = filtered_data[filtered_data['Country Name'] == selected_country]
if selected_year != "All":
    filtered_data = filtered_data[filtered_data['Time'] == selected_year]

# --- Dashboard Sections ---

st.header("Data Quality Metrics")
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

st.markdown("---")

st.header("Data Access & Security")
col4, col5, col6 = st.columns(3)
data_access_metrics = calculate_data_access_metrics(filtered_data)
data_security_metrics = calculate_data_security_metrics(filtered_data) # This will mostly use simulated data without a real log

with col4:
    st.metric(label="Number of Data Access Requests", value=f"{data_access_metrics['Number of Data Access Requests']:,}")
with col5:
    st.metric(label="Number of Approved Requests", value=f"{data_access_metrics['Number of Approved Requests']:,}")
with col6:
    st.metric(label="Avg. Time to Approve Requests", value=f"{data_access_metrics['Average Time to Approve Requests (days)']:.1f} days")

st.metric(label="Number of Unauthorized Access Attempts", value=f"{data_security_metrics['Number of Unauthorized Access Attempts']:,}")


st.markdown("---")

st.header("Data Privacy & Compliance")
col7, col8 = st.columns(2)
data_privacy_metrics = calculate_data_privacy_metrics(filtered_data)
compliance_metrics = calculate_compliance_metrics(filtered_data)

with col7:
    st.metric(label="Compliance Rate with Privacy Policies", value=f"{data_privacy_metrics['Compliance Rate with Privacy Policies']:.2%}")
    st.plotly_chart(create_gauge_chart(data_privacy_metrics['Compliance Rate with Privacy Policies'], "Privacy Compliance Rate"), use_container_width=True)
with col8:
    st.metric(label="General Compliance Rate", value=f"{compliance_metrics['Compliance Rate (General)']:.2%}")
    st.plotly_chart(create_gauge_chart(compliance_metrics['Compliance Rate (General)'], "General Compliance Rate"), use_container_width=True)

st.markdown("---")

st.header("Data Distribution & Trends")

# Example: Data points by Indicator
if not filtered_data.empty and 'Indicator Name' in filtered_data.columns:
    indicator_counts = filtered_data['Indicator Name'].value_counts().reset_index()
    indicator_counts.columns = ['Indicator Name', 'Count']
    # Show top N indicators
    n_top_indicators = st.slider("Show Top N Indicators:", 5, 20, 10)
    st.plotly_chart(create_bar_chart(indicator_counts.head(n_top_indicators), 'Indicator Name', 'Count', f"Top {n_top_indicators} Indicators by Data Points"), use_container_width=True)
else:
    st.info("No 'Indicator Name' data or filtered data is empty for distribution analysis.")


# Example: Value trends over time for a selected indicator (if 'Time' and 'Value' exist)
if 'Time' in filtered_data.columns and 'Value' in filtered_data.columns and 'Indicator Name' in filtered_data.columns:
    st.subheader("Indicator Value Trends Over Time")
    available_indicators = filtered_data['Indicator Name'].dropna().unique().tolist()
    if available_indicators:
        selected_trend_indicator = st.selectbox("Select Indicator for Trend:", available_indicators)
        trend_data = filtered_data[filtered_data['Indicator Name'] == selected_trend_indicator].sort_values('Time')
        if not trend_data.empty:
            # Aggregate if multiple entries for same year/indicator (e.g., average)
            trend_data_agg = trend_data.groupby('Time')['Value'].mean().reset_index()
            st.plotly_chart(create_line_chart(trend_data_agg, 'Time', 'Value', f"Trend of {selected_trend_indicator}"), use_container_width=True)
        else:
            st.info("No data for selected indicator trend.")
    else:
        st.info("No indicators available for trend analysis.")
else:
    st.info("Required columns ('Time', 'Value', 'Indicator Name') not found for trend analysis.")


st.markdown("---")
st.caption("Developed as a Data Governance Dashboard using Streamlit.")
