import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration to wide mode
st.set_page_config(
    page_title="Big Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# --- CONFIGURATION ---
# Increase this value to make charts even taller
CHART_HEIGHT = 600

# --- 1. Load and Preprocess Data ---


@st.cache_data
def load_data():
    df = pd.read_csv('train.csv')

    # Convert datetime to datetime objects
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Extract useful features
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['month'] = df['datetime'].dt.month_name()
    df['day_of_week'] = df['datetime'].dt.day_name()

    # Ensure day_of_week is ordered correctly for plotting
    days_order = ['Monday', 'Tuesday', 'Wednesday',
                  'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(
        df['day_of_week'], categories=days_order, ordered=True)

    # Map categorical variables for better readability
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_mapping = {
        1: 'Clear/Cloudy',
        2: 'Mist/Cloudy',
        3: 'Light Snow/Rain',
        4: 'Heavy Rain/Ice'
    }

    df['season_label'] = df['season'].map(season_mapping)
    df['weather_label'] = df['weather'].map(weather_mapping)

    return df


df = load_data()

# --- 2. Sidebar Widgets for Filtering ---
st.sidebar.header("Filter Options")

# Widget 1: Date Range Picker
min_date = df['date'].min()
max_date = df['date'].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Widget 2: Season Multiselect
available_seasons = df['season_label'].unique()
selected_seasons = st.sidebar.multiselect(
    "Select Season(s)",
    options=available_seasons,
    default=available_seasons
)

# Widget 3: Weather Multiselect
available_weather = df['weather_label'].unique()
selected_weather = st.sidebar.multiselect(
    "Select Weather Condition(s)",
    options=available_weather,
    default=available_weather
)

# Widget 4: Hour Slider
selected_hour_range = st.sidebar.slider(
    "Select Hour Range",
    min_value=0,
    max_value=23,
    value=(0, 23)
)

# --- 3. Filter Data Based on Selection ---
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    mask_date = (df['date'] >= start_date) & (df['date'] <= end_date)
else:
    mask_date = (df['date'] == date_range[0])

mask_season = df['season_label'].isin(selected_seasons)
mask_weather = df['weather_label'].isin(selected_weather)
mask_hour = (df['hour'] >= selected_hour_range[0]) & (
    df['hour'] <= selected_hour_range[1])

filtered_df = df[mask_date & mask_season & mask_weather & mask_hour]

# --- 4. Main Dashboard Layout ---
st.title("🚲 Extended Bike Sharing Analysis")
st.markdown("### Interactive Dashboard for Bike Sharing Data Exploration")

# KPI Row (Full Width)
total_rentals = filtered_df['count'].sum()
avg_temp = filtered_df['temp'].mean()
avg_humidity = filtered_df['humidity'].mean()
if not filtered_df.empty:
    max_rentals_hour = filtered_df.groupby('hour')['count'].sum().idxmax()
else:
    max_rentals_hour = 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Rentals", f"{total_rentals:,}")
col2.metric("Avg Temp", f"{avg_temp:.1f} °C")
col3.metric("Avg Humidity", f"{avg_humidity:.1f} %")
col4.metric("Peak Hour", f"{max_rentals_hour}:00")

st.markdown("---")

# Row 1: Time Series & Hourly Trends
# We keep 2 columns but force a large height
col_row1_1, col_row1_2 = st.columns(2)

with col_row1_1:
    st.subheader("1. Daily Rentals Over Time")
    daily_df = filtered_df.groupby('date')['count'].sum().reset_index()
    fig_daily = px.line(daily_df, x='date', y='count',
                        markers=True, template="plotly_white")
    fig_daily.update_layout(height=CHART_HEIGHT)  # <-- Set Height
    st.plotly_chart(fig_daily, use_container_width=True)

with col_row1_2:
    st.subheader("2. Hourly Demand (Working vs Non-Working)")
    hourly_df = filtered_df.groupby(['hour', 'workingday'])[
        'count'].mean().reset_index()
    hourly_df['workingday'] = hourly_df['workingday'].map(
        {0: 'Non-Working Day', 1: 'Working Day'})

    fig_hourly = px.line(
        hourly_df, x='hour', y='count', color='workingday',
        markers=True, template="plotly_white",
        labels={'count': 'Avg Rentals'}
    )
    fig_hourly.update_layout(height=CHART_HEIGHT)  # <-- Set Height
    st.plotly_chart(fig_hourly, use_container_width=True)

st.markdown("---")

# Row 2: Seasonality & Weather
col_row2_1, col_row2_2 = st.columns(2)

with col_row2_1:
    st.subheader("3. Rentals by Season")
    season_df = filtered_df.groupby('season_label')[
        'count'].sum().reset_index()
    fig_season = px.bar(
        season_df, x='season_label', y='count',
        color='season_label', template="plotly_white",
        title='Total Rentals by Season'
    )
    fig_season.update_layout(height=CHART_HEIGHT)  # <-- Set Height
    st.plotly_chart(fig_season, use_container_width=True)

with col_row2_2:
    st.subheader("4. Temperature vs Count")
    fig_temp = px.scatter(
        filtered_df, x='temp', y='count',
        color='season_label', size='humidity',
        opacity=0.5, template="plotly_white",
        title='Rentals vs Temperature (Size = Humidity)'
    )
    fig_temp.update_layout(height=CHART_HEIGHT)  # <-- Set Height
    st.plotly_chart(fig_temp, use_container_width=True)

st.markdown("---")

# Row 3: User Types & Correlation (Bigger Layout)
# Instead of splitting 1:2, we make them full width or equal large split for better visibility

st.subheader("5. User Split & Correlations")
col_row3_1, col_row3_2 = st.columns(2)

with col_row3_1:
    # User Split
    user_types = filtered_df[['casual', 'registered']].sum().reset_index()
    user_types.columns = ['User Type', 'Count']
    fig_pie = px.pie(user_types, values='Count', names='User Type',
                     hole=0.4, template="plotly_white", title="Casual vs Registered")
    fig_pie.update_layout(height=CHART_HEIGHT)  # <-- Set Height
    st.plotly_chart(fig_pie, use_container_width=True)

with col_row3_2:
    # Correlation Heatmap
    corr_cols = ['temp', 'atemp', 'humidity',
                 'windspeed', 'casual', 'registered', 'count']
    corr_matrix = filtered_df[corr_cols].corr()

    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title="Correlation Matrix"
    )
    fig_corr.update_layout(height=CHART_HEIGHT)  # <-- Set Height
    st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("---")

# Row 4: Large Weekly Heatmap (Full Width)
st.subheader("6. Weekly Usage Patterns (Day vs Hour)")
st.markdown("Identify peak usage times during the week.")

heatmap_data = filtered_df.groupby(['day_of_week', 'hour'])[
    'count'].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(
    index='day_of_week', columns='hour', values='count')

fig_heatmap = px.imshow(
    heatmap_pivot,
    labels=dict(x="Hour of Day", y="Day of Week", color="Avg Rentals"),
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    color_continuous_scale='Viridis',
    aspect="auto"
)
# Make this one even taller because it has a lot of data
fig_heatmap.update_layout(xaxis_nticks=24, height=700)
st.plotly_chart(fig_heatmap, use_container_width=True)
st.markdown("---")
st.markdown("© 2024 Big Bike Sharing Dashboard")
