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
        'electronics': 0.0020,
        'furniture': 0.0014,
        'hospitality': 0.0016,
        'education': 0.0006,
        'recreation': 0.0012
    }

    # Safely get electricity and gas, default to 0 if missing or invalid
    electricity = data.get('electricity', 0)
    gas = data.get('gas', 0)

    # Convert to float safely
    try:
        electricity = float(electricity)
    except (ValueError, TypeError):
        electricity = 0

    try:
        gas = float(gas)
    except (ValueError, TypeError):
        gas = 0

    household_emissions = electricity * factors.get('electricity', 0) + gas * factors.get('gas', 0)

    emissions = {
        'Household': household_emissions,
        'Cars': sum((c['miles_driven'] / c['fuel_efficiency']) * factors['fuel'] for c in data.get('cars', [])),
        'Motorcycle': sum((b['miles_driven'] / b['fuel_efficiency']) * factors['fuel'] for b in data.get('motorcycle', [])),
        'Bus': data.get('bus', 0) * 0.05,
        'Secondary': sum(data.get(k, 0) * factors[k] for k in factors if k not in ['electricity', 'gas', 'fuel', 'flights'])
    }

    total = sum(emissions.values()) / 1000  # to metric tons
    return emissions, total

# --- Page Setup ---
st.set_page_config(page_title="🌱 Carbon Footprint Calculator")
st.title("🌍 Pakistan Carbon Footprint Calculator")

st.markdown("""
Welcome to your personal carbon footprint dashboard. Fill in details across the tabs to get an estimate of your annual CO₂ emissions.
""")

tabs = st.tabs(["Household", "Vehicles", "Secondary", "Total"])
user_data = {}

# --- 🏠 Household Tab ---
with tabs[0]:
    st.markdown("## 🏠 Household Emissions")
    with st.expander("➕ Enter your household energy usage"):
        col1, col2 = st.columns(2)
        with col1:
            user_data['electricity'] = st.number_input("Electricity (kWh/year)", min_value=0, value=None, placeholder="e.g. 10,000", format="%d")
        with col2:
            user_data['gas'] = st.number_input("Natural Gas (m³/year)", min_value=0, value=None, placeholder='e.g. 5,000', format="%d")

    if user_data['electricity'] is None or user_data['gas'] is None:
        st.markdown(""" ⚠️ Please enter both electricity and gas usage to calculate household emissions.""")
    elif isinstance(user_data['electricity'], (int, float)) and isinstance(user_data['gas'], (int, float)):
        household_emissions = calculate_emissions(user_data)[0]['Household'] / 1000
        st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🧮 Total Household Emissions: <span style='color:#d43f3a'>{household_emissions:.2f}</span> metric tons CO₂</h4>",
        unsafe_allow_html=True
    )

# --- 🚗 Vehicles Tab ---
with tabs[1]:
    # Page Title
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🚘 Vehicle Emissions</h2>"
        "<p style='color: gray; font-size: 1rem;'>Add your vehicle details to estimate yearly CO₂ emissions.</p>",
        unsafe_allow_html=True
    )

    user_data['cars'] = []
    user_data['motorcycle'] = []

    with st.container():
        st.markdown("### 🚗 Cars")
        with st.expander("➕ Add your car details"):
            car_cols = st.columns(3)
            with car_cols[1]:
                num_cars = st.number_input("Number of Cars", min_value=0, value=1, step=1, key='num_cars', format="%d")
            user_data['cars'] = []
            for i in range(num_cars):
                st.markdown(f"**Car {i+1}**", help="Enter annual distance and average efficiency")
                cols = st.columns(2)
                with cols[0]:
                    miles = st.number_input("Kilometers Driven Per Year", min_value=0, value=15000, key=f'car_miles_{i}', format="%d")
                with cols[1]:
                    efficiency = st.number_input("Fuel Efficiency (km/l)", min_value=1.0, value=12.0, key=f'car_eff_{i}')
                user_data['cars'].append({'miles_driven': miles, 'fuel_efficiency': efficiency})
        car_emissions = calculate_emissions(user_data)[0]['Cars'] / 1000
        st.metric(label="Car Emissions", value=f"{car_emissions:,.2f} metric tons CO₂")


    # BIKE SECTION
    with st.container():
        st.markdown("### 🏍️ Motorcycles")
        with st.expander("➕ Add motorcycle details"):
            bike_cols = st.columns(3)
            with bike_cols[1]:
                num_bikes = st.number_input("Number of Motorcycles", min_value=0, value=1, step=1, key='num_bikes', format="%d")
            user_data['motorcycle'] = []
            for i in range(num_bikes):
                st.markdown(f"**Motorcycle {i+1}**", help="Enter annual distance and fuel efficiency")
                cols = st.columns(2)
                with cols[0]:
                    miles = st.number_input("Kilometers Driven Per Year", min_value=0, value=8000, key=f'bike_miles_{i}', format="%d")
                with cols[1]:
                    efficiency = st.number_input("Fuel Efficiency (km/l)", min_value=1.0, value=30.0, key=f'bike_eff_{i}')
                user_data['motorcycle'].append({'miles_driven': miles, 'fuel_efficiency': efficiency})
        bike_emissions = calculate_emissions(user_data)[0]['Motorcycle'] / 1000
        st.metric(label="Motorcycle Emissions", value=f"{bike_emissions:,.2f} metric tons CO₂")


    # BUS SECTION
    with st.container():
        st.markdown("### 🚌 Public Bus Travel")
        cols = st.columns(2)
        with cols[0]:
            user_data['bus'] = st.number_input("Kilometers Traveled by Bus Per Year", min_value=0, value=5000, key='bus_km', format="%d")
        with cols[1]:
            st.markdown("")

        bus_emissions = calculate_emissions(user_data)[0]['Bus'] / 1000
        st.metric(label="Bus Emissions", value=f"{bus_emissions:,.2f} metric tons CO₂")


    # TOTAL EMISSIONS (Optional Apple-style summary)
    total = car_emissions + bike_emissions + bus_emissions
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🧮 Total Vehicle Emissions: <span style='color:#d43f3a'>{total:.2f}</span> metric tons CO₂</h4>",
        unsafe_allow_html=True
    )


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

    # Sort categories for consistent layout
    sorted_emissions = dict(sorted(emissions.items(), key=lambda x: x[1], reverse=True))

    # Create horizontal bar plot
    fig, ax = plt.subplots(figsize=(12, 2.5))  # Small footprint
    bars = ax.barh(list(sorted_emissions.keys()), list(sorted_emissions.values()), color=['#4F8EF7', '#F75C03'])/1000

    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{width:.1f} t CO₂", va='center', fontsize=9)

    # Style tweaks
    ax.set_xlim(0, max(sorted_emissions.values()) * 1.2)
    ax.set_xlabel("Emissions (metric tons CO₂)", fontsize=9)
    ax.set_title("Household Emission Sources", fontsize=11, weight='bold')
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(left=False, bottom=False)
    ax.grid(axis='x', linestyle='--', alpha=0.3)

    st.pyplot(fig)


    st.markdown("### 📚 Comparison Benchmarks")
    col1, col2, col3 = st.columns(3)
    col1.metric("🇵🇰 Pakistan Average", "0.98 tCO₂")
    col2.metric("🇪🇺 EU Average", "6.80 tCO₂")
    col3.metric("🌍 Global Average", "4.79 tCO₂")

    st.markdown("> To stay below 2°C global warming, the footprint per person must fall below **2 tCO₂/year by 2050**.")

