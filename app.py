import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Emission Calculation Function ---
def calculate_emissions(data):
    factors = {
        'electricity': 0.5004,
        'gas': 2.2,
        'fuel': 2.7,
        'flights': 200,
        'food': 0.0015,
        'pharmaceuticals': 0.0012,
        'clothing': 0.0013,
        'paper_products': 0.0009,
        'electronics': 0.0020,
        'furniture': 0.0014,
        'hospitality': 0.0016,
        'telecom': 0.0008,
        'insurance': 0.0007,
        'education': 0.0006,
        'recreation': 0.0012
    }

    emissions = {
        'Household': sum(data.get(k, 0) * factors.get(k, 0) for k in ['electricity', 'gas']),
        'Cars': sum((c['miles_driven'] / c['fuel_efficiency']) * factors['fuel'] for c in data.get('cars', [])),
        'Bikes/Rickshaw': sum((b['miles_driven'] / b['fuel_efficiency']) * factors['fuel'] for b in data.get('bikes_rickshaw', [])),
        'Bus': data.get('bus', 0) * 0.05,
        'Secondary': sum(data.get(k, 0) * factors[k] for k in factors if k not in ['electricity', 'gas', 'fuel', 'flights'])
    }

    total = sum(emissions.values()) / 1000  # to metric tons
    return emissions, total

# --- Page Setup ---
st.set_page_config(page_title="🌱 Carbon Footprint Calculator", layout="wide")
st.title("🌍 Pakistan Carbon Footprint Calculator")

st.markdown("""
Welcome to your personal carbon footprint dashboard. Fill in details across the tabs to get an accurate, real-time estimate of your annual CO₂ emissions.
""")

tabs = st.tabs(["🏠 Household", "🚘 Vehicles", "🛍️ Secondary", "📊 Results"])
user_data = {}

# --- 🏠 Household Tab ---
with tabs[0]:
    st.markdown("## 🏠 Household Emissions")
    with st.expander("Enter your household energy usage"):
        col1, col2 = st.columns(2)
        with col1:
            user_data['electricity'] = st.number_input("Electricity (kWh/year)", min_value=0, value=10000, format="%d")
        with col2:
            user_data['gas'] = st.number_input("Natural Gas (m³/year)", min_value=0, value=5000, format="%d")

    household_emissions = calculate_emissions(user_data)[0]['Household'] / 1000
    st.metric(label="Household Emissions", value=f"{household_emissions:,.2f} metric tons CO₂")

# --- 🚘 Vehicles Tab ---
with tabs[1]:
    st.markdown("## 🚘 Vehicle Emissions")
    user_data['cars'], user_data['bikes_rickshaw'] = [], []

    with st.expander("🚗 Car Usage"):
        num_cars = st.number_input("Number of Cars", 0, 5, 1, key='num_cars')
        for i in range(num_cars):
            st.markdown(f"**Car {i+1}**")
            col1, col2 = st.columns(2)
            with col1:
                km = st.number_input("Kilometers Driven Per Year", 0, 100_000, 15000, key=f'car_km_{i}')
            with col2:
                fe = st.number_input("Fuel Efficiency (km/l)", 1.0, 100.0, 12.0, key=f'car_fe_{i}')
            user_data['cars'].append({'miles_driven': km, 'fuel_efficiency': fe})
        st.metric("Car Emissions", f"{calculate_emissions(user_data)[0]['Cars'] / 1000:,.2f} metric tons CO₂")

    with st.expander("🏍️ Motorcycle / Rickshaw Usage"):
        num_bikes = st.number_input("Number of Motorcycles/Rickshaws", 0, 5, 1, key='num_bikes')
        for i in range(num_bikes):
            st.markdown(f"**Motorcycle/Rickshaw {i+1}**")
            col1, col2 = st.columns(2)
            with col1:
                km = st.number_input("Kilometers Driven Per Year", 0, 100_000, 8000, key=f'bike_km_{i}')
            with col2:
                fe = st.number_input("Fuel Efficiency (km/l)", 1.0, 100.0, 30.0, key=f'bike_fe_{i}')
            user_data['bikes_rickshaw'].append({'miles_driven': km, 'fuel_efficiency': fe})
        st.metric("Motorcycle/Rickshaw Emissions", f"{calculate_emissions(user_data)[0]['Bikes/Rickshaw'] / 1000:,.2f} metric tons CO₂")

    with st.expander("🚌 Bus Travel"):
        user_data['bus'] = st.number_input("Bus Kilometers Per Year", 0, 100_000, 5000, key='bus_km')
        st.metric("Bus Emissions", f"{calculate_emissions(user_data)[0]['Bus'] / 1000:,.2f} metric tons CO₂")

    total_vehicle_emissions = (
        calculate_emissions(user_data)[0]['Cars'] +
        calculate_emissions(user_data)[0]['Bikes/Rickshaw'] +
        calculate_emissions(user_data)[0]['Bus']
    ) / 1000
    st.metric("Total Vehicle Emissions", f"{total_vehicle_emissions:,.2f} metric tons CO₂")

# --- 🛍️ Secondary Emissions Tab ---
with tabs[2]:
    st.markdown("## 🛍️ Secondary Consumption")
    categories = ['food', 'pharmaceuticals', 'clothing', 'electronics', 'furniture', 'hospitality', 'education', 'recreation']
    with st.expander("Enter your yearly spending in PKR"):
        for cat in categories:
            label = cat.replace('_', ' ').title()
            user_data[cat] = st.number_input(f"{label}", min_value=0, value=300000, step=5000, format="%d")

    sec_emissions = calculate_emissions(user_data)[0]['Secondary'] / 1000
    st.metric("Secondary Emissions", f"{sec_emissions:,.2f} metric tons CO₂")

# --- 📊 Results Tab ---
with tabs[3]:
    st.markdown("## 📊 Results Overview")
    emissions, total = calculate_emissions(user_data)

    st.metric(label="🌱 Total Annual Carbon Footprint", value=f"{total:,.2f} metric tons CO₂", delta=f"{total - 0.98:+.2f} vs PK Avg")

    # Pie Chart
    max_category = max(emissions, key=emissions.get)
    explode = [0.1 if k == max_category else 0 for k in emissions]
    fig, ax = plt.subplots()
    ax.pie(emissions.values(), labels=emissions.keys(), explode=explode, autopct='%1.0f%%', startangle=90, colors=plt.cm.Set3.colors)
    ax.axis("equal")
    st.pyplot(fig)

    st.markdown(f"### 🔍 Highest Source of Emissions: **{max_category}**")

    st.markdown("### 📚 Comparison Benchmarks")
    col1, col2, col3 = st.columns(3)
    col1.metric("🇵🇰 Pakistan Average", "0.98 tCO₂")
    col2.metric("🇪🇺 EU Average", "6.80 tCO₂")
    col3.metric("🌍 Global Average", "4.79 tCO₂")

    st.markdown("> To stay below 2°C global warming, the footprint per person must fall below **2 tCO₂/year by 2050**.")

