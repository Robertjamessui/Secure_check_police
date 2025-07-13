import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="SecureCheck", layout="wide") 
st.title(" SecureCheck: Police Check Post Dashboard")

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="securecheck"
)

# Function to load data from MySQL
@st.cache_data 
def load_data():
    query = "SELECT * FROM traffic_logs"
    df = pd.read_sql(query, con=mydb)
    return df

df = load_data()

# Display the data
st.subheader("All Check Post Records")
st.dataframe(df)


st.sidebar.header("Filter Options")

# Unique filter values
countries = df['country_name'].dropna().unique()
genders = df['driver_gender'].dropna().unique()
violations = df['violation'].dropna().unique()

# Sidebar filters
selected_country = st.sidebar.multiselect("Select Country", sorted(countries))
selected_gender = st.sidebar.multiselect("Select Gender", sorted(genders))
selected_violation = st.sidebar.multiselect("Select Violation", sorted(violations))

# Apply filters
filtered_df = df.copy()

if selected_country:
    filtered_df = filtered_df[filtered_df['country_name'].isin(selected_country)]
if selected_gender:
    filtered_df = filtered_df[filtered_df['driver_gender'].isin(selected_gender)]
if selected_violation:
    filtered_df = filtered_df[filtered_df['violation'].isin(selected_violation)]

st.subheader(" Filtered Records")
st.dataframe(filtered_df) 



import plotly.express as px

st.subheader("Insights & Analysis")

# 1. Drug-related stops by vehicle count (if vehicle_number column is available)
if 'drugs_related_stop' in df.columns:
    drug_related = filtered_df[filtered_df['drugs_related_stop'] == True]
    st.markdown("**Top Drug-Related Violations**")
    st.bar_chart(drug_related['violation'].value_counts().head(10))

# 2. Arrest Rate by Gender
st.markdown("**Arrest Rate by Gender**")
gender_arrest = df.groupby('driver_gender')['is_arrested'].mean().reset_index()
st.dataframe(gender_arrest)

# 3. Stop Duration Distribution
st.markdown("**Stop Duration Distribution**")
duration_counts = df['stop_duration'].value_counts().reset_index()
fig = px.pie(duration_counts, names='stop_duration', values='count', title="Stop Duration Distribution")

# 4. Most Common Violations
st.markdown("**Most Common Violations**")
violation_counts = df['violation'].value_counts().head(10)
st.bar_chart(violation_counts)

st.subheader(" Visual Insights") 

tab1, tab2 = st.tabs(["Stops by Violation", "Driver Gender Distribution"])

with tab1:
    st.markdown("### Stops by Violation Type")
    violation_df = df['violation'].value_counts().reset_index()
    violation_df.columns = ['violation', 'count']
    fig1 = px.bar(violation_df, x='violation', y='count', color='violation', title='Violation Types Count')
    st.plotly_chart(fig1)

with tab2:
    st.markdown("### Driver Gender Distribution")
    gender_df = df['driver_gender'].value_counts().reset_index()
    gender_df.columns = ['Gender', 'Count']
    fig2 = px.pie(gender_df, names='Gender', values='Count', title='Driver Gender Share')
    st.plotly_chart(fig2)

# -----------------------
# 🔍 Additional Insights
# -----------------------
st.subheader("🔍 Additional Insights")

# 1️⃣ Driver Age Distribution (Histogram)
if 'driver_age' in df.columns:
    st.markdown("**Driver Age Distribution**")
    fig_age = px.histogram(df, x='driver_age', nbins=20, title="Driver Age Distribution", color_discrete_sequence=["#FF7676"])
    st.plotly_chart(fig_age, use_container_width=True)

# 2️⃣ Arrest Time Heatmap (Hour vs Arrests)
if 'stop_datetime' in df.columns and 'is_arrested' in df.columns:
    df['hour'] = df['stop_datetime'].dt.hour
    heatmap_data = df[df['is_arrested'] == True].groupby('hour').size().reset_index(name='arrest_count')
    fig_heatmap = px.bar(heatmap_data, x='hour', y='arrest_count',
                         labels={'hour': 'Hour of Day', 'arrest_count': 'Arrests'},
                         title=" Arrests by Hour of Day", color='arrest_count', color_continuous_scale='Blues')
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.header(" Add New Police Log & Predict Outcome and Violation")

with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["Male", "Female", "Other"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a Search Conducted?", ["Yes", "No"])
    search_type = st.text_input("Search Type")
    is_arrested = st.selectbox("Was a Drug Involved?", ["Yes", "No"])
    stop_duration = st.selectbox("Stop Duration", ["0-15 Min", "16-30 Min", "30+ Min"])
    vehicle_number = st.text_input("Vehicle Number")

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

if submitted:
    # Simulated Prediction (replace with ML later)
    simulated_outcome = "Citation" if driver_age > 25 else "Warning"
    simulated_violation = "Speeding" if int(stop_time.strftime("%H")) in range(7, 19) else "Equipment"

    st.success(" Prediction Generated")
    st.markdown(f"""
     A {driver_age}-year-old {driver_gender.lower()} driver was stopped  
    for **{simulated_violation}** at **{stop_time.strftime('%I:%M %p')}** in {country_name}.  
    {'A search was conducted' if search_conducted == 'Yes' else 'No search was conducted'},  
    and the driver **received a {simulated_outcome}**.  
    The stop lasted **{stop_duration}** and was **{'drug-related' if is_arrested == 'Yes' else 'not drug-related'}**.
    """)
 
st.markdown("## Advanced Insights")
st.markdown("#### Select a Query to Run")

query_options = [
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops (Year, Month, Hour)",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country",
    "Top 5 Violations with Highest Arrest Rates"
]

selected_query = st.selectbox(" Choose Analysis", query_options)
if st.button("Run Query"):

    if selected_query == "Yearly Breakdown of Stops and Arrests by Country":
        query = """
        SELECT 
            country_name,
            YEAR(stop_datetime) AS year,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests
        FROM traffic_logs
        GROUP BY country_name, year
        ORDER BY year DESC, total_stops DESC
        """
    
    elif selected_query == "Driver Violation Trends Based on Age and Race":
        query = """
        SELECT 
            driver_race,
            driver_age,
            violation,
            COUNT(*) AS count
        FROM traffic_logs
        WHERE driver_age IS NOT NULL
        GROUP BY driver_race, driver_age, violation
        ORDER BY count DESC
        """

    elif selected_query == "Time Period Analysis of Stops (Year, Month, Hour)":
        query = """
        SELECT 
            YEAR(stop_datetime) AS year,
            MONTH(stop_datetime) AS month,
            HOUR(stop_datetime) AS hour,
            COUNT(*) AS stop_count
        FROM traffic_logs
        GROUP BY year, month, hour
        ORDER BY year DESC, month, hour
        """

    elif selected_query == "Violations with High Search and Arrest Rates":
        query = """
        SELECT 
            violation,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS total_searches,
            SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests
        FROM traffic_logs
        GROUP BY violation
        HAVING total_stops > 50
        ORDER BY total_searches DESC, total_arrests DESC
        """

    elif selected_query == "Driver Demographics by Country":
        query = """
        SELECT 
            country_name,
            driver_gender,
            driver_race,
            ROUND(AVG(driver_age), 1) AS avg_age,
            COUNT(*) AS count
        FROM traffic_logs
        GROUP BY country_name, driver_gender, driver_race
        ORDER BY count DESC
        """

    elif selected_query == "Top 5 Violations with Highest Arrest Rates":
        query = """
        SELECT 
            violation,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
            ROUND(AVG(is_arrested) * 100, 2) AS arrest_rate_percent
        FROM traffic_logs
        GROUP BY violation
        HAVING total_stops > 50
        ORDER BY arrest_rate_percent DESC
        LIMIT 5
        """

    result_df = pd.read_sql(query, con=mydb)
    st.dataframe(result_df)
