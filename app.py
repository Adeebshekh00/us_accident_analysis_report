import folium.features
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import plotly.express as px
from folium.plugins import HeatMap
import folium.plugins



APP_TITLE = "US Accident Analysis Report"


def time_analysis(df, year):
    
    df = df[df['Start_Time'].dt.year == year]
    st.markdown("**Since sample data is taken, it might contain discontinuity.**")
  
    if df.empty:
        st.write("No data available for the selected filters.")
        return

    st.subheader("~Analysis of Accidents by hour of Day")

    fig, ax = plt.subplots()
    sns.histplot(df['Start_Time'].dt.hour, bins=24, ax=ax)
    ax.set_title("Distribution of Accidents by Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Count")
    st.pyplot(fig)
    st.markdown(" This shows that generally overall majority of accidents are from 7-10am and 3 - 6pm ")

    st.subheader("~Analysis of Accidents by Hours on weekends")
    weekends_start_time = df[df['Start_Time'].dt.dayofweek.isin([5, 6])]
    fig, ax = plt.subplots()
    sns.histplot(weekends_start_time['Start_Time'].dt.hour, bins=24, ax=ax)
    ax.set_title("Distribution of Accidents by Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    st.markdown(" -This shows that generally majority of accidents are between 10am - 3pm on weekends")


    st.subheader("~Analysis of Accidents by Hours on working days")
    notweekends_start_time = df[df['Start_Time'].dt.dayofweek.isin([0, 4])]
    fig, ax = plt.subplots()
    sns.histplot(notweekends_start_time['Start_Time'].dt.hour, bins=24, ax=ax)
    ax.set_title("Distribution of Accidents by Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    st.markdown(" -This shows that generally majority of accidents are from 7-10am and 3 - 6pm  on working days")

    st.subheader("~Accidents on Working days vs Weekends")
    fig, ax = plt.subplots()
    sns.histplot(df['Start_Time'].dt.day_of_week, bins=7, ax=ax)
    ax.set_title("Distribution of Accidents by Days of Week")
    ax.set_xlabel("Days Of Week")
    ax.set_ylabel("Count")
    st.pyplot(fig)


    st.subheader("~Analysis of Accidents Month wise")
    fig, ax = plt.subplots()
    sns.histplot(df.Start_Time.dt.month,bins=12)
    ax.set_title("Distribution of Accidents per month")
    ax.set_xlabel("Months of year")
    ax.set_ylabel("Count")
    st.pyplot(fig)


    # Conclusion
    st.subheader("Conclusion")
    st.markdown("""
    **Peak Accident Hours:**
    - On working days, the majority of accidents occur during two peak periods: **7–9 AM and 3–6 PM**.
    - On weekends, the peak accident period shifts to **10 AM–3 PM**, likely due to leisure-related travel.

    **Working Days vs. Weekends:**
    - Accidents are significantly more frequent on working days compared to weekends, reflecting the impact of weekday commuting and work-related travel on accident rates.

    **Dataset Completeness:**
    - Some months and years exhibit missing data, as evident by gaps in the histograms.
    """)

def state_analysis(df,year):

    df['Year'] = df['Year'].astype(int)
    df = df[df['Year'] == year]
    map = folium.Map(location=[38,-96.5],zoom_start=4,scrollWheelZoom=False , tiles="CartoDB positron")
    
    choropleth = folium.Choropleth(
        geo_data="datasets/us-state-boundaries.geojson",
        data = df,
        columns=('State','Count'),
        key_on = 'feature.id',
        line_opacity=0.8,
        highlight=True
    )

    df_indexed = df.set_index('State')
    for feature in choropleth.geojson.data['features']:
        state_name = feature['id']
        feature['properties']['Accidents'] = 'Accidents: ' + '{:,}'.format(df_indexed.loc[state_name, 'Count']) if state_name in list(df_indexed.index) else ''
    
   
    choropleth.geojson.add_to(map)
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['name','Accidents'],labels=False)
    )


    st_map = st_folium(map,width=700,height = 500)


    st.subheader("~Bar Plot")
    fig_bar = px.bar(
            df.sort_values(by="Count", ascending=False),
            x="State",
            y="Count",
            color="Count",
            color_continuous_scale="Viridis",
            labels={"Count": "Accidents", "State": "State"},
            title=f"Accidents Distribution Across States in {year}"
    )

    fig_bar.update_layout(
        width=1500, 
        height=600,
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    top_rows = df.sort_values(by="Count", ascending=False).head(20)
    st.subheader("~Top 20 States with Maximum Number of Accidents")
    st.table(top_rows.reset_index(drop=True))


    st.markdown("""
    **Conclusion on State-Wise Accidents Analysis:**
    - On average, **California, Florida, and Texas** report the highest number of accidents each year. This trend may be attributed to their **large populations**, which contribute to increased road traffic and potential for accidents.
    
    - In contrast, **South Dakota , North Dakota , Maine , Wyoming and New Hampshire** consistently show the lowest accident rates annually. This could be linked to their **smaller populations** and the **unique geographical characteristics** of these regions, which may lead to less congested roadways.
    
    - It is important to note that some anomalies have been identified in the dataset. For instance, the data for **2023 is incomplete**, which may affect the accuracy of the reported accident figures. Careful consideration should be given to these discrepancies when interpreting the results.
    """)

def city_analysis():

    cities_plot = pd.read_csv("datasets/Cities_barChart.csv")
    st.subheader("~Bar Plot")
    fig_bar = px.bar(
            cities_plot[:100].sort_values(by="Accident_Count", ascending=False),
            x="city",
            y="Accident_Count",
            color="Accident_Count",
            color_continuous_scale="Viridis",
            labels={"Accident_Count": "Accidents", "city": "city"},
            title="Accidents Distribution Across Cities(Top 100 cities)"
    )

    fig_bar.update_layout(
        width=1500, 
        height=600,
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("~Cities with more than 1000 accidents per Year")
    m = folium.Map(location=[38, -90], zoom_start=4, scrollWheelZoom=False)

    cities_plot = pd.read_csv("datasets/Cities_barChart.csv")
    cities_geodf = pd.read_csv("datasets/cities_geodata.csv")
    high_accident_cities = cities_plot[cities_plot['Accident_Count'] >= 8000]

    danger_cities_df = pd.merge(cities_geodf, high_accident_cities, on="city", how="inner")
    st.markdown("-Number of such cities : 128")
    for _, row in danger_cities_df.iterrows():
        folium.Marker(
            location=[row['lat'], row['lng']], 
            tooltip=f"City: {row['city']}<br>Accidents: {row['Accident_Count']}", 
        ).add_to(m)

    st_folium(m, width=900)

    top_rows = cities_plot.sort_values(by="Accident_Count", ascending=False).head(20)
    st.subheader("~Top 20 Cities with Maximum Number of Accidents")
    st.table(top_rows.reset_index(drop=True))

    st.markdown("""
    **Conclusion on City-Wise Accidents Analysis:**
    - The dataset includes a total of **13,679** unique cities. Among them, only 128 cities **(less than 1% of the total)** report more than **1,000 accidents** per year. These cities tend to have larger populations, which may contribute to higher traffic volume and, consequently, more accidents. Other factors such as urbanization, traffic density, and infrastructure quality could also play a role in the elevated accident numbers.
    
    - On the other hand, there are over **4,000 cities** that report fewer than **10 accidents** over the span of **8 years**. This anomaly could be attributed to these cities having very small populations, leading to lower traffic and fewer accidents. However, this pattern also raises questions about the completeness or accuracy of accident reporting in these cities, suggesting that further investigation may be necessary to confirm the reliability of this data.
    
    - Overall, this analysis highlights the significant correlation between city population size and the frequency of accidents, while also underscoring the need for further scrutiny regarding the lower-incident cities to ensure the data reflects real-world conditions.
    """)

def traffic_features_analysis(df):

    df['year'] = df['year'].astype(int)
    # Plot the density plot
    # Create the line plot
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='year', y='Crossing', label='Crossing')
    sns.lineplot(data=df, x='year', y='Junction', label='Junction')
    sns.lineplot(data=df, x='year', y='Station', label='Station')
    sns.lineplot(data=df, x='year', y='Stop', label='Stop')
    sns.lineplot(data=df, x='year', y='Traffic_Signal', label='Traffic_Signal')

    # Customize the plot
    plt.title("Accident Counts by Traffic Feature and Year")
    plt.xlabel("Year")
    plt.ylabel("Accident Counts")
    plt.legend(title='Traffic Features', loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(plt)
    st.subheader("~Accident_Count with Some Traffic Features Nearby")

    st.table(df)

    st.markdown(f"**- Number of Accidents near Crossings: {df['Crossing'].sum()}**")
    st.markdown(f"**- Number of Accidents near Junctions: {df['Junction'].sum()}**") 
    st.markdown(f"**- Number of Accidents near Stations: {df['Station'].sum()}**")
    st.markdown(f"**- Number of Accidents near Stops: {df['Stop'].sum()}**")
    st.markdown(f"**- Number of Accidents near Traffic Signals: {df['Traffic_Signal'].sum()}**")

   
    st.markdown("""
    ## Conclusion on the Impact of Traffic Features on Accidents

    The analysis of traffic features reveals critical insights regarding accidents:

    - **Accident Concentration Near Traffic features:** A significant portion of accidents, over **36%,** of total accidents occur various traffic features, indicating these locations as key hotspots for traffic incidents.

    - **Trends in Accident Data:** A notable decline in accident counts from 2022 onwards, particularly in 2023, raises concerns about data completeness and accuracy. This suggests potential missing information or underreporting, warranting further investigation.

    ### Precautionary Measures

    To enhance road safety around traffic signals, the following measures are recommended:

    1. **Enhanced Traffic Signal Monitoring:** Implement advanced monitoring systems to analyze traffic flow and accident patterns in real-time, allowing for optimized signal timings and improved safety at high-risk intersections.

    2. **Increased Fines for Traffic Violations:** Enforce stricter fines for traffic violations near signalized intersections. This can deter reckless driving behaviors and encourage adherence to traffic rules, ultimately contributing to reduced accident rates.

    By implementing these strategies, we can improve road safety and reduce accidents related to traffic features.
    """)


def street_analysis(df,street_geodata):

    st.subheader("~HeatMap for Regions which experience largest Severe Accidents")

    street_geodata = street_geodata.dropna(subset=["Start_Lat", "Start_Lng"])

    coord_list = list(zip(street_geodata["Start_Lat"], street_geodata["Start_Lng"]))
    m = folium.Map(location=[38, -90], zoom_start=4, scrollWheelZoom=False, tiles="CartoDB dark_matter")
    HeatMap(coord_list, radius=20).add_to(m)

    st_folium(m, width=900)

    st.subheader("~Most Frequent Accidental Streets for Each City")
    selected_city = st.selectbox("Select a city:", df["City"].unique())

    city_data = df[df["City"] == selected_city]
    st.table(city_data)
    

def weather_analysis(w_df,v_df,wind_df):
    st.subheader("~Bar Plot of various weather conditions")
    fig_bar = px.bar(
            w_df,
            x="Weather_Condition",
            y="Count",
            color="Count",
            color_continuous_scale="Inferno",
            labels={"Count": "Count", "Weather_Condition": "Weather_Condition"},
            title="Accidents Distribution for various Weathers"
    )

    fig_bar.update_layout(
        width=1500, 
        height=600,
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("~Cities experiencing accidents during high windspeed")

    col1, col2, col3 = st.columns([1, 2, 2])  

    with col2:  
      st.dataframe(wind_df, height=300)
    
    st.subheader("~Accident Count in Cities Under Zero Visibility Conditions")

    col1, col2, col3 = st.columns([1, 3, 2])  

    with col2:  
      st.dataframe(v_df, height=300)

    st.subheader("~Frequent high precipitation spots")
    data = {'Cities': ['Brooklyn', 'Jersey City', 'New York', 'Miami', 'Baton Rouge'],
        'Accident_Count': [355, 66,63, 36, 13]}

    df = pd.DataFrame(data)
    st.table(df)


    st.markdown("""
    ## Conclusion on the Impact of Weather on Accidents

    The analysis of weather conditions reveals significant insights regarding accidents:

    - **Accident Frequency During Normal Weather Conditions:** A majority of accidents occur during normal weather conditions such as fair and cloudy days, suggesting that factors like work-related rush may play a more critical role in accident occurrences than extreme weather.

    - **Impact of High Wind Speeds:** Cities like **Oklahoma, Dallas, and Miami** experience high wind speeds, which correlate with increased accident counts. This indicates that wind conditions can significantly affect driver behavior and vehicle control.

    - **High Precipitation Areas:** Locations with frequent high precipitation are generally **coastal areas**, highlighting a potential link between weather patterns and accident rates in these regions.""")



def introduction():
    st.markdown("## Welcome to the US Accident Analysis Report")

    
    st.markdown(
        """
        This app provides insights into  accidents across the United States based on a comprehensive dataset consisting of **7.7 million rows of data**.

        ### About the Dataset
        - **Source:** The data represents detailed information on accidents in US, including time, location, weather conditions, and more.
        - **Purpose:** To explore, analyze, and identify key patterns in accident occurrences and their contributing factors.
        
        **[View the Dataset](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents)**
        """
    )

    st.markdown(
        """
        ### Analyses Included
        _This section highlights the types of analyses conducted on the dataset. Examples include:_
        
        - Temporal Analysis (e.g., trends across days, months, and years)
        - Analysing majorily affected State,City 
        - Severity Distribution of Accidents over Streets
        - Geographic Maps of Accident Hotspots
        - Correlations Between Traffic features and Accidents
        - Impact of Weather Conditions on Accidents

        """
    )

    st.markdown(
        """
        ---
        #### Ready to dive in?
        Use the sidebar to select a specific analysis or visualization.

        🚀 **Analyze data like never before!**
        """
    )




def main():
    st.set_page_config(page_title=APP_TITLE)
    st.title(APP_TITLE)

    st.sidebar.image("datasets/Us_report_Image.webp", caption="Accident Analysis", use_container_width=True)

    # Load data
    df = pd.read_csv("datasets/US_Accidents_time_analysis.csv")
    df['Start_Time'] = pd.to_datetime(df['Start_Time'], errors='coerce')

    df_state_analysis = pd.read_csv("datasets/US_Accidents_state_analysis.csv")
    obstruciton_df = pd.read_csv("datasets/obstruction_accident_data.csv")
    frequent_cities = pd.read_csv("datasets/frequentAccident_Streets.csv")
    street_geodata = pd.read_csv("datasets/street_geodata.csv")
    weather_df = pd.read_csv("datasets/Weather_condition.csv")
    low_visibility_cities = pd.read_csv("datasets/zero_visibility_cities.csv")
    high_windspeed_cities = pd.read_csv("datasets/high_windspeed_cities.csv")


    with st.sidebar:
        st.header("Navigation")
        section = st.radio(
            "Choose Section:",
            options=["Introduction","Time Analysis", "State-Wise Analysis", "City-Wise Analysis", "Street-Wise Analysis", "Impact of Traffic Features","Weather Impact Analysis"],
        )

        year = None
        if section in ["Time Analysis", "State-Wise Analysis"]:
            st.header("Filters")
            year = st.slider("Select Year", min_value=2016, max_value=2023, value=2018)

    if section == "Introduction":
        introduction()
    elif section == "Time Analysis":
        st.header("Time Analysis of Data")
        if year is not None: 
            time_analysis(df, year)
    elif section == "State-Wise Analysis":
        st.header("Analysis of Accidents over States")
        if year is not None:  
            state_analysis(df_state_analysis, year)
    elif section == "City-Wise Analysis":
        st.header("Analysis of Accidents over Cities")
        city_analysis()
    elif section == "Street-Wise Analysis":
        st.header("Analysis of Accidents Over Streets")
        street_analysis(frequent_cities, street_geodata)
    elif section == "Impact of Traffic Features":
        st.header("Analysis of Impact of Traffic Features")
        traffic_features_analysis(obstruciton_df)
    elif section == "Weather Impact Analysis":
        st.header("Analysis of Impact of Weather")
        weather_analysis(weather_df,low_visibility_cities,high_windspeed_cities)

if __name__ == "__main__":
    main()
