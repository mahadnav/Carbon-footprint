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
    transition: all 0.5s ease;
    filter: blur(0px);
    opacity: 1;
    transform: scale(1);
}

.scroll-section.blur-out {
    filter: blur(6px);
    opacity: 0;
    transform: scale(0.8);
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
}, { threshold: 0.25 });
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
    """
    Applies CSS to make the tabs sticky.
    """
    return st.markdown("""
        <style>
            .stTabs [data-baseweb="tab-list"] {
                /* FIX: Makes the tab bar sticky */
                position: sticky;
                top: 0;
                z-index: 999;

                /* Original Styles */
                display: flex;
                gap: 5px !important;
                background-color: #90EE90 !important;
                justify-content: center;
                overflow-x: auto;
                white-space: nowrap;
                max-width: 98%;
                border-radius: 20px;
                padding: 5px 0; /* Added slight vertical padding for better appearance */
                margin: auto;
                width: fit-content;
            }

            .stTabs [data-baseweb="tab"] {
                padding: 10px 40px;
                background-color: #90EE90;
                border-radius: 20px;
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

    low_income = np.random.normal(loc=0.9, scale=1.8, size=5000)      # 50%
    middle_income = np.random.normal(loc=2.1, scale=1, size=4000)     # 40%
    high_income = np.random.normal(loc=9, scale=3, size=1000)         # 10%

    pakistan_emissions = np.concatenate([low_income, middle_income, high_income])
    pakistan_emissions = pakistan_emissions[pakistan_emissions > 0]

    user_percentile = stats.percentileofscore(pakistan_emissions, total_emissions)

    return max(user_percentile, 1)

image_base64 = get_base64_image("footprint.png")

######################### Main Code #########################

st.set_page_config(page_title="🇵🇰 Carbon Footprint Calculator", layout="wide")

# Use markdown for the title with the effect
st.markdown("""
<div class="scroll-section">
    <h1>🇵🇰 Carbon Footprint Calculator</h1>
    <div style='font-size: 1.5rem; font-weight: 500; margin-bottom: 0.5rem; color: #222;'>
        Your personal carbon footprint dashboard!
    </div>

</div>
""", unsafe_allow_html=True)

tabs_style()
tabs = st.tabs(["Household", "Transport", "Secondary", "Total"])

# Initialize user_data in session_state if it doesn't exist
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {
        'people_count': 1,
        'electricity': 0,
        'gas': 0,
        'cars': [],
        'motorcycle': [],
        'bus': 0,
        'flight_distance': 0,
        'food': 0,
        'clothing': 0,
        'electronics': 0,
        'furniture': 0,
        'recreation': 0
    }

# --- Energy Tab ---
with tabs[0]:
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>⚡ Energy Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Add your household energy use details to estimate yearly CO₂e emissions.</h4>",
        unsafe_allow_html=True
    )
    _, col2, _ = st.columns(3)
    with col2:
        people_count = st.number_input("How many people live in your household?", min_value=1, value=st.session_state.user_data.get('people_count', 1), step=1)
        st.session_state.user_data['people_count'] = people_count

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
            st.session_state.user_data['electricity'] = net_electricty
        else:
            solar_units = st.number_input("Total units generated by solar this year",
                                            min_value=0, value=0,
                                            placeholder="Enter the number of units e.g. 7,000",
                                            format="%d")
            electricity_consumption = st.number_input("Total household electricity consumption this year (units)", min_value=0, value=0, placeholder="Enter the number of units e.g. 10,000", format="%d")
            net_electricty = electricity_consumption - solar_units
            st.session_state.user_data['electricity'] = max(net_electricty, 0)

        elec_emissions = (st.session_state.user_data['electricity'] * 0.0005004) / people_count
        st.markdown(f"""
            <div style='font-size: 1.2rem; font-weight: normal;'>
                Estimated Emissions From Electricity Consumption: <span style='color:#4CAF50'>{elec_emissions:.2f}</span> tCO₂e
            </div>
        """, unsafe_allow_html=True)

    expander_style()
    with st.expander("**➕ Natural Gas**"):
        gas_consumption = st.number_input("Natural Gas (m³)", min_value=0, value=0, placeholder='e.g. 3,500', format="%d")
        st.session_state.user_data['gas'] = gas_consumption
        gas_emissions = (gas_consumption * 0.0022) / people_count
        st.markdown(f"""
            <div style='font-size: 1.2rem; font-weight: normal;'>
                Estimated Emissions From Natural Gas Consumption: <span style='color:#4CAF50'>{gas_emissions:.2f}</span> tCO₂e
            </div>
        """, unsafe_allow_html=True)

    if st.session_state.user_data.get('electricity') is None or st.session_state.user_data.get('gas') is None:
        st.markdown(""" ⚠️ Please enter both electricity and gas usage to calculate household emissions.""")
    elif isinstance(st.session_state.user_data.get('electricity', 0), (int, float)) and isinstance(st.session_state.user_data.get('gas', 0), (int, float)):
        household_emissions = calculate_emissions(st.session_state.user_data)[0]['Household']
        st.markdown(
            f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>"
            f"⚡ Your Energy Carbon Footprint is <span style='color:#d43f3a'>{household_emissions:.2f}</span> tCO₂e</h4>",
            unsafe_allow_html=True
        )

# --- Transport Tab ---
with tabs[1]:
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🚘 Transport Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Add your transport details to estimate yearly CO₂e emissions.</h4>",
        unsafe_allow_html=True
    )
    # CARS
    with st.container():
        st.markdown("### 🚗 Cars")
        with st.expander("**➕ Add car details**"):
            num_cars = st.number_input("Number of Cars", min_value=0, value=0, step=1, key='num_cars', format="%d")
            cars_data = []
            for i in range(num_cars):
                st.markdown(f"**Car {i+1}**")
                cols = st.columns(2)
                miles = cols[0].number_input("Kilometers Driven Per Year", min_value=0, value=15000, key=f'car_miles_{i}', format="%d")
                efficiency = cols[1].number_input("Fuel Efficiency (km/l)", min_value=1.0, value=12.0, key=f'car_eff_{i}')
                cars_data.append({'miles_driven': miles, 'fuel_efficiency': efficiency})
            st.session_state.user_data['cars'] = cars_data
            car_emissions = calculate_emissions(st.session_state.user_data)[0]['Cars']
            st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions for Your Car Travel: <span style='color:#4CAF50'>{car_emissions:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)

    # MOTORCYCLES
    with st.container():
        st.markdown("### 🏍️ Motorcycles")
        with st.expander("**➕ Add motorcycle details**"):
            num_bikes = st.number_input("Number of Motorcycles", min_value=0, value=0, step=1, key='num_bikes', format="%d")
            bikes_data = []
            for i in range(num_bikes):
                st.markdown(f"**Motorcycle {i+1}**")
                cols = st.columns(2)
                miles = cols[0].number_input("Kilometers Driven Per Year", min_value=0, value=8000, key=f'bike_miles_{i}', format="%d")
                efficiency = cols[1].number_input("Fuel Efficiency (km/l)", min_value=1.0, value=30.0, key=f'bike_eff_{i}')
                bikes_data.append({'miles_driven': miles, 'fuel_efficiency': efficiency})
            st.session_state.user_data['motorcycle'] = bikes_data
            bike_emissions = calculate_emissions(st.session_state.user_data)[0]['Motorcycle']
            st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions for Your Motorcycle Travel: <span style='color:#4CAF50'>{bike_emissions:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)

    # BUS
    with st.container():
        st.markdown("### 🚌 Public Bus Travel")
        with st.expander("**➕ Add bus travel details**"):
            bus_km = st.number_input("Kilometers Traveled by Bus Per Year", min_value=0, value=0, key='bus_km', format="%d")
            st.session_state.user_data['bus'] = bus_km
            bus_emissions = calculate_emissions(st.session_state.user_data)[0]['Bus']
            st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions for Your Bus Travel: <span style='color:#4CAF50'>{bus_emissions:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)

    # AIR TRAVEL
    with st.container():
        st.markdown("### ✈️ Air Travel")
        # Airports data...
        airports = {
            "Islamabad (ISB)": (33.6167, 73.0991), "Lahore (LHE)": (31.5216, 74.4036), "Karachi (KHI)": (24.9065, 67.1608),
            "Dubai (DXB)": (25.2532, 55.3657), "London Heathrow (LHR)": (51.4700, -0.4543), "New York JFK (JFK)": (40.6413, -73.7781)
            # Add all other airports from your original list here
        }
        with st.expander("**➕ Add flight details**"):
            flights_taken = st.radio("Have you taken a flight this year?", ["Yes", "No"], index=1, horizontal=True)
            flight_distance = 0
            if flights_taken == "Yes":
                num_legs = st.number_input("How many destinations in your trip?", min_value=1, value=1, step=1)
                total_flight_distance = 0
                for i in range(num_legs):
                    st.markdown(f"**Leg {i + 1}**")
                    cols = st.columns([2, 2, 1])
                    dep = cols[0].selectbox(f"Departure City (Leg {i+1})", options=sorted(list(airports.keys())), index=None, key=f"dep_{i}")
                    arr = cols[1].selectbox(f"Arrival City (Leg {i+1})", options=sorted(list(airports.keys())), index=None, key=f"arr_{i}")
                    is_round = cols[2].checkbox("Return?", key=f"return_{i}", value=True)
                    if dep and arr and dep != arr:
                        dist_km = geodesic(airports[dep], airports[arr]).km
                        total_flight_distance += dist_km * 2 if is_round else dist_km
                flight_distance = total_flight_distance
            st.session_state.user_data['flight_distance'] = flight_distance
            flight_emissions = calculate_emissions(st.session_state.user_data)[0]['Flights']
            st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions for Your Air Travel: <span style='color:#4CAF50'>{flight_emissions:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)

    vehicle_emissions = car_emissions + bike_emissions + bus_emissions + flight_emissions
    st.markdown(f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>🚗 Your Transportation Carbon Footprint is <span style='color:#d43f3a'>{vehicle_emissions:.2f}</span> tCO₂e</h4>", unsafe_allow_html=True)

# --- Secondary Emissions Tab ---
with tabs[2]:
    st.markdown(
        "<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🛍️ Secondary Emissions</h2>"
        "<h4 style='color: gray; font-size: 1.15rem;'>Estimate your yearly CO₂ emissions from lifestyle choices.</h4>",
        unsafe_allow_html=True
    )
    diet_emission_factors = {"Meat-heavy (mutton/beef)": 3.3, "Meat-heavy (chicken)": 1.9, "Average (mixed)": 2.5, "Vegetarian": 1.7, "Vegan": 1.5}
    spending_ranges = {"0 PKR": 0, "less than 5,000 PKR": 2500, "5,000 - 10,000 PKR": 7500, "10,000 - 20,000 PKR": 15000, "20,000 - 50,000 PKR": 35000, "50,000 - 100,000 PKR": 75000, "100,000 - 200,000 PKR": 150000, "greater than 200,000 PKR": 250000}
    device_emission_factor = 0.35
    clothing_emission = 0.007
    furniture_emission = 0.0014
    recreation_emission = 0.0009
    emission_per_pkr = 0.00089

    with st.expander("**🍽️ What kind of diet do you follow?**"):
        diet_type = st.radio("Select your diet type", list(diet_emission_factors.keys()), index=2)
        st.session_state.user_data['food'] = diet_emission_factors[diet_type] * 1000

    with st.expander("**📱 How many new electronic devices did you purchase this year?**"):
        devices = st.slider("Number of new devices:", 0, 10, 0)
        st.session_state.user_data['electronics'] = devices * device_emission_factor * 1000

    with st.expander("**👕 Clothing Spending**"):
        choice = st.selectbox("Select yearly spending on clothing:", list(spending_ranges.keys()))
        st.session_state.user_data['clothing'] = spending_ranges[choice] * clothing_emission

    with st.expander("**🪑 Furniture Spending**"):
        choice = st.selectbox("Select yearly spending on furniture:", list(spending_ranges.keys()))
        st.session_state.user_data['furniture'] = spending_ranges[choice] * emission_per_pkr

    with st.expander("**🎮 Recreation Spending**"):
        choice = st.selectbox("Select yearly spending on recreation:", list(spending_ranges.keys()))
        st.session_state.user_data['recreation'] = spending_ranges[choice] * emission_per_pkr

    sec_emissions = calculate_emissions(st.session_state.user_data)[0]['Secondary']
    st.markdown(f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>🛒 Your Secondary Carbon Footprint is <span style='color:#d43f3a'>{sec_emissions:.2f}</span> tCO₂e</h4>", unsafe_allow_html=True)


# --- Results Tab ---
with tabs[3]:
    # Calculate final results right before displaying them
    final_emissions, total_emissions = calculate_emissions(st.session_state.user_data)
    total_emissions = round(total_emissions, 2)
    household_emissions = round(final_emissions['Household'], 2)
    vehicle_emissions = round(final_emissions['Cars'] + final_emissions['Motorcycle'] + final_emissions['Bus'] + final_emissions['Flights'], 2)
    sec_emissions = round(final_emissions['Secondary'], 2)

    st.markdown("""
        <style>
            .main-title { font-size: 36px; color: black; font-weight: bold; }
            .result-box { background-color: #FDD835; padding: 20px; text-align: center; border-radius: 10px; height: 100%; min-height: 200px; display: flex; flex-direction: column; justify-content: center; }
            .black-box { background-color: #212121; color: white; padding: 20px; border-radius: 10px; height: 100%; text-align: center; }
            .grey-box { background-color: #636363; color: white; padding: 20px; border-radius: 10px; height: 100%; text-align: center;}
            .category-box { padding: 20px; border-radius: 10px; text-align: center; color: white; }
        </style>
    """, unsafe_allow_html=True)

    if total_emissions < 6.7:
        st.markdown("<div class='main-title'>🎉 Well done!</div>", unsafe_allow_html=True)
        st.markdown("Your annual footprint is **below the global average**. Keep it up!")
    else:
        st.markdown("<div class='main-title'>🚨 Heads up!</div>", unsafe_allow_html=True)
        st.markdown("Your annual footprint is **above the global average**.")

    col1, col2, col3 = st.columns([2, 1, 1], gap='small')
    with col1:
        st.markdown(f"""
            <div class='result-box'>
                <div style='font-size: 24px;'><b>Your Annual Carbon Footprint</b></div>
                <div style='font-size: 65px; font-weight: bold;'>{total_emissions}
                <span style='font-size: 24px; font-weight: normal;'> tCO₂e</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='black-box' style='margin-bottom: 10px;'>
                <div style='font-size: 16px;'>National Average</div>
                <div style='font-size: 36px; font-weight: bold;'>2.1 tCO₂e</div>
            </div>
            <div class='black-box'>
                <div style='font-size: 16px;'>Global Average</div>
                <div style='font-size: 36px; font-weight: bold;'>6.7 tCO₂e</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class='grey-box' style='margin-bottom: 10px;'>
                <div style='font-size: 16px;'>Your footprint is</div>
                <div style='font-size: 36px; font-weight: bold;'>{round(total_emissions/6.7 * 100)}<span style='font-size: 24px;'>%</span></div>
                <div style='font-size: 14px;'>of the global average</div>
            </div>
            <div class='grey-box'>
                <div style='font-size: 16px;'>More than</div>
                <div style='font-size: 36px; font-weight: bold;'>{min(round(user_percentile(total_emissions), 1), 99)}<span style='font-size: 24px;'>%</span></div>
                <div style='font-size: 14px;'>of Pakistan's population</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>Let's break it down...</div>", unsafe_allow_html=True)

    colA, colB, colC = st.columns(3, gap='small')
    colA.markdown(f"<div class='category-box' style='background-color: #1A237E;'><b>⚡ Household</b><br><span style='font-size: 24px;'><b>{household_emissions}</b></span> tCO₂e</div>", unsafe_allow_html=True)
    colB.markdown(f"<div class='category-box' style='background-color: #1B5E20;'><b>🚗 Transport</b><br><span style='font-size: 24px;'><b>{vehicle_emissions}</b></span> tCO₂e</div>", unsafe_allow_html=True)
    colC.markdown(f"<div class='category-box' style='background-color: #AD1457;'><b>🛒 Secondary</b><br><span style='font-size: 24px;'><b>{sec_emissions}</b></span> tCO₂e</div>", unsafe_allow_html=True)