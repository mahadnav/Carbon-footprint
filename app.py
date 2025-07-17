import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to calculate emissions
def calculate_emissions(data):
    # Emission factors tailored for Pakistan (kg CO2 per unit)
    factors = {
        'electricity': 0.5004,  # kg CO2 per kWh (Pakistan energy mix)
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
categories = ["Household", "Vehicles", "Secondary", "Results"]
tab1, tab2, tab3, tab4 = st.tabs(categories)

user_data = {}

# Household Tab
with tab1:
    st.markdown("### 🏠 Household Emissions")
    user_data['electricity'] = st.number_input("Electricity Usage (kWh per year)", min_value=0, value=10000)
    user_data['gas'] = st.number_input("Natural Gas Usage (cubic meters per year)", min_value=0, value=5000)
    if st.button("Calculate Household Emissions"):
        st.write(f"Household Emissions: {calculate_emissions(user_data)[0]['Household'] / 1000:.2f} metric tons CO₂")

# Vehicle Emissions Tab
with tab2:
    st.markdown("### 🚘 Vehicle Emissions")
    user_data['cars'] = []
    user_data['bikes_rickshaw'] = []

    # Cars Section
    st.subheader("🚗 Cars")
    num_cars = st.number_input("Number of Cars", min_value=0, value=1, step=1, key='num_cars')
    for i in range(num_cars):
        st.markdown(f"**Car {i+1}**")
        miles_driven = st.number_input("Kilometers Driven Per Year (Car)", min_value=0, value=15000, key=f'car_miles_{i}')
        fuel_efficiency = st.number_input("Fuel Efficiency (km per litre) (Car)", min_value=1.0, value=12.0, key=f'car_eff_{i}')
        user_data['cars'].append({'miles_driven': miles_driven, 'fuel_efficiency': fuel_efficiency})

    # Motorcycles/Rickshaw Section
    st.subheader("🏍️ Motorcycles")
    num_bikes = st.number_input("Number of Motorcycles", min_value=0, value=1, step=1, key='num_bikes')
    for i in range(num_bikes):
        st.markdown(f"**Motorcycle {i+1}**")
        miles_driven = st.number_input("Kilometers Driven Per Year (Bike)", min_value=0, value=8000, key=f'bike_miles_{i}')
        fuel_efficiency = st.number_input("Fuel Efficiency (km per litre) (Bike)", min_value=1.0, value=30.0, key=f'bike_eff_{i}')
        user_data['bikes_rickshaw'].append({'miles_driven': miles_driven, 'fuel_efficiency': fuel_efficiency})

    # Bus Section
    st.subheader("🚌 Bus Travel")
    user_data['bus'] = st.number_input("Kilometers Traveled by Bus Per Year", min_value=0, value=5000, key='bus_km')

    if st.button("Calculate Vehicle Emissions"):
        emissions = calculate_emissions(user_data)[0]
        st.write(f"**Car Emissions:** {emissions['Cars'] / 1000:.2f} metric tons CO₂")
        st.write(f"**Motorcycle/Rickshaw Emissions:** {emissions['Bikes/Rickshaw'] / 1000:.2f} metric tons CO₂")
        st.write(f"**Bus Emissions:** {emissions['Bus'] / 1000:.2f} metric tons CO₂")

# Secondary Tab
with tab3:
    st.markdown("### 🛍️ Secondary Emissions")
    for category in ['food', 'pharmaceuticals', 'clothing', 'electronics', 'furniture', 'hospitality', 'education', 'recreation']:
        user_data[category] = st.number_input(f"Annual Spending on {category.replace('_', ' ').title()} (PKR)", min_value=0, value=300000)
    if st.button("Calculate Secondary Emissions"):
        st.write(f"Secondary Emissions: {calculate_emissions(user_data)[0]['Secondary'] / 1000:.2f} metric tons CO₂")

# Results Tab
with tab4:
    if st.button("Calculate My Carbon Footprint"):
        emissions, total_co2 = calculate_emissions(user_data)
        st.success(f"🌱 Your estimated annual carbon footprint is **{total_co2:.2f} metric tons of CO₂**.")

        # Pie chart visualization with explosion of the highest-emission category
        labels = emissions.keys()
        sizes = emissions.values()
        max_category = max(emissions, key=emissions.get)  # Find category with highest emissions
        explode = [0.1 if key == max_category else 0 for key in emissions]  # Explode highest-emission sector
        
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90, explode=explode, colors=plt.cm.Paired.colors)
        ax.axis('equal')
        st.pyplot(fig)
        
        # Identify sector with highest emissions
        st.markdown(f"#### 🚨 The sector with the highest emissions is: **{max_category}**")

        st.header("📊 Facts")
        st.markdown(
        "* The average footprint for people in Pakistan is 0.98 metric tons"
        "\n* The average for the European Union is about 6.8 metric tons"
        "\n* The average worldwide carbon footprint is about 4.79 metric tons"
        "\n* To avoid a 2℃ rise in global temperatures, the average global carbon footprint must be reduced to under 2 metric tons by 2050"
        )
