import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. PAGE CONFIGURATION & THEME ---
st.set_page_config(
    page_title="Washington DC Bike Share Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make it look professional
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .metric-card { background-color: #f9f9f9; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---


@st.cache_data
def load_and_prep_data():
    df = pd.read_csv('train.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Feature Engineering
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month_name()
    df['day'] = df['datetime'].dt.day_name()
    df['hour'] = df['datetime'].dt.hour

    # Operational Periods (Creative Logic)
    def get_period(h):
        if 5 <= h < 10:
            return '🌅 Morning Rush'
        elif 10 <= h < 15:
            return '☀️ Mid-Day'
        elif 15 <= h < 20:
            return '🌇 Evening Rush'
        else:
            return '🌙 Night'
    df['period'] = df['hour'].apply(get_period)

    # Mappings for clear readability
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_map = {1: 'Clear/Nice', 2: 'Cloudy/Mist',
                   3: 'Rain/Snow', 4: 'Extreme Weather'}
    df['season_label'] = df['season'].map(season_map)
    df['weather_label'] = df['weather'].map(weather_map)
    df['working_day_str'] = df['workingday'].map(
        {0: 'Weekend/Holiday', 1: 'Work Day'})

    # Ordering
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    day_order = ['Monday', 'Tuesday', 'Wednesday',
                 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['month'] = pd.Categorical(
        df['month'], categories=month_order, ordered=True)
    df['day'] = pd.Categorical(df['day'], categories=day_order, ordered=True)

    return df


df = load_and_prep_data()

# --- 3. SIDEBAR INTELLIGENCE ---
st.sidebar.title("🎮 Control Panel")
st.sidebar.markdown("Filter the insights below:")

selected_year = st.sidebar.multiselect(
    "Select Year", options=[2011, 2012], default=[2011, 2012])
selected_season = st.sidebar.multiselect(
    "Select Season", options=df['season_label'].unique(), default=df['season_label'].unique())

# Filter Engine
filtered_df = df[
    (df['year'].isin(selected_year)) &
    (df['season_label'].isin(selected_season))
]

# --- 4. EXECUTIVE SUMMARY (Top KPIs) ---
st.title("🚲 Washington D.C. Bike Rental Data Dashboard")
st.markdown("A 360-degree view of growth, usage, and operations.")

col1, col2, col3, col4 = st.columns(4)
total_rides = filtered_df['count'].sum()
avg_rides = filtered_df['count'].mean()
peak_hour = filtered_df.groupby('hour')['count'].sum().idxmax()
core_user = "Registered" if filtered_df['registered'].sum(
) > filtered_df['casual'].sum() else "Casual"

col1.metric("Total Rides", f"{total_rides:,.0f}", delta="Volume")
col2.metric("Avg Hourly Rides", f"{avg_rides:.0f}", delta="Demand")
col3.metric("Busiest Hour", f"{peak_hour}:00", delta="Peak Time")
col4.metric("Dominant User", core_user, delta="Customer Base")

st.markdown("---")

# --- 5. THEMATIC TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Growth Overview",
    "👥 Usage Patterns",
    "🌍 Environmental Impact",
    "⏱️ Daily Operations"
])

# === TAB 1: GROWTH OVERVIEW ===
with tab1:
    st.header("Business Growth & Trends")
    st.caption("How is the service performing over time?")

    # PLOT 1: Monthly Growth (Year over Year) - Plotly
    monthly_growth = filtered_df.groupby(['month', 'year'])[
        'count'].mean().reset_index()
    fig1 = px.line(
        monthly_growth, x='month', y='count', color='year', markers=True,
        title="<b>Monthly Growth Trajectory (2011 vs 2012)</b>",
        labels={'count': 'Average Rentals', 'month': 'Month', 'year': 'Year'},
        template="plotly_white"
    )
    fig1.update_traces(line=dict(width=3))
    st.plotly_chart(fig1, use_container_width=True)

# === TAB 2: USAGE PATTERNS ===
with tab2:
    st.header("Understanding the Rider")
    st.caption("Who rides, and when?")

    c1, c2 = st.columns(2)

    with c1:
        # PLOT 2: User Segmentation - Plotly Donut
        user_sums = filtered_df[['casual', 'registered']].sum().reset_index()
        user_sums.columns = ['User Type', 'Count']
        fig2 = px.pie(
            user_sums, values='Count', names='User Type', hole=0.5,
            title="<b>User Segmentation: Casual vs Registered</b>",
            color_discrete_sequence=['#FF6F61', '#6B5B95']
        )
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        # PLOT 3: Working vs Non-Working Trends - Plotly Line
        work_trend = filtered_df.groupby(['hour', 'working_day_str'])[
            'count'].mean().reset_index()
        fig3 = px.line(
            work_trend, x='hour', y='count', color='working_day_str',
            title="<b>Commuters vs Weekenders: Hourly Demand</b>",
            labels={'count': 'Avg Rentals', 'working_day_str': 'Day Type'}
        )
        st.plotly_chart(fig3, use_container_width=True)

# === TAB 3: ENVIRONMENTAL IMPACT ===
with tab3:
    st.header("Weather & Environmental Factors")
    st.caption("How external conditions affect demand.")

    c3, c4 = st.columns(2)

    with c3:
        # PLOT 4: Weather Impact (Seaborn/Matplotlib) - STATIC
        st.subheader("Impact of Weather Conditions")
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=filtered_df, x='weather_label', y='count', hue='season_label',
            palette="viridis", ax=ax4, errorbar=None
        )
        ax4.set_ylabel("Total Rentals")
        ax4.set_xlabel("")
        ax4.legend(title="Season")
        sns.despine()
        st.pyplot(fig4)

    with c4:
        # PLOT 5: Correlation Matrix (Seaborn) - STATIC
        st.subheader("Factor Correlation Analysis")
        corr_cols = filtered_df[[
            'temp', 'humidity', 'windspeed', 'count', 'casual', 'registered']].corr()
        fig5, ax5 = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr_cols, annot=True, cmap="coolwarm", fmt=".2f", ax=ax5)
        st.pyplot(fig5)

# === TAB 4: DAILY OPERATIONS ===
with tab4:
    st.header("Operational Heatmaps")
    st.caption("Optimizing fleet availability based on hotspots.")

    # PLOT 6: Weekly Heatmap - Plotly
    heatmap_data = filtered_df.groupby(['day', 'hour'])[
        'count'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(
        index='day', columns='hour', values='count')

    fig6 = px.imshow(
        heatmap_pivot,
        labels=dict(x="Hour of Day", y="Day of Week", color="Avg Demand"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale="Magma",
        title="<b>Weekly Demand Heatmap (Where are the hotspots?)</b>",
        aspect="auto"
    )
    st.plotly_chart(fig6, use_container_width=True)

    # PLOT 7: Operational Periods - Plotly Bar
    st.subheader("Shift Analysis")
    period_counts = filtered_df.groupby('period')['count'].mean().reindex(
        ['🌅 Morning Rush', '☀️ Mid-Day', '🌇 Evening Rush', '🌙 Night']
    ).reset_index()

    fig7 = px.bar(
        period_counts, x='period', y='count', color='count',
        title="<b>Average Rentals by Operational Shift</b>",
        color_continuous_scale="Blues",
        text_auto='.0f'
    )
    st.plotly_chart(fig7, use_container_width=True)

# --- 6. FOOTER ---
st.markdown("---")
st.caption("© 2024 Bike rental Data Team.")
