import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Initialize session state for vehicles
if 'vehicles' not in st.session_state:
    st.session_state['vehicles'] = []

# Function to calculate emissions
def calculate_emissions(data):
    # Emission factors tailored for Pakistan (kg CO2 per unit)
    factors = {
        'electricity': 0.38,  
        'gas': 2.0,  
        'fuel': 2.7,  
        'flights': 200,  
        'food': 0.0015,
        'pharmaceuticals': 0.0012,
        'clothing': 0.0013,
        'paper_products': 0.0009,
        'computers_it': 0.0018,
        'electronics': 0.0020,
        'vehicles': 0.0025,
        'furniture': 0.0014,
        'hospitality': 0.0016,
        'telecom': 0.0008,
        'finance': 0.0011,
        'insurance': 0.0007,
        'education': 0.0006,
        'recreation': 0.0012
    }
    
    # Vehicle emission factors (kg CO2 per km)
    vehicle_factors = {
        'Car (Petrol)': 0.35,
        'Car (Diesel)': 0.28,
        'Motorcycle': 0.12,
        'Bus': 0.05,
        'Rickshaw': 0.15
    }
    
    emissions = {'Household': 0, 'Transport': 0, 'Secondary': 0}

    # Household emissions
    emissions['Household'] = sum(data.get(key, 0) * factors.get(key, 0) for key in ['electricity', 'gas'])
    
    # Transport emissions
    emissions['Transport'] += sum(data.get(key, 0) * factors.get(key, 0) for key in ['fuel', 'flights'])

    # Check for vehicles
    vehicles = data.get('vehicles', [])
    if isinstance(vehicles, list):
        emissions['Transport'] += sum(vehicle.get('miles_driven', 0) * vehicle_factors.get(vehicle.get('vehicle_type', ''), 0) for vehicle in vehicles)

    # Secondary emissions
    emissions['Secondary'] = sum(data.get(key, 0) * factors.get(key, 0) for key in factors if key not in ['electricity', 'gas', 'fuel', 'flights'])
    
    total_emissions = sum(emissions.values()) / 1000  # Convert kg to metric tons
    return emissions, total_emissions

# Streamlit UI
st.set_page_config(page_title='Carbon Footprint Calculator - Pakistan')
st.title('🌍 Pakistan Carbon Footprint Calculator')
st.sidebar.header("Navigation")

# User inputs in different tabs
categories = ["Household", "Transport", "Secondary", "Results"]
tab1, tab2, tab3, tab4 = st.tabs(categories)

user_data = {}

# Household Tab
with tab1:
    st.header("🏠 Household Emissions")
    user_data['electricity'] = st.number_input("Electricity Usage (kWh per year)", min_value=0, value=3500)
    user_data['gas'] = st.number_input("Natural Gas Usage (cubic meters per year)", min_value=0, value=1200)
    
    if st.button("Calculate Household Emissions"):
        household_emissions = calculate_emissions(user_data)[0]['Household'] / 1000
        st.write(f"Household Emissions: **{household_emissions:.2f} metric tons CO₂**")

# Transport Tab
with tab2:
    st.header("🚗 Transport Emissions")
    
    num_vehicles = st.number_input("Number of Vehicles", min_value=0, value=len(st.session_state['vehicles']), step=1)

    for i in range(num_vehicles):
        st.subheader(f"Vehicle {i+1}")
        vehicle_type = st.selectbox(f"Select Vehicle Type {i+1}", 
                                    ["Car (Petrol)", "Car (Diesel)", "Motorcycle", "Bus", "Rickshaw"], 
                                    key=f'vehicle_type_{i}')
        miles_driven = st.number_input(f"Kilometers Driven Per Year (Vehicle {i+1})", 
                                       min_value=0, value=15000, key=f'miles_driven_{i}')
    
    user_data['vehicles'] = st.session_state['vehicles']
    user_data['fuel'] = st.number_input("Fuel Consumption (liters per year)", min_value=0, value=800)
    user_data['flights'] = st.number_input("Number of Domestic Flights Per Year", min_value=0, value=1)
    
    if st.button("Calculate Transport Emissions"):
        transport_emissions = calculate_emissions(user_data)[0][1].value / 1000
        st.write(f"Transport Emissions: **{transport_emissions:.2f} metric tons CO₂**")

# Secondary Tab
with tab3:
    st.header("🛍️ Secondary Emissions")
    
    for category in ['food', 'pharmaceuticals', 'clothing', 'paper_products', 'computers_it', 'electronics', 
                     'vehicles', 'furniture', 'hospitality', 'telecom', 'finance', 'insurance', 'education', 'recreation']:
        user_data[category] = st.number_input(f"Annual Spending on {category.replace('_', ' ').title()} (PKR)", 
                                              min_value=0, value=300000)

    if st.button("Calculate Secondary Emissions"):
        secondary_emissions = calculate_emissions(user_data)[0]['Secondary'] / 1000
        st.write(f"Secondary Emissions: **{secondary_emissions:.2f} metric tons CO₂**")

# Calculate and Display Results
with tab4:
    if st.button("Calculate My Carbon Footprint"):
        emissions, total_co2 = calculate_emissions(user_data)
        st.success(f"🌱 Your estimated annual carbon footprint is **{total_co2:.1f} metric tons of CO₂**.")
        
        # Display category-wise emissions
        st.subheader("Category-wise Carbon Emissions (Metric Tons CO₂)")
        st.write(emissions)
        
        # Plot the emissions
        fig, ax = plt.subplots()
        ax.bar(emissions.keys(), [val / 1000 for val in emissions.values()], color=['blue', 'green', 'orange'])
        ax.set_ylabel("Metric Tons CO₂")
        ax.set_title("Carbon Emissions Breakdown")
        st.pyplot(fig)
