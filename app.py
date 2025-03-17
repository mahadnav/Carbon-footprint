import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to calculate emissions
def calculate_emissions(data):
    # Emission factors tailored for Pakistan (kg CO2 per unit)
    factors = {
        'electricity': 0.425,  # kg CO2 per kWh (Pakistan energy mix)
        'gas': 2.2,  # kg CO2 per cubic meter (Natural Gas)
        'fuel': 2.7,  # kg CO2 per liter (Petrol/Diesel)
        'flights': 200,  # kg CO2 per flight (domestic estimate)
        'food': 0.0015,
        'pharmaceuticals': 0.0012,
        'clothing': 0.0013,
        'paper_products': 0.0009,
        'electronics': 0.0020,
        'furniture': 0.0014,
        'hospitality': 0.0016,
        'telecom': 0.0008,
        'insurance': 0.0007,
        'education': 0.0006,
        'recreation': 0.0012
    }
    
    # Fuel-based emission factor (kg CO2 per liter)
    fuel_emission_factor = 2.7  # kg CO2 per liter (Petrol)
    
    emissions = {}
    emissions['Household'] = sum(data.get(key, 0) * factors.get(key, 0) for key in ['electricity', 'gas'])
    
    emissions['Cars'] = sum(
        (car['miles_driven'] / car['fuel_efficiency']) * fuel_emission_factor
        for car in data.get('cars', [])
    )
    
    emissions['Bikes/Rickshaw'] = sum(
        (bike['miles_driven'] / bike['fuel_efficiency']) * fuel_emission_factor
        for bike in data.get('bikes_rickshaw', [])
    )
    
    emissions['Bus'] = data.get('bus', 0) * 0.05  # Emission factor for bus
    
    emissions['Secondary'] = sum(data.get(key, 0) * factors.get(key, 0) for key in factors if key not in ['electricity', 'gas', 'fuel', 'flights'])
    
    total_emissions = sum(emissions.values()) / 1000  # Convert kg to metric tons
    return emissions, total_emissions

# Streamlit UI
st.set_page_config(page_title='🌱 Carbon Footprint Calculator')
st.title('🌍 Pakistan Carbon Footprint Calculator')

# User inputs in different tabs
categories = ["Household", "Cars", "Bikes/Rickshaw", "Bus", "Secondary", "Results"]
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(categories)

user_data = {}

# Household Tab
with tab1:
    st.header("🏠 Household Emissions")
    user_data['electricity'] = st.number_input("Electricity Usage (kWh per year)", min_value=0, value=3500)
    user_data['gas'] = st.number_input("Natural Gas Usage (cubic meters per year)", min_value=0, value=1200)
    if st.button("Calculate Household Emissions"):
        st.write(f"Household Emissions: {calculate_emissions(user_data)[0]['Household'] / 1000:.2f} metric tons CO₂")

# Cars Tab
with tab2:
    st.header("🚗 Car Emissions")
    user_data['cars'] = []
    num_cars = st.number_input("Number of Cars", min_value=0, value=1, step=1)
    for i in range(num_cars):
        st.subheader(f"Car {i+1}")
        miles_driven = st.number_input(f"Kilometers Driven Per Year", min_value=0, value=15000, key=f'car_miles_{i}')
        fuel_efficiency = st.number_input(f"Fuel Efficiency (km per litre)", min_value=1.0, value=12.0, key=f'car_efficiency_{i}')
        user_data['cars'].append({'miles_driven': miles_driven, 'fuel_efficiency': fuel_efficiency})
    if st.button("Calculate Car Emissions"):
        st.write(f"Car Emissions: {calculate_emissions(user_data)[0]['Cars'] / 1000:.2f} metric tons CO₂")

# Bikes/Rickshaw Tab
with tab3:
    st.header("🏍️ Motorcycles")
    user_data['bikes_rickshaw'] = []
    num_bikes = st.number_input("Number of Motorcycles", min_value=0, value=1, step=1)
    for i in range(num_bikes):
        st.subheader(f"Motorcycle {i+1}")
        miles_driven = st.number_input(f"Kilometers Driven Per Year", min_value=0, value=8000, key=f'bike_miles_{i}')
        fuel_efficiency = st.number_input(f"Fuel Efficiency (km per litre)", min_value=1.0, value=30.0, key=f'bike_efficiency_{i}')
        user_data['bikes_rickshaw'].append({'miles_driven': miles_driven, 'fuel_efficiency': fuel_efficiency})
    if st.button("Calculate Motorcycle Emissions"):
        st.write(f"Motorcyle Emissions: {calculate_emissions(user_data)[0]['Bikes/Rickshaw'] / 1000:.2f} metric tons CO₂")

# Bus Tab
with tab4:
    st.header("🚌 Bus Emissions")
    user_data['bus'] = st.number_input("Kilometers Traveled by Bus Per Year", min_value=0, value=5000)
    if st.button("Calculate Bus Emissions"):
        st.write(f"Bus Emissions: {calculate_emissions(user_data)[0]['Bus'] / 1000:.2f} metric tons CO₂")

# Secondary Tab
with tab5:
    st.header("🛍️ Secondary Emissions")
    for category in ['food', 'pharmaceuticals', 'clothing', 'paper_products', 'electronics', 'furniture', 'hospitality', 'telecom', 'insurance', 'education', 'recreation']:
        user_data[category] = st.number_input(f"Annual Spending on {category.replace('_', ' ').title()} (PKR)", min_value=0, value=300000)
    if st.button("Calculate Secondary Emissions"):
        st.write(f"Secondary Emissions: {calculate_emissions(user_data)[0]['Secondary'] / 1000:.2f} metric tons CO₂")

# Results Tab
with tab6:
    if st.button("Calculate My Carbon Footprint"):
        emissions, total_co2 = calculate_emissions(user_data)
        st.success(f"🌱 Your estimated annual carbon footprint is **{total_co2:.2f} metric tons of CO₂**.")

        # Pie chart visualization with explosion of the highest-emission category
        labels = emissions.keys()
        sizes = emissions.values()
        max_category = max(emissions, key=emissions.get)  # Find category with highest emissions
        explode = [0.1 if key == max_category else 0 for key in emissions]  # Explode highest-emission sector
        
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, explode=explode, colors=plt.cm.Paired.colors)
        ax.axis('equal')
        st.pyplot(fig)
        
        # Identify sector with highest emissions
        st.write(f"🚨 The sector with the highest emissions is: **{max_category}**")
