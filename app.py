import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import streamlit.components.v1 as components
import pandas as pd
from geopy.distance import geodesic
import base64
from scipy import stats
import numpy as np


# CSS for scroll blur effect
st.markdown("""
<style>
.scroll-section {
    transition: all 0.3s ease;
    filter: blur(0px);
    opacity: 1;
    transform: scale(1);
}

.scroll-section.blur-out {
    filter: blur(6px);
    opacity: 0;
    transform: scale(0.5);
}
</style>
""", unsafe_allow_html=True)


# JavaScript to blur content leaving the visible window
components.html("""
<script>
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) {
      entry.target.classList.add("blur-out");
    } else {
      entry.target.classList.remove("blur-out");
    }
  });
}, { threshold: 0.1 });
const sections = parent.document.querySelectorAll('.scroll-section');
sections.forEach(el => observer.observe(el));
</script>
""", height=0) 



def expander_style():
        return st.markdown("""
        <style>
        details summary {
            color: #333;
            transition: color 0.2s ease;
        }

        details:hover summary {
            color: #2E8B57 !important;
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

def tabs_style():
    return st.markdown("""
        <style>
                       
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            gap: 5px !important;
            background-color: #90EE90 !important;
            justify-content: center;
            overflow-x: auto;
            white-space: nowrap;
            max-width: 98%;
            border-radius: 20px;
            padding: 0;
            margin: auto;
            width: fit-content;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 10px 40px;
            background-color: #90EE90;
            border-radius: 20px 20px 20px 20px;
            margin-right: 0.5px;
            transition: all 0.3s ease-in-out;
        }
                       
        .stTabs [data-baseweb="tab"] > div:hover {
            font-size: 16px !important;
            font-weight: bold;
            transition: font-size 0.3s ease-in-out;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #4CAF50;
            font-weight: bold;
            color: white;         
        }

        .stTabs [aria-selected="true"] {
            background-color: #4CAF50 !important;
            color: white !important;
            font-weight: bold;
            box-shadow: none !important;
            border-bottom: none !important;
        }
        
        div[data-baseweb="tab-highlight"] {
            background-color: transparent !important;
        }

        div[data-baseweb="tab-border"] {
            background-color: transparent !important;
        }
                       
        .stTabs::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

def selectbox_style():
    st.markdown("""
        <style>
                
        .stSelectbox > div {
            border-radius: 12px !important;
            border: none !important;
            background-color: none !important;
            padding: 6px 10px !important;
        }

        .stSelectbox > div:hover {
            box-shadow: none;       
        }

        .stSelectbox div[data-baseweb="select"] > div:first-child {
            background-color: #fcfcfc;
            border-radius: 10px;
            border: 1.2px solid #4CAF50;
        }

        .stSelectbox [data-baseweb="select"] > div:focus {
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }

        .stSelectbox input:focus {
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }

        .stSelectbox [data-baseweb="option"] {
            font-size: 16px !important;
            color: #4CAF50 !important;
            padding: 10px 14px !important;
        }

        .stSelectbox input {
            color: #4CAF50 !important;
            font-size: 16px !important;
        }

        .stSelectbox svg {
            stroke: #4CAF50 !important;
            width: 20px !important;
            height: 20px !important;
            transition: transform 0.5s ease-in-out;
        }
        
        .stSelectbox > div > div > svg {
            transform: rotate(180deg);
        }
        </style>
    """, unsafe_allow_html=True)

def radio_style(margin):
    st.markdown(f"""
        <style>
        /* Center radio buttons */
        .stRadio > div {{
            justify-content: center;
            margin-left: {margin}px;
        }}
        
        label[data-baseweb="radio"] {{
            background-color: #fafafa;
            padding: 8px 10px;
            border-radius: 15px;
            margin: 10px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }}
    </style>
    """, unsafe_allow_html=True)

def calculate_emissions(data):
    factors = {
        'electricity': 0.5004, # kg CO2e per kWh
        'gas': 2.2, # kg CO2e per m³
        'fuel': 2.7, # kg CO2e per litre of petrol
        'bus': 0.1234, # kg CO2e per km per passenger
        'flights': 0.115, # kg CO2e per km per passenger
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
    total_household_emissions = (electricity * factors['electricity']) + (gas * factors['gas'])
    household_emissions = total_household_emissions / people

    emissions = {
        'Household': household_emissions / 1000,
        'Cars': sum((c['miles_driven'] / c['fuel_efficiency']) * factors['fuel'] for c in data.get('cars', [])) / 1000,
        'Motorcycle': sum((b['miles_driven'] / b['fuel_efficiency']) * factors['fuel'] for b in data.get('motorcycle', [])) / 1000,
        'Bus': data.get('bus', 0) * factors['bus'] / 1000,
        'Flights': data.get('flight_distance', 0) * factors['flights']/1000,
        'Secondary': sum(data.get(k, 0) for k in ['food', 'clothing', 'electronics', 'furniture', 'recreation']) / 1000
    }

    total = sum(emissions.values())  # to metric tonnes
    return emissions, total

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def user_percentile(total_emissions):
    # Simulate realistic income-based emissions distribution
    np.random.seed(42)

    low_income = np.random.normal(loc=0.9, scale=1.8, size=5000)        # 50%
    middle_income = np.random.normal(loc=2.1, scale=1, size=4000)       # 40%
    high_income = np.random.normal(loc=9, scale=3, size=1000)           # 10%

    pakistan_emissions = np.concatenate([low_income, middle_income, high_income])
    pakistan_emissions = pakistan_emissions[pakistan_emissions > 0]

    user_percentile = stats.percentileofscore(pakistan_emissions, total_emissions)

    return max(user_percentile, 1)

image_base64 = get_base64_image("footprint.png")

######################### Main Code #########################

st.set_page_config(page_title="🇵🇰 Carbon Footprint Calculator", layout="wide")

# Use markdown for the title with the effect
st.markdown("""
<style>
            .block-container {
                    padding-top: -500px;
                    padding-bottom: 0rem;
                    padding-left: 1em;
                    padding-right: 1rem;
                }
</style>
<div class="scroll-section">
    <h1>🇵🇰 Carbon Footprint Calculator</h1>
    <div style='font-size: 1.5rem; font-weight: 500; margin-bottom: 0.5rem; color: #222;'>
        Your personal carbon footprint dashboard!
    </div>
            
</div>
""", unsafe_allow_html=True)

# st.title("🇵🇰 Pakistan Carbon Footprint Calculator")

# st.markdown("""
#     <div style='font-size: 1.5rem; font-weight: 500; margin-bottom: 0.5rem; color: #222;'>
#         Your personal carbon footprint dashboard!
#     </div>
# """, unsafe_allow_html=True)

tabs_style()         
tabs = st.tabs(["Household", "Transport", "Secondary", "Total"])

user_data = {}

# --- Energy Tab ---
with tabs[0]:
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>⚡ Energy Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Add your household energy use details to estimate yearly CO₂e emissions.</h4>",
        unsafe_allow_html=True
    )
    _, col2, _ = st.columns(3)
    with col2:
        people_count = st.number_input("How many people live in your household?", min_value=1, value=1, step=1, key='people_count')
        user_data['people_count'] = people_count
    
    expander_style()
    with st.expander("**➕ Electricity**"):
        col1, col2, col3 = st.columns([1.8, 2, 1])
        with col2:
            radio_style(95)
            st.markdown("<h5 style='text-align: left;'>Do you have solar installed in your house?</h5>", unsafe_allow_html=True)
            is_solar = st.radio("", 
                                options=["Yes", "No"], 
                                index=1, 
                                key="is_solar",
                                horizontal=True,
                                label_visibility="collapsed")
        if is_solar == "No":
            net_electricty = st.number_input("Total household electricity consumption this year (units)", min_value=0, value=0, placeholder="Enter the number of units e.g. 10,000", format="%d")
            user_data['electricity'] = net_electricty
        else:
            solar_units = st.number_input("Total units generated by solar this year", 
                                            min_value=0, value=0, 
                                            placeholder="Enter the number of units e.g. 7,000", 
                                            format="%d")
            electricity_consumption = st.number_input("Total household electricity consumption this year (units)", min_value=0, value=0, placeholder="Enter the number of units e.g. 10,000", format="%d")
            net_electricty = electricity_consumption - solar_units
            
            user_data['electricity'] = max(net_electricty, 0)
        elec_emissions = (user_data['electricity'] * 0.0005004) / people_count
        
        st.markdown(f"""
                <div style='font-size: 1.2rem; font-weight: normal;'>
                    Estimated Emissions From Electricity Consumption: <span style='color:#4CAF50'>{elec_emissions:.2f}</span> tCO₂e
                </div>
            """, unsafe_allow_html=True)
    
    expander_style()
    with st.expander("**➕ Natural Gas**"):
            gas_consumption = st.number_input("Natural Gas (m³)", min_value=0, value=0, placeholder='e.g. 3,500', format="%d")
            user_data['gas'] = gas_consumption
            gas_emissions = (gas_consumption * 0.0022) / people_count
            st.markdown(f"""
                <div style='font-size: 1.2rem; font-weight: normal;'>
                    Estimated Emissions From Natural Gas Consumption: <span style='color:#4CAF50'>{gas_emissions:.2f}</span> tCO₂e
                </div>
            """, unsafe_allow_html=True)


    if user_data['electricity'] is None or user_data['gas'] is None:
        st.markdown(""" ⚠️ Please enter both electricity and gas usage to calculate household emissions.""")
    elif isinstance(user_data['electricity'], (int, float)) and isinstance(user_data['gas'], (int, float)):
        household_emissions = calculate_emissions(user_data)[0]['Household']
        st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"⚡ Your Energy Carbon Footprint is <span style='color:#d43f3a'>{household_emissions:.2f}</span> tCO₂e</h4>",
        unsafe_allow_html=True
    )

# --- Transport Tab ---
with tabs[1]:
    # Page Title
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🚘 Transport Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Add your transport details to estimate yearly CO₂e emissions.</h4>",
        unsafe_allow_html=True
    )

    # CAR SECTION
    with st.container():
        st.markdown("### 🚗 Cars")

        user_data['cars'] = []

        expander_style()
        with st.expander("**➕ Add car details**"):
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
            st.markdown(f"""
                <div style='font-size: 1.2rem; font-weight: normal;'>
                    Estimated Emissions for Your Car Travel: <span style='color:#4CAF50'>{car_emissions:.2f}</span> tCO₂e
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
                <div style='font-size: 1.2rem; font-weight: normal;'>
                    Estimated Emissions for Your Motorcycle Travel: <span style='color:#4CAF50'>{bike_emissions:.2f}</span> tCO₂e
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
                <div style='font-size: 1.2rem; font-weight: normal;'>
                    Estimated Emissions for Your Bus Travel: <span style='color:#4CAF50'>{bus_emissions:.2f}</span> tCO₂e
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
        with st.expander("**➕ Add flight details**"):
            # Create three columns and center the radio button in the middle one
            _, col2, _ = st.columns([1.8, 2, 1])

            with col2:
                st.markdown("<h5 style='text-align: left;'>Have you taken a flight this year?</h5>", unsafe_allow_html=True)
                radio_style(50)
                flights_taken = st.radio(
                    label="",
                    options=["Yes", "No"],
                    index=1,
                    horizontal=True,
                    label_visibility="collapsed"
                )
            
            if flights_taken == "No":
                flight_distance = 0
            else:
                # Select number of legs in the trip
                num_legs = st.number_input("How many destinations are in your trip?", min_value=1, max_value=20, value=1, step=1, key="num_legs")

                round_trip_flags = []
                legs = []

                st.markdown("### Trip Details")
                for i in range(num_legs):
                    st.markdown(f"**Leg {i + 1}**")
                    col1, col2, col3 = st.columns([4, 4, 2])
                    with col1:
                        dep = st.selectbox(f"Departure City (Leg {i + 1})", options=sorted(list(airports.keys())), index=None, placeholder='Choose your departure city', key=f"dep_{i}")
                    with col2:
                        arrival_options = sorted([airport for airport in airports.keys() if airport != dep])
                        arr = st.selectbox(f"Arrival City (Leg {i + 1})", options=arrival_options, index=None, placeholder="Choose your arrival city", key=f"arr_{i}")
                    with col3:
                        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
                        is_round = st.checkbox("Return?", key=f"return_{i}", value=True)

                    legs.append((dep, arr))
                    round_trip_flags.append(is_round)

                if arr == None or dep == None:
                    flight_distance = 0
                else:
                    flight_distance = 0
                    for (dep, arr), is_round in zip(legs, round_trip_flags):
                        if dep != arr:
                            dist_km = geodesic(airports[dep], airports[arr]).km
                            if is_round:
                                dist_km *= 2
                            flight_distance += dist_km
            
            # Store flight emissions in user_data
            user_data['flight_distance'] = flight_distance
            flight_emissions = calculate_emissions(user_data)[0]['Flights']

            st.markdown(f"""
                <div style='font-size: 1.2rem; font-weight: normal;'>
                    Estimated Emissions for Your Air Travel: <span style='color:#4CAF50'>{flight_emissions:.2f}</span> tCO₂e
                </div>
            """, unsafe_allow_html=True)


    # TOTAL TRANSPORT EMISSIONS
    vehicle_emissions = car_emissions + bike_emissions + bus_emissions + flight_emissions
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🚗 Your Transportation Carbon Footprint is <span style='color:#d43f3a'>{vehicle_emissions:.2f}</span> tCO₂e</h4>",
        unsafe_allow_html=True
    )

# --- Secondary Emissions Tab ---
with tabs[2]:
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🛍️ Secondary Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Estimate your yearly CO₂ emissions from lifestyle choices.</h4>",
        unsafe_allow_html=True
    )

    # --- EPA Emission Factors ---
    diet_emission_factors = {
        "Meat-heavy (mutton/beef)": 3.3,
        "Meat-heavy (chicken)": 1.9,
        "Average (mixed)": 2.5,
        "Vegetarian": 1.7,
        "Vegan": 1.5
    }

    device_emission_factor = 0.35
    emission_per_pkr = 0.00089

    # --- Spending Ranges ---
    spending_ranges = {
        "0 PKR": 0,
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
    electronic_emission = 0.0017
    expander_style()
    with st.expander("**📱 How many new electronic devices did you purchase this year?**"):
        devices = st.slider("Number of new devices (phones, laptops, etc.):", 0, 10, 0, key="device_count")
        user_data['electronics'] = devices * device_emission_factor * 1000  # convert to kg

    # --- Clothing ---
    clothing_emission = 0.007
    expander_style()
    with st.expander("**👕 Clothing Spending**"):
        selectbox_style()
        choice = st.selectbox("Select your yearly spending on clothing:", list(spending_ranges.keys()), index=0, key="clothing_range")
        user_data['clothing'] = spending_ranges[choice] * clothing_emission

    # --- Furniture ---
    furniture_emission = 0.0014
    expander_style()
    with st.expander("**🪑 Furniture Spending**"):
        selectbox_style()
        choice = st.selectbox("Select your yearly spending on furniture:", list(spending_ranges.keys()), index=0, key="furniture_range")
        user_data['furniture'] = spending_ranges[choice] * emission_per_pkr

    # --- Recreation ---
    recreation_emission = 0.0009
    expander_style()
    with st.expander("**🎮 Recreation Spending**"):
        selectbox_style()
        choice = st.selectbox("Select your yearly spending on recreation (travel, entertainment):", list(spending_ranges.keys()), index=0, key="recreation_range")
        user_data['recreation'] = spending_ranges[choice] * emission_per_pkr

    # --- Result ---
    sec_emissions = calculate_emissions(user_data)[0]['Secondary']
    st.markdown(
        f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
        f"🛒 Your Secondary Carbon Footprint is <span style='color:#d43f3a'>{sec_emissions:.2f}</span> tCO₂e</h4>",
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

    if total_emissions < 6.7:
        st.markdown("<div class='main-title'>🎉 Well done!</div>", unsafe_allow_html=True)
        st.markdown("Your annual footprint is **below the global average**. Keep it up!")
    else:
        st.markdown("<div class='main-title'>🚨 Heads up!</div>", unsafe_allow_html=True)
        st.markdown("Your annual footprint is **above the global average**. Check how much of a differnence can your bring with small changes in your lifestyle.")
    
    col1, col2, col3 = st.columns([2, 1, 1], gap='small')
    with col1:
        st.markdown(f"""
                    <style>
                        .result-box {{
                            background-color: #FFD43B;
                            border-radius: 10px;
                            text-align: center;
                            min-height: 319px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            position: relative;
                            overflow: hidden;
                        }}

                        .result-box::before {{
                            content: "";
                            background-image: url("data:image/png;base64,{image_base64}");
                            background-repeat: no-repeat;
                            background-position: center;
                            background-size: 350px;
                            opacity: 0.1;
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            z-index: 0;
                        }}

                        .result-box > div {{
                            position: relative;
                            z-index: 1;
                        }}
                    </style>
                """, unsafe_allow_html=True)
                    
        st.markdown(f"""
            <div class='result-box'>
                <div style='font-size: 24px;'><b>Your Annual Carbon Footprint</b></div>
                <div style='font-size: 65px; font-weight: bold;'>{total_emissions}
                <span style='font-size: 24px; font-weight: normal;'> tCO₂e</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='black-box'>
                <div style='font-size: 16px;'>National Average Carbon Footprint</div>
                <div style='font-size: 36px; font-weight: bold;'>2.1 tCO₂e</div>
                <div style='font-size: 16px;'>per capita</div>
            </div>
            <div style='height: 20px;'></div>
            <div class='black-box'>
                <div style='font-size: 16px;'>Global Average</div>
                <div style='font-size: 36px; font-weight: bold;'>6.7 tCO₂e</div>
                <div style='font-size: 16px;'>per capita</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style='height: 17px;'></div>
            <div class='grey-box'>
                <div style='font-size: 16px;'>Your Carbon Footprint is</div>
                <div style='font-size: 36px; font-weight: bold;'>
                    {round(total_emissions/6.7 * 100)}
                    <span style='font-size: 24px;'>%</span>
                </div>
                <div style='font-size: 16px;'>of the global average</div>
            </div>

            <div style='height: 20px;'></div>

            <div class='grey-box'>
                <div style='font-size: 16px;'>Your Carbon Foorprint is more than</div>
                <div style='font-size: 36px; font-weight: bold;'>
                    {min(round(user_percentile(total_emissions), 1), 99)}
                    <span style='font-size: 24px;'>%</span>
                    <div style='font-size: 16px; font-weight: normal;'>of Pakistan's population</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)

    st.markdown("<div class='main-title'>Let's break it down...</div>", unsafe_allow_html=True)
    st.markdown(f"<h6 style='font-size: 16px;'>Your footprint is equal to <b>{total_emissions} tCO₂e</b></h6>", unsafe_allow_html=True)

    colA, colB, colC = st.columns(3, gap='small')
    with colA:
        if household_emissions != 0:
            st.markdown(f"""
                <div style='height: 17px;'></div>
                <div class='category-box' style='background-color: #1A237E;'>
                    <div style='font-size: 24px; color: #fafafa;'><b>⚡ Household</b></div>
                    <div style='color: #fafafa;'>
                        Your consumption is equal to 
                        <span style='font-size: 24px;'><b>{household_emissions:.2f}</b></span>
                        tCO₂e
                    </div>
                    <div style='height: 10px;'></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='height: 17px;'></div>
                <div class='category-box' style='background-color: #1A237E;'>
                    <div style='font-size: 24px; color: #fafafa;'><b>⚡ Household</b></div>
                    <div style='color: #fafafa;'>
                        Your consumption is equal to 
                        <span style='font-size: 24px;'><b>0</b></span>
                        tCO₂e
                    </div>
                    <div style='height: 10px;'></div>
                </div>
            """, unsafe_allow_html=True)

    with colB:
        if vehicle_emissions != 0:
            st.markdown(f"""
                <div style='height: 17px;'></div>
                <div class='category-box' style='background-color: #1B5E20;'>
                    <div style='font-size: 24px; color: #ffffff;'><b>🚗 Transport</b></div>
                    <div style='color: #fafafa;'>
                        Your consumption is equal to 
                        <span style='font-size: 24px;'><b>{vehicle_emissions:.2f}</b></span>
                        tCO₂e
                    </div>
                    <div style='height: 10px;'></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='height: 17px;'></div>
                <div class='category-box' style='background-color: #1B5E20;'>
                    <div style='font-size: 24px; color: #ffffff;'><b>🚗 Transport</b></div>
                    <div style='color: #fafafa;'>
                        Your consumption is equal to 
                        <span style='font-size: 24px;'><b>0</b></span>
                        tCO₂e
                    </div>
                    <div style='height: 10px;'></div>
                </div>
            """, unsafe_allow_html=True)

    with colC:
        if sec_emissions != 0:
            st.markdown(f"""
                <div style='height: 17px;'></div>
                <div class='category-box' style='background-color: #AD1457;'>
                    <div style='font-size: 24px; color: #ffffff;'><b>🛒 Secondary</b></div>
                    <div style='color: #fafafa;'>
                        Your consumption is equal to 
                        <span style='font-size: 24px;'><b>{sec_emissions:.2f}</b></span>
                        tCO₂e
                    </div>
                    <div style='height: 10px;'></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='height: 17px;'></div>
                <div class='category-box' style='background-color: #AD1457;'>
                    <div style='font-size: 24px; color: #ffffff;'><b>🛒 Secondary</b></div>
                    <div style='color: #fafafa;'>
                        Your consumption is equal to 
                        <span style='font-size: 24px;'><b>0</b></span>
                        tCO₂e
                    </div>
                    <div style='height: 10px;'></div>
                </div>
            """, unsafe_allow_html=True)

