import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to calculate emissions
def calculate_emissions(data):
    factors = {
        'electricity': 0.5004,
        'gas': 2.2,
        'fuel': 2.7,
        'flights': 200,
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
    fuel_emission_factor = 2.7

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

    emissions['Bus'] = data.get('bus', 0) * 0.05

    emissions['Secondary'] = sum(data.get(key, 0) * factors.get(key, 0)
                                 for key in factors if key not in ['electricity', 'gas', 'fuel', 'flights'])

    total_emissions = sum(emissions.values()) / 1000  # kg to metric tons
    return emissions, total_emissions

# Streamlit UI
st.set_page_config(page_title='🌱 Carbon Footprint Calculator')
st.title('🌍 Pakistan Carbon Footprint Calculator')

categories = ["Household", "Vehicles", "Secondary", "Results"]
tab1, tab2, tab3, tab4 = st.tabs(categories)

user_data = {}

# --- Household Tab ---
with tab1:
    st.markdown("### 🏠 Household Emissions")
    user_data['electricity'] = st.number_input("Electricity Usage (kWh per year)", min_value=0, value=10000, format="%d")
    user_data['gas'] = st.number_input("Natural Gas Usage (cubic meters per year)", min_value=0, value=5000, format="%d")

    household_emissions = calculate_emissions(user_data)[0]['Household'] / 1000
    st.metric("Household Emissions", value=f"{household_emissions:,.2f} metric tons CO₂")

# --- Vehicle Emissions Tab ---
with tab2:
    st.markdown("## 🚘 Vehicle Emissions")
    st.markdown(
        """
        Efficiently track your emissions from all personal vehicles below. 
        Metrics update instantly as you enter your data.
        """
    )

    # CAR SECTION
    with st.container():
        st.markdown("### 🚗 Cars")
        with st.expander("➕ Add your car details"):
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
        car_emissions = calculate_emissions(user_data)[0]['Cars'] / 1000
        st.metric(label="Car Emissions", value=f"{car_emissions:,.2f} metric tons CO₂")

    st.divider()

    # BIKE/RICKSHAW SECTION
    with st.container():
        st.markdown("### 🏍️ Motorcycles / Rickshaws")
        with st.expander("➕ Add motorcycle or rickshaw details"):
            num_bikes = st.number_input("Number of Motorcycles/Rickshaws", min_value=0, value=1, step=1, key='num_bikes', format="%d")
            user_data['bikes_rickshaw'] = []
            for i in range(num_bikes):
                st.markdown(f"**Motorcycle/Rickshaw {i+1}**", help="Enter annual distance and fuel efficiency")
                cols = st.columns(2)
                with cols[0]:
                    miles = st.number_input("Kilometers Driven Per Year", min_value=0, value=8000, key=f'bike_miles_{i}', format="%d")
                with cols[1]:
                    efficiency = st.number_input("Fuel Efficiency (km/l)", min_value=1.0, value=30.0, key=f'bike_eff_{i}')
                user_data['bikes_rickshaw'].append({'miles_driven': miles, 'fuel_efficiency': efficiency})
        bike_emissions = calculate_emissions(user_data)[0]['Bikes/Rickshaw'] / 1000
        st.metric(label="Motorcycle/Rickshaw Emissions", value=f"{bike_emissions:,.2f} metric tons CO₂")

    st.divider()

    # BUS SECTION
    with st.container():
        st.markdown("### 🚌 Public Bus Travel")
        cols = st.columns(2)
        with cols[0]:
            user_data['bus'] = st.number_input("Kilometers Traveled by Bus Per Year", min_value=0, value=5000, key='bus_km', format="%d")
        with cols[1]:
            st.markdown("")

        bus_emissions = calculate_emissions(user_data)[0]['Bus'] / 1000
        st.metric(label="Bus Emissions", value=f"{bus_emissions:,.2f} metric tons CO₂")

    st.divider()

    # TOTAL VEHICLE EMISSIONS (Optional Summary)
    total_vehicle_emissions = (car_emissions + bike_emissions + bus_emissions)
    st.subheader("🚦 Total Vehicle Emissions")
    st.metric(value=f"{total_vehicle_emissions:,.2f} metric tons CO₂")

# --- Secondary Tab ---
with tab3:
    st.markdown("### 🛍️ Secondary Emissions")
    for category in ['food', 'pharmaceuticals', 'clothing', 'electronics', 'furniture', 'hospitality', 'education', 'recreation']:
        user_data[category] = st.number_input(f"Annual Spending on {category.replace('_', ' ').title()} (PKR)", min_value=0, value=300000, format="%d")

    secondary_emissions = calculate_emissions(user_data)[0]['Secondary'] / 1000
    st.info(f"Secondary Emissions: **{secondary_emissions:,.2f}** metric tons CO₂")

# --- Results Tab ---
with tab4:
    emissions, total_co2 = calculate_emissions(user_data)
    st.success(f"🌱 Your estimated annual carbon footprint is **{total_co2:,.2f} metric tons of CO₂**.")

    # Pie chart
    labels = emissions.keys()
    sizes = emissions.values()
    max_category = max(emissions, key=emissions.get)
    explode = [0.1 if key == max_category else 0 for key in emissions]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90, explode=explode, colors=plt.cm.Paired.colors)
    ax.axis('equal')
    st.pyplot(fig)

    st.markdown(f"#### 🚨 The sector with the highest emissions is: **{max_category}**")

    st.header("📊 Facts")
    st.markdown(
        "* The average footprint for people in Pakistan is **0.98** metric tons\n"
        "* The average for the European Union is about **6.8** metric tons\n"
        "* The global average is about **4.79** metric tons\n"
        "* To avoid a 2℃ rise in global temperatures, the average must fall below **2** metric tons by **2050**"
    )
