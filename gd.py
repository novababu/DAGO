import streamlit as st
import plotly.express as px
import pandas as pd
from io import StringIO

# --- Data Loading (as previously defined and corrected) ---
esg_data_content = """Country Name,Country Code,Indicator Name,Indicator Code,2010,2015,2020
Arab World,ARB,Access to clean fuels and technologies for cooking (% of population),EG.CFT.ACCS.ZS,81.8096301963981,83.8975960063981,84.5101713274267
Arab World,ARB,CO2 emissions (metric tons per capita),EN.ATM.CO2E.PC,4.63064477024689,4.95692831352378,4.71284470207848
United States,USA,CO2 emissions (metric tons per capita),EN.ATM.CO2E.PC,13.359288,12.000407,9.176472
India,IND,CO2 emissions (metric tons per capita),EN.ATM.CO2E.PC,1.475037,1.676943,1.845198
United States,USA,Adjusted savings: natural resources depletion (% of GNI),NY.ADJ.DRES.GN.ZS,0.160354,0.158876,0.158013
India,IND,Adjusted savings: natural resources depletion (% of GNI),NY.ADJ.DRES.GN.ZS,2.100939,2.236987,2.339023
"""

esg_country_content = """Country Code,Short Name,Region,Income Group
USA,United States,North America,High income
IND,India,Asia,Lower middle income
CAN,Canada,North America,High income
ARB,Arab World,Aggregates,Aggregates
"""

esg_series_content = """Series Code,Topic,Indicator Name,Short definition,Long definition
EG.CFT.ACCS.ZS,"Environment: Energy and mining","Access to clean fuels and technologies for cooking (% of population)","The share of population with access to clean cooking fuels and technologies.","Access to clean cooking fuels and technologies is the percentage of population primarily using improved cooking stoves or fuels (e.g., electricity, natural gas, LPG, biogas, solar) for cooking."
EN.ATM.CO2E.PC,"Environment: Emissions","CO2 emissions (metric tons per capita)","Carbon dioxide emissions are those stemming from the burning of fossil fuels and the manufacture of cement.","Carbon dioxide emissions are those stemming from the burning of fossil fuels and the manufacture of cement. They include carbon dioxide produced during consumption of solid, liquid, and gas fuels and gas flaring."
NY.ADJ.DRES.GN.ZS,"Environment: Environmental policy and institutions","Adjusted savings: natural resources depletion (% of GNI)","Natural resource depletion is the sum of net forest depletion, energy depletion, and mineral depletion.","Natural resource depletion is the sum of net forest depletion, energy depletion, and mineral depletion."
"""

# Load data
esg_data = pd.read_csv(StringIO(esg_data_content))
esg_country = pd.read_csv(StringIO(esg_country_content))
esg_series = pd.read_csv(StringIO(esg_series_content))

# Strip whitespace from key columns in all dataframes
esg_data['Country Code'] = esg_data['Country Code'].str.strip()
esg_data['Indicator Code'] = esg_data['Indicator Code'].str.strip()
esg_country['Country Code'] = esg_country['Country Code'].str.strip()
esg_series['Series Code'] = esg_series['Series Code'].str.strip()

# Melt ESGData.csv to long format for easier plotting
years = [col for col in esg_data.columns if col.isdigit()]
esg_data_melted = esg_data.melt(
    id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
    value_vars=years,
    var_name="Year",
    value_name="Value"
)

# Convert 'Year' to integer and 'Value' to numeric
esg_data_melted["Year"] = pd.to_numeric(esg_data_melted["Year"])
esg_data_melted["Value"] = pd.to_numeric(esg_data_melted["Value"], errors='coerce')

# Merge with ESGCountry for region and income group
esg_data_merged = pd.merge(
    esg_data_melted,
    esg_country[["Country Code", "Short Name", "Region", "Income Group"]],
    on="Country Code",
    how="left"
)

# Merge with ESGSeries for Topic (Category) and Description
esg_data_merged = pd.merge(
    esg_data_merged,
    esg_series[["Series Code", "Topic", "Indicator Name", "Short definition", "Long definition"]],
    left_on="Indicator Code",
    right_on="Series Code",
    how="left",
    suffixes=('_data', '_series')
)

# Drop redundant columns after merge
esg_data_merged.drop(columns=["Series Code"], inplace=True)

# --- Streamlit Dashboard Code ---

st.set_page_config(layout="wide")

st.title("ESG Data Dashboard")

st.markdown("""
This dashboard provides an interactive way to explore Environmental, Social, and Governance (ESG) data.
Use the filters on the sidebar to select countries, indicators, and years to visualize trends and comparisons.
""")

# Sidebar filters
st.sidebar.header("Filter Data")

# Country selection
all_countries = sorted(esg_data_merged['Country Name'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=all_countries if len(all_countries) <= 5 else all_countries[:5]
)

# Indicator selection
all_indicators = sorted(esg_data_merged['Indicator Name_data'].unique())
selected_indicators = st.sidebar.multiselect(
    "Select Indicators",
    options=all_indicators,
    default=all_indicators[0] if all_indicators else []
)

# Year selection
min_year = int(esg_data_merged['Year'].min())
max_year = int(esg_data_merged['Year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter data based on selections
filtered_df = esg_data_merged[
    (esg_data_merged['Country Name'].isin(selected_countries)) &
    (esg_data_merged['Indicator Name_data'].isin(selected_indicators)) &
    (esg_data_merged['Year'] >= selected_years[0]) &
    (esg_data_merged['Year'] <= selected_years[1])
]

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
else:
    st.subheader("ESG Data Trends")

    # Line chart for time series data
    fig = px.line(
        filtered_df,
        x="Year",
        y="Value",
        color="Country Name",
        line_dash="Indicator Name_data",
        title="Indicator Values Over Time",
        hover_data={
            "Country Name": True,
            "Indicator Name_data": True,
            "Year": True,
            "Value": ':.2f',
            "Short definition": True
        }
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Detailed Data View")
    st.dataframe(filtered_df)

st.sidebar.markdown("---")
st.sidebar.info("Data sourced from various ESG datasets.")
