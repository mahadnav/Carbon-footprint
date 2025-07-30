import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import streamlit.components.v1 as components
import pandas as pd
from geopy.distance import geodesic
import base64
from scipy import stats
import numpy as np


# --- CSS AND JAVASCRIPT FOR DISAPPEARING EFFECT ---
st.markdown("""
<style>
.disappearing-section {
    /* Base state of the sections */
    opacity: 1;
    max-height: 1000px; /* A value larger than any individual section */
    transform: translateY(0);
    overflow: hidden;
    transition: opacity 0.6s ease-out, max-height 0.7s ease-in-out, transform 0.6s ease-out, margin 0.7s ease-in-out, padding 0.7s ease-in-out;
}

.disappearing-section.fade-out {
    /* State when the section is scrolled out of view */
    opacity: 0;
    max-height: 0px;
    transform: translateY(-20px);
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    border: none !important; /* Hide borders when faded */
}
</style>
""", unsafe_allow_html=True)

# JavaScript to apply the 'fade-out' class
if 'disappearing_script_injected' not in st.session_state:
    components.html("""
    <script>
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const isAbove = entry.boundingClientRect.y < 0;

        if (!entry.isIntersecting && isAbove) {
          entry.target.classList.add("fade-out");
        } else {
          entry.target.classList.remove("fade-out");
        }
      });
    }, { threshold: 0.0 });

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    const observeSections = () => {
        const sections = parent.document.querySelectorAll('.disappearing-section');
        sections.forEach(el => observer.observe(el));
    }
    
    observeSections();

    const mutationObserver = new MutationObserver(debounce(observeSections, 50));
    mutationObserver.observe(parent.document.body, { childList: true, subtree: true });

    </script>
    """, height=0)
    st.session_state['disappearing_script_injected'] = True
# --- END OF EFFECT CODE ---


def expander_style():
    return st.markdown("""<style>details summary{color:#333;transition:color .2s ease}details:hover summary{color:#2E8B57!important;cursor:pointer}details{margin-bottom:16px;border-radius:6px;border:1px solid #eee;padding:5px}</style>""", unsafe_allow_html=True)

def tabs_style():
    return st.markdown("""<style>.stTabs [data-baseweb=tab-list]{display:flex;gap:5px!important;background-color:#90ee90!important;justify-content:center;overflow-x:auto;white-space:nowrap;max-width:98%;border-radius:20px;padding:0;margin:auto;width:fit-content}.stTabs [data-baseweb=tab]{padding:10px 40px;background-color:#90ee90;border-radius:20px;margin-right:.5px;transition:all .3s ease-in-out}.stTabs [data-baseweb=tab] > div:hover{font-size:16px!important;font-weight:700;transition:font-size .3s ease-in-out}.stTabs [data-baseweb=tab]:hover{background-color:#4caf50;font-weight:700;color:#fff}.stTabs [aria-selected=true]{background-color:#4caf50!important;color:#fff!important;font-weight:700;box-shadow:none!important;border-bottom:none!important}div[data-baseweb=tab-highlight],div[data-baseweb=tab-border]{background-color:transparent!important}.stTabs::-webkit-scrollbar-thumb{background:#ccc;border-radius:4px}</style>""", unsafe_allow_html=True)

def selectbox_style():
    st.markdown("""<style>.stSelectbox > div{border-radius:12px!important;border:none!important;background-color:transparent!important;padding:6px 10px!important}.stSelectbox > div:hover{box-shadow:none}.stSelectbox div[data-baseweb=select] > div:first-child{background-color:#fcfcfc;border-radius:10px;border:1.2px solid #4caf50}.stSelectbox [data-baseweb=select] > div:focus{outline:none!important;box-shadow:none!important;border:none!important}.stSelectbox input:focus{outline:none!important;box-shadow:none!important;border:none!important}.stSelectbox [data-baseweb=option]{font-size:16px!important;color:#4caf50!important;padding:10px 14px!important}.stSelectbox input{color:#4caf50!important;font-size:16px!important}.stSelectbox svg{stroke:#4caf50!important;width:20px!important;height:20px!important;transition:transform .5s ease-in-out}.stSelectbox > div > div > svg{transform:rotate(180deg)}</style>""", unsafe_allow_html=True)

def radio_style(margin):
    st.markdown(f"""<style>.stRadio > div{{justify-content:center;margin-left:{margin}px}}label[data-baseweb=radio]{{background-color:#fafafa;padding:8px 10px;border-radius:15px;margin:10px;font-weight:700;cursor:pointer;transition:background-color .3s ease}}</style>""", unsafe_allow_html=True)

def calculate_emissions(data):
    factors = {'electricity': 0.5004, 'gas': 2.2, 'fuel': 2.7, 'bus': 0.1234, 'flights': 0.115}
    people = max(data.get('people_count', 1), 1)
    electricity = float(data.get('electricity', 0) or 0)
    gas = float(data.get('gas', 0) or 0)
    household_emissions = ((electricity * factors['electricity']) + (gas * factors['gas'])) / people
    emissions = {
        'Household': household_emissions / 1000,
        'Cars': sum((c['miles_driven'] / c['fuel_efficiency']) * factors['fuel'] for c in data.get('cars', [])) / 1000,
        'Motorcycle': sum((b['miles_driven'] / b['fuel_efficiency']) * factors['fuel'] for b in data.get('motorcycle', [])) / 1000,
        'Bus': data.get('bus', 0) * factors['bus'] / 1000,
        'Flights': data.get('flight_distance', 0) * factors['flights'] / 1000,
        'Secondary': sum(data.get(k, 0) for k in ['food', 'clothing', 'electronics', 'furniture', 'recreation']) / 1000
    }
    total = sum(emissions.values())
    return emissions, total

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def user_percentile(total_emissions):
    np.random.seed(42)
    emissions_data = np.concatenate([np.random.normal(loc=0.9, scale=1.8, size=5000), np.random.normal(loc=2.1, scale=1, size=4000), np.random.normal(loc=9, scale=3, size=1000)])
    emissions_data = emissions_data[emissions_data > 0]
    return max(stats.percentileofscore(emissions_data, total_emissions), 1)

######################### Main Code #########################

st.set_page_config(page_title="🇵🇰 Carbon Footprint Calculator", layout="wide")

st.markdown("""
<div class='disappearing-section'>
    <h1>🇵🇰 Carbon Footprint Calculator</h1>
    <div style='font-size: 1.5rem; font-weight: 500; margin-bottom: 0.5rem; color: #222;'>
        Your personal carbon footprint dashboard!
    </div>
</div>
""", unsafe_allow_html=True)

tabs_style()
tabs = st.tabs(["Household", "Transport", "Secondary", "Total"])
user_data = {}

# --- Energy Tab ---
with tabs[0]:
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>⚡ Energy Emissions</h2><h4 style='color: gray; font-size: 1.15rem;'>Add your household energy use details to estimate yearly CO₂e emissions.</h4>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    _, col2, _ = st.columns(3)
    with col2:
        people_count = st.number_input("How many people live in your household?", min_value=1, value=1, step=1, key='people_count')
        user_data['people_count'] = people_count
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    expander_style()
    with st.expander("**➕ Electricity**"):
        col1, col2, col3 = st.columns([1.8, 2, 1])
        with col2:
            radio_style(95)
            st.markdown("<h5 style='text-align: left;'>Do you have solar installed in your house?</h5>", unsafe_allow_html=True)
            is_solar = st.radio("", options=["Yes", "No"], index=1, key="is_solar", horizontal=True, label_visibility="collapsed")
        if is_solar == "No":
            net_electricty = st.number_input("Total household electricity consumption this year (units)", min_value=0, value=0, placeholder="Enter the number of units e.g. 10,000", format="%d")
            user_data['electricity'] = net_electricty
        else:
            solar_units = st.number_input("Total units generated by solar this year", min_value=0, value=0, placeholder="Enter the number of units e.g. 7,000", format="%d")
            electricity_consumption = st.number_input("Total household electricity consumption this year (units)", min_value=0, value=0, placeholder="Enter the number of units e.g. 10,000", format="%d")
            user_data['electricity'] = max(electricity_consumption - solar_units, 0)
        elec_emissions = (user_data.get('electricity', 0) * 0.0005004) / (user_data.get('people_count', 1) or 1)
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions From Electricity Consumption: <span style='color:#4CAF50'>{elec_emissions:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("**➕ Natural Gas**"):
        gas_consumption = st.number_input("Natural Gas (m³)", min_value=0, value=0, placeholder='e.g. 3,500', format="%d")
        user_data['gas'] = gas_consumption
        gas_emissions = (gas_consumption * 0.0022) / (user_data.get('people_count', 1) or 1)
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions From Natural Gas Consumption: <span style='color:#4CAF50'>{gas_emissions:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    if user_data.get('electricity') is not None and user_data.get('gas') is not None:
        household_emissions = calculate_emissions(user_data)[0]['Household']
        st.markdown(f"<h4 style='color: #444; text-align: center; margin-top: 2rem;'>⚡ Your Energy Carbon Footprint is <span style='color:#d43f3a'>{household_emissions:.2f}</span> tCO₂e</h4>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Transport Tab ---
with tabs[1]:
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🚘 Transport Emissions</h2><h4 style='color: gray; font-size: 1.15rem;'>Add your transport details to estimate yearly CO₂e emissions.</h4>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("### 🚗 Cars"):
        num_cars = st.number_input("Number of Cars", min_value=0, value=0, step=1, key='num_cars', format="%d")
        user_data['cars'] = []
        for i in range(num_cars):
            st.markdown(f"**Car {i+1}**", help="Enter annual distance and average efficiency")
            cols = st.columns(2)
            miles = cols[0].number_input("Kilometers Driven Per Year", min_value=0, value=15000, key=f'car_miles_{i}', format="%d")
            efficiency = cols[1].number_input("Fuel Efficiency (km/l)", min_value=1.0, value=12.0, key=f'car_eff_{i}')
            user_data['cars'].append({'miles_driven': miles, 'fuel_efficiency': efficiency})
        car_emissions_val = calculate_emissions(user_data)[0]['Cars']
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions for Your Car Travel: <span style='color:#4CAF50'>{car_emissions_val:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("### 🏍️ Motorcycles"):
        num_bikes = st.number_input("Number of Motorcycles", min_value=0, value=0, step=1, key='num_bikes', format="%d")
        user_data['motorcycle'] = []
        for i in range(num_bikes):
            st.markdown(f"**Motorcycle {i+1}**", help="Enter annual distance and fuel efficiency")
            cols = st.columns(2)
            miles = cols[0].number_input("Kilometers Driven Per Year", min_value=0, value=8000, key=f'bike_miles_{i}', format="%d")
            efficiency = cols[1].number_input("Fuel Efficiency (km/l)", min_value=1.0, value=30.0, key=f'bike_eff_{i}')
            user_data['motorcycle'].append({'miles_driven': miles, 'fuel_efficiency': efficiency})
        bike_emissions_val = calculate_emissions(user_data)[0]['Motorcycle']
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions for Your Motorcycle Travel: <span style='color:#4CAF50'>{bike_emissions_val:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("### 🚌 Public Bus Travel"):
        user_data['bus'] = st.number_input("Kilometers Traveled by Bus Per Year", min_value=0, value=0, key='bus_km', format="%d")
        bus_emissions_val = calculate_emissions(user_data)[0]['Bus']
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions for Your Bus Travel: <span style='color:#4CAF50'>{bus_emissions_val:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("### ✈️ Air Travel"):
        airports = {"Islamabad (ISB)": (33.6167, 73.0991), "Lahore (LHE)": (31.5216, 74.4036), "Karachi (KHI)": (24.9065, 67.1608), "Dubai (DXB)": (25.2532, 55.3657), "Jeddah (JED)": (21.6796, 39.1565), "London Heathrow (LHR)": (51.4700, -0.4543)}
        flights_taken = st.radio("Have you taken a flight this year?", ["Yes", "No"], index=1, horizontal=True)
        flight_distance = 0
        if flights_taken == "Yes":
            num_legs = st.number_input("How many destinations in your trip?", 1, 20, 1)
            legs, round_trip_flags = [], []
            for i in range(num_legs):
                st.markdown(f"**Leg {i + 1}**")
                col1, col2, col3 = st.columns([4, 4, 2])
                dep = col1.selectbox(f"Departure (Leg {i+1})", sorted(list(airports.keys())), index=None, key=f"dep_{i}")
                arr = col2.selectbox(f"Arrival (Leg {i+1})", sorted([a for a in airports if a != dep]), index=None, key=f"arr_{i}")
                is_round = col3.checkbox("Return?", key=f"return_{i}", value=True)
                if dep and arr:
                    dist_km = geodesic(airports[dep], airports[arr]).km
                    flight_distance += dist_km * 2 if is_round else dist_km
        user_data['flight_distance'] = flight_distance
        flight_emissions_val = calculate_emissions(user_data)[0]['Flights']
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: normal;'>Estimated Emissions for Your Air Travel: <span style='color:#4CAF50'>{flight_emissions_val:.2f}</span> tCO₂e</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Secondary Emissions Tab ---
with tabs[2]:
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>🛍️ Secondary Emissions</h2><h4 style='color: gray; font-size: 1.15rem;'>Estimate your yearly CO₂ emissions from lifestyle choices.</h4>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    diet_emission_factors = {"Meat-heavy (mutton/beef)": 3.3, "Meat-heavy (chicken)": 1.9, "Average (mixed)": 2.5, "Vegetarian": 1.7, "Vegan": 1.5}
    spending_ranges = {"0 PKR": 0, "less than 5,000 PKR": 2500, "5,000 - 10,000 PKR": 7500, "10,000 - 20,000 PKR": 15000, "20,000 - 50,000 PKR": 35000, "50,000 - 100,000 PKR": 75000, "100,000 - 200,000 PKR": 150000, "greater than 200,000 PKR": 250000}

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("**🍽️ What kind of diet do you follow?**"):
        if "diet_type" not in st.session_state: st.session_state["diet_type"] = "Average (mixed)"
        cols = st.columns(len(diet_emission_factors))
        for i, (diet, _) in enumerate(diet_emission_factors.items()):
            is_selected = st.session_state["diet_type"] == diet
            bg_color, text_color, border_color = ("#4CAF50", "white", "#4CAF50") if is_selected else ("#f0f0f0", "black", "#ccc")
            with cols[i], stylable_container(key=f"btn_{diet}", css_styles=f"""[data-testid="stButton"] button {{background-color:{bg_color};color:{text_color};border:1px solid {border_color};}}"""):
                if st.button(diet, use_container_width=True):
                    st.session_state["diet_type"] = diet
                    st.rerun()
        user_data['food'] = diet_emission_factors[st.session_state['diet_type']] * 1000
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("**📱 How many new electronic devices did you purchase this year?**"):
        devices = st.slider("Number of new devices (phones, laptops, etc.):", 0, 10, 0, key="device_count")
        user_data['electronics'] = devices * 0.035 * 1000
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("**👕 Clothing Spending**"):
        selectbox_style()
        choice = st.selectbox("Select your yearly spending on clothing:", list(spending_ranges.keys()), index=0, key="clothing_range")
        user_data['clothing'] = spending_ranges[choice] * 0.007
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("**🪑 Furniture Spending**"):
        selectbox_style()
        choice = st.selectbox("Select your yearly spending on furniture:", list(spending_ranges.keys()), index=0, key="furniture_range")
        user_data['furniture'] = spending_ranges[choice] * 0.0014
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    with st.expander("**🎮 Recreation Spending**"):
        selectbox_style()
        choice = st.selectbox("Select your yearly spending on recreation (travel, entertainment):", list(spending_ranges.keys()), index=0, key="recreation_range")
        user_data['recreation'] = spending_ranges[choice] * 0.0009
    st.markdown("</div>", unsafe_allow_html=True)


# --- Final Calculation before rendering last tab ---
all_emissions, total_emissions = calculate_emissions(user_data)
household_emissions = all_emissions['Household']
vehicle_emissions = all_emissions['Cars'] + all_emissions['Motorcycle'] + all_emissions['Bus'] + all_emissions['Flights']
sec_emissions = all_emissions['Secondary']
total_emissions = round(total_emissions, 2)


# --- Results Tab ---
with tabs[3]:
    image_base64 = get_base64_image("footprint.png")
    
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    if total_emissions < 6.7:
        st.markdown("<div class='main-title' style='font-size:36px;font-weight:700;'>🎉 Well done!</div><p>Your annual footprint is <b>below the global average</b>. Keep it up!</p>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='main-title' style='font-size:36px;font-weight:700;'>🚨 Heads up!</div><p>Your annual footprint is <b>above the global average</b>.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1], gap='small')
    with col1:
        st.markdown(f"""<div style='background-color:#FFD43B;border-radius:10px;text-align:center;min-height:319px;display:flex;flex-direction:column;justify-content:center;position:relative;overflow:hidden;'><div style='background-image:url(data:image/png;base64,{image_base64});background-repeat:no-repeat;background-position:center;background-size:350px;opacity:.1;position:absolute;top:0;left:0;right:0;bottom:0;z-index:0;'></div><div style='position:relative;z-index:1;'><div style='font-size:24px;'><b>Your Annual Carbon Footprint</b></div><div style='font-size:65px;font-weight:700;'>{total_emissions}<span style='font-size:24px;font-weight:400'> tCO₂e</span></div></div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='black-box' style='background-color:#212121;color:#fff;padding:20px;border-radius:10px;height:142px;margin-bottom:20px;'><div style='font-size:16px'>National Average</div><div style='font-size:36px;font-weight:700'>2.1 tCO₂e</div><div style='font-size:16px'>per capita</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='black-box' style='background-color:#212121;color:#fff;padding:20px;border-radius:10px;height:142px;'><div style='font-size:16px'>Global Average</div><div style='font-size:36px;font-weight:700'>6.7 tCO₂e</div><div style='font-size:16px'>per capita</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='grey-box' style='background-color:#636363;color:#fff;padding:20px;border-radius:10px;height:142px;margin-bottom:20px;'><div style='font-size:16px'>Your footprint is</div><div style='font-size:36px;font-weight:700'>{round(total_emissions/6.7*100)}<span style='font-size:24px'>%</span></div><div style='font-size:16px'>of the global average</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grey-box' style='background-color:#636363;color:#fff;padding:20px;border-radius:10px;height:142px;'><div style='font-size:16px'>More than</div><div style='font-size:36px;font-weight:700'>{min(round(user_percentile(total_emissions),1),99)}<span style='font-size:24px'>%</span></div><div style='font-size:16px'>of Pakistan's population</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'><hr style='margin: 30px 0;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    st.markdown("<div class='main-title' style='font-size:36px;font-weight:700;'>Let's break it down...</div>", unsafe_allow_html=True)
    st.markdown(f"<h6 style='font-size:16px;'>Your footprint is equal to <b>{total_emissions} tCO₂e</b></h6>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='disappearing-section'>", unsafe_allow_html=True)
    colA, colB, colC = st.columns(3, gap='small')
    with colA:
        st.markdown(f"<div style='background-color:#1A237E;color:#fff;padding:20px;border-radius:10px;text-align:center;height:100%'><div style='font-size:24px'><b>⚡ Household</b></div>Your consumption is equal to <span style='font-size:24px'><b>{household_emissions:.2f}</b></span> tCO₂e</div>", unsafe_allow_html=True)
    with colB:
        st.markdown(f"<div style='background-color:#1B5E20;color:#fff;padding:20px;border-radius:10px;text-align:center;height:100%'><div style='font-size:24px'><b>🚗 Transport</b></div>Your consumption is equal to <span style='font-size:24px'><b>{vehicle_emissions:.2f}</b></span> tCO₂e</div>", unsafe_allow_html=True)
    with colC:
        st.markdown(f"<div style='background-color:#AD1457;color:#fff;padding:20px;border-radius:10px;text-align:center;height:100%'><div style='font-size:24px'><b>🛒 Secondary</b></div>Your consumption is equal to <span style='font-size:24px'><b>{sec_emissions:.2f}</b></span> tCO₂e</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)