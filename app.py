import streamlit as st
import pandas as pd

# Function to calculate emissions
def calculate_emissions(data):
    # Emission factors tailored for Pakistan (kg CO2 per unit)
    factors = {
        'electricity': 0.38,  # kg CO2 per kWh (Pakistan energy mix)
        'gas': 2.0,  # kg CO2 per cubic meter (Natural Gas)
        'fuel': 2.7,  # kg CO2 per liter (Petrol/Diesel)
        'flights': 200,  # kg CO2 per flight (domestic estimate)
        'food': 0.0015,  # kg CO2 per PKR spent on food and drink products
        'pharmaceuticals': 0.0012,
        'clothing': 0.0013,  # kg CO2 per PKR spent on clothing, textiles, and shoes
        'paper_products': 0.0009,  # kg CO2 per PKR spent on paper products
        'computers_it': 0.0018,
        'electronics': 0.0020,  # TV, radio, and phone equipment
        'vehicles': 0.0025,  # Motor vehicles (not including fuel costs)
        'furniture': 0.0014,
        'hospitality': 0.0016,  # Hotels, restaurants, and pubs
        'telecom': 0.0008,  # Telephone and mobile phone call costs
        'finance': 0.0011,  # Banking and finance (mortgage, loan interest payments)
        'insurance': 0.0007,
        'education': 0.0006,
        'recreation': 0.0012  # Recreational, cultural, and sporting activities
    }
    
    # Vehicle-specific emission factors (kg CO2 per km)
    vehicle_factors = {
        'Car (Petrol)': 0.35,
        'Car (Diesel)': 0.28,
        'Motorcycle': 0.12,
        'Bus': 0.05,
        'Rickshaw': 0.15
    }
    
    total_emissions = sum(data[key] * factors.get(key, 0) for key in data if key in factors)
    
    if 'vehicles' in data:
        for vehicle in data['vehicles']:
            total_emissions += vehicle['miles_driven'] * vehicle_factors.get(vehicle['vehicle_type'], 0)
    
    return total_emissions / 1000  # Convert kg to metric tons

# Streamlit UI
st.set_page_config(page_title='Carbon Footprint Calculator - Pakistan', layout='wide')
st.title('🌍 Pakistan Carbon Footprint Calculator')
st.sidebar.header("Navigation")

# User inputs in different tabs
categories = ["Household", "Transport", "Secondary"]
tab1, tab2, tab3 = st.tabs(categories)

user_data = {}

# Household Tab
with tab1:
    st.header("🏠 Household Emissions")
    user_data['electricity'] = st.number_input("Electricity Usage (kWh per year)", min_value=0, value=3500)
    user_data['gas'] = st.number_input("Natural Gas Usage (cubic meters per year)", min_value=0, value=1200)

# Transport Tab
with tab2:
    st.header("🚗 Transport Emissions")
    user_data['vehicles'] = []
    num_vehicles = st.number_input("Number of Vehicles", min_value=0, value=1, step=1)
    for i in range(num_vehicles):
        st.subheader(f"Vehicle {i+1}")
        vehicle_type = st.selectbox(f"Select Vehicle Type {i+1}", ["Car (Petrol)", "Car (Diesel)", "Motorcycle", "Bus", "Rickshaw"], key=f'vehicle_type_{i}')
        miles_driven = st.number_input(f"Kilometers Driven Per Year (Vehicle {i+1})", min_value=0, value=15000, key=f'miles_driven_{i}')
        user_data['vehicles'].append({'vehicle_type': vehicle_type, 'miles_driven': miles_driven})
    
    user_data['fuel'] = st.number_input("Fuel Consumption (liters per year)", min_value=0, value=800)
    user_data['flights'] = st.number_input("Number of Domestic Flights Per Year", min_value=0, value=1)

# Secondary Tab
with tab3:
    st.header("🛍️ Secondary Emissions")
    user_data['food'] = st.number_input("Annual Spending on Food & Drink (PKR)", min_value=0, value=600000)
    user_data['pharmaceuticals'] = st.number_input("Annual Spending on Pharmaceuticals (PKR)", min_value=0, value=200000)
    user_data['clothing'] = st.number_input("Annual Spending on Clothes & Shoes (PKR)", min_value=0, value=300000)
    user_data['paper_products'] = st.number_input("Annual Spending on Paper Products (PKR)", min_value=0, value=100000)
    user_data['computers_it'] = st.number_input("Annual Spending on Computers & IT (PKR)", min_value=0, value=500000)
    user_data['electronics'] = st.number_input("Annual Spending on TV, Radio, Phone Equipment (PKR)", min_value=0, value=400000)
    user_data['vehicles'] = st.number_input("Annual Spending on Motor Vehicles (PKR)", min_value=0, value=800000)
    user_data['furniture'] = st.number_input("Annual Spending on Furniture (PKR)", min_value=0, value=300000)
    user_data['hospitality'] = st.number_input("Annual Spending on Hotels, Restaurants, Pubs (PKR)", min_value=0, value=500000)
    user_data['telecom'] = st.number_input("Annual Spending on Telephone Calls (PKR)", min_value=0, value=150000)
    user_data['finance'] = st.number_input("Annual Spending on Banking & Finance (PKR)", min_value=0, value=400000)
    user_data['insurance'] = st.number_input("Annual Spending on Insurance (PKR)", min_value=0, value=200000)
    user_data['education'] = st.number_input("Annual Spending on Education (PKR)", min_value=0, value=600000)
    user_data['recreation'] = st.number_input("Annual Spending on Recreation & Sports (PKR)", min_value=0, value=350000)

# Calculate Total Emissions
if st.button("Calculate My Carbon Footprint"):
    total_co2 = calculate_emissions(user_data)
    st.success(f"🌱 Your estimated annual carbon footprint is **{total_co2:.2f} metric tons of CO₂**.")
