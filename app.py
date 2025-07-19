import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd


def calculate_emissions(data):
    factors = {
        'electricity': 0.5004,
        'gas': 2.2,
        'fuel': 2.7,
        'flights': 200,
        'food': 0.0016,
        'clothing': 0.007,
        'electronics': 0.0017,
        'furniture': 0.0014,
        'recreation': 0.0009
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
        'Secondary': sum(data.get(k, 0) for k in ['food', 'clothing', 'electronics', 'furniture', 'recreation']) / 1000
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
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>⚡ Energy Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.25rem;'>Add your household energy use details to estimate yearly CO₂ emissions.</h4>",
        unsafe_allow_html=True
    )
    _, col2, _ = st.columns(3)
    with col2:
        people_count = st.number_input("How many people live in your household?", min_value=1, value=1, step=1, key='people_count')
        user_data['people_count'] = people_count
    with st.expander("➕ Enter your household energy usage"):
        col1, col2 = st.columns(2)
        with col1:
            user_data['electricity'] = st.number_input("Electricity (kWh/year)", min_value=0, value=10000, placeholder="e.g. 10,000", format="%d")
        with col2:
            user_data['gas'] = st.number_input("Natural Gas (m³/year)", min_value=0, value=5000, placeholder='e.g. 5,000', format="%d")

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
        "<h4 style='color: gray; font-size: 1.25rem;'>Add your vehicle details to estimate yearly CO₂ emissions.</h4>",
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


    # TOTAL EMISSIONS
    vehicle_emissions = car_emissions + bike_emissions + bus_emissions
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🚗 Your Transportation Carbon Footprint: <span style='color:#d43f3a'>{vehicle_emissions:.2f}</span> metric tons CO₂</h4>",
        unsafe_allow_html=True
    )


with tabs[2]:
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🛍️ Secondary Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.25rem;'>Estimate your yearly CO₂ emissions from lifestyle choices</h4>",
        unsafe_allow_html=True
    )

    # --- EPA Emission Factors ---
    diet_emission_factors = {
        "Meat-heavy": 3.3,
        "Average (mixed)": 2.5,
        "Vegetarian": 1.7,
        "Vegan": 1.5
    }

    device_emission_factor = 0.35
    emission_per_pkr = 0.00089

    # --- Spending Ranges ---
    spending_ranges = {
        "0 - 5,000 PKR": 2500,
        "5,000 - 10,000 PKR": 7500,
        "10,000 - 20,000 PKR": 15000,
        "20,000 - 50,000 PKR": 35000,
        "50,000 - 100,000 PKR": 75000,
        "100,000+ PKR": 125000
    }

    with stylable_container(
        key="custom_expander_title",
        css_styles="""
            div.expander-title {
                font-weight: bold;
                color: #333;
                transition: color 0.2s ease;
            }
            div.expander-title:hover {
                color: #2c7be5;  /* Your hover color */
            }
        """,
    ):
        # --- Food/Diet ---
        with st.expander("**🍽️ What kind of diet do you follow?**"):
            diet_options = list(diet_emission_factors.keys())

            # Setup initial session state
            if "diet_type" not in st.session_state:
                st.session_state["diet_type"] = "Average (mixed)"

            cols = st.columns(len(diet_emission_factors))

            for i, (diet, _) in enumerate(diet_emission_factors.items()):
                is_selected = st.session_state["diet_type"] == diet

                # Apply a different color if selected
                bg_color = "#4CAF50" if is_selected else "#f0f0f0"
                text_color = "white" if is_selected else "black"
                border_color = "#4CAF50" if is_selected else "#ccc"

                with cols[i]:
                    with stylable_container(
                        f"button_style_{diet.replace(' ', '_')}",
                        css_styles=f"""
                            button {{
                                background-color: {bg_color};
                                color: {text_color};
                                border: 1px solid {border_color};
                                border-radius: 6px;
                                margin-bottom: 16px;
                                transition: all 0.2s ease;
                            }}
                            button:hover {{
                                background-color: #45a049 !important;
                                color: white !important;
                                border-color: #45a049 !important;
                            }}
                            button:active {{
                                background-color: #3e8e41 !important;
                                color: white !important;
                                border-color: #3e8e41 !important;
                                transform: scale(0.98);
                            }}
                            button:focus,
                            button:focus-visible {{
                                color: white !important;
                                border-color: #3e8e41 !important;
                                box-shadow: none !important;
                            }}
                        """,
                    ):
                        if st.button(diet, use_container_width=True):
                            st.session_state["diet_type"] = diet
                            st.rerun()

        # Store selection in user_data
        user_data['food'] = diet_emission_factors[st.session_state['diet_type']] * 1000  # convert to kg

    # --- Electronics ---
    with st.expander("**📱 How many new electronic devices did you purchase this year?**"):
        devices = st.slider("Number of new devices (phones, laptops, etc.):", 0, 10, 2, key="device_count")
        user_data['electronics'] = devices * device_emission_factor * 1000  # convert to kg

    # --- Clothing ---
    with st.expander("**👕 Clothing Spending**"):
        choice = st.selectbox("Select your yearly spending on clothing:", list(spending_ranges.keys()), index=2, key="clothing_range")
        user_data['clothing'] = spending_ranges[choice] * emission_per_pkr

    # --- Furniture ---
    with st.expander("**🪑 Furniture Spending**"):
        choice = st.selectbox("Select your yearly spending on furniture:", list(spending_ranges.keys()), index=2, key="furniture_range")
        user_data['furniture'] = spending_ranges[choice] * emission_per_pkr

    # --- Recreation ---
    with st.expander("**🎮 Recreation Spending**"):
        choice = st.selectbox("Select your yearly spending on recreation (travel, entertainment):", list(spending_ranges.keys()), index=2, key="recreation_range")
        user_data['recreation'] = spending_ranges[choice] * emission_per_pkr

    # --- Result ---
    sec_emissions = calculate_emissions(user_data)[0]['Secondary']
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🛒 Your Secondary Carbon Footprint: <span style='color:#d43f3a'>{sec_emissions:.2f}</span> metric tons CO₂e</h4>",
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

    if total_emissions < 2.1:
        st.markdown("<div class='main-title'>🎉 Congratulations!</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Your annual footprint is less that the national average!</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='main-title'>🚨 Oops!</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Your annual footprint is above the national average. Let's work on reducing it!</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    with col1:
        st.markdown("""
                    <style>
                        .result-box {
                            background-color: #FFD43B;
                            border-radius: 10px;
                            text-align: center;
                            min-height: 295px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        }
                    </style>
                """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class='result-box'>
                <div style='font-size: 20px;'>Your Carbon Footprint</div>
                <div style='font-size: 50px; font-weight: bold;'>{total_emissions}</div>
                <div style='font-size: 20px;'>tonnes CO₂</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='black-box'>
                <div style='font-size: 16px;'>National Average Carbon Footprint</div>
                <div style='font-size: 36px;'>2.1 tonnes CO₂</div>
            </div>
            <div style='height: 20px;'></div>
            <div class='black-box'>
                <div style='font-size: 16px;'>Your Carbon Footprint is</div>
                <div style='font-size: 36px;'>{round(total_emissions/6.7 * 100)}%</div>
                <div style='font-size: 16px;'>of the Global Average for 2025</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='black-box'>
                <div style='font-size: 16px;'>Global Average</div>
                <div style='font-size: 36px;'>6.7 tonnes CO₂</div>
            </div>
            <div style='height: 20px;'></div>
            <!--
            <div class='black-box'>
                <div style='font-size: 16px;'>GO WILD - WWF'S CLUB FOR KIDS</div>
                <div style='margin-top: 10px;'>Fun facts, puzzles, crafts & more</div>
            </div>
            -->
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)

    st.markdown("<div class='main-title'>Let's break it down...</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Your footprint is equal to <b>{total_emissions}T</b></div>", unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='category-box' style='background-color: #3FA9D5;'>
                <div style='font-size: 24px; font-color: white'><b>⚡ Household Energy</b></div>
                <div>Your consumption is equal to <b>{household_emissions:.2f} tonnes CO₂</b></div>
            </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='category-box' style='background-color: #4CAF50;'>
                <div style='font-size: 24px;'><b>🚗 Transport</b></div>
                <div>Your consumption is equal to <b>{vehicle_emissions:.2f} tonnes CO₂</b></div>
            </div>
        """, unsafe_allow_html=True)

    with colC:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='category-box' style='background-color: #F1A9FF;'>
                <div style='font-size: 24px;'><b>🛒 Secondary</b></div>
                <div>Your consumption is equal to <b>{sec_emissions:.2f} tonnes CO₂</b></div>
            </div>
        """, unsafe_allow_html=True)

