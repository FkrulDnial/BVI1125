import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time

# URL of the new Google Sheet (published version)
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1pb55kAq3twA4VUZRVxeEy-MVlHtsiSCP9sdhaTyXE3s/gviz/tq?tqx=out:csv'

# Set page configuration to make the layout more beautiful
st.set_page_config(page_title="Fish Hatchery Water Quality Monitoring", page_icon="🐟", layout="wide")

# Function to fetch data from the Google Sheet
def fetch_data():
    response = requests.get(SHEET_URL)
    data = pd.read_csv(StringIO(response.text))
    return data

# Add a header with custom style and logo beside the text
st.markdown("""
    <h1 style="text-align: center; color: #1AA7EC; display: flex; justify-content: center; align-items: center;">
        <img src="https://brand.umpsa.edu.my/images/2024/02/28/logo-umpsa-full-color__4041x3027.png" width="40" style="margin-right: 10px;">
        Fish Hatchery Water Quality Monitoring System
    </h1>
""", unsafe_allow_html=True)

# Move the "Select Page" widget to the sidebar
page = st.sidebar.radio("Select Page", ("Data Table", "Data Trend"))

# Create a placeholder to update the content
placeholder = st.empty()

# Set up auto-refresh with rerun every 10 seconds (or as needed)
while True:
    # Fetch the latest data from Google Sheets
    data = fetch_data()

    # Sort the data by the 'Timestamp' column in descending order to show the latest data on top
    if 'Timestamp' in data.columns:
        data['Timestamp'] = pd.to_datetime(data['Timestamp'])
        data = data.sort_values(by='Timestamp', ascending=False)

    # Clean the 'Temperature (°C)' and 'pH' columns (remove TDS)
    data['Temperature (°C)'] = pd.to_numeric(data['Temperature (°C)'].replace({',': ''}, regex=True), errors='coerce')
    data['pH'] = pd.to_numeric(data['pH'].replace({',': ''}, regex=True), errors='coerce')

    # Count the number of times "Water Detected" is true or equals "Yes" (adjust this condition based on your data)
    water_detected_count = data[data['Water Detected'] == "Yes"].shape[0]

    # Add a header for the water detection count in the sidebar with block-style design
    st.sidebar.markdown("<h2 style='color: #1AA7EC;'>Water Detection Count</h2>", unsafe_allow_html=True)

    # Display the count in the sidebar with a block-style design
    st.sidebar.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; border: 2px solid #1AA7EC; padding: 10px; border-radius: 10px; margin-top: 20px;">
            <div style="font-size: 24px; color: #1AA7EC; text-align: center;">
                <b>{water_detected_count}</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Extract the latest row
    latest_data = data.iloc[0] if not data.empty else None

    # Calculate temperature statistics for the most recent data (e.g., the last 10 rows or a recent time window)
    recent_data = data.head(10)  # You can adjust the number of rows to consider, for example, the last 10 rows

    # Calculate average, minimum, and maximum values for recent data
    avg_temp = recent_data['Temperature (°C)'].mean().round(2)
    min_temp = recent_data['Temperature (°C)'].min().round(2)
    max_temp = recent_data['Temperature (°C)'].max().round(2)

    with placeholder.container():
        if page == "Data Table":
            # Display latest data in a block-style layout with a heading
            if latest_data is not None:
                st.markdown("<h2 style='color: #1AA7EC; text-align: center;'>Real-time Monitoring</h2>", unsafe_allow_html=True)

                # Format the timestamp as DD-MM-YYYY HH-MM
                formatted_timestamp = latest_data['Timestamp'].strftime('%d-%m-%Y %H:%M')

                # Create a horizontal block for the latest data
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; border: 2px solid #1AA7EC; padding: 10px; border-radius: 10px; margin-bottom: 20px;">
                        <div style="flex: 1; text-align: center;">
                            <b>Timestamp:</b><br>{formatted_timestamp}
                        </div>
                        <div style="flex: 1; text-align: center;">
                            <b>Temperature (°C):</b><br>{latest_data['Temperature (°C)']}
                        </div>
                        <div style="flex: 1; text-align: center;">
                            <b>pH:</b><br>{latest_data['pH']}
                        </div>
                        <div style="flex: 1; text-align: center;">
                            <b>Water Detected:</b><br>{latest_data['Water Detected']}
                        </div>
                        <div style="flex: 1; text-align: center;">
                            <b>Time of Day:</b><br>{latest_data['Time of Day']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # Add Date Filter widget below the latest data block
            st.markdown("<h2 style='color: #1AA7EC;'>Filter</h2>", unsafe_allow_html=True)

            # Create a single row with columns for start date, end date, and time of day filter
            col1, col2, col3 = st.columns(3)

            with col1:
                start_date = st.date_input("Start date", data['Timestamp'].min().date())
            with col2:
                end_date = st.date_input("End date", data['Timestamp'].max().date())
            with col3:
                time_of_day = st.selectbox("Select Time of Day", ['All', 'Morning', 'Afternoon', 'Evening', 'Night'])

            # Filter the data by the selected date range and time of day
            filtered_data = data[(data['Timestamp'] >= pd.to_datetime(start_date)) & (data['Timestamp'] <= pd.to_datetime(end_date))]
            
            if time_of_day != 'All':
                filtered_data = filtered_data[filtered_data['Time of Day'] == time_of_day]

            # Show the data with enhanced styling for the Data Table
            st.markdown("<hr style='border: 1px solid #1AA7EC;'>", unsafe_allow_html=True)
            st.write(f"Displaying data from {start_date} to {end_date} and Time of Day: {time_of_day}:")

            # Show the filtered table with full width
            st.dataframe(filtered_data.style.set_table_styles([ 
                {'selector': 'thead th', 'props': [('background-color', '#1AA7EC'), ('color', 'white')]},  # Header color
                {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#f9f9f9')]},  # Odd row background
                {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#e7e7e7')]},  # Even row background
            ]), use_container_width=True)

        elif page == "Data Trend":
            # Add a widget to choose between Temperature or pH
            trend_option = st.selectbox(
                "Select Data Trend to Display",
                ("Temperature (°C)", "pH")
            )

            # Display the statistics for the most recent data (above the graph)
            st.markdown("<h2 style='color: #1AA7EC; text-align: center;'>Recent Statistics</h2>", unsafe_allow_html=True)

            # Display the statistics in block-style layout
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; border: 2px solid #1AA7EC; padding: 10px; border-radius: 10px; margin-bottom: 20px;">
                    <div style="flex: 1; text-align: center;">
                        <b>Average {trend_option}:</b><br>{recent_data[trend_option].mean().round(2)}
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <b>Minimum {trend_option}:</b><br>{recent_data[trend_option].min().round(2)}
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <b>Maximum {trend_option}:</b><br>{recent_data[trend_option].max().round(2)}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Show the selected data trend chart
            st.subheader(f"{trend_option} Trend")
            if trend_option == "Temperature (°C)":
                st.line_chart(data[['Timestamp', 'Temperature (°C)']].set_index('Timestamp'))
            elif trend_option == "pH":
                st.line_chart(data[['Timestamp', 'pH']].set_index('Timestamp'))

    # Pause for 10 seconds before fetching new data
    time.sleep(10)
    st.rerun()  # Trigger a rerun to refresh the data
