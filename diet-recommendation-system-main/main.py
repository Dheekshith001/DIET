import streamlit as st
import pickle
import pandas as pd
import random

# Load ML model
with open('food_model.pickle', 'rb') as file:
    model = pickle.load(file)

# Load dataset
food_data = pd.read_csv('done_food_data.csv')

# Exclude keywords for vegetarian filtering
exclude_keywords = ['Egg', 'Fish', 'meat', 'beef', 'Chicken', 'Beef', 'Deer', 'lamb', 'crab', 'pork',
                    'Turkey', 'flesh', 'Ostrich', 'Emu', 'cuttelfish', 'Seaweed', 'crayfish', 'shrimp', 'Octopus']

# App title
st.title("Food Recommendation and Prediction App")

# Navigation
page = st.sidebar.selectbox("Go to", ["Home", "Search Foods", "Muscle Gain", "Weight Gain", "Weight Loss"])

# --- Prediction Page ---
if page == "Home":
    st.subheader("Enter your nutritional inputs:")
    input_1 = st.number_input("Input 1")
    input_2 = st.number_input("Input 2")
    input_3 = st.number_input("Input 3")

    if st.button("Predict"):
        try:
            inputs = [[input_1, input_2, input_3]]
            prediction = model.predict(inputs)

            category_map = {
                'Muscle_Gain': 'Muscle Gain',
                'Weight_Gain': 'Weight Gain',
                'Weight_Loss': 'Weight Loss'
            }

            result = category_map.get(prediction[0], 'General food')
            st.success(f"Recommended Category: {result}")
        except Exception as e:
            st.error(f"Error in prediction: {e}")

# --- Common filter UI ---
def food_filters(data):
    veg = st.checkbox("Vegetarian only")
    iron = st.checkbox("High in Iron (>6 mg)")
    calcium = st.checkbox("High in Calcium (>150 mg)")

    if iron:
        data = data[data['Iron_mg'] > 6]
    if calcium:
        data = data[data['Calcium_mg'] > 150]
    if veg:
        data = data[~data['Descrip'].str.contains('|'.join(exclude_keywords), case=False)]
    
    return data

# --- Recommendation Pages ---
if page in ["Muscle Gain", "Weight Gain", "Weight Loss"]:
    category_key = page.replace(" ", "_")
    st.subheader(f"{page} Food Recommendations")

    filtered_data = food_data[food_data['category'] == category_key]
    filtered_data = food_filters(filtered_data)

    if st.button("Get Recommendations"):
        sample = filtered_data['Descrip'].sample(n=min(5, len(filtered_data))).tolist()
        if sample:
            st.write("### Recommended Foods:")
            for food in sample:
                st.write(f"- {food}")
        else:
            st.warning("No foods found with the selected filters.")

# --- Search Page ---
if page == "Search Foods":
    sort_by = st.selectbox("Sort by", options=food_data.columns.tolist(), index=food_data.columns.get_loc("Descrip"))
    sorted_data = food_data.sort_values(by=sort_by)

    st.write("### All Foods")
    st.dataframe(sorted_data)
