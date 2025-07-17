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
        'Household': household_emissions / 1000,
        'Cars': sum((c['miles_driven'] / c['fuel_efficiency']) * factors['fuel'] for c in data.get('cars', [])) / 1000,
        'Motorcycle': sum((b['miles_driven'] / b['fuel_efficiency']) * factors['fuel'] for b in data.get('motorcycle', [])) / 1000,
        'Bus': data.get('bus', 0) * 0.05 / 1000,
        'Secondary': sum(data.get(k, 0) * factors[k] for k in factors if k not in ['electricity', 'gas', 'fuel', 'flights']) / 1000
    }

    total = sum(emissions.values())  # to metric tons
    return emissions, total

st.set_page_config(page_title="Carbon Footprint Calculator", layout="centered")

# Custom styling for Apple-like polish
st.markdown("""
    <style>
        h1, h2, h3 {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            font-weight: 600;
        }
        .block-container {
            padding: 2rem 1rem;
        }
        input {
            font-size: 16px !important;
        }
        button[kind="primary"] {
            background-color: #007AFF;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Page flow setup
pages = [
    "Welcome",
    "Household Emissions",
    "Transport Emissions",
    "Secondary Emissions",
    "Summary"
]

if "page" not in st.session_state:
    st.session_state.page = 0

user_data = st.session_state.get("user_data", {})

# Page logic
page = pages[st.session_state.page]
st.title(page)

if page == "Welcome":
    st.markdown("### Welcome to the Carbon Footprint Calculator")
    st.markdown("Let’s understand how your lifestyle impacts the environment.")

elif page == "Household Emissions":
    electricity = st.number_input("Electricity Usage (kWh/year)", min_value=0, step=100, format="%d")
    gas = st.number_input("Gas Usage (cubic meters/year)", min_value=0, step=10, format="%d")
    user_data['electricity'] = electricity
    user_data['gas'] = gas

elif page == "Transport Emissions":
    st.markdown("### 🚗 Vehicle Usage")
    car_km = st.number_input("Car travel distance (km/year)", min_value=0, step=100, format="%d")
    user_data['car_km'] = car_km

elif page == "Secondary Emissions":
    st.markdown("### 🛍️ Secondary Emissions")
    sec_options = ['Low', 'Medium', 'High']
    sec_choice = st.selectbox("What best describes your overall consumption habits?", sec_options)
    sec_mapping = {'Low': 0.7, 'Medium': 1.0, 'High': 1.5}
    user_data['secondary'] = sec_mapping[sec_choice]

elif page == "Summary":
    st.markdown("### 📊 Your Emission Summary")
    emissions = calculate_emissions(user_data)[0]
    for key, val in emissions.items():
        st.metric(label=key, value=f"{val/1000:,.2f} metric tons CO₂")

    fig, ax = plt.subplots()
    ax.bar(emissions.keys(), [v / 1000 for v in emissions.values()], color='skyblue')
    ax.set_ylabel("Metric Tons CO₂")
    ax.set_title("Emissions Breakdown")
    st.pyplot(fig)

# Save user data back to session
st.session_state["user_data"] = user_data

# Navigation buttons
col1, col2 = st.columns(2)

with col1:
    if st.session_state.page > 0:
        if st.button("← Back"):
            st.session_state.page -= 1

with col2:
    if st.session_state.page < len(pages) - 1:
        if st.button("Next →"):
            st.session_state.page += 1
