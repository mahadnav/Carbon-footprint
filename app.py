import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
from geopy.distance import geodesic

def expander_style():
        return st.markdown("""
        <style>
        details summary {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333;
            transition: color 0.2s ease;
        }

        details:hover summary {
            color: #2E8B57 !important; /* Hover color */
            cursor: pointer;
        }

        details {
            margin-bottom: 16px;
            border-radius: 6px;
            border: 1px solid #eee;
            padding: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

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

    total = sum(emissions.values())  # to metric tonnes
    return emissions, total

# --- Page Setup ---
st.set_page_config(page_title="🇵🇰 Carbon Footprint Calculator", layout="wide")
st.title("🇵🇰 Pakistan Carbon Footprint Calculator")

st.markdown("""
Welcome to your personal carbon footprint dashboard. Fill in details across the tabs to get an estimate of your annual CO₂ emissions.
""")

tabs = st.tabs(["Household", "Transport", "Secondary", "Total"])
user_data = {}

# --- Energy Tab ---
with tabs[0]:
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>⚡ Energy Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Add your household energy use details to estimate yearly CO₂ emissions.</h4>",
        unsafe_allow_html=True
    )
    _, col2, _ = st.columns(3)
    with col2:
        people_count = st.number_input("How many people live in your household?", min_value=1, value=1, step=1, key='people_count')
        user_data['people_count'] = people_count
    
    expander_style()
    with st.expander("**➕ Enter your household energy usage**"):
        col1, col2 = st.columns(2)
        with col1:
            user_data['electricity'] = st.number_input("Electricity (kWh/year)", min_value=0, value=0, placeholder="e.g. 10,000", format="%d")
        with col2:
            user_data['gas'] = st.number_input("Natural Gas (m³/year)", min_value=0, value=0, placeholder='e.g. 3,500', format="%d")

    if user_data['electricity'] is None or user_data['gas'] is None:
        st.markdown(""" ⚠️ Please enter both electricity and gas usage to calculate household emissions.""")
    elif isinstance(user_data['electricity'], (int, float)) and isinstance(user_data['gas'], (int, float)):
        household_emissions = calculate_emissions(user_data)[0]['Household']
        st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"⚡ Your Energy Carbon Footprint: <span style='color:#d43f3a'>{household_emissions:.2f}</span> tonnes CO₂</h4>",
        unsafe_allow_html=True
    )

# --- Vehicles Tab ---
with tabs[1]:
    # Page Title
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🚘 Vehicle Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Add your vehicle details to estimate yearly CO₂ emissions.</h4>",
        unsafe_allow_html=True
    )

    # CAR SECTION
    with st.container():
        st.markdown("### 🚗 Cars")

        user_data['cars'] = []

        expander_style()
        with st.expander("**➕ Add your car details**"):
            car_cols = st.columns(3)
            with car_cols[1]:
                num_cars = st.number_input("Number of Cars", min_value=0, value=0, step=1, key='num_cars', format="%d")
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
            st.metric(label="Car Emissions", value=f"{car_emissions:,.2f} tonnes CO₂")
            st.markdown(f"""
                <div style='font-size: 1.5rem; font-weight: normal;'>
                    Estimated Emissions for Your Car Travel: <span style='color:#4CAF50'>{car_emissions:.2f}</span> tonnes CO₂
                </div>
            """, unsafe_allow_html=True)

    # BIKE SECTION
    with st.container():
        st.markdown("### 🏍️ Motorcycles")

        user_data['motorcycle'] = []
        
        expander_style()
        with st.expander("**➕ Add motorcycle details**"):
            bike_cols = st.columns(3)
            with bike_cols[1]:
                num_bikes = st.number_input("Number of Motorcycles", min_value=0, value=0, step=1, key='num_bikes', format="%d")
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
            st.markdown(f"""
                <div style='font-size: 1.5rem; font-weight: normal;'>
                    Estimated Emissions for Your Motorcycle Travel: <span style='color:#4CAF50'>{bike_emissions:.2f}</span> tonnes CO₂
                </div>
            """, unsafe_allow_html=True)

    # BUS SECTION
    with st.container():
        st.markdown("### 🚌 Public Bus Travel")
        
        expander_style()
        with st.expander("**➕ Add bus travel details**"):
            cols = st.columns(2)
            with cols[0]:
                user_data['bus'] = st.number_input("Kilometers Traveled by Bus Per Year", min_value=0, value=0, key='bus_km', format="%d")
            with cols[1]:
                st.markdown("")

            bus_emissions = calculate_emissions(user_data)[0]['Bus']
            st.markdown(f"""
                <div style='font-size: 1.5rem; font-weight: normal;'>
                    Estimated Emissions for Your Bus Travel: <span style='color:#4CAF50'>{bus_emissions:.2f}</span> tonnes CO₂
                </div>
            """, unsafe_allow_html=True)

    # AIR TRAVEL SECTION
    with st.container():
        st.markdown("### ✈️ Air Travel")

        airports = {
            # --- Pakistan Airports ---
            "Islamabad (ISB)": (33.6167, 73.0991),
            "Lahore (LHE)": (31.5216, 74.4036),
            "Karachi (KHI)": (24.9065, 67.1608),
            "Multan (MUX)": (30.2032, 71.4191),
            "Peshawar (PEW)": (33.9939, 71.5146),
            "Quetta (UET)": (30.2514, 66.9378),
            "Sialkot (SKT)": (32.5356, 74.3639),
            "Faisalabad (LYP)": (31.3654, 72.9948),
            "Bahawalpur (BHV)": (29.3481, 71.7180),
            "Rahim Yar Khan (RYK)": (28.3839, 70.2796),
            "Gwadar (GWD)": (25.2322, 62.3295),
            "Turbat (TUK)": (25.9864, 63.0302),
            "Skardu (KDU)": (35.3354, 75.5361),
            "Gilgit (GIL)": (35.9188, 74.3336),

            # --- Gulf / Middle East ---
            "Dubai (DXB)": (25.2532, 55.3657),
            "Abu Dhabi (AUH)": (24.4329, 54.6511),
            "Sharjah (SHJ)": (25.3286, 55.5171),
            "Doha (DOH)": (25.2736, 51.6080),
            "Muscat (MCT)": (23.5933, 58.2844),
            "Jeddah (JED)": (21.6796, 39.1565),
            "Riyadh (RUH)": (24.9576, 46.6988),
            "Dammam (DMM)": (26.4711, 49.7979),
            "Medina (MED)": (24.5539, 39.7051),
            "Gassim (ELQ)": (26.3028, 43.7744),
            "Bahrain (BAH)": (26.2708, 50.6336),
            "Kuwait City (KWI)": (29.2266, 47.9689),
            "Musandam (KHS)": (26.2081, 56.2625),
            "Sana'a (SAH)": (15.4675, 44.2194),
            "Aden (ADE)": (12.7844, 45.0161),
            "Erbil (EBL)": (36.2333, 44.0083),
            "Basra (BSR)": (30.5494, 47.6542),
            "Sulaymaniyah (ISU)": (35.5600, 45.4400),
            "Najaf (NJF)": (31.9894, 44.4042),
            "Sulaymaniyah (ISU)": (35.5600, 45.4400),
            "Kuwait City (KWI)": (29.2266, 47.9689),
            "Muscat (MCT)": (23.5933, 58.2844),

            # --- Central & South Asia ---
            "Tashkent (TAS)": (41.2579, 69.2817),
            "Baku (GYD)": (40.4675, 50.0467),
            "Kuala Lumpur (KUL)": (2.7456, 101.7092),
            "Beijing (PEK)": (40.0801, 116.5846),
            "Baghdad (BGW)": (33.2625, 44.2346),
            "Najaf (NJF)": (31.9894, 44.4042),
            "Bishkek (FRU)": (43.0617, 74.4777),
            "Almaty (ALA)": (43.3528, 77.0402),
            "Dushanbe (DYU)": (38.5433, 68.7811),
            "Kathmandu (KTM)": (27.6961, 85.3597),
            "Colombo (CMB)": (7.1800, 79.8842),
            "Dhaka (DAC)": (23.8431, 90.3978),
            "Mumbai (BOM)": (19.0887, 72.8689),
            "Delhi (DEL)": (28.5562, 77.1000),
            "Chennai (MAA)": (12.9948, 80.1785),
            "Bangkok (BKK)": (13.6811, 100.7476),
            "Singapore (SIN)": (1.3502, 103.9940),
            "Hong Kong (HKG)": (22.3080, 113.9185),
            "Jakarta (CGK)": (-6.1256, 106.6552),
            "Seoul (ICN)": (37.4692, 126.4500),
            "Tokyo (NRT)": (35.7647, 140.3864),
            "Shanghai (PVG)": (31.1436, 121.8052),
            "Manila (MNL)": (14.5086, 121.0190),
            "Hanoi (HAN)": (21.2210, 105.8042),
            "Ho Chi Minh City (SGN)": (10.8181, 106.6511),
            "Kabul (KBL)": (34.5650, 69.2120),

            # --- Europe & North America ---
            "London Heathrow (LHR)": (51.4700, -0.4543),
            "London Gatwick (LGW)": (51.1537, -0.1821),
            "Paris Charles de Gaulle (CDG)": (49.0097, 2.5479),
            "Toronto Pearson (YYZ)": (43.6777, -79.6248),
            "New York JFK (JFK)": (40.6413, -73.7781),
            "Los Angeles (LAX)": (33.9425, -118.4081),
            "San Francisco (SFO)": (37.6189, -122.3750),
            "Chicago O'Hare (ORD)": (41.9742, -87.9073),
            "Miami (MIA)": (25.7932, -80.2906),
            "Dallas Fort Worth (DFW)": (32.8968, -97.0380),
            "Atlanta (ATL)": (33.6407, -84.4279),
            "Seattle (SEA)": (47.4502, -122.3088),
            "Washington Dulles (IAD)": (38.9445, -77.4558),
            "Boston Logan (BOS)": (42.3641, -71.0052),
            "Vancouver (YVR)": (49.1939, -123.1830),
            "Montreal (YUL)": (45.4706, -73.7400),
            "Calgary (YYC)": (51.1139, -114.0200),
            "Ottawa (YOW)": (45.3222, -75.6692),
            "Mexico City (MEX)": (19.4361, -99.0721)
        }

        expander_style()
        with st.expander("**➕ Add your flight details**"):
            flights_taken = st.radio("Have you taken any flights in the past year?", 
                                options=["Yes", "No"], 
                                index=1, 
                                key="flights_taken", 
                                horizontal=True
                                )
            
            if flights_taken == "No":
                flight_emissions = 0
            else:
                # Select number of legs (segments) in the trip
                num_legs = st.number_input("How many destinations are in your trip?", min_value=1, max_value=6, value=1, step=1, key="num_legs")

                # Toggle for return or one-way flight for each leg
                round_trip_flags = []
                legs = []

                st.markdown("### Trip Details")
                for i in range(num_legs):
                    st.markdown(f"**Leg {i + 1}**")
                    col1, col2, col3 = st.columns([4, 4, 2])
                    with col1:
                        dep = st.selectbox(f"Departure Airport (Leg {i + 1})", list(airports.keys()), key=f"dep_{i}")
                    with col2:
                        arr = st.selectbox(f"Arrival Airport (Leg {i + 1})", list(airports.keys()), key=f"arr_{i}")
                    with col3:
                        st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)  # Empty space for alignment
                        is_round = st.checkbox("Return?", key=f"return_{i}", value=True)

                    legs.append((dep, arr))
                    round_trip_flags.append(is_round)

                # Constants
                flight_emission_factor = 0.00015  # tonnes CO₂ per km per passenger

                # Calculate total emissions
                flight_emissions = 0
                for (dep, arr), is_round in zip(legs, round_trip_flags):
                    if dep != arr:
                        dist_km = geodesic(airports[dep], airports[arr]).km
                        if is_round:
                            dist_km *= 2
                        emissions = dist_km * flight_emission_factor
                        flight_emissions += emissions

            st.markdown(f"""
                <div style='font-size: 1.5rem; font-weight: normal;'>
                    Estimated Emissions for Your Air Travel: <span style='color:#4CAF50'>{flight_emissions:.2f}</span> tonnes CO₂
                </div>
            """, unsafe_allow_html=True)


    # TOTAL EMISSIONS
    vehicle_emissions = car_emissions + bike_emissions + bus_emissions + flight_emissions
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🚗 Your Transportation Carbon Footprint: <span style='color:#d43f3a'>{vehicle_emissions:.2f}</span> tonnes CO₂e</h4>",
        unsafe_allow_html=True
    )

with tabs[2]:
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🛍️ Secondary Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Estimate your yearly CO₂ emissions from lifestyle choices.</h4>",
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
        "0": 0,
        "less than 5,000 PKR": 2500,
        "5,000 - 10,000 PKR": 7500,
        "10,000 - 20,000 PKR": 15000,
        "20,000 - 50,000 PKR": 35000,
        "50,000 - 100,000 PKR": 75000,
        "100,000 - 200,000 PKR": 150000,
        "greater than 200,000 PKR": 250000,
    }

    # --- Food/Diet ---
    expander_style()
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
                    key=f"custom_button_{diet.replace(' ', '_')}",
                    css_styles=f"""
                        [data-testid="stButton"] button {{
                            background-color: {bg_color};
                            color: {text_color};
                            border: 1px solid {border_color};
                            border-radius: 6px;
                            margin-bottom: 16px;
                            transition: all 0.2s ease;
                        }}
                        [data-testid="stButton"] button:hover {{
                            background-color: #45a049 !important;
                            color: white !important;
                            border-color: #45a049 !important;
                        }}
                        [data-testid="stButton"] button:active {{
                            background-color: #3e8e41 !important;
                            color: white !important;
                            border-color: #3e8e41 !important;
                            transform: scale(0.98);
                        }}
                        [data-testid="stButton"] button:focus {{
                            outline: none !important;
                            box-shadow: none !important;
                        }}
                        [data-testid="stButton"] button:focus,
                        [data-testid="stButton"] button:focus-visible {{
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
    expander_style()
    with st.expander("**📱 How many new electronic devices did you purchase this year?**"):
        devices = st.slider("Number of new devices (phones, laptops, etc.):", 0, 10, 2, key="device_count")
        user_data['electronics'] = devices * device_emission_factor * 1000  # convert to kg

    # --- Clothing ---
    expander_style()
    with st.expander("**👕 Clothing Spending**"):
        choice = st.selectbox("Select your yearly spending on clothing:", list(spending_ranges.keys()), index=0, key="clothing_range")
        user_data['clothing'] = spending_ranges[choice] * emission_per_pkr

    # --- Furniture ---
    expander_style()
    with st.expander("**🪑 Furniture Spending**"):
        choice = st.selectbox("Select your yearly spending on furniture:", list(spending_ranges.keys()), index=0, key="furniture_range")
        user_data['furniture'] = spending_ranges[choice] * emission_per_pkr

    # --- Recreation ---
    expander_style()
    with st.expander("**🎮 Recreation Spending**"):
        choice = st.selectbox("Select your yearly spending on recreation (travel, entertainment):", list(spending_ranges.keys()), index=0, key="recreation_range")
        user_data['recreation'] = spending_ranges[choice] * emission_per_pkr

    # --- Result ---
    sec_emissions = calculate_emissions(user_data)[0]['Secondary']
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🛒 Your Secondary Carbon Footprint: <span style='color:#d43f3a'>{sec_emissions:.2f}</span> tonnes CO₂e</h4>",
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
            .grey-box {
                background-color: #636363;
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
        st.markdown("<div class='main-title'>🎉 Hooray!</div>", unsafe_allow_html=True)
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
                            min-height: 319px;
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
                <div style='font-size: 20px;'>tonnes CO₂e</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='black-box'>
                <div style='font-size: 16px;'>National Average Carbon Footprint</div>
                <div style='font-size: 36px;'>2.1 tonnes CO₂e</div>
                <div style='font-size: 16px;'>per capita</div>
            </div>
            <div style='height: 20px;'></div>
            <div class='grey-box'>
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
                <div style='font-size: 36px;'>6.7 tonnes CO₂e</div>
                <div style='font-size: 16px;'>per capita</div>
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
                <div>Your consumption is equal to <b>{household_emissions:.2f} tonnes CO₂e</b></div>
            </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='category-box' style='background-color: #4CAF50;'>
                <div style='font-size: 24px;'><b>🚗 Transport</b></div>
                <div>Your consumption is equal to <b>{vehicle_emissions:.2f} tonnes CO₂e</b></div>
            </div>
        """, unsafe_allow_html=True)

    with colC:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='category-box' style='background-color: #F1A9FF;'>
                <div style='font-size: 24px;'><b>🛒 Secondary</b></div>
                <div>Your consumption is equal to <b>{sec_emissions:.2f} tonnes CO₂e</b></div>
            </div>
        """, unsafe_allow_html=True)

