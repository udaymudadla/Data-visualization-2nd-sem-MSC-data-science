# 🚲 Capital Bikeshare Analytics Dashboard

## 📌 Project Overview
This project is an interactive data visualization dashboard built using **Streamlit**. It analyzes the **Washington D.C. Bike Sharing dataset** (2011-2012) to uncover trends in user behavior, environmental impacts, and operational efficiency.

The dashboard is designed for executives and operations managers to get a "360-degree view" of the bike-sharing business at a glance.

## 🚀 Live Demo
https://data-visualization-2nd-sem-msc-data-science-57efegviwrducqswq2.streamlit.app/


## 📊 Key Features
The dashboard is organized into **4 Strategic Tabs**:

1.  **📈 Growth Overview**: Tracks business growth month-over-month and compares performance between 2011 and 2012.
2.  **👥 Usage Patterns**: Analyzes customer demographics (Casual vs. Registered) and distinguishes between commuter and leisure ride patterns.
3.  **🌍 Environmental Impact**: Visualizes how weather conditions (Temperature, Humidity, Season) correlate with rental demand.
4.  **⏱️ Daily Operations**: A heat map and shift analysis to help identify peak hours and optimize fleet management.

## 🛠️ Technologies Used
* **Streamlit**: For the web application framework.
* **Pandas**: For data manipulation and feature engineering.
* **Plotly Express**: For interactive, zoomable charts.
* **Seaborn & Matplotlib**: For statistical visualizations (Correlation Heatmaps).

## 📂 Project Structure
```text
├── dashboard.py              # Main dashboard application code
├── train.csv           # The dataset file
├── requirements.txt    # List of Python dependencies
└── README.md           # Project documentation
