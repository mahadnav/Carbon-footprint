import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def calculate_emissions(data):
    factors = {
        'electricity': 0.5004,
        'gas': 2.2,
        'fuel': 2.7,
        'flights': 200,
        'food': 0.0015,
        'clothing': 0.0013,
        'electronics': 0.0020,
        'furniture': 0.0014,
        'recreation': 0.0012
    }

    electricity = data.get('electricity', 0)
    gas = data.get('gas', 0)
    people = max(data.get('people_count', 1), 1)  # Avoid division by 0

    try:
        electricity = float(electricity)
    except (ValueError, TypeError):
        electricity = 0

    try:
        gas = float(gas)
    except (ValueError, TypeError):
        gas = 0

    # Household emissions per capita
    total_household_emissions = electricity * factors['electricity'] + gas * factors['gas']
    household_emissions = total_household_emissions / people

    emissions = {
        'Household': household_emissions / 1000,
        'Cars': sum((c['miles_driven'] / c['fuel_efficiency']) * factors['fuel'] for c in data.get('cars', [])) / 1000,
        'Motorcycle': sum((b['miles_driven'] / b['fuel_efficiency']) * factors['fuel'] for b in data.get('motorcycle', [])) / 1000,
        'Bus': data.get('bus', 0) * 0.05 / 1000,
        'Secondary': sum(data.get(k, 0) * factors[k] for k in factors if k not in ['electricity', 'gas', 'fuel', 'flights']) / 1000
    }

    total = sum(emissions.values())  # to metric tons
    return emissions, total

# --- Page Setup ---
st.set_page_config(page_title="🌱 Carbon Footprint Calculator", layout="wide")
st.title("🌍 Pakistan Carbon Footprint Calculator")

st.markdown("""
Welcome to your personal carbon footprint dashboard. Fill in details across the tabs to get an estimate of your annual CO₂ emissions.
""")

tabs = st.tabs(["Household", "Transport", "Secondary", "Total"])
user_data = {}

# --- Energy Tab ---
with tabs[0]:
    st.markdown("## ⚡ Energy Emissions")
    _, col2, _ = st.columns(3)
    with col2:
        people_count = st.number_input("How many people live in your household?", min_value=1, value=1, step=1, key='people_count')
        user_data['people_count'] = people_count
    with st.expander("➕ Enter your household energy usage"):
        col1, col2 = st.columns(2)
        with col1:
            user_data['electricity'] = st.number_input("Electricity (kWh/year)", min_value=0, value=None, placeholder="e.g. 10,000", format="%d")
        with col2:
            user_data['gas'] = st.number_input("Natural Gas (m³/year)", min_value=0, value=None, placeholder='e.g. 5,000', format="%d")

    if user_data['electricity'] is None or user_data['gas'] is None:
        st.markdown(""" ⚠️ Please enter both electricity and gas usage to calculate household emissions.""")
    elif isinstance(user_data['electricity'], (int, float)) and isinstance(user_data['gas'], (int, float)):
        household_emissions = calculate_emissions(user_data)[0]['Household']
        st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"⚡ Your Energy Carbon Footprint: <span style='color:#d43f3a'>{household_emissions:.2f}</span> metric tons CO₂</h4>",
        unsafe_allow_html=True
    )

# --- Vehicles Tab ---
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
            car_emissions = calculate_emissions(user_data)[0]['Cars']
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
            bike_emissions = calculate_emissions(user_data)[0]['Motorcycle']
            st.metric(label="Motorcycle Emissions", value=f"{bike_emissions:,.2f} metric tons CO₂")


    # BUS SECTION
    with st.container():
        st.markdown("### 🚌 Public Bus Travel")
        with st.expander("➕ Add bus travel details"):
            cols = st.columns(2)
            with cols[0]:
                user_data['bus'] = st.number_input("Kilometers Traveled by Bus Per Year", min_value=0, value=0, key='bus_km', format="%d")
            with cols[1]:
                st.markdown("")

            bus_emissions = calculate_emissions(user_data)[0]['Bus']
            st.metric(label="Bus Emissions", value=f"{bus_emissions:,.2f} metric tons CO₂")


    # TOTAL EMISSIONS (Optional Apple-style summary)
    vehicle_emissions = car_emissions + bike_emissions + bus_emissions
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🚗 Your Transportation Carbon FOotprint: <span style='color:#d43f3a'>{vehicle_emissions:.2f}</span> metric tons CO₂</h4>",
        unsafe_allow_html=True
    )


# --- Secondary Emissions Tab ---
with tabs[2]:
    st.markdown("## 🛍️ Secondary Consumption")
    categories = ['food', 'clothing', 'electronics', 'furniture', 'recreation']

    spending_ranges = {
        "0 - 5,000 PKR": 2500,
        "5,000 - 10,000 PKR": 7500,
        "10,000 - 20,000 PKR": 15000,
        "20,000 - 50,000 PKR": 35000,
        "50,000 - 100,000 PKR": 75000,
        "100,000+ PKR": 125000
    }

    with st.expander("🛒 Select your approximate yearly spending per category"):
        for cat in categories:
            label = cat.replace('_', ' ').title()
            choice = st.selectbox(
                f"{label} Spending",
                options=list(spending_ranges.keys()),
                index=2,  # default to mid-range
                key=f"{cat}_range"
            )
            user_data[cat] = spending_ranges[choice]

    sec_emissions = calculate_emissions(user_data)[0]['Secondary']
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🚗 Your Secondary Carbon Footprint: <span style='color:#d43f3a'>{sec_emissions:,.2f}</span> metric tons CO₂</h4>",
        unsafe_allow_html=True
    )

total_emissions = round(calculate_emissions(user_data)[1], 2)

# --- Results Tab ---
with tabs[3]:
    st.markdown("""
        <style>
            .main-title {
                font-size: 36px;
                color: black;
                font-weight: bold;
            }
            .subtitle {
                font-size: 18px;
                color: #555;
            }
            .result-box {
                background-color: #FDD835;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
                height: 100%;
            }
            .black-box {
                background-color: #212121;
                color: white;
                padding: 20px;
                border-radius: 10px;
                height: 100%;
            }
            .category-box {
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 10px;
                height: 100%;
                text-align: center;
            }
            .reduce-button {
                margin-top: 10px;
                display: inline-block;
                padding: 8px 16px;
                background-color: black;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-size: 14px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-title'>🎉 Congratulations!</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Your annual footprint is close to the national average, but there's still room to improve!</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    with col1:
        st.markdown(f"""
            <div class='result-box'>
                <div style='font-size: 20px;'>YOUR FOOTPRINT IS EQUAL TO</div>
                <div style='font-size: 50px; font-weight: bold;'>{total_emissions}</div>
                <div style='font-size: 20px;'>TONNES*</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class='black-box'>
                <div style='font-size: 16px;'>EU AVERAGE FOOTPRINT FOR 2025</div>
                <div style='font-size: 36px;'>6.9 TONNES</div>
            </div>
            <div style='height: 20px;'></div>
            <div class='black-box'>
                <div style='font-size: 16px;'>YOUR FOOTPRINT IS</div>
                <div style='font-size: 36px;'>{total_emissions/6.3 * 100}%</div>
                <div style='font-size: 16px;'>OF THE WORLD AVERAGE FOR 2025</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class='black-box'>
                <div style='font-size: 16px;'>WORLD AVERAGE</div>
                <div style='font-size: 36px;'>6.3 TONNES</div>
            </div>
            <div style='height: 20px;'></div>
            <div class='black-box'>
                <div style='font-size: 16px;'>GO WILD - WWF'S CLUB FOR KIDS</div>
                <div style='margin-top: 10px;'>Fun facts, puzzles, crafts & more</div>
                <div><button class='reduce-button'>CHECK IT OUT</button></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)

    st.markdown("<div class='main-title'>LET'S BREAK IT DOWN</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Your footprint is equal to <b>{total_emissions}T</b></div>", unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("""
            <div class='category-box' style='background-color: #03A9F4;'>
                <div style='font-size: 24px;'>🏠 HOME</div>
                <div>Your consumption is equal to <b>2 TONNES</b></div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        st.markdown("""
            <div class='category-box' style='background-color: #FF9800;'>
                <div style='font-size: 24px;'>🚗 TRAVEL</div>
                <div>Your consumption is equal to <b>2 TONNES</b></div>
            </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown("""
            <div class='category-box' style='background-color: #00BCD4;'>
                <div style='font-size: 24px;'>🍽 FOOD</div>
                <div>Your consumption is equal to <b>2 TONNES</b></div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        st.markdown("""
            <div class='category-box' style='background-color: #E91E63;'>
                <div style='font-size: 24px;'>🛒 STUFF</div>
                <div>Your consumption is equal to <b>1 TONNES</b></div>
            </div>
        """, unsafe_allow_html=True)

